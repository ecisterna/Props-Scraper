"""
Utilidades para el DAG de Airflow - Transformación de datos
Este módulo contiene las funciones para limpiar y transformar los datos extraídos
"""

import pandas as pd
import numpy as np
import re
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DataTransformer:
    """Clase para transformar y limpiar datos de propiedades"""
    
    def __init__(self):
        self.price_patterns = {
            'usd': r'USD?\s*[\$]?\s*([\d.,]+)',
            'dolares': r'[\$]?\s*([\d.,]+)',
            'pesos': r'[\$]?\s*([\d.,]+)',
            'number': r'([\d.,]+)'
        }
    
    def clean_price(self, price_str: str) -> Dict[str, Any]:
        """Limpia y extrae información del precio"""
        if not price_str or price_str.lower() in ['consultar', 'consultar precio', 'sin precio']:
            return {
                'precio_numerico': None,
                'moneda': None,
                'precio_original': price_str,
                'precio_valido': False
            }
        
        # Determinar moneda
        moneda = 'USD'
        if any(word in price_str.lower() for word in ['peso', 'ars', '$ar']):
            moneda = 'ARS'
        
        # Extraer número
        precio_numerico = None
        for pattern_name, pattern in self.price_patterns.items():
            match = re.search(pattern, price_str, re.IGNORECASE)
            if match:
                try:
                    # Limpiar el número (quitar puntos de miles, convertir comas a puntos)
                    number_str = match.group(1).replace(',', '').replace('.', '')
                    if len(number_str) > 3:  # Si tiene más de 3 dígitos, los últimos 2-3 pueden ser decimales
                        if ',' in match.group(1):  # Si había coma, probablemente son decimales
                            number_str = number_str[:-2] + '.' + number_str[-2:]
                    precio_numerico = float(number_str)
                    break
                except ValueError:
                    continue
        
        return {
            'precio_numerico': precio_numerico,
            'moneda': moneda,
            'precio_original': price_str,
            'precio_valido': precio_numerico is not None
        }
    
    def extract_surface_area(self, superficie_str: str) -> Optional[float]:
        """Extrae el área en metros cuadrados"""
        if not superficie_str:
            return None
        
        # Buscar números seguidos de m², m2, metros, etc.
        patterns = [
            r'([\d.,]+)\s*m[²2]',
            r'([\d.,]+)\s*metros',
            r'([\d.,]+)\s*mts'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, superficie_str, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', '.'))
                except ValueError:
                    continue
        
        return None
    
    def extract_rooms_bathrooms(self, text: str) -> Dict[str, Optional[int]]:
        """Extrae número de habitaciones y baños"""
        result = {'habitaciones': None, 'banos': None}
        
        if not text:
            return result
        
        # Patrones para habitaciones/ambientes
        room_patterns = [
            r'(\d+)\s*amb',
            r'(\d+)\s*dor',
            r'(\d+)\s*hab',
            r'(\d+)\s*cuarto'
        ]
        
        for pattern in room_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result['habitaciones'] = int(match.group(1))
                    break
                except ValueError:
                    continue
        
        # Patrones para baños
        bathroom_patterns = [
            r'(\d+)\s*baño',
            r'(\d+)\s*bath'
        ]
        
        for pattern in bathroom_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result['banos'] = int(match.group(1))
                    break
                except ValueError:
                    continue
        
        return result
    
    def clean_location(self, location_str: str) -> Dict[str, str]:
        """Limpia y estructura la información de ubicación"""
        if not location_str:
            return {
                'ubicacion_completa': '',
                'barrio': '',
                'zona': '',
                'ciudad': ''
            }
        
        # Dividir por comas para obtener diferentes niveles
        parts = [part.strip() for part in location_str.split(',')]
        
        return {
            'ubicacion_completa': location_str,
            'barrio': parts[0] if len(parts) > 0 else '',
            'zona': parts[1] if len(parts) > 1 else '',
            'ciudad': parts[-1] if len(parts) > 0 else ''
        }
    
    def validate_property_data(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida y marca la calidad de los datos de una propiedad"""
        validation = {
            'tiene_precio': property_data.get('precio_valido', False),
            'tiene_ubicacion': bool(property_data.get('barrio', '')),
            'tiene_caracteristicas': any([
                property_data.get('habitaciones'),
                property_data.get('banos'),
                property_data.get('superficie_m2')
            ]),
            'tiene_link': bool(property_data.get('link', '')),
            'calidad_score': 0
        }
        
        # Calcular score de calidad (0-100)
        score = 0
        if validation['tiene_precio']:
            score += 30
        if validation['tiene_ubicacion']:
            score += 25
        if validation['tiene_caracteristicas']:
            score += 25
        if validation['tiene_link']:
            score += 20
        
        validation['calidad_score'] = score
        validation['calidad_nivel'] = 'alta' if score >= 80 else 'media' if score >= 50 else 'baja'
        
        return validation
    
    def transform_properties_data(self, raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Transforma la data cruda en un DataFrame limpio y estructurado"""
        logger.info(f"Iniciando transformación de {len(raw_data)} propiedades")
        
        transformed_data = []
        
        for i, prop in enumerate(raw_data):
            try:
                # Limpiar precio
                price_info = self.clean_price(prop.get('precio', ''))
                
                # Limpiar ubicación
                location_info = self.clean_location(prop.get('ubicacion', ''))
                
                # Extraer superficie
                superficie_m2 = self.extract_surface_area(prop.get('superficie', ''))
                
                # Extraer habitaciones y baños
                rooms_info = self.extract_rooms_bathrooms(
                    f"{prop.get('habitaciones', '')} {prop.get('banos', '')}"
                )
                
                # Crear registro transformado
                transformed_prop = {
                    # Identificación
                    'id_propiedad': f"prop_{i+1}_{datetime.now().strftime('%Y%m%d')}",
                    'titulo': prop.get('titulo', '').strip(),
                    'fuente': prop.get('fuente', 'ArgentProp'),
                    'link': prop.get('link', ''),
                    'imagen_url': prop.get('imagen_url', ''),
                    
                    # Información de precio
                    'precio_original': price_info['precio_original'],
                    'precio_numerico': price_info['precio_numerico'],
                    'moneda': price_info['moneda'],
                    'precio_valido': price_info['precio_valido'],
                    
                    # Información de ubicación
                    'ubicacion_completa': location_info['ubicacion_completa'],
                    'barrio': location_info['barrio'],
                    'zona': location_info['zona'],
                    'ciudad': location_info['ciudad'],
                    
                    # Características físicas
                    'habitaciones': rooms_info['habitaciones'],
                    'banos': rooms_info['banos'],
                    'superficie_m2': superficie_m2,
                    
                    # Metadatos
                    'fecha_scraping': prop.get('fecha_scraping', datetime.now().isoformat()),
                    'fecha_transformacion': datetime.now().isoformat()
                }
                
                # Validar calidad de datos
                validation_info = self.validate_property_data(transformed_prop)
                transformed_prop.update(validation_info)
                
                transformed_data.append(transformed_prop)
                
            except Exception as e:
                logger.error(f"Error transformando propiedad {i}: {e}")
                continue
        
        # Crear DataFrame
        df = pd.DataFrame(transformed_data)
        
        # Optimizar tipos de datos
        if not df.empty:
            # Convertir a tipos apropiados
            df['precio_numerico'] = pd.to_numeric(df['precio_numerico'], errors='coerce')
            df['superficie_m2'] = pd.to_numeric(df['superficie_m2'], errors='coerce')
            df['habitaciones'] = pd.to_numeric(df['habitaciones'], errors='coerce').astype('Int64')
            df['banos'] = pd.to_numeric(df['banos'], errors='coerce').astype('Int64')
            df['calidad_score'] = pd.to_numeric(df['calidad_score'], errors='coerce')
            
            # Convertir fechas
            df['fecha_scraping'] = pd.to_datetime(df['fecha_scraping'])
            df['fecha_transformacion'] = pd.to_datetime(df['fecha_transformacion'])
        
        logger.info(f"Transformación completada. DataFrame final: {df.shape}")
        return df

def transform_properties_data(**context) -> str:
    """
    Task function para Airflow - Transforma datos de propiedades
    Returns: path del archivo con los datos transformados
    """
    # Obtener path de datos raw desde la task anterior
    ti = context['ti']
    raw_data_path = ti.xcom_pull(task_ids='extract_properties')
    
    logger.info(f"Iniciando transformación de datos desde: {raw_data_path}")
    
    # Cargar datos raw
    with open(raw_data_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    logger.info(f"Cargados {len(raw_data)} registros para transformar")
    
    # Inicializar transformer
    transformer = DataTransformer()
    
    # Transformar datos
    df_transformed = transformer.transform_properties_data(raw_data)
    
    if df_transformed.empty:
        raise ValueError("La transformación resultó en un DataFrame vacío")
    
    # Guardar datos transformados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    transformed_data_path = f"/tmp/transformed_properties_{timestamp}.parquet"
    
    df_transformed.to_parquet(transformed_data_path, index=False)
    
    logger.info(f"Datos transformados guardados en: {transformed_data_path}")
    logger.info(f"Forma del DataFrame: {df_transformed.shape}")
    
    # Log de estadísticas de calidad
    quality_stats = df_transformed['calidad_nivel'].value_counts()
    logger.info(f"Distribución de calidad: {quality_stats.to_dict()}")
    
    return transformed_data_path
