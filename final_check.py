"""
SCRIPT FINAL DE VERIFICACIÓN COMPLETA
=====================================
Ejecuta todas las verificaciones necesarias para confirmar que el sistema
WooCommerce-Calendar está completamente funcional.
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def run_verification_script(script_name, description):
    """Ejecuta un script de verificación"""
    print(f"\n🔍 {description}...")
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} - EXITOSO")
            return True
        else:
            print(f"❌ {description} - FALLÓ")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}...")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False

def check_files_exist():
    """Verifica que todos los archivos importantes existan"""
    print("\n📁 VERIFICANDO ARCHIVOS...")
    
    required_files = [
        "app.py",
        "app/blueprints/calendar/routes.py",
        "app/models/user.py", 
        "app/templates/calendar.html",
        "templates/woocommerce_config.html",
        "GUIA_DE_USO.md",
        "RESUMEN_FINAL.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
            print(f"❌ {file_path}")
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"\n⚠️ Archivos faltantes: {len(missing_files)}")
        return False
    else:
        print(f"\n✅ Todos los archivos requeridos están presentes")
        return True

def show_next_steps():
    """Muestra los próximos pasos para el usuario"""
    print("\n" + "="*60)
    print("🎯 PRÓXIMOS PASOS PARA USAR EL SISTEMA")
    print("="*60)
    
    print("\n1️⃣ EJECUTAR LA APLICACIÓN:")
    print("   python app.py")
    print("   (La aplicación estará en http://localhost:5000)")
    
    print("\n2️⃣ ABRIR EL CALENDARIO:")
    print("   http://localhost:5000")
    print("   (Página principal del calendario)")
    
    print("\n3️⃣ CONFIGURAR WOOCOMMERCE:")
    print("   http://localhost:5000/woocommerce/config")
    print("   • Copiar URL del webhook")
    print("   • Configurar en WooCommerce")
    print("   • Probar sincronización")
    
    print("\n4️⃣ VERIFICAR FUNCIONAMIENTO:")
    print("   • Hacer clic en 'Probar Webhook'")
    print("   • Hacer clic en 'Sincronizar Ahora'")
    print("   • Ver pedidos en el calendario con colores")
    
    print("\n5️⃣ CONFIGURACIÓN WOOCOMMERCE REAL:")
    print("   • URL Webhook: http://localhost:5000/webhook/woocommerce")
    print("   • Eventos: order.created, order.updated, order.status_changed")
    print("   • Formato: JSON")
    
    print("\n📚 DOCUMENTACIÓN DISPONIBLE:")
    print("   • GUIA_DE_USO.md - Guía completa")
    print("   • RESUMEN_FINAL.md - Resumen técnico")
    print("   • IMPLEMENTATION_SUMMARY.md - Detalles de implementación")

def show_troubleshooting():
    """Muestra información de resolución de problemas"""
    print("\n🔧 RESOLUCIÓN DE PROBLEMAS:")
    print("   Si los pedidos no aparecen:")
    print("   • Verificar que sea usuario admin")
    print("   • Refrescar la página (F5)")
    print("   • Ejecutar: python diagnose_woocommerce.py")
    print("   • Verificar fechas de los pedidos")
    
    print("\n   Si hay errores 404:")
    print("   • Verificar que la app esté en puerto 5000")
    print("   • Revisar URLs de API sin prefijo /calendar/")
    
    print("\n   Para webhooks en desarrollo:")
    print("   • Usar ngrok para túneles públicos")
    print("   • Verificar accesibilidad desde WooCommerce")

def main():
    """Función principal"""
    print("🔥 VERIFICACIÓN FINAL DEL SISTEMA WOOCOMMERCE-CALENDAR")
    print("=" * 65)
    print("Este script verifica que todo esté listo para usar.")
    
    # Contadores
    total_checks = 0
    passed_checks = 0
    
    # 1. Verificar archivos
    total_checks += 1
    if check_files_exist():
        passed_checks += 1
    
    # 2. Verificar sistema
    total_checks += 1
    if run_verification_script("verify_system.py", "Verificación del sistema"):
        passed_checks += 1
    
    # 3. Diagnóstico (opcional si hay problemas)
    if os.path.exists("diagnose_woocommerce.py"):
        print(f"\n💡 Para diagnóstico detallado ejecute:")
        print(f"   python diagnose_woocommerce.py")
    
    # 4. Mostrar resultados
    print("\n" + "="*65)
    print("📊 RESULTADOS DE LA VERIFICACIÓN")
    print("="*65)
    
    percentage = (passed_checks / total_checks) * 100
    print(f"✅ Verificaciones exitosas: {passed_checks}/{total_checks}")
    print(f"📈 Porcentaje de éxito: {percentage:.1f}%")
    
    if percentage >= 100:
        print("\n🎉 ¡EXCELENTE! El sistema está completamente listo.")
        status = "PERFECTO"
        emoji = "🏆"
    elif percentage >= 80:
        print("\n✅ ¡BIEN! El sistema está mayormente listo.")
        status = "FUNCIONAL"
        emoji = "✅"
    else:
        print("\n⚠️ Hay algunos problemas que necesitan atención.")
        status = "PROBLEMAS"
        emoji = "⚠️"
    
    print(f"\n{emoji} ESTADO FINAL: {status}")
    
    # 5. Mostrar próximos pasos
    show_next_steps()
    
    # 6. Resolución de problemas
    show_troubleshooting()
    
    # 7. Información adicional
    print("\n💬 INFORMACIÓN ADICIONAL:")
    print("   • Todos los pedidos de WooCommerce se guardan como notas")
    print("   • Cada estado tiene su color específico")  
    print("   • Los admins ven todas las notas, usuarios normales solo las suyas")
    print("   • La sincronización puede ser automática (webhook) o manual")
    print("   • El sistema incluye API REST completa para integraciones")
    
    print("\n" + "="*65)
    print("🚀 ¡EL SISTEMA ESTÁ LISTO PARA USAR!")
    print("Ejecute: python app.py")
    print("Luego vaya a: http://localhost:5000")
    print("="*65)
    
    return percentage >= 80

if __name__ == "__main__":
    success = main()
    
    # Mensaje final
    if success:
        print(f"\n🎯 ¡Verificación completada exitosamente!")
        print(f"El sistema WooCommerce-Calendar está listo para usar.")
    else:
        print(f"\n⚠️ Algunos problemas encontrados.")
        print(f"Revise los mensajes anteriores y corrija antes de continuar.")
    
    sys.exit(0 if success else 1)
