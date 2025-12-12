"""
Script para crear la tabla cotizaciones en PostgreSQL Railway
Ejecutar una sola vez después de hacer push de models.py actualizado
"""

from models import Base, create_db_engine, Cotizacion
import os

def crear_tabla_cotizaciones():
    """Crear solo la tabla cotizaciones sin afectar las demás"""
    try:
        # Verificar que DATABASE_URL exista
        if not os.getenv("DATABASE_URL"):
            print("❌ ERROR: DATABASE_URL no configurada")
            print("   Configura las variables de entorno primero")
            return False
        
        print("🔄 Conectando a PostgreSQL...")
        engine = create_db_engine()
        
        print("🔄 Creando tabla cotizaciones...")
        # Crear solo la tabla Cotizacion
        Cotizacion.__table__.create(bind=engine, checkfirst=True)
        
        print("✅ Tabla cotizaciones creada exitosamente!")
        print("\n📋 Estructura de la tabla:")
        print("   - id (String): NASSA-2025-0001")
        print("   - fecha_creacion (DateTime)")
        print("   - Datos del cliente (nombre, email, telefono, direccion, ciudad, nic)")
        print("   - Datos del sistema (tipo_vivienda, sistema_electrico, tipo_sistema_fv)")
        print("   - Datos de consumo (consumo_mensual, valor_factura, valor_kwh, etc.)")
        print("   - Equipos (panel_id/nombre, inversor_id/nombre, bateria_id/nombre)")
        print("   - Opción 1 (num_paneles_op1, capacidad_op1, valor_op1, etc.)")
        print("   - Opción 2 (tiene_opcion2, num_paneles_op2, capacidad_op2, etc.)")
        print("   - JSON completo (datos_completos)")
        print("   - Estado (email_enviado, fecha_envio_email, num_opciones)")
        print("   - Metadata (legalizacion, seleccion_manual, created_at, updated_at)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando tabla: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("CREAR TABLA COTIZACIONES EN POSTGRESQL")
    print("="*60)
    
    exito = crear_tabla_cotizaciones()
    
    if exito:
        print("\n✅ TABLA CREADA CORRECTAMENTE")
        print("\n🎯 Próximos pasos:")
        print("   1. Prueba generando una cotización en Railway")
        print("   2. Verifica que se guarde en la tabla")
        print("   3. Prueba enviar email y confirma que actualiza estado")
    else:
        print("\n❌ FALLÓ LA CREACIÓN")
        print("\n🔧 Soluciones:")
        print("   1. Verifica que DATABASE_URL esté configurada en Railway")
        print("   2. Revisa los logs de error arriba")
        print("   3. Asegúrate de tener models.py actualizado")
