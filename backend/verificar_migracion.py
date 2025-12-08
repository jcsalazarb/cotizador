#!/usr/bin/env python3
"""
Script para verificar que la migración a PostgreSQL fue exitosa
"""

import os
from dotenv import load_dotenv
from models import get_db_session, Panel, Inversor, Bateria, Ciudad, Parametro, Consecutivo

# Cargar variables de entorno
load_dotenv()

def verificar_migracion():
    """Verificar conteos de registros en PostgreSQL"""
    
    # Usar DATABASE_URL de Railway si está disponible, sino local
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL no configurada")
        return
    
    print(f"🔗 Conectando a: {database_url[:30]}...")
    
    session = get_db_session()
    
    try:
        # Contar registros
        paneles_count = session.query(Panel).count()
        inversores_count = session.query(Inversor).count()
        baterias_count = session.query(Bateria).count()
        ciudades_count = session.query(Ciudad).count()
        parametros_count = session.query(Parametro).count()
        consecutivo_count = session.query(Consecutivo).count()
        
        print("\n" + "="*50)
        print("📊 VERIFICACIÓN DE MIGRACIÓN POSTGRESQL")
        print("="*50)
        print(f"✅ Paneles:      {paneles_count:>3} registros")
        print(f"✅ Inversores:   {inversores_count:>3} registros")
        print(f"✅ Baterías:     {baterias_count:>3} registros")
        print(f"✅ Ciudades:     {ciudades_count:>3} registros")
        print(f"✅ Parámetros:   {parametros_count:>3} secciones")
        print(f"✅ Consecutivo:  {consecutivo_count:>3} registro")
        print("="*50)
        
        # Verificar ciudades específicas
        print("\n🏙️ Muestra de ciudades migradas:")
        ciudades_muestra = session.query(Ciudad).limit(10).all()
        for c in ciudades_muestra:
            print(f"   - {c.nombre:20} (key: {c.key:25} HSP: {c.hsp})")
        
        if ciudades_count == 160:
            print("\n🎉 ¡Migración EXITOSA! Las 160 ciudades están en PostgreSQL")
        elif ciudades_count == 161:
            print("\n🎉 ¡Migración EXITOSA! Las 161 ciudades están en PostgreSQL (incluye default)")
        else:
            print(f"\n⚠️ ADVERTENCIA: Se esperaban 160-161 ciudades, pero hay {ciudades_count}")
        
    except Exception as e:
        print(f"❌ Error al verificar: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    verificar_migracion()
