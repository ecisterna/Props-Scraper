from flask import Flask, request, jsonify, render_template
from bs4 import BeautifulSoup
import requests
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
import logging

app = Flask(__name__)

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuración por defecto para el scraping automático
DEFAULT_CONFIG = {
    'property_type': 'departamentos',
    'operation_type': 'venta',
    'location': 'capital-federal',
    'price_range_from': 50000,
    'price_range_to': 200000,
    'currency': 'dolares',
    'max_pages': 3,
    'sort_by': 'masnuevos'
}

def scrape_props(property_type, operation_type, location, price_range_from, price_range_to, currency, max_pages, sort_by):
    current_page = 1
    data = []

    while current_page <= max_pages:
        try:
            url = f'https://www.argenprop.com/{property_type}/{operation_type}/{location}?{price_range_from}-{price_range_to}-{currency}&orden-{sort_by}&pagina-{str(current_page)}'
            response = requests.get(url, timeout=10).text
            doc = BeautifulSoup(response, 'html.parser')
            
            all_props = doc.find_all('div', class_= 'listing__item')
            
            for prop in all_props:
                item = {}
                
                link = prop.find('a')
                if link:
                    title = link.find('h2', class_= 'card__title')
                    if title:
                        item['Nombre'] = title.text.strip()
                    else:
                        item['Nombre'] = 'No title available'
                    
                    price = link.find('p', class_='card__price')
                    if price:
                        item['Precio'] = price.text.strip()
                    else:
                        item['Precio'] = 'No price available'
                        
                    address = link.find('p', class_='card__address')
                    if address:
                        item['Dirección'] = address.text.strip()
                    else:
                        item['Dirección'] = 'No address available'
                    
                    item['Link'] = 'https://www.argenprop.com' + link['href']
                    item['Fecha_Scraping'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    data.append(item)
                    
        except Exception as e:
            logger.error(f"Error scraping page {current_page}: {str(e)}")
        
        current_page += 1
    
    return data

def save_to_excel(data, filename=None):
    """Guarda los datos en un archivo Excel"""
    if not data:
        logger.warning("No hay datos para guardar")
        return
    
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'scraping_results_{timestamp}.xlsx'
    
    # Crear directorio de resultados si no existe
    results_dir = 'resultados'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    filepath = os.path.join(results_dir, filename)
    
    try:
        df = pd.DataFrame(data)
        
        # Si el archivo ya existe, agregar los datos como una nueva hoja
        if os.path.exists(filepath):
            with pd.ExcelWriter(filepath, mode='a', engine='openpyxl', if_sheet_exists='new') as writer:
                sheet_name = f'Scraping_{datetime.now().strftime("%Y%m%d_%H%M")}'
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            df.to_excel(filepath, index=False)
        
        logger.info(f"Datos guardados en: {filepath}")
        return filepath
    
    except Exception as e:
        logger.error(f"Error guardando archivo Excel: {str(e)}")
        return None

def scheduled_scraping():
    """Función que se ejecuta automáticamente cada día"""
    logger.info("Iniciando scraping programado...")
    
    try:
        data = scrape_props(**DEFAULT_CONFIG)
        
        if data:
            filename = f'scraping_diario_{datetime.now().strftime("%Y%m%d")}.xlsx'
            filepath = save_to_excel(data, filename)
            
            if filepath:
                logger.info(f"Scraping completado. {len(data)} propiedades encontradas y guardadas en {filepath}")
            else:
                logger.error("Error al guardar los datos")
        else:
            logger.warning("No se encontraron propiedades en el scraping")
    
    except Exception as e:
        logger.error(f"Error en el scraping programado: {str(e)}")

@app.route('/scrape', methods=['GET'])
def scrape():
    property_type = request.args.get('property_type', type=str)
    operation_type = request.args.get('operation_type', type=str)
    location = request.args.get('location', type=str)
    price_range_from = request.args.get('price_range_from', type=int)
    price_range_to = request.args.get('price_range_to', type=int)
    currency = request.args.get('currency', type=str)
    max_pages = request.args.get('max_pages', type=int)
    sort_by = request.args.get('sort_by', type=str)

    if property_type not in ['departamentos', 'casas'] or operation_type not in ['venta', 'alquiler'] or sort_by not in ['masnuevos', 'menorprecio', 'mayorprecio'] or currency not in ['dolares', 'pesos']:
        return jsonify({"error": "Invalid input."}), 400

    data = scrape_props(property_type, operation_type, location, price_range_from, price_range_to, currency, max_pages, sort_by)

    return jsonify(data)

@app.route('/scrape_and_save', methods=['GET'])
def scrape_and_save():
    """Endpoint para hacer scraping y guardar en Excel"""
    property_type = request.args.get('property_type', DEFAULT_CONFIG['property_type'])
    operation_type = request.args.get('operation_type', DEFAULT_CONFIG['operation_type'])
    location = request.args.get('location', DEFAULT_CONFIG['location'])
    price_range_from = request.args.get('price_range_from', DEFAULT_CONFIG['price_range_from'], type=int)
    price_range_to = request.args.get('price_range_to', DEFAULT_CONFIG['price_range_to'], type=int)
    currency = request.args.get('currency', DEFAULT_CONFIG['currency'])
    max_pages = request.args.get('max_pages', DEFAULT_CONFIG['max_pages'], type=int)
    sort_by = request.args.get('sort_by', DEFAULT_CONFIG['sort_by'])

    if property_type not in ['departamentos', 'casas'] or operation_type not in ['venta', 'alquiler'] or sort_by not in ['masnuevos', 'menorprecio', 'mayorprecio'] or currency not in ['dolares', 'pesos']:
        return jsonify({"error": "Invalid input."}), 400

    try:
        data = scrape_props(property_type, operation_type, location, price_range_from, price_range_to, currency, max_pages, sort_by)
        
        if data:
            filepath = save_to_excel(data)
            return jsonify({
                "success": True,
                "message": f"Scraping completado. {len(data)} propiedades encontradas.",
                "file_path": filepath,
                "data_count": len(data)
            })
        else:
            return jsonify({
                "success": False,
                "message": "No se encontraron propiedades"
            })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/config', methods=['GET', 'POST'])
def config():
    """Endpoint para ver/modificar la configuración del scraping automático"""
    global DEFAULT_CONFIG
    
    if request.method == 'POST':
        # Actualizar configuración
        new_config = request.get_json()
        DEFAULT_CONFIG.update(new_config)
        return jsonify({"success": True, "message": "Configuración actualizada", "config": DEFAULT_CONFIG})
    
    return jsonify(DEFAULT_CONFIG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    """Endpoint para verificar el estado del scheduler"""
    try:
        jobs = scheduler.get_jobs()
        job_info = []
        for job in jobs:
            job_info.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else None
            })
        
        return jsonify({
            "scheduler_running": scheduler.running,
            "jobs": job_info,
            "current_config": DEFAULT_CONFIG
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Configurar el scheduler
    scheduler = BackgroundScheduler()
    
    # Programar el scraping diario a las 9:00 AM
    scheduler.add_job(
        func=scheduled_scraping,
        trigger="cron",
        hour=9,
        minute=0,
        id='daily_scraping',
        name='Scraping Diario de Propiedades'
    )
    
    # Iniciar el scheduler
    scheduler.start()
    logger.info("Scheduler iniciado. El scraping se ejecutará diariamente a las 9:00 AM")
    
    try:
        app.run(debug=True, use_reloader=False)  # use_reloader=False para evitar problemas con el scheduler
    except (KeyboardInterrupt, SystemExit):
        logger.info("Cerrando aplicación...")
        scheduler.shutdown()
