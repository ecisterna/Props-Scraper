"""
Script de verificación pre-entrega para el DAG de Airflow
Verifica que todos los componentes estén correctamente configurados
"""

import os
import sys
import importlib.util
from pathlib import Path

def check_file_exists(filepath, description):
    """Verifica que un archivo existe"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NO ENCONTRADO")
        return False

def check_python_syntax(filepath):
    """Verifica la sintaxis de un archivo Python"""
    try:
        spec = importlib.util.spec_from_file_location("module", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✅ Sintaxis válida: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error de sintaxis en {filepath}: {e}")
        return False

def check_imports(filepath):
    """Verifica que las imports necesarias están disponibles"""
    try:
        # Leer el archivo y buscar imports
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Lista de imports críticos
        critical_imports = [
            'pandas',
            'numpy', 
            'requests',
            'beautifulsoup4'
        ]
        
        missing = []
        for imp in critical_imports:
            try:
                __import__(imp)
            except ImportError:
                missing.append(imp)
        
        if missing:
            print(f"⚠️ Dependencias faltantes: {missing}")
            return False
        else:
            print(f"✅ Todas las dependencias están disponibles")
            return True
            
    except Exception as e:
        print(f"❌ Error verificando imports: {e}")
        return False

def main():
    print("🔍 VERIFICACIÓN PRE-ENTREGA DEL PIPELINE ETL")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    all_checks_passed = True
    
    # 1. Verificar estructura de archivos
    print("\n📁 VERIFICANDO ESTRUCTURA DE ARCHIVOS")
    print("-" * 40)
    
    required_files = {
        'DAG principal': base_path / 'dags' / 'propiedades_etl_dag.py',
        'Módulo de extracción': base_path / 'airflow_utils' / 'extraction.py',
        'Módulo de transformación': base_path / 'airflow_utils' / 'transformation.py',
        'Módulo de carga': base_path / 'airflow_utils' / 'loading.py',
        'Init del módulo': base_path / 'airflow_utils' / '__init__.py',
        'Dockerfile': base_path / 'Dockerfile',
        'Configuración Astro': base_path / 'astro.yaml',
        'Requirements': base_path / 'requirements.txt',
        'Script de prueba': base_path / 'test_pipeline_local.py',
        'Documentación Airflow': base_path / 'README_AIRFLOW.md'
    }
    
    for description, filepath in required_files.items():
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    
    # 2. Verificar directorios
    print("\n📂 VERIFICANDO DIRECTORIOS")
    print("-" * 40)
    
    required_dirs = {
        'DAGs': base_path / 'dags',
        'Utilidades': base_path / 'airflow_utils',
        'Datos': base_path / 'data'
    }
    
    for description, dirpath in required_dirs.items():
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            print(f"✅ Directorio {description}: {dirpath}")
        else:
            print(f"❌ Directorio {description}: {dirpath} - NO ENCONTRADO")
            all_checks_passed = False
    
    # 3. Verificar sintaxis Python
    print("\n🐍 VERIFICANDO SINTAXIS PYTHON")
    print("-" * 40)
    
    python_files = [
        base_path / 'airflow_utils' / 'extraction.py',
        base_path / 'airflow_utils' / 'transformation.py',
        base_path / 'airflow_utils' / 'loading.py',
        base_path / 'test_pipeline_local.py'
    ]
    
    for filepath in python_files:
        if os.path.exists(filepath):
            if not check_python_syntax(filepath):
                all_checks_passed = False
    
    # 4. Verificar contenido del DAG
    print("\n⚙️ VERIFICANDO CONTENIDO DEL DAG")
    print("-" * 40)
    
    dag_file = base_path / 'dags' / 'propiedades_etl_dag.py'
    if os.path.exists(dag_file):
        try:
            with open(dag_file, 'r', encoding='utf-8') as f:
                dag_content = f.read()
            
            # Verificar elementos clave del DAG
            dag_checks = {
                'DAG definido': 'dag = DAG(' in dag_content,
                'Tasks de extracción': 'extract_properties' in dag_content,
                'Tasks de transformación': 'transform_properties' in dag_content,
                'Tasks de carga': 'load_dataset' in dag_content,
                'Tasks de validación': 'validate_dataset' in dag_content,
                'Configuración de parámetros': 'SCRAPING_CONFIG' in dag_content,
                'Documentación': 'dag.doc_md' in dag_content
            }
            
            for check_name, passed in dag_checks.items():
                if passed:
                    print(f"✅ {check_name}")
                else:
                    print(f"❌ {check_name}")
                    all_checks_passed = False
                    
        except Exception as e:
            print(f"❌ Error leyendo DAG: {e}")
            all_checks_passed = False
    
    # 5. Verificar requirements.txt
    print("\n📦 VERIFICANDO DEPENDENCIAS")
    print("-" * 40)
    
    req_file = base_path / 'requirements.txt'
    if os.path.exists(req_file):
        try:
            with open(req_file, 'r') as f:
                requirements = f.read()
            
            required_packages = [
                'apache-airflow',
                'pandas',
                'beautifulsoup4',
                'requests',
                'numpy'
            ]
            
            for package in required_packages:
                if package in requirements:
                    print(f"✅ {package} incluido")
                else:
                    print(f"❌ {package} faltante")
                    all_checks_passed = False
                    
        except Exception as e:
            print(f"❌ Error leyendo requirements: {e}")
            all_checks_passed = False
    
    # 6. Verificar configuración Astro
    print("\n🚀 VERIFICANDO CONFIGURACIÓN ASTRO")
    print("-" * 40)
    
    astro_file = base_path / 'astro.yaml'
    dockerfile = base_path / 'Dockerfile'
    
    if os.path.exists(astro_file):
        print("✅ astro.yaml presente")
    else:
        print("❌ astro.yaml faltante")
        all_checks_passed = False
    
    if os.path.exists(dockerfile):
        print("✅ Dockerfile presente")
    else:
        print("❌ Dockerfile faltante")
        all_checks_passed = False
    
    # 7. Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    if all_checks_passed:
        print("🎉 ¡TODAS LAS VERIFICACIONES PASARON!")
        print("✅ El proyecto está listo para la entrega")
        print("\n📌 PASOS PARA LA DEMO:")
        print("1. astro dev start")
        print("2. Abrir http://localhost:8080")
        print("3. Activar DAG 'propiedades_etl_pipeline'")
        print("4. Monitorear ejecución en tiempo real")
        print("5. Verificar archivos generados en /tmp/data/")
        
        print("\n📌 ALTERNATIVA LOCAL:")
        print("python test_pipeline_local.py")
        
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print("⚠️ Revisar los errores antes de la entrega")
        print("\n🔧 POSIBLES SOLUCIONES:")
        print("- Verificar que todos los archivos estén presentes")
        print("- Instalar dependencias: pip install -r requirements.txt")
        print("- Revisar sintaxis de archivos Python")
        print("- Verificar configuración de Astro CLI")
    
    print(f"\n📊 Resultado: {'ÉXITO' if all_checks_passed else 'FALLÓ'}")
    return all_checks_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
