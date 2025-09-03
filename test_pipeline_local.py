"""
Script para probar el pipeline ETL de forma local sin Airflow
Útil para debugging y desarrollo
"""

import sys
import os
import logging
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar funciones del pipeline
from airflow_utils.extraction import extract_properties_data, PropsScraper
from airflow_utils.transformation import transform_properties_data, DataTransformer
from airflow_utils.loading import load_final_dataset, DataLoader

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_pipeline_locally():
    """Ejecuta el pipeline completo de forma local"""
    
    print("🚀 INICIANDO PRUEBA LOCAL DEL PIPELINE ETL")
    print("=" * 60)
    
    # Configuración de prueba (reducida para testing)
    config = {
        'property_type': 'departamentos',
        'operation_type': 'venta',
        'location': 'capital-federal',
        'price_range_from': 100000,
        'price_range_to': 200000,
        'currency': 'dolares',
        'max_pages': 2,  # Solo 2 páginas para prueba rápida
        'sort_by': 'masnuevos'
    }
    
    try:
        # ============== FASE 1: EXTRACCIÓN ==============
        print("\n📥 FASE 1: EXTRACCIÓN DE DATOS")
        print("-" * 40)
        
        scraper = PropsScraper()
        raw_data = scraper.scrape_properties(config)
        
        if not raw_data:
            raise ValueError("No se pudieron extraer datos")
        
        print(f"✅ Extracción exitosa: {len(raw_data)} propiedades")
        
        # Guardar datos raw
        import json
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_file = f"test_raw_data_{timestamp}.json"
        
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)
        print(f"📁 Datos raw guardados en: {raw_file}")
        
        # ============== FASE 2: TRANSFORMACIÓN ==============
        print("\n🔄 FASE 2: TRANSFORMACIÓN DE DATOS")
        print("-" * 40)
        
        transformer = DataTransformer()
        df_transformed = transformer.transform_properties_data(raw_data)
        
        if df_transformed.empty:
            raise ValueError("La transformación resultó en un DataFrame vacío")
        
        print(f"✅ Transformación exitosa: {df_transformed.shape}")
        
        # Guardar datos transformados
        parquet_file = f"test_transformed_data_{timestamp}.parquet"
        df_transformed.to_parquet(parquet_file, index=False)
        print(f"📁 Datos transformados guardados en: {parquet_file}")
        
        # ============== FASE 3: CARGA ==============
        print("\n💾 FASE 3: CARGA DEL DATASET")
        print("-" * 40)
        
        # Crear directorio de salida
        output_dir = f"test_output_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        
        loader = DataLoader(data_dir=output_dir)
        base_filename = f"propiedades_test_{timestamp}"
        
        # Guardar en múltiples formatos
        files_created = {}
        files_created['excel'] = loader.save_to_excel(df_transformed, base_filename)
        files_created['csv'] = loader.save_to_csv(df_transformed, base_filename)
        files_created['parquet'] = loader.save_to_parquet(df_transformed, base_filename)
        files_created['json'] = loader.save_to_json(df_transformed, base_filename)
        files_created['metadata'] = loader.create_metadata_file(df_transformed, base_filename)
        
        print(f"✅ Dataset final creado en directorio: {output_dir}")
        
        # ============== FASE 4: VALIDACIÓN ==============
        print("\n✅ FASE 4: VALIDACIÓN")
        print("-" * 40)
        
        # Validaciones básicas
        validations = {
            'total_records': len(df_transformed) > 0,
            'has_valid_prices': df_transformed['precio_valido'].sum() > 0,
            'has_locations': df_transformed['barrio'].notna().sum() > 0,
            'quality_acceptable': df_transformed['calidad_score'].mean() >= 20,
            'files_exist': all(os.path.exists(path) for path in files_created.values())
        }
        
        print("Resultados de validación:")
        for check, passed in validations.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {check}: {status}")
        
        # ============== REPORTE FINAL ==============
        print("\n📊 REPORTE FINAL")
        print("=" * 60)
        print(f"📅 Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📈 Total de propiedades procesadas: {len(df_transformed)}")
        print(f"💰 Propiedades con precio válido: {df_transformed['precio_valido'].sum()}")
        print(f"📍 Barrios únicos encontrados: {df_transformed['barrio'].nunique()}")
        print(f"⭐ Calidad promedio: {df_transformed['calidad_score'].mean():.1f}/100")
        
        if df_transformed['precio_valido'].any():
            precios_validos = df_transformed[df_transformed['precio_valido'] == True]['precio_numerico']
            print(f"💵 Precio promedio: ${precios_validos.mean():,.2f}")
            print(f"💵 Rango de precios: ${precios_validos.min():,.2f} - ${precios_validos.max():,.2f}")
        
        print(f"\n📁 Archivos generados:")
        for format_name, filepath in files_created.items():
            print(f"  - {format_name.upper()}: {filepath}")
        
        print(f"\n🎉 ¡PIPELINE EJECUTADO EXITOSAMENTE!")
        
        # Limpiar archivos temporales
        try:
            os.remove(raw_file)
            os.remove(parquet_file)
            print(f"\n🧹 Archivos temporales eliminados")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN EL PIPELINE: {str(e)}")
        logger.error(f"Error en pipeline: {e}", exc_info=True)
        return False

def test_individual_components():
    """Prueba componentes individuales del pipeline"""
    
    print("\n🔧 PRUEBA DE COMPONENTES INDIVIDUALES")
    print("=" * 60)
    
    # Test de scraper
    print("\n🔍 Probando scraper...")
    try:
        scraper = PropsScraper()
        test_url = scraper.build_search_url({
            'property_type': 'departamentos',
            'operation_type': 'venta',
            'location': 'capital-federal',
            'currency': 'dolares'
        })
        print(f"✅ URL generada: {test_url}")
    except Exception as e:
        print(f"❌ Error en scraper: {e}")
    
    # Test de transformer
    print("\n🔄 Probando transformer...")
    try:
        transformer = DataTransformer()
        
        # Datos de prueba
        test_data = [{
            'titulo': 'Departamento 2 ambientes en Palermo',
            'precio': 'USD 150.000',
            'ubicacion': 'Palermo, Capital Federal',
            'habitaciones': '2 amb',
            'banos': '1 baño',
            'superficie': '45 m²',
            'link': 'https://ejemplo.com/prop1',
            'fecha_scraping': datetime.now().isoformat()
        }]
        
        df_test = transformer.transform_properties_data(test_data)
        print(f"✅ Transformación test: {df_test.shape}")
        print(f"   Precio extraído: ${df_test.iloc[0]['precio_numerico']:,.2f}")
        print(f"   Barrio extraído: {df_test.iloc[0]['barrio']}")
        
    except Exception as e:
        print(f"❌ Error en transformer: {e}")
    
    # Test de loader
    print("\n💾 Probando loader...")
    try:
        import pandas as pd
        
        # DataFrame de prueba
        test_df = pd.DataFrame([{
            'id_propiedad': 'test_001',
            'titulo': 'Propiedad de prueba',
            'precio_numerico': 150000,
            'barrio': 'Palermo',
            'calidad_score': 85
        }])
        
        loader = DataLoader(data_dir="test_loader_output")
        csv_path = loader.save_to_csv(test_df, "test_dataset")
        print(f"✅ CSV de prueba creado: {csv_path}")
        
        # Limpiar
        os.remove(csv_path)
        os.rmdir("test_loader_output")
        
    except Exception as e:
        print(f"❌ Error en loader: {e}")

if __name__ == "__main__":
    print("🔧 EJECUTANDO PRUEBAS DEL PIPELINE ETL")
    print("=" * 60)
    
    # Opción para elegir tipo de prueba
    print("\nOpciones disponibles:")
    print("1. Prueba completa del pipeline (recomendado)")
    print("2. Prueba de componentes individuales")
    print("3. Ambas")
    
    try:
        opcion = input("\nSelecciona una opción (1-3) [1]: ").strip() or "1"
        
        if opcion in ["1", "3"]:
            print("\n" + "="*60)
            success = test_pipeline_locally()
            if not success:
                sys.exit(1)
        
        if opcion in ["2", "3"]:
            test_individual_components()
            
        print(f"\n✅ Pruebas completadas exitosamente!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Prueba cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        sys.exit(1)
