from flask import Flask, request, jsonify, render_template
from bs4 import BeautifulSoup
import requests
import pandas as pd

app = Flask(__name__)

def scrape_props(property_type, operation_type, location, price_range_from, price_range_to, currency, max_pages, sort_by):
    current_page = 1
    data = []

    while current_page <= max_pages:
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

                data.append(item)
                
        current_page += 1
    return data

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

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
