"""
Script de prueba para verificar que la configuración de Google Sheets funciona
"""

try:
    from google_sheets_config import GoogleSheetsManager, save_to_google_sheets
    print("✅ Módulo de Google Sheets importado correctamente")
    
    # Datos de prueba
    test_data = [
        {
            "Título": "Departamento de prueba",
            "Precio": "$150,000",
            "Ubicación": "Capital Federal",
            "Habitaciones": "2",
            "Baños": "1",
            "Link": "https://ejemplo.com/prop1"
        },
        {
            "Título": "Casa de prueba",
            "Precio": "$200,000",
            "Ubicación": "Zona Norte",
            "Habitaciones": "3",
            "Baños": "2",
            "Link": "https://ejemplo.com/prop2"
        }
    ]
    
    print("\n🔍 Verificando si tienes el archivo credentials.json...")
    import os
    if os.path.exists('credentials.json'):
        print("✅ Archivo credentials.json encontrado")
        
        print("\n🚀 Intentando conectar con Google Sheets...")
        print("ℹ️ Si es la primera vez, se abrirá tu navegador para autenticarte")
        
        # Intenta guardar datos de prueba
        url = save_to_google_sheets(test_data, "Props Scraper - PRUEBA")
        
        if url:
            print(f"\n🎉 ¡ÉXITO! Prueba completada exitosamente")
            print(f"🔗 Puedes ver tus datos de prueba en: {url}")
            print("\n📝 Pasos siguientes:")
            print("1. Ve al enlace de arriba para ver tus datos en Google Sheets")
            print("2. Ejecuta 'python daily_scraper.py' para hacer scraping real")
            print("3. O ejecuta 'python application_scheduler.py' para la app con scheduler")
        else:
            print("\n⚠️ No se pudo obtener la URL, pero es posible que los datos se hayan guardado")
            print("📋 Revisa tu Google Drive para ver si se creó la hoja 'Props Scraper - PRUEBA'")
    
    else:
        print("❌ No se encontró el archivo credentials.json")
        print("\n📖 Necesitas configurar Google Sheets primero:")
        print("1. Lee el archivo CONFIGURACION_GOOGLE_SHEETS.md")
        print("2. Descarga las credenciales desde Google Cloud Console")
        print("3. Guárdalas como 'credentials.json' en esta carpeta")
        print("4. Ejecuta este script nuevamente")

except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("\n🔧 Solución:")
    print("pip install -r requirements.txt")

except Exception as e:
    print(f"❌ Error durante la prueba: {e}")
    print("\n🔧 Posibles soluciones:")
    print("1. Verifica que tienes credentials.json")
    print("2. Asegúrate de tener conexión a internet")
    print("3. Revisa que las APIs estén habilitadas en Google Cloud Console")
    print("4. Consulta el archivo CONFIGURACION_GOOGLE_SHEETS.md")

print("\n" + "="*60)
print("INFORMACIÓN ADICIONAL:")
print("="*60)
print("📄 Guía completa: CONFIGURACION_GOOGLE_SHEETS.md")
print("🌐 Google Cloud Console: https://console.cloud.google.com/")
print("📊 Una vez configurado, tus datos se guardarán automáticamente en Google Drive")
print("💾 También se mantendrá un respaldo local en archivos Excel")
