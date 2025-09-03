"""
DAG de Airflow para el scraping y procesamiento de propiedades inmobiliarias

Este DAG implementa un pipeline completo ETL (Extract, Transform, Load) para:
1. Extraer datos de propiedades desde ArgentProp
2. Transformar y limpiar los datos 
3. Cargar el dataset final en múltiples formatos
4. Validar la calidad del dataset generado

Autor: Props Scraper Team
Fecha: Septiembre 2025
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

# Importar funciones de utilidades
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from airflow_utils.extraction import extract_properties_data
from airflow_utils.transformation import transform_properties_data
from airflow_utils.loading import load_final_dataset, validate_final_dataset

# Configuración del DAG
default_args = {
    'owner': 'props-scraper-team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': days_ago(1),
}

# Parámetros de configuración para el scraping
SCRAPING_CONFIG = {
    'property_type': 'departamentos',
    'operation_type': 'venta', 
    'location': 'capital-federal',
    'price_range_from': 50000,
    'price_range_to': 300000,
    'currency': 'dolares',
    'max_pages': 10,
    'sort_by': 'masnuevos'
}

# Definición del DAG
dag = DAG(
    'propiedades_etl_pipeline',
    default_args=default_args,
    description='Pipeline ETL completo para datos de propiedades inmobiliarias',
    schedule_interval='@daily',  # Ejecutar diariamente
    catchup=False,
    max_active_runs=1,
    tags=['real-estate', 'etl', 'scraping', 'propiedades'],
    params=SCRAPING_CONFIG,
)

# Documentación del DAG
dag.doc_md = """
# Pipeline ETL de Propiedades Inmobiliarias

## Descripción del Problema
Este DAG aborda la necesidad de obtener datos actualizados del mercado inmobiliario argentino 
para análisis de precios, tendencias y características de propiedades. Los datos se extraen 
de ArgentProp, uno de los portales inmobiliarios más importantes de Argentina.

## Fuente de Datos
- **Sitio web**: ArgentProp (www.argenprop.com)
- **Método**: Web scraping automatizado
- **Tipo de datos**: Propiedades en venta (departamentos principalmente)
- **Ubicación**: Capital Federal, Argentina
- **Actualización**: Diaria

## Arquitectura del Pipeline

### 1. Extracción (Extract)
- Scraping web de ArgentProp
- Extracción de metadatos de propiedades
- Manejo de rate limiting y errores
- Almacenamiento temporal en JSON

### 2. Transformación (Transform)
- Limpieza y normalización de datos
- Extracción de precios numéricos
- Geolocalización y categorización
- Validación de calidad de datos
- Cálculo de métricas de completitud

### 3. Carga (Load)
- Generación de dataset en múltiples formatos
- Creación de reportes de calidad
- Metadatos del dataset
- Validación final

## Decisiones de Diseño

### Tecnologías Elegidas
- **Airflow**: Orquestación y scheduling
- **pandas**: Manipulación de datos
- **BeautifulSoup**: Web scraping
- **Parquet**: Almacenamiento eficiente

### Calidad de Datos
- Score de calidad por registro (0-100)
- Validaciones de completitud
- Detección de datos anómalos
- Reportes automáticos de calidad

### Formatos de Salida
- **Excel**: Para análisis manual
- **CSV**: Compatibilidad universal
- **Parquet**: Eficiencia en big data
- **JSON**: Integración con APIs
- **Metadata**: Documentación automática

## Monitoreo y Alertas
- Logs detallados en cada etapa
- Métricas de calidad automáticas
- Validaciones de integridad
- Alertas en caso de fallas

## Uso del Dataset
El dataset generado puede ser utilizado para:
- Análisis de precios inmobiliarios
- Estudios de mercado
- Machine Learning predictivo
- Dashboards y visualizaciones
- Research académico
"""

# ================================================================
# DEFINICIÓN DE TASKS
# ================================================================

# Task inicial - Setup
start_task = DummyOperator(
    task_id='start_pipeline',
    dag=dag,
)

# Task de preparación del entorno
prepare_environment = BashOperator(
    task_id='prepare_environment',
    bash_command="""
    echo "🚀 Iniciando pipeline ETL de propiedades"
    echo "📅 Fecha: {{ ds }}"
    echo "⏰ Hora: {{ ts }}"
    echo "🔧 Preparando directorios..."
    mkdir -p /tmp/data
    mkdir -p /tmp/logs
    echo "✅ Entorno preparado"
    """,
    dag=dag,
)

# Task 1: Extracción de datos
extract_task = PythonOperator(
    task_id='extract_properties',
    python_callable=extract_properties_data,
    params=SCRAPING_CONFIG,
    dag=dag,
)

# Task 2: Transformación de datos
transform_task = PythonOperator(
    task_id='transform_properties',
    python_callable=transform_properties_data,
    dag=dag,
)

# Task 3: Carga del dataset
load_task = PythonOperator(
    task_id='load_dataset',
    python_callable=load_final_dataset,
    dag=dag,
)

# Task 4: Validación final
validate_task = PythonOperator(
    task_id='validate_dataset',
    python_callable=validate_final_dataset,
    dag=dag,
)

# Task de generación de reporte final
generate_report = BashOperator(
    task_id='generate_final_report',
    bash_command="""
    echo "📊 REPORTE FINAL DEL PIPELINE"
    echo "================================"
    echo "📅 Fecha de ejecución: {{ ds }}"
    echo "⏰ Hora de finalización: {{ ts }}"
    echo "✅ Pipeline ejecutado exitosamente"
    echo "📁 Archivos generados en: /tmp/data/"
    echo "📋 Logs disponibles en: /tmp/logs/"
    echo "🎉 Dataset de propiedades listo para uso"
    
    # Listar archivos generados
    echo ""
    echo "📁 Archivos generados:"
    ls -la /tmp/data/ | grep propiedades || echo "No se encontraron archivos"
    
    # Mostrar tamaño total
    echo ""
    echo "💾 Espacio utilizado:"
    du -sh /tmp/data/ 2>/dev/null || echo "Directorio no encontrado"
    """,
    dag=dag,
)

# Task final
end_task = DummyOperator(
    task_id='end_pipeline',
    dag=dag,
)

# ================================================================
# DEFINICIÓN DE DEPENDENCIAS
# ================================================================

# Configurar la secuencia de ejecución
start_task >> prepare_environment >> extract_task >> transform_task >> load_task >> validate_task >> generate_report >> end_task

# ================================================================
# DOCUMENTACIÓN DE TASKS
# ================================================================

extract_task.doc_md = """
## Task: Extracción de Propiedades

Esta task realiza el web scraping de ArgentProp para extraer datos de propiedades.

### Parámetros de Configuración:
- **property_type**: Tipo de propiedad (departamentos, casas)
- **operation_type**: Tipo de operación (venta, alquiler)
- **location**: Ubicación geográfica
- **price_range**: Rango de precios a filtrar
- **max_pages**: Número máximo de páginas a scrapear

### Datos Extraídos:
- Título de la propiedad
- Precio publicado
- Ubicación detallada
- Características (habitaciones, baños, superficie)
- URL de la propiedad
- Imagen principal
- Fecha de scraping

### Salida:
Archivo JSON con datos crudos en `/tmp/raw_properties_TIMESTAMP.json`
"""

transform_task.doc_md = """
## Task: Transformación de Datos

Esta task limpia y transforma los datos crudos extraídos.

### Transformaciones Aplicadas:
- **Precios**: Normalización de formatos monetarios
- **Ubicaciones**: Parseo de barrio, zona y ciudad
- **Características**: Extracción de números de habitaciones y baños
- **Superficie**: Conversión a metros cuadrados numéricos
- **Calidad**: Cálculo de score de calidad por registro

### Validaciones:
- Detección de precios válidos
- Validación de ubicaciones
- Completitud de características
- Score de calidad (0-100)

### Salida:
Archivo Parquet con datos transformados en `/tmp/transformed_properties_TIMESTAMP.parquet`
"""

load_task.doc_md = """
## Task: Carga del Dataset

Esta task genera el dataset final en múltiples formatos.

### Formatos Generados:
- **Excel**: Incluye hojas de estadísticas y calidad
- **CSV**: Formato universal para análisis
- **Parquet**: Formato eficiente para big data
- **JSON**: Para integración con APIs
- **Metadata**: Documentación del dataset

### Reportes Incluidos:
- Estadísticas descriptivas
- Distribución por barrios
- Análisis de precios
- Métricas de calidad

### Salida:
Múltiples archivos en `/tmp/data/propiedades_dataset_TIMESTAMP.*`
"""

validate_task.doc_md = """
## Task: Validación del Dataset

Esta task valida la calidad e integridad del dataset final.

### Validaciones Realizadas:
- Presencia de registros
- Calidad mínima de datos
- Existencia de archivos
- Completitud de campos críticos

### Métricas Evaluadas:
- Total de propiedades
- Porcentaje con precios válidos
- Diversidad de ubicaciones
- Score promedio de calidad

### Criterios de Éxito:
- Mínimo 1 registro extraído
- Al menos 30% de calidad promedio
- Presencia de precios y ubicaciones
- Todos los archivos generados correctamente
"""
