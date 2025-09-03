"""
Utilidades para el DAG de Airflow - Extracción de datos
Este módulo contiene las funciones para hacer scraping de propiedades
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
import time
import random
import logging
import re
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class PropsScraper:
    """Clase principal para hacer scraping de propiedades"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://www.argenprop.com"
        
    def build_search_url(self, config: Dict[str, Any]) -> str:
        """Construye la URL de búsqueda basada en la configuración"""
        url = f"{self.base_url}/{config['property_type']}-{config['operation_type']}"
        
        # Agregar ubicación
        if config.get('location'):
            url += f"/{config['location']}"
        
        # Agregar parámetros de precio
        params = []
        if config.get('price_range_from'):
            params.append(f"precio-desde-{config['price_range_from']}")
        if config.get('price_range_to'):
            params.append(f"precio-hasta-{config['price_range_to']}")
        
        # Agregar moneda
        if config.get('currency') and config['currency'] == 'dolares':
            params.append("dolares")
        
        # Agregar ordenamiento
        if config.get('sort_by'):
            params.append(f"orden-{config['sort_by']}")
        
        if params:
            url += "/" + "/".join(params)
        
        return url
    
    def extract_property_data(self, property_element) -> Dict[str, Any]:
        """Extrae los datos de una propiedad individual"""
        try:
            # Título
            title_elem = property_element.find('h2', class_='card__title')
            title = title_elem.get_text(strip=True) if title_elem else "Sin título"
            
            # Precio
            price_elem = property_element.find('p', class_='card__price')
            price = price_elem.get_text(strip=True) if price_elem else "Consultar precio"
            
            # Ubicación
            location_elem = property_element.find('p', class_='card__location')
            location = location_elem.get_text(strip=True) if location_elem else "Ubicación no especificada"
            
            # Link
            link_elem = property_element.find('a')
            link = self.base_url + link_elem.get('href') if link_elem and link_elem.get('href') else ""
            
            # Características (habitaciones, baños, etc.)
            features = {}
            features_container = property_element.find('div', class_='card__features')
            if features_container:
                feature_items = features_container.find_all('span')
                for item in feature_items:
                    text = item.get_text(strip=True)
                    if 'amb' in text or 'dor' in text:
                        features['habitaciones'] = text
                    elif 'baño' in text:
                        features['banos'] = text
                    elif 'm²' in text:
                        features['superficie'] = text
            
            # Imagen
            img_elem = property_element.find('img')
            img_url = img_elem.get('src') if img_elem else ""
            
            return {
                'titulo': title,
                'precio': price,
                'ubicacion': location,
                'habitaciones': features.get('habitaciones', ''),
                'banos': features.get('banos', ''),
                'superficie': features.get('superficie', ''),
                'link': link,
                'imagen_url': img_url,
                'fecha_scraping': datetime.now().isoformat(),
                'fuente': 'ArgentProp'
            }
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de propiedad: {e}")
            return None
    
    def scrape_page(self, url: str) -> List[Dict[str, Any]]:
        """Hace scraping de una página específica"""
        try:
            logger.info(f"Scrapeando página: {url}")
            
            # Delay aleatorio para evitar bloqueos
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar contenedor de propiedades
            properties_container = soup.find('div', class_='listing__items')
            if not properties_container:
                logger.warning("No se encontró contenedor de propiedades")
                return []
            
            # Extraer propiedades individuales
            property_elements = properties_container.find_all('div', class_='card')
            
            properties_data = []
            for prop_elem in property_elements:
                prop_data = self.extract_property_data(prop_elem)
                if prop_data:
                    properties_data.append(prop_data)
            
            logger.info(f"Extraídas {len(properties_data)} propiedades de la página")
            return properties_data
            
        except requests.RequestException as e:
            logger.error(f"Error de conexión: {e}")
            return []
        except Exception as e:
            logger.error(f"Error general en scrape_page: {e}")
            return []
    
    def scrape_properties(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Función principal para hacer scraping de propiedades"""
        logger.info("Iniciando scraping de propiedades")
        logger.info(f"Configuración: {config}")
        
        base_url = self.build_search_url(config)
        max_pages = config.get('max_pages', 5)
        
        all_properties = []
        
        for page in range(1, max_pages + 1):
            if page == 1:
                url = base_url
            else:
                url = f"{base_url}/pagina-{page}"
            
            page_properties = self.scrape_page(url)
            
            if not page_properties:
                logger.warning(f"No se encontraron propiedades en página {page}, terminando")
                break
            
            all_properties.extend(page_properties)
            logger.info(f"Página {page}/{max_pages} completada. Total acumulado: {len(all_properties)}")
        
        logger.info(f"Scraping completado. Total de propiedades: {len(all_properties)}")
        return all_properties

def extract_properties_data(**context) -> str:
    """
    Task function para Airflow - Extrae datos de propiedades
    Returns: path del archivo con los datos extraídos
    """
    # Obtener configuración desde XCom o usar configuración por defecto
    config = context.get('params', {})
    
    # Configuración por defecto
    default_config = {
        'property_type': 'departamentos',
        'operation_type': 'venta',
        'location': 'capital-federal',
        'price_range_from': 50000,
        'price_range_to': 300000,
        'currency': 'dolares',
        'max_pages': 10,
        'sort_by': 'masnuevos'
    }
    
    # Combinar configuración
    final_config = {**default_config, **config}
    
    logger.info(f"Iniciando extracción con configuración: {final_config}")
    
    # Inicializar scraper
    scraper = PropsScraper()
    
    # Extraer datos
    properties_data = scraper.scrape_properties(final_config)
    
    if not properties_data:
        raise ValueError("No se pudieron extraer datos de propiedades")
    
    # Guardar datos en archivo temporal
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_data_path = f"/tmp/raw_properties_{timestamp}.json"
    
    import json
    with open(raw_data_path, 'w', encoding='utf-8') as f:
        json.dump(properties_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Datos extraídos guardados en: {raw_data_path}")
    logger.info(f"Total de propiedades extraídas: {len(properties_data)}")
    
    # Retornar path para siguiente task
    return raw_data_path
