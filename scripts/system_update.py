#!/usr/bin/env python3
"""
Script para manejar actualizaciones del sistema
==============================================

Este script maneja las actualizaciones automáticas del sistema,
incluyendo git pull, instalación de dependencias y migraciones.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_executable_paths():
    """Obtener rutas de ejecutables según el entorno"""
    python_executable = sys.executable
    venv_path = os.path.dirname(python_executable)
    
    if os.name == 'nt':  # Windows
        return {
            'python': python_executable,
            'pip': os.path.join(venv_path, 'pip.exe'),
            'flask': os.path.join(venv_path, 'flask.exe'),
        }
    else:  # Unix/Linux
        return {
            'python': python_executable,
            'pip': os.path.join(venv_path, 'pip'),
            'flask': os.path.join(venv_path, 'flask'),
        }

def run_command(command, timeout=120, cwd=None):
    """Ejecutar comando con manejo de errores robusto"""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd or os.getcwd()
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Comando timeout después de {timeout} segundos',
            'returncode': -1
        }
    except FileNotFoundError as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Comando no encontrado: {str(e)}',
            'returncode': -2
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Error inesperado: {str(e)}',
            'returncode': -3
        }

def update_git():
    """Actualizar código desde git"""
    print("🔄 Actualizando código desde Git...")
    
    # Verificar si es un repositorio git
    if not os.path.exists('.git'):
        return {
            'success': True,  # No fallar si no es repo git
            'message': 'No es un repositorio Git - saltando actualización',
            'output': ''
        }
    
    # Git fetch
    result = run_command(['git', 'fetch'], timeout=60)
    if not result['success']:
        return {
            'success': True,  # No fallar por git en producción
            'message': f'Git fetch falló: {result["stderr"]}',
            'output': result['stderr']
        }
    
    # Git pull
    result = run_command(['git', 'pull', 'origin', 'main'], timeout=120)
    if not result['success']:
        return {
            'success': True,  # No fallar por git en producción
            'message': f'Git pull falló: {result["stderr"]}',
            'output': result['stderr']
        }
    
    return {
        'success': True,
        'message': 'Código actualizado desde Git',
        'output': result['stdout']
    }

def update_dependencies():
    """Actualizar dependencias de Python"""
    print("📦 Actualizando dependencias...")
    
    executables = get_executable_paths()
    
    # Intentar pip desde venv
    if os.path.exists(executables['pip']):
        command = [executables['pip'], 'install', '-r', 'requirements.txt']
    else:
        # Fallback a python -m pip
        command = [executables['python'], '-m', 'pip', 'install', '-r', 'requirements.txt']
    
    result = run_command(command, timeout=300)
    
    return {
        'success': True,  # No fallar por warnings de pip
        'message': 'Dependencias actualizadas' if result['success'] else f'Advertencias en pip: {result["stderr"]}',
        'output': result['stdout'] + '\n' + result['stderr']
    }

def run_migrations():
    """Ejecutar migraciones de base de datos"""
    print("🗄️  Ejecutando migraciones...")
    
    executables = get_executable_paths()
    
    # Configurar entorno
    env = os.environ.copy()
    env['FLASK_APP'] = 'run.py'
    
    # Intentar flask CLI
    if os.path.exists(executables['flask']):
        command = [executables['flask'], 'db', 'upgrade']
        result = run_command(command, timeout=180)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Migraciones ejecutadas con Flask CLI',
                'output': result['stdout']
            }
        else:
            print(f"Flask CLI falló: {result['stderr']}")
    
    # Fallback: python -m flask
    command = [executables['python'], '-m', 'flask', 'db', 'upgrade']
    result = run_command(command, timeout=180)
    
    if result['success']:
        return {
            'success': True,
            'message': 'Migraciones ejecutadas con python -m flask',
            'output': result['stdout']
        }
    
    # Último fallback: método programático
    print("Intentando método programático para migraciones...")
    try:
        from app import create_app
        from flask_migrate import upgrade
        
        app = create_app()
        with app.app_context():
            upgrade()
        
        return {
            'success': True,
            'message': 'Migraciones ejecutadas programáticamente',
            'output': 'Upgrade ejecutado directamente en Python'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error en migraciones: {str(e)}',
            'output': f'Flask CLI error: {result["stderr"]}\nMétodo programático error: {str(e)}'
        }

def perform_full_update():
    """Realizar actualización completa del sistema"""
    results = {
        'git': None,
        'dependencies': None,
        'migrations': None,
        'overall_success': False,
        'logs': []
    }
    
    try:
        # 1. Actualizar Git
        git_result = update_git()
        results['git'] = git_result
        results['logs'].append(f"Git: {git_result['message']}")
        
        # 2. Actualizar dependencias
        deps_result = update_dependencies()
        results['dependencies'] = deps_result
        results['logs'].append(f"Dependencies: {deps_result['message']}")
        
        # 3. Ejecutar migraciones (crítico)
        migration_result = run_migrations()
        results['migrations'] = migration_result
        results['logs'].append(f"Migrations: {migration_result['message']}")
        
        # El éxito general depende principalmente de las migraciones
        results['overall_success'] = migration_result['success']
        
        return results
        
    except Exception as e:
        results['logs'].append(f"Error inesperado: {str(e)}")
        return results

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Actualizar sistema')
    parser.add_argument('--git-only', action='store_true', help='Solo actualizar Git')
    parser.add_argument('--deps-only', action='store_true', help='Solo actualizar dependencias')
    parser.add_argument('--migrate-only', action='store_true', help='Solo ejecutar migraciones')
    parser.add_argument('--json', action='store_true', help='Salida en formato JSON')
    
    args = parser.parse_args()
    
    if args.git_only:
        result = update_git()
    elif args.deps_only:
        result = update_dependencies()
    elif args.migrate_only:
        result = run_migrations()
    else:
        result = perform_full_update()
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if isinstance(result, dict) and 'overall_success' in result:
            # Resultado completo
            for log in result['logs']:
                print(log)
            print(f"\n{'✅ Actualización completada' if result['overall_success'] else '❌ Actualización falló'}")
        else:
            # Resultado individual
            print(f"{'✅' if result['success'] else '❌'} {result['message']}")
            if result.get('output'):
                print(f"Output: {result['output']}")

if __name__ == "__main__":
    main()
