"""
Script de configuración para el scraper de propiedades
Permite modificar fácilmente los parámetros de scraping
"""

import json
import os

# Configuración por defecto
DEFAULT_CONFIG = {
    "property_type": "departamentos",  # departamentos, casas
    "operation_type": "venta",         # venta, alquiler
    "location": "capital-federal",     # capital-federal, zona-norte, zona-oeste, zona-sur, etc.
    "price_range_from": 50000,         # precio mínimo
    "price_range_to": 200000,          # precio máximo
    "currency": "dolares",             # dolares, pesos
    "max_pages": 5,                    # número máximo de páginas a scrapear
    "sort_by": "masnuevos"            # masnuevos, menorprecio, mayorprecio
}

def load_config():
    """Carga la configuración desde archivo"""
    config_file = "scraper_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config):
    """Guarda la configuración en archivo"""
    config_file = "scraper_config.json"
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"Configuración guardada en {config_file}")
        return True
    except Exception as e:
        print(f"Error guardando configuración: {e}")
        return False

def show_config(config):
    """Muestra la configuración actual"""
    print("\n=== CONFIGURACIÓN ACTUAL ===")
    print(f"Tipo de propiedad: {config['property_type']}")
    print(f"Tipo de operación: {config['operation_type']}")
    print(f"Ubicación: {config['location']}")
    print(f"Rango de precios: ${config['price_range_from']:,} - ${config['price_range_to']:,}")
    print(f"Moneda: {config['currency']}")
    print(f"Páginas máximas: {config['max_pages']}")
    print(f"Ordenar por: {config['sort_by']}")
    print("============================\n")

def update_config():
    """Interfaz para actualizar la configuración"""
    config = load_config()
    
    print("Configurador del Scraper de Propiedades")
    print("="*40)
    
    show_config(config)
    
    while True:
        print("¿Qué deseas modificar?")
        print("1. Tipo de propiedad (departamentos/casas)")
        print("2. Tipo de operación (venta/alquiler)")
        print("3. Ubicación")
        print("4. Rango de precios")
        print("5. Moneda (dolares/pesos)")
        print("6. Número máximo de páginas")
        print("7. Criterio de ordenamiento")
        print("8. Ver configuración actual")
        print("9. Guardar y salir")
        print("0. Salir sin guardar")
        
        choice = input("\nSelecciona una opción (0-9): ").strip()
        
        if choice == '1':
            print("\nTipos de propiedad disponibles:")
            print("- departamentos")
            print("- casas")
            new_value = input("Ingresa el tipo de propiedad: ").strip().lower()
            if new_value in ['departamentos', 'casas']:
                config['property_type'] = new_value
                print(f"✓ Tipo de propiedad actualizado a: {new_value}")
            else:
                print("✗ Valor inválido")
        
        elif choice == '2':
            print("\nTipos de operación disponibles:")
            print("- venta")
            print("- alquiler")
            new_value = input("Ingresa el tipo de operación: ").strip().lower()
            if new_value in ['venta', 'alquiler']:
                config['operation_type'] = new_value
                print(f"✓ Tipo de operación actualizado a: {new_value}")
            else:
                print("✗ Valor inválido")
        
        elif choice == '3':
            print("\nEjemplos de ubicaciones:")
            print("- capital-federal")
            print("- zona-norte")
            print("- zona-oeste")
            print("- zona-sur")
            print("- provincia-buenos-aires")
            new_value = input("Ingresa la ubicación: ").strip().lower()
            if new_value:
                config['location'] = new_value
                print(f"✓ Ubicación actualizada a: {new_value}")
        
        elif choice == '4':
            try:
                min_price = int(input("Ingresa el precio mínimo: "))
                max_price = int(input("Ingresa el precio máximo: "))
                if min_price >= 0 and max_price > min_price:
                    config['price_range_from'] = min_price
                    config['price_range_to'] = max_price
                    print(f"✓ Rango de precios actualizado: ${min_price:,} - ${max_price:,}")
                else:
                    print("✗ Valores inválidos (el precio máximo debe ser mayor al mínimo)")
            except ValueError:
                print("✗ Ingresa números válidos")
        
        elif choice == '5':
            print("\nMonedas disponibles:")
            print("- dolares")
            print("- pesos")
            new_value = input("Ingresa la moneda: ").strip().lower()
            if new_value in ['dolares', 'pesos']:
                config['currency'] = new_value
                print(f"✓ Moneda actualizada a: {new_value}")
            else:
                print("✗ Valor inválido")
        
        elif choice == '6':
            try:
                pages = int(input("Ingresa el número máximo de páginas (1-20): "))
                if 1 <= pages <= 20:
                    config['max_pages'] = pages
                    print(f"✓ Páginas máximas actualizado a: {pages}")
                else:
                    print("✗ Ingresa un número entre 1 y 20")
            except ValueError:
                print("✗ Ingresa un número válido")
        
        elif choice == '7':
            print("\nCriterios de ordenamiento disponibles:")
            print("- masnuevos")
            print("- menorprecio")
            print("- mayorprecio")
            new_value = input("Ingresa el criterio: ").strip().lower()
            if new_value in ['masnuevos', 'menorprecio', 'mayorprecio']:
                config['sort_by'] = new_value
                print(f"✓ Criterio de ordenamiento actualizado a: {new_value}")
            else:
                print("✗ Valor inválido")
        
        elif choice == '8':
            show_config(config)
        
        elif choice == '9':
            if save_config(config):
                print("✓ Configuración guardada exitosamente")
                break
            else:
                print("✗ Error al guardar la configuración")
        
        elif choice == '0':
            print("Saliendo sin guardar...")
            break
        
        else:
            print("✗ Opción inválida")
        
        print()

if __name__ == "__main__":
    update_config()
