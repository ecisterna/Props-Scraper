# 📊 Configuración de Google Sheets para Props Scraper

Este archivo te explica cómo configurar Google Sheets para que tu scraper guarde automáticamente los resultados en Google Drive (Excel de Google).

## 🚀 Pasos para Configurar Google Sheets

### 1. Crear un Proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Dale un nombre como "Props Scraper" o similar

### 2. Habilitar Google Sheets API

1. En el menú lateral, ve a "APIs y servicios" > "Biblioteca"
2. Busca "Google Sheets API"
3. Haz clic en "Google Sheets API" y presiona "HABILITAR"
4. También busca y habilita "Google Drive API"

### 3. Crear Credenciales

1. Ve a "APIs y servicios" > "Credenciales"
2. Haz clic en "CREAR CREDENCIALES" > "ID de cliente de OAuth 2.0"
3. Si es la primera vez, configura la pantalla de consentimiento:
   - Tipo de usuario: Externo
   - Información de la aplicación:
     - Nombre: "Props Scraper"
     - Correo de asistencia: tu email
   - Dominios autorizados: (deja en blanco)
   - Información de contacto: tu email
4. Para crear el ID de cliente:
   - Tipo de aplicación: "Aplicación de escritorio"
   - Nombre: "Props Scraper Desktop"
5. **Descarga el archivo JSON** y guárdalo como `credentials.json` en la carpeta del proyecto

### 4. Preparar el Archivo de Credenciales

1. Descarga el archivo JSON de credenciales
2. Renómbralo a `credentials.json`
3. Colócalo en la misma carpeta que tus scripts de Python:
   ```
   Props-Scraper/
   ├── credentials.json          ← AQUÍ
   ├── daily_scraper.py
   ├── application_scheduler.py
   └── google_sheets_config.py
   ```

### 5. Instalar Dependencias

Ejecuta en la terminal (en la carpeta del proyecto):

```bash
pip install -r requirements.txt
```

### 6. Primera Ejecución y Autenticación

La primera vez que ejecutes el scraper:

1. Se abrirá automáticamente tu navegador
2. Inicia sesión con tu cuenta de Google
3. Acepta los permisos solicitados
4. Se creará automáticamente un archivo `token.json` (no lo borres)

## 🎯 Uso

### Opción 1: Script Independiente con Google Sheets

```bash
python daily_scraper.py
```

**Resultado:**
- ✅ Crea/actualiza una hoja de Google Sheets
- ✅ Guarda respaldo local en Excel
- ✅ Acceso desde cualquier dispositivo

### Opción 2: Aplicación Flask con Scheduler

```bash
python application_scheduler.py
```

**Resultado:**
- ✅ Scraping automático diario a las 9:00 AM
- ✅ Guarda en Google Sheets y Excel local
- ✅ API web para control manual

## 📱 Acceso a tus Datos

Una vez configurado, podrás acceder a tus datos desde:

- **Google Sheets** en tu Google Drive
- **Aplicación móvil** de Google Sheets
- **Cualquier navegador** con tu cuenta de Google
- **Excel local** como respaldo

## 🔗 Nombre de las Hojas de Cálculo

El scraper creará automáticamente hojas con nombres como:

- `Props Scraper - Departamentos Venta`
- `Props Scraper - Casas Alquiler`

Cada día se actualiza la hoja con los nuevos datos.

## 🛡️ Seguridad

- **credentials.json**: Mantén este archivo privado, no lo subas a repositorios públicos
- **token.json**: Se crea automáticamente, tampoco lo compartas
- Solo tu cuenta de Google tendrá acceso a las hojas creadas

## ❓ Solución de Problemas

### Error: "No se encontró el archivo credentials.json"
- Verifica que el archivo esté en la carpeta correcta
- Asegúrate de que se llame exactamente `credentials.json`

### Error de autenticación
- Borra el archivo `token.json` y vuelve a ejecutar
- Verifica que las APIs estén habilitadas en Google Cloud Console

### No se puede acceder a Google Sheets
- Verifica tu conexión a internet
- Como respaldo, siempre se guarda en Excel local

## 🎉 ¡Listo!

Una vez configurado, tu scraper automáticamente:

1. **Scrapea propiedades** según tu configuración
2. **Guarda en Google Sheets** (accesible desde cualquier lugar)
3. **Mantiene respaldo local** en Excel
4. **Ejecuta automáticamente** todos los días

¡Ya no tendrás que preocuparte por el espacio en tu computadora!
