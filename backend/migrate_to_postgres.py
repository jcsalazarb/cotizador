"""
Script de migración: JSON → PostgreSQL
Ejecutar UNA SOLA VEZ después de desplegar en Railway
"""

import os
import sys
import json
from pathlib import Path

# Agregar el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from models import (
    init_database, 
    get_db_session, 
    Panel, Inversor, Bateria, Ciudad, Parametro, Consecutivo, Estadistica
)

def migrate():
    print("🔄 Iniciando migración de JSON a PostgreSQL...")
    
    # Verificar DATABASE_URL
    if not os.getenv("DATABASE_URL"):
        print("❌ ERROR: Variable DATABASE_URL no encontrada")
        print("   Asegúrate de que PostgreSQL esté configurado en Railway")
        return False
    
    try:
        # 1. Crear todas las tablas
        print("\n📊 Paso 1: Creando tablas...")
        init_database()
        print("✅ Tablas creadas exitosamente")
        
        # 2. Obtener sesión
        session = get_db_session()
        
        # 3. MIGRAR EQUIPOS
        CONFIG_DIR = Path(__file__).parent / "config"
        equipos_file = CONFIG_DIR / "equipos.json"
        
        if not equipos_file.exists():
            print("❌ ERROR: No se encontró equipos.json")
            return False
            
        with open(equipos_file, "r", encoding="utf-8") as f:
            equipos = json.load(f)
        
        # 3a. Migrar Paneles
        print("\n☀️ Paso 2: Migrando paneles...")
        paneles_migrados = 0
        for panel_data in equipos.get("paneles", []):
            panel = Panel(
                id=panel_data["id"],
                nombre=panel_data["nombre"],
                capacidad=panel_data["capacidad"],
                precio=panel_data["precio"],
                descripcion=panel_data["descripcion"],
                eficienciaPanel=panel_data.get("eficienciaPanel", 0.90),
                area=panel_data.get("area", 2.0),
                default=panel_data.get("default", False)
            )
            session.merge(panel)
            paneles_migrados += 1
        print(f"✅ Migrados {paneles_migrados} paneles")
        
        # 3b. Migrar Inversores
        print("\n⚡ Paso 3: Migrando inversores...")
        inversores_migrados = 0
        for inv_data in equipos.get("inversores", []):
            # Mapear campos antiguos a nuevos
            sistema_electrico = inv_data.get("sistemaElectrico") or inv_data.get("tipo_sistema", ["monofasico"])
            
            inversor = Inversor(
                id=inv_data["id"],
                nombre=inv_data["nombre"],
                capacidad=inv_data["capacidad"],
                precio=inv_data["precio"],
                descripcion=inv_data["descripcion"],
                eficiencia=inv_data.get("eficiencia", 0.90),
                sistemaElectrico=sistema_electrico,
                tipo=inv_data.get("tipo", "STRING"),
                paneles_por_inversor=inv_data.get("paneles_por_inversor", 0),
                sobredimensionamiento=inv_data.get("sobredimensionamiento", 0.40),
                default=inv_data.get("default", False)
            )
            session.merge(inversor)
            inversores_migrados += 1
        print(f"✅ Migrados {inversores_migrados} inversores")
        
        # 3c. Migrar Baterías
        print("\n🔋 Paso 4: Migrando baterías...")
        baterias_migradas = 0
        for bat_data in equipos.get("baterias", []):
            bateria = Bateria(
                id=bat_data["id"],
                nombre=bat_data["nombre"],
                capacidad=bat_data["capacidad"],
                precio=bat_data["precio"],
                descripcion=bat_data["descripcion"],
                default=bat_data.get("default", False)
            )
            session.merge(bateria)
            baterias_migradas += 1
        print(f"✅ Migradas {baterias_migradas} baterías")
        
        # 4. MIGRAR CIUDADES
        print("\n🏙️ Paso 5: Migrando ciudades...")
        ciudades_file = CONFIG_DIR / "ciudades.json"
        if ciudades_file.exists():
            with open(ciudades_file, "r", encoding="utf-8") as f:
                ciudades = json.load(f)
            
            ciudades_migradas = 0
            for key, data in ciudades.items():
                if key != "default":
                    ciudad = Ciudad(
                        key=key,
                        nombre=data.get("nombre", key.replace("_", " ").title()),
                        hsp=data["hsp"]
                    )
                    session.merge(ciudad)
                    ciudades_migradas += 1
            print(f"✅ Migradas {ciudades_migradas} ciudades")
        
        # 5. MIGRAR PARÁMETROS
        print("\n⚙️ Paso 6: Migrando parámetros...")
        parametros_file = CONFIG_DIR / "parametros.json"
        if parametros_file.exists():
            with open(parametros_file, "r", encoding="utf-8") as f:
                parametros = json.load(f)
            
            parametros_migrados = 0
            for seccion, data in parametros.items():
                param = Parametro(seccion=seccion, data=data)
                session.merge(param)
                parametros_migrados += 1
            print(f"✅ Migrados {parametros_migrados} bloques de parámetros")
        
        # 6. MIGRAR CONSECUTIVO
        print("\n🔢 Paso 7: Migrando consecutivo...")
        consecutivo_file = CONFIG_DIR / "consecutivo.json"
        if consecutivo_file.exists():
            with open(consecutivo_file, "r", encoding="utf-8") as f:
                consecutivo_data = json.load(f)
            
            consecutivo = Consecutivo(
                id=1,
                ano_actual=consecutivo_data["ano_actual"],
                ultimo_consecutivo=consecutivo_data["ultimo_consecutivo"]
            )
            session.merge(consecutivo)
            print("✅ Migrado consecutivo")
        
        # 7. MIGRAR ESTADÍSTICAS
        print("\n📈 Paso 8: Migrando estadísticas...")
        estadisticas_file = CONFIG_DIR / "estadisticas.json"
        if estadisticas_file.exists():
            with open(estadisticas_file, "r", encoding="utf-8") as f:
                stats_data = json.load(f)
            
            stats = Estadistica(
                id=1,
                total_cotizaciones=stats_data.get("total_cotizaciones", 0),
                total_email_enviados=stats_data.get("total_email_enviados", 0)
            )
            session.merge(stats)
            print("✅ Migradas estadísticas")
        
        # COMMIT FINAL
        session.commit()
        session.close()
        
        print("\n" + "="*50)
        print("🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        print("="*50)
        print(f"   Paneles: {paneles_migrados}")
        print(f"   Inversores: {inversores_migrados}")
        print(f"   Baterías: {baterias_migradas}")
        print(f"   Ciudades: {ciudades_migradas}")
        print(f"   Parámetros: {parametros_migrados}")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN MIGRACIÓN: {e}")
        import traceback
        traceback.print_exc()
        if 'session' in locals():
            session.rollback()
            session.close()
        return False


if __name__ == "__main__":
    print("="*50)
    print("  MIGRACIÓN JSON → PostgreSQL")
    print("  Sistema de Cotización Solar NASSA")
    print("="*50)
    
    success = migrate()
    
    if success:
        print("\n✅ Puedes continuar con la actualización de server.py")
        sys.exit(0)
    else:
        print("\n❌ La migración falló. Revisa los errores arriba.")
        sys.exit(1)
