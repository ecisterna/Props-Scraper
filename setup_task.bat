@echo off
REM Script para configurar el Programador de tareas de Windows
REM Este script crea una tarea que ejecuta el scraper diariamente

echo Configurando tarea programada para el scraper de propiedades...

REM Obtener la ruta actual
set CURRENT_DIR=%~dp0
set PYTHON_PATH=%CURRENT_DIR%.venv\Scripts\python.exe
set SCRIPT_PATH=%CURRENT_DIR%daily_scraper.py

echo Directorio actual: %CURRENT_DIR%
echo Python: %PYTHON_PATH%
echo Script: %SCRIPT_PATH%

REM Crear la tarea programada
schtasks /create ^
    /tn "PropsScraper_Daily" ^
    /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\"" ^
    /sc daily ^
    /st 09:00 ^
    /sd %date% ^
    /ru SYSTEM ^
    /f

if %errorlevel% == 0 (
    echo.
    echo ✓ Tarea programada creada exitosamente!
    echo   - Nombre: PropsScraper_Daily
    echo   - Horario: Todos los días a las 9:00 AM
    echo   - Script: %SCRIPT_PATH%
    echo.
    echo Para ver la tarea: schtasks /query /tn "PropsScraper_Daily"
    echo Para ejecutar manualmente: schtasks /run /tn "PropsScraper_Daily"
    echo Para eliminar la tarea: schtasks /delete /tn "PropsScraper_Daily" /f
) else (
    echo.
    echo ✗ Error al crear la tarea programada
    echo   Asegúrate de ejecutar este script como Administrador
)

echo.
pause
