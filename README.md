# # Props Scraper - Scraping Automático de Propiedades

Este proyecto permite hacer scraping de propiedades de ArgentProp y programar ejecuciones automáticas diarias que guardan los resultados en archivos Excel.

## 📁 Estructura del Proyecto

```
Props-Scraper/
├── application.py              # Aplicación Flask original
├── application_scheduler.py    # Aplicación Flask con scheduler integrado
├── daily_scraper.py           # Script independiente para scraping diario
├── config_scraper.py          # Configurador de parámetros
├── setup_task.bat            # Script para configurar tarea de Windows
├── requirements.txt           # Dependencias del proyecto
├── templates/                 # Plantillas HTML
├── resultados/               # Carpeta donde se guardan los Excel
├── logs/                     # Carpeta de logs
└── README.md                 # Este archivo
```

## 🚀 Opciones de Implementación

### Opción 1: Aplicación con Scheduler Integrado

La aplicación Flask corre continuamente y ejecuta el scraping automáticamente.

**Características:**
- ✅ Scheduler integrado con APScheduler
- ✅ Se ejecuta diariamente a las 9:00 AM
- ✅ API REST para control manual
- ✅ Interfaz web disponible
- ✅ Configuración modificable en tiempo real

**Uso:**
```bash
python application_scheduler.py
```

**Endpoints disponibles:**
- `GET /` - Interfaz web
- `GET /scrape_and_save` - Scraping manual y guardar en Excel
- `GET /config` - Ver configuración actual
- `POST /config` - Modificar configuración
- `GET /status` - Estado del scheduler

### Opción 2: Script Independiente + Programador de Windows

Script que se ejecuta una vez y termina, ideal para el Programador de tareas de Windows.

**Características:**
- ✅ Ejecución independiente
- ✅ Logs detallados
- ✅ Reporte de estadísticas
- ✅ Archivo histórico acumulativo
- ✅ Configuración mediante archivo JSON

**Configuración automática:**
```bash
# Ejecutar como Administrador
setup_task.bat
```

**Ejecución manual:**
```bash
python daily_scraper.py
```

## ⚙️ Configuración

### Configurar Parámetros de Scraping

```bash
python config_scraper.py
```

Este script te permite modificar:
- Tipo de propiedad (departamentos/casas)
- Tipo de operación (venta/alquiler)
- Ubicación (capital-federal, zona-norte, etc.)
- Rango de precios
- Moneda (dólares/pesos)
- Número máximo de páginas
- Criterio de ordenamiento

### Configuración por Defecto

```json
{
  "property_type": "departamentos",
  "operation_type": "venta",
  "location": "capital-federal",
  "price_range_from": 50000,
  "price_range_to": 200000,
  "currency": "dolares",
  "max_pages": 5,
  "sort_by": "masnuevos"
}
```

## 📊 Archivos de Salida

### Estructura de Excel Generado

Cada archivo Excel contiene las siguientes columnas:
- **Nombre**: Título de la propiedad
- **Precio**: Precio de la propiedad
- **Dirección**: Ubicación de la propiedad
- **Link**: URL completa a la propiedad
- **Fecha_Scraping**: Timestamp del scraping
- **Pagina**: Número de página donde se encontró
- **Tipo_Propiedad**: Tipo de propiedad (departamentos/casas)
- **Tipo_Operacion**: Tipo de operación (venta/alquiler)
- **Ubicacion**: Ubicación buscada

### Archivos Generados

1. **Archivo Diario**: `scraping_departamentos_venta_YYYYMMDD.xlsx`
   - Resultados del día específico

2. **Archivo Histórico**: `scraping_historico.xlsx`
   - Acumula todos los resultados históricos
   - Elimina duplicados automáticamente

## 🔧 Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd Props-Scraper
```

2. **Crear entorno virtual**
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

## 🕒 Programación Automática

### Windows - Programador de Tareas

1. **Ejecución automática del script de configuración:**
```bash
# Ejecutar como Administrador
setup_task.bat
```

2. **Configuración manual:**
- Abrir "Programador de tareas" de Windows
- Crear tarea básica
- Nombre: "Props Scraper Daily"
- Desencadenador: Diariamente a las 9:00 AM
- Acción: Iniciar programa
- Programa: `C:\ruta\al\proyecto\.venv\Scripts\python.exe`
- Argumentos: `C:\ruta\al\proyecto\daily_scraper.py`

### Comandos Útiles para el Programador de Tareas

```bash
# Ver la tarea
schtasks /query /tn "PropsScraper_Daily"

# Ejecutar manualmente
schtasks /run /tn "PropsScraper_Daily"

# Eliminar la tarea
schtasks /delete /tn "PropsScraper_Daily" /f
```

## 📋 Logs y Monitoreo

### Logs del Script Independiente
- Ubicación: `logs/scraping_YYYYMMDD.log`
- Contiene: Inicio/fin, errores, estadísticas, resumen

### Logs del Scheduler Integrado
- Se muestran en la consola
- Incluyen información del scheduler y scraping

## 🔍 Resolución de Problemas

### Problemas Comunes

1. **Error de permisos en Programador de tareas**
   - Ejecutar `setup_task.bat` como Administrador

2. **Timeout en requests**
   - Verificar conexión a internet
   - El script reintenta automáticamente

3. **No se generan archivos Excel**
   - Verificar que existan datos para scrapear
   - Revisar logs para errores específicos

4. **Scheduler no funciona**
   - Usar `use_reloader=False` en Flask
   - Verificar que no haya errores en el código

### Verificar Estado

```python
# Para application_scheduler.py
# Visitar: http://localhost:5000/status

# Para daily_scraper.py
# Revisar logs en: logs/scraping_YYYYMMDD.log
```

## 📈 Personalización

### Modificar Horario de Ejecución

**Scheduler integrado (application_scheduler.py):**
```python
scheduler.add_job(
    func=scheduled_scraping,
    trigger="cron",
    hour=9,        # Cambiar hora aquí
    minute=0,      # Cambiar minuto aquí
    id='daily_scraping'
)
```

**Programador de Windows:**
- Modificar la línea `/st 09:00` en `setup_task.bat`

### Agregar Nuevos Parámetros

1. Modificar `SCRAPING_CONFIG` en `daily_scraper.py`
2. Actualizar `DEFAULT_CONFIG` en `application_scheduler.py`
3. Agregar opciones en `config_scraper.py`

## ⚠️ Disclaimer

Este proyecto es solo para fines educativos. Asegúrate de cumplir con los términos de servicio del sitio web que estés scrapeando y respeta los límites de rate limiting para evitar sobrecargar los servidores.
 
