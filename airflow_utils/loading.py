"""
Utilidades para el DAG de Airflow - Carga de datos
Este módulo contiene las funciones para cargar los datos finales
"""

import pandas as pd
import numpy as np
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class DataLoader:
    """Clase para cargar datos en diferentes destinos"""
    
    def __init__(self, data_dir: str = "/tmp/data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def save_to_excel(self, df: pd.DataFrame, filename: str) -> str:
        """Guarda DataFrame en formato Excel"""
        filepath = os.path.join(self.data_dir, f"{filename}.xlsx")
        
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja principal con todos los datos
                df.to_excel(writer, sheet_name='Propiedades', index=False)
                
                # Hoja de estadísticas
                self._create_stats_sheet(df, writer)
                
                # Hoja de calidad de datos
                self._create_quality_sheet(df, writer)
            
            logger.info(f"Datos guardados en Excel: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error guardando Excel: {e}")
            raise
    
    def save_to_csv(self, df: pd.DataFrame, filename: str) -> str:
        """Guarda DataFrame en formato CSV"""
        filepath = os.path.join(self.data_dir, f"{filename}.csv")
        
        try:
            df.to_csv(filepath, index=False, encoding='utf-8')
            logger.info(f"Datos guardados en CSV: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error guardando CSV: {e}")
            raise
    
    def save_to_parquet(self, df: pd.DataFrame, filename: str) -> str:
        """Guarda DataFrame en formato Parquet (más eficiente)"""
        filepath = os.path.join(self.data_dir, f"{filename}.parquet")
        
        try:
            df.to_parquet(filepath, index=False)
            logger.info(f"Datos guardados en Parquet: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error guardando Parquet: {e}")
            raise
    
    def save_to_json(self, df: pd.DataFrame, filename: str) -> str:
        """Guarda DataFrame en formato JSON"""
        filepath = os.path.join(self.data_dir, f"{filename}.json")
        
        try:
            # Convertir DataFrame a JSON con formato legible
            df.to_json(filepath, orient='records', indent=2, force_ascii=False)
            logger.info(f"Datos guardados en JSON: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error guardando JSON: {e}")
            raise
    
    def _create_stats_sheet(self, df: pd.DataFrame, writer):
        """Crea hoja de estadísticas descriptivas"""
        try:
            stats_data = []
            
            # Estadísticas generales
            stats_data.extend([
                ['Total de propiedades', len(df)],
                ['Propiedades con precio válido', df['precio_valido'].sum()],
                ['Propiedades con ubicación', df['barrio'].notna().sum()],
                ['', ''],
            ])
            
            # Estadísticas de precios (solo para propiedades con precio válido)
            if 'precio_numerico' in df.columns:
                precios_validos = df[df['precio_valido'] == True]['precio_numerico']
                if not precios_validos.empty:
                    stats_data.extend([
                        ['=== ESTADÍSTICAS DE PRECIOS ===', ''],
                        ['Precio promedio', f"${precios_validos.mean():,.2f}"],
                        ['Precio mediano', f"${precios_validos.median():,.2f}"],
                        ['Precio mínimo', f"${precios_validos.min():,.2f}"],
                        ['Precio máximo', f"${precios_validos.max():,.2f}"],
                        ['Desviación estándar', f"${precios_validos.std():,.2f}"],
                        ['', ''],
                    ])
            
            # Distribución por barrio (top 10)
            if 'barrio' in df.columns:
                top_barrios = df['barrio'].value_counts().head(10)
                stats_data.extend([
                    ['=== TOP 10 BARRIOS ===', ''],
                ])
                for barrio, count in top_barrios.items():
                    stats_data.append([barrio, count])
                stats_data.append(['', ''])
            
            # Distribución por número de habitaciones
            if 'habitaciones' in df.columns:
                hab_dist = df['habitaciones'].value_counts().sort_index()
                stats_data.extend([
                    ['=== DISTRIBUCIÓN POR HABITACIONES ===', ''],
                ])
                for hab, count in hab_dist.items():
                    if pd.notna(hab):
                        stats_data.append([f"{int(hab)} habitaciones", count])
                stats_data.append(['', ''])
            
            # Calidad de datos
            if 'calidad_nivel' in df.columns:
                calidad_dist = df['calidad_nivel'].value_counts()
                stats_data.extend([
                    ['=== CALIDAD DE DATOS ===', ''],
                ])
                for nivel, count in calidad_dist.items():
                    stats_data.append([f"Calidad {nivel}", count])
            
            # Crear DataFrame de estadísticas
            stats_df = pd.DataFrame(stats_data, columns=['Métrica', 'Valor'])
            stats_df.to_excel(writer, sheet_name='Estadísticas', index=False)
            
        except Exception as e:
            logger.error(f"Error creando hoja de estadísticas: {e}")
    
    def _create_quality_sheet(self, df: pd.DataFrame, writer):
        """Crea hoja de reporte de calidad de datos"""
        try:
            quality_data = []
            
            # Completitud de datos
            completitud = []
            for col in df.columns:
                if col not in ['fecha_scraping', 'fecha_transformacion']:
                    total = len(df)
                    no_nulos = df[col].notna().sum()
                    porcentaje = (no_nulos / total * 100) if total > 0 else 0
                    completitud.append([col, no_nulos, total, f"{porcentaje:.1f}%"])
            
            quality_data.extend([
                ['=== COMPLETITUD DE DATOS ===', '', '', ''],
                ['Campo', 'Registros válidos', 'Total', 'Porcentaje'],
            ])
            quality_data.extend(completitud)
            quality_data.append(['', '', '', ''])
            
            # Distribución de calidad
            if 'calidad_score' in df.columns:
                quality_data.extend([
                    ['=== DISTRIBUCIÓN DE CALIDAD ===', '', '', ''],
                    ['Score promedio', f"{df['calidad_score'].mean():.1f}", '', ''],
                    ['Score mediano', f"{df['calidad_score'].median():.1f}", '', ''],
                    ['Score mínimo', f"{df['calidad_score'].min():.1f}", '', ''],
                    ['Score máximo', f"{df['calidad_score'].max():.1f}", '', ''],
                ])
            
            # Crear DataFrame de calidad
            quality_df = pd.DataFrame(quality_data)
            quality_df.to_excel(writer, sheet_name='Calidad', index=False, header=False)
            
        except Exception as e:
            logger.error(f"Error creando hoja de calidad: {e}")
    
    def create_metadata_file(self, df: pd.DataFrame, filename: str) -> str:
        """Crea archivo de metadatos del dataset"""
        metadata = {
            'dataset_info': {
                'nombre': 'Propiedades ArgentProp',
                'descripcion': 'Dataset de propiedades inmobiliarias scrapeadas de ArgentProp',
                'fecha_creacion': datetime.now().isoformat(),
                'fuente': 'ArgentProp (www.argenprop.com)',
                'metodo_extraccion': 'Web Scraping automatizado',
                'total_registros': len(df),
                'periodo': 'Datos actuales al momento del scraping'
            },
            'esquema': {
                col: {
                    'tipo': str(df[col].dtype),
                    'nulos': int(df[col].isna().sum()),
                    'completitud': f"{((len(df) - df[col].isna().sum()) / len(df) * 100):.1f}%"
                } for col in df.columns
            },
            'estadisticas': {
                'precios_validos': int(df['precio_valido'].sum()) if 'precio_valido' in df.columns else 0,
                'precio_promedio': float(df[df['precio_valido'] == True]['precio_numerico'].mean()) if 'precio_numerico' in df.columns and df['precio_valido'].any() else None,
                'barrios_unicos': int(df['barrio'].nunique()) if 'barrio' in df.columns else 0,
                'calidad_promedio': float(df['calidad_score'].mean()) if 'calidad_score' in df.columns else None
            },
            'calidad': {
                'score_promedio': float(df['calidad_score'].mean()) if 'calidad_score' in df.columns else None,
                'distribucion_calidad': df['calidad_nivel'].value_counts().to_dict() if 'calidad_nivel' in df.columns else {}
            }
        }
        
        filepath = os.path.join(self.data_dir, f"{filename}_metadata.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Metadatos guardados en: {filepath}")
        return filepath

def load_final_dataset(**context) -> Dict[str, str]:
    """
    Task function para Airflow - Carga el dataset final
    Returns: dict con paths de todos los archivos creados
    """
    # Obtener path de datos transformados
    ti = context['ti']
    transformed_data_path = ti.xcom_pull(task_ids='transform_properties')
    
    logger.info(f"Iniciando carga de dataset desde: {transformed_data_path}")
    
    # Cargar datos transformados
    df = pd.read_parquet(transformed_data_path)
    
    logger.info(f"Dataset cargado: {df.shape[0]} registros, {df.shape[1]} columnas")
    
    # Inicializar loader
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"propiedades_dataset_{timestamp}"
    
    loader = DataLoader()
    
    # Guardar en múltiples formatos
    files_created = {}
    
    try:
        # Excel (formato principal para análisis)
        files_created['excel'] = loader.save_to_excel(df, base_filename)
        
        # CSV (formato universal)
        files_created['csv'] = loader.save_to_csv(df, base_filename)
        
        # Parquet (formato eficiente)
        files_created['parquet'] = loader.save_to_parquet(df, base_filename)
        
        # JSON (formato API-friendly)
        files_created['json'] = loader.save_to_json(df, base_filename)
        
        # Metadatos
        files_created['metadata'] = loader.create_metadata_file(df, base_filename)
        
        # Log de resumen
        logger.info("Dataset final creado exitosamente:")
        logger.info(f"  - Total de registros: {len(df)}")
        logger.info(f"  - Propiedades con precio: {df['precio_valido'].sum()}")
        logger.info(f"  - Barrios únicos: {df['barrio'].nunique()}")
        logger.info(f"  - Calidad promedio: {df['calidad_score'].mean():.1f}/100")
        
        for format_name, filepath in files_created.items():
            logger.info(f"  - {format_name.upper()}: {filepath}")
        
        return files_created
        
    except Exception as e:
        logger.error(f"Error durante la carga: {e}")
        raise

def validate_final_dataset(**context) -> bool:
    """
    Task function para Airflow - Valida el dataset final
    Returns: True si la validación es exitosa
    """
    # Obtener información del dataset
    ti = context['ti']
    files_info = ti.xcom_pull(task_ids='load_dataset')
    
    logger.info("Iniciando validación del dataset final")
    
    # Cargar dataset principal
    df = pd.read_parquet(files_info['parquet'])
    
    # Validaciones críticas
    validations = {
        'total_records': len(df) > 0,
        'has_valid_prices': df['precio_valido'].sum() > 0,
        'has_locations': df['barrio'].notna().sum() > 0,
        'has_links': df['link'].notna().sum() > 0,
        'quality_acceptable': df['calidad_score'].mean() >= 30,  # Al menos 30% de calidad promedio
        'files_exist': all(os.path.exists(path) for path in files_info.values())
    }
    
    # Log de resultados
    logger.info("Resultados de validación:")
    for check, passed in validations.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"  {check}: {status}")
    
    # Estadísticas finales
    logger.info(f"\nEstadísticas finales del dataset:")
    logger.info(f"  Total de propiedades: {len(df)}")
    logger.info(f"  Propiedades con precio válido: {df['precio_valido'].sum()} ({df['precio_valido'].mean()*100:.1f}%)")
    logger.info(f"  Barrios únicos: {df['barrio'].nunique()}")
    logger.info(f"  Calidad promedio: {df['calidad_score'].mean():.1f}/100")
    
    if 'precio_numerico' in df.columns and df['precio_valido'].any():
        precios_validos = df[df['precio_valido'] == True]['precio_numerico']
        logger.info(f"  Precio promedio: ${precios_validos.mean():,.2f}")
        logger.info(f"  Rango de precios: ${precios_validos.min():,.2f} - ${precios_validos.max():,.2f}")
    
    # Determinar si la validación es exitosa
    validation_passed = all(validations.values())
    
    if validation_passed:
        logger.info("🎉 ¡Validación exitosa! El dataset está listo para su uso.")
    else:
        logger.error("❌ Validación fallida. Revisar los datos antes de continuar.")
        failed_checks = [check for check, passed in validations.items() if not passed]
        logger.error(f"Validaciones fallidas: {failed_checks}")
    
    return validation_passed
