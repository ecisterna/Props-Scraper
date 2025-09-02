"""
Configuración para Google Sheets
Este archivo maneja la conexión y operaciones con Google Sheets
"""

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import json
from datetime import datetime
import pandas as pd

# Scopes necesarios para Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class GoogleSheetsManager:
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        """
        Inicializa el manager de Google Sheets
        
        Args:
            credentials_file: Archivo de credenciales de Google API
            token_file: Archivo donde se guarda el token de autenticación
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.gc = None
        self.authenticate()
    
    def authenticate(self):
        """Autentica con Google Sheets API"""
        creds = None
        
        # El archivo token.json almacena los tokens de acceso y actualización del usuario.
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        
        # Si no hay credenciales válidas disponibles, permite al usuario autenticarse.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"No se encontró el archivo de credenciales '{self.credentials_file}'. "
                        "Por favor, descarga las credenciales desde Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Guarda las credenciales para la próxima ejecución
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        # Inicializa gspread con las credenciales
        self.gc = gspread.authorize(creds)
        print("✅ Autenticación exitosa con Google Sheets")
    
    def create_or_get_spreadsheet(self, spreadsheet_name="Props Scraper - Resultados"):
        """
        Crea o obtiene una hoja de cálculo
        
        Args:
            spreadsheet_name: Nombre de la hoja de cálculo
            
        Returns:
            Objeto Spreadsheet de gspread
        """
        try:
            # Intenta abrir la hoja existente
            spreadsheet = self.gc.open(spreadsheet_name)
            print(f"📊 Hoja de cálculo '{spreadsheet_name}' encontrada")
        except gspread.SpreadsheetNotFound:
            # Crea una nueva hoja de cálculo
            spreadsheet = self.gc.create(spreadsheet_name)
            print(f"📊 Nueva hoja de cálculo '{spreadsheet_name}' creada")
            
            # Comparte la hoja contigo (opcional)
            # spreadsheet.share('tu_email@gmail.com', perm_type='user', role='writer')
            
        return spreadsheet
    
    def save_properties_to_sheet(self, properties_data, spreadsheet_name="Props Scraper - Resultados"):
        """
        Guarda los datos de propiedades en Google Sheets
        
        Args:
            properties_data: Lista de diccionarios con los datos de propiedades
            spreadsheet_name: Nombre de la hoja de cálculo
        """
        if not properties_data:
            print("⚠️ No hay datos para guardar")
            return
        
        try:
            # Obtiene o crea la hoja de cálculo
            spreadsheet = self.create_or_get_spreadsheet(spreadsheet_name)
            
            # Crea el nombre de la hoja con la fecha actual
            today = datetime.now().strftime("%Y-%m-%d")
            sheet_name = f"Scraping_{today}"
            
            # Verifica si la hoja ya existe
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                print(f"📋 Hoja '{sheet_name}' ya existe, se actualizará")
            except gspread.WorksheetNotFound:
                # Crea una nueva hoja
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="20")
                print(f"📋 Nueva hoja '{sheet_name}' creada")
            
            # Convierte los datos a DataFrame para facilitar el manejo
            df = pd.DataFrame(properties_data)
            
            # Agrega columna de timestamp
            df['Fecha_Scraping'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Prepara los datos para Google Sheets
            # Encabezados
            headers = list(df.columns)
            
            # Datos (convierte todo a string para evitar problemas)
            data = df.astype(str).values.tolist()
            
            # Limpia la hoja y agrega los nuevos datos
            worksheet.clear()
            
            # Agrega encabezados
            worksheet.append_row(headers)
            
            # Agrega los datos
            if data:
                worksheet.append_rows(data)
            
            # Formatea los encabezados (opcional)
            worksheet.format('A1:Z1', {
                "backgroundColor": {
                    "red": 0.2,
                    "green": 0.6,
                    "blue": 0.9
                },
                "textFormat": {
                    "foregroundColor": {
                        "red": 1.0,
                        "green": 1.0,
                        "blue": 1.0
                    },
                    "fontSize": 12,
                    "bold": True
                }
            })
            
            print(f"✅ {len(data)} propiedades guardadas en Google Sheets")
            print(f"🔗 URL: {spreadsheet.url}")
            
            return spreadsheet.url
            
        except Exception as e:
            print(f"❌ Error al guardar en Google Sheets: {str(e)}")
            # Como fallback, guarda en Excel local
            self.save_to_local_excel(properties_data)
            return None
    
    def save_to_local_excel(self, properties_data):
        """
        Método de respaldo para guardar en Excel local si falla Google Sheets
        """
        try:
            if not os.path.exists('resultados'):
                os.makedirs('resultados')
            
            today = datetime.now().strftime("%Y-%m-%d")
            filename = f"resultados/propiedades_{today}.xlsx"
            
            df = pd.DataFrame(properties_data)
            df['Fecha_Scraping'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            df.to_excel(filename, index=False)
            print(f"💾 Guardado como respaldo en: {filename}")
            
        except Exception as e:
            print(f"❌ Error al guardar respaldo local: {str(e)}")
    
    def get_sheet_url(self, spreadsheet_name="Props Scraper - Resultados"):
        """
        Obtiene la URL de la hoja de cálculo
        
        Args:
            spreadsheet_name: Nombre de la hoja de cálculo
            
        Returns:
            URL de la hoja de cálculo
        """
        try:
            spreadsheet = self.gc.open(spreadsheet_name)
            return spreadsheet.url
        except Exception as e:
            print(f"❌ Error al obtener URL: {str(e)}")
            return None

# Función de utilidad para uso rápido
def save_to_google_sheets(properties_data, spreadsheet_name="Props Scraper - Resultados"):
    """
    Función de utilidad para guardar datos rápidamente en Google Sheets
    
    Args:
        properties_data: Lista de diccionarios con los datos
        spreadsheet_name: Nombre de la hoja de cálculo
        
    Returns:
        URL de la hoja de cálculo o None si falla
    """
    try:
        manager = GoogleSheetsManager()
        return manager.save_properties_to_sheet(properties_data, spreadsheet_name)
    except Exception as e:
        print(f"❌ Error en save_to_google_sheets: {str(e)}")
        return None
