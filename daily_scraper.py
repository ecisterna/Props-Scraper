"""
Script independiente para scraping diario de propiedades
Se puede ejecutar desde el Programador de tareas de Windows
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
import os
import logging
import sys

# Configuración de logging
def setup_logging():
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_filename = f'scraping_{datetime.now().strftime("%Y%m%d")}.log'
    log_filepath = os.path.join(log_dir, log_filename)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filepath),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

# Configuración del scraping
SCRAPING_CONFIG = {
    'property_type': 'departamentos',        # departamentos, casas
    'operation_type': 'venta',               # venta, alquiler
    'location': 'capital-federal',           # capital-federal, zona-norte, etc.
    'price_range_from': 50000,              # precio mínimo
    'price_range_to': 200000,               # precio máximo
    'currency': 'dolares',                   # dolares, pesos
    'max_pages': 5,                          # número máximo de páginas a scrapear
    'sort_by': 'masnuevos'                  # masnuevos, menorprecio, mayorprecio
}

def scrape_props(config):
    """Función principal de scraping"""
    logger.info("Iniciando scraping con configuración:")
    logger.info(f"  - Tipo: {config['property_type']}")
    logger.info(f"  - Operación: {config['operation_type']}")
    logger.info(f"  - Ubicación: {config['location']}")
    logger.info(f"  - Rango: {config['price_range_from']} - {config['price_range_to']} {config['currency']}")
    logger.info(f"  - Páginas máximas: {config['max_pages']}")
    
    current_page = 1
    data = []
    total_props = 0

    while current_page <= config['max_pages']:
        try:
            url = f"https://www.argenprop.com/{config['property_type']}/{config['operation_type']}/{config['location']}?{config['price_range_from']}-{config['price_range_to']}-{config['currency']}&orden-{config['sort_by']}&pagina-{str(current_page)}"
            
            logger.info(f"Scrapeando página {current_page}...")
            
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            doc = BeautifulSoup(response.text, 'html.parser')
            all_props = doc.find_all('div', class_='listing__item')
            
            if not all_props:
                logger.warning(f"No se encontraron propiedades en la página {current_page}")
                break
            
            page_props = 0
            for prop in all_props:
                item = {}
                
                link = prop.find('a')
                if link:
                    # Título
                    title = link.find('h2', class_='card__title')
                    item['Nombre'] = title.text.strip() if title else 'No title available'
                    
                    # Precio
                    price = link.find('p', class_='card__price')
                    item['Precio'] = price.text.strip() if price else 'No price available'
                    
                    # Dirección
                    address = link.find('p', class_='card__address')
                    item['Dirección'] = address.text.strip() if address else 'No address available'
                    
                    # Link completo
                    item['Link'] = 'https://www.argenprop.com' + link['href']
                    
                    # Información adicional
                    item['Fecha_Scraping'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    item['Pagina'] = current_page
                    item['Tipo_Propiedad'] = config['property_type']
                    item['Tipo_Operacion'] = config['operation_type']
                    item['Ubicacion'] = config['location']

                    data.append(item)
                    page_props += 1
            
            total_props += page_props
            logger.info(f"  - Página {current_page}: {page_props} propiedades encontradas")
            
        except requests.RequestException as e:
            logger.error(f"Error de conexión en página {current_page}: {str(e)}")
            break
        except Exception as e:
            logger.error(f"Error inesperado en página {current_page}: {str(e)}")
            break
        
        current_page += 1
    
    logger.info(f"Scraping completado. Total de propiedades: {total_props}")
    return data

def save_to_excel(data, config):
    """Guarda los datos en un archivo Excel"""
    if not data:
        logger.warning("No hay datos para guardar")
        return None
    
    # Crear directorio de resultados si no existe
    results_dir = 'resultados'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # Nombre del archivo con fecha
    timestamp = datetime.now().strftime('%Y%m%d')
    filename = f'scraping_{config["property_type"]}_{config["operation_type"]}_{timestamp}.xlsx'
    filepath = os.path.join(results_dir, filename)
    
    try:
        df = pd.DataFrame(data)
        
        # Archivo principal con todos los datos
        main_filepath = os.path.join(results_dir, 'scraping_historico.xlsx')
        
        # Guardar archivo del día
        df.to_excel(filepath, index=False)
        logger.info(f"Archivo diario guardado: {filepath}")
        
        # Agregar al archivo histórico
        if os.path.exists(main_filepath):
            # Leer archivo existente
            try:
                existing_df = pd.read_excel(main_filepath)
                # Combinar con nuevos datos
                combined_df = pd.concat([existing_df, df], ignore_index=True)
                # Eliminar duplicados basados en el link (si los hay)
                combined_df = combined_df.drop_duplicates(subset=['Link'], keep='last')
                combined_df.to_excel(main_filepath, index=False)
                logger.info(f"Datos agregados al archivo histórico: {main_filepath}")
            except Exception as e:
                logger.error(f"Error actualizando archivo histórico: {str(e)}")
                # Si hay error, guardar como nuevo archivo
                df.to_excel(main_filepath, index=False)
        else:
            # Crear nuevo archivo histórico
            df.to_excel(main_filepath, index=False)
            logger.info(f"Nuevo archivo histórico creado: {main_filepath}")
        
        return filepath
    
    except Exception as e:
        logger.error(f"Error guardando archivo Excel: {str(e)}")
        return None

def create_summary_report(data, config):
    """Crea un reporte resumen del scraping"""
    if not data:
        return
    
    try:
        df = pd.DataFrame(data)
        
        # Estadísticas básicas
        total_props = len(df)
        
        # Análisis de precios (si hay datos de precio válidos)
        prices = []
        for price_str in df['Precio']:
            if 'No price available' not in price_str:
                # Extraer números del string de precio
                import re
                numbers = re.findall(r'[\d.,]+', price_str.replace('.', '').replace(',', ''))
                if numbers:
                    try:
                        price_num = float(numbers[0])
                        prices.append(price_num)
                    except:
                        pass
        
        summary = {
            'fecha_scraping': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_propiedades': total_props,
            'configuracion': config,
            'precio_promedio': sum(prices) / len(prices) if prices else 0,
            'precio_minimo': min(prices) if prices else 0,
            'precio_maximo': max(prices) if prices else 0,
            'propiedades_con_precio': len(prices)
        }
        
        logger.info("=== RESUMEN DEL SCRAPING ===")
        logger.info(f"Fecha: {summary['fecha_scraping']}")
        logger.info(f"Total de propiedades: {summary['total_propiedades']}")
        logger.info(f"Propiedades con precio: {summary['propiedades_con_precio']}")
        if prices:
            logger.info(f"Precio promedio: ${summary['precio_promedio']:,.2f}")
            logger.info(f"Precio mínimo: ${summary['precio_minimo']:,.2f}")
            logger.info(f"Precio máximo: ${summary['precio_maximo']:,.2f}")
        logger.info("========================")
        
    except Exception as e:
        logger.error(f"Error creando reporte resumen: {str(e)}")

def main():
    """Función principal"""
    global logger
    logger = setup_logging()
    
    logger.info("=== INICIO DE SCRAPING DIARIO ===")
    
    try:
        # Realizar scraping
        data = scrape_props(SCRAPING_CONFIG)
        
        if data:
            # Guardar en Excel
            filepath = save_to_excel(data, SCRAPING_CONFIG)
            
            # Crear reporte resumen
            create_summary_report(data, SCRAPING_CONFIG)
            
            if filepath:
                logger.info(f"Scraping exitoso. Archivo guardado: {filepath}")
                return True
            else:
                logger.error("Error al guardar el archivo")
                return False
        else:
            logger.warning("No se encontraron propiedades")
            return False
    
    except Exception as e:
        logger.error(f"Error general en el scraping: {str(e)}")
        return False
    
    finally:
        logger.info("=== FIN DE SCRAPING DIARIO ===")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
