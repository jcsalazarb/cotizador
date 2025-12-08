"""
Migración: Agregar columna factorTemperatura a tabla ciudades
Sistema de Cotización Solar NASSA

Este script agrega el campo factorTemperatura con valores por defecto
basados en el clima de cada región de Colombia.

Valores de referencia:
- Costa Caribe (Santa Marta, Barranquilla, Cartagena): 0.85 (alta temperatura)
- Interior/Valles (Medellín, Cali, Bucaramanga): 0.90 (temperatura moderada)
- Alta Montaña (Bogotá, Tunja, Pasto): 0.92 (baja temperatura)
- Default: 0.90
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Conectar a PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# Si no está en .env, solicitar manualmente
if not DATABASE_URL:
    print("⚠️  DATABASE_URL no encontrada en .env")
    print("\nPor favor ingresa la URL de PostgreSQL:")
    print("Formato: postgresql://user:password@host:port/database")
    DATABASE_URL = input("\nDATABASE_URL: ").strip()
    
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL es requerida para ejecutar la migración")

engine = create_engine(DATABASE_URL)

# Valores de factorTemperatura por ciudad (ciudades no listadas usarán el default 0.90)
FACTORES_TEMPERATURA = {
    # Costa Caribe - Alta temperatura = menor factor (0.85)
    "santa_marta": 0.85,
    "barranquilla": 0.85,
    "cartagena": 0.85,
    "valledupar": 0.86,
    "riohacha": 0.85,
    "sincelejo": 0.86,
    "monteria": 0.86,
    "magangue": 0.85,
    "cienaga": 0.85,
    "fundacion": 0.85,
    "aracataca": 0.85,
    "zona_bananera": 0.85,
    "pueblo_viejo": 0.85,
    "algarrobo": 0.85,
    "albania_guajira": 0.84,
    "maicao": 0.84,
    "uribia": 0.84,
    
    # Interior/Valles - Temperatura moderada (0.88-0.90)
    "medellin": 0.89,
    "cali": 0.88,
    "bucaramanga": 0.89,
    "cucuta": 0.88,
    "pereira": 0.89,
    "manizales": 0.91,
    "armenia": 0.89,
    "ibague": 0.88,
    "neiva": 0.87,
    "villavicencio": 0.88,
    "yopal": 0.87,
    "florencia": 0.87,
    
    # Alta Montaña - Baja temperatura = mayor factor (0.92-0.93)
    "bogota": 0.92,
    "tunja": 0.92,
    "pasto": 0.93,
    "popayan": 0.91,
    "duitama": 0.92,
    "sogamoso": 0.92,
    "zipaquira": 0.92,
    "chia": 0.92,
    "facatativa": 0.92,
}

def migrar_factor_temperatura():
    """
    Agrega la columna factorTemperatura a la tabla ciudades
    y actualiza los valores basados en el clima de cada región.
    """
    with engine.connect() as conn:
        # 1. Verificar si la columna ya existe
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='ciudades' AND column_name='factorTemperatura'
        """))
        
        if result.fetchone():
            print("⚠️  La columna factorTemperatura ya existe en la tabla ciudades")
            respuesta = input("¿Deseas actualizar los valores? (s/n): ")
            if respuesta.lower() != 's':
                print("❌ Migración cancelada")
                return
        else:
            # 2. Agregar la columna con valor por defecto 0.90
            print("📊 Agregando columna factorTemperatura...")
            conn.execute(text("""
                ALTER TABLE ciudades 
                ADD COLUMN "factorTemperatura" DOUBLE PRECISION DEFAULT 0.90
            """))
            conn.commit()
            print("✅ Columna agregada exitosamente")
        
        # 3. Actualizar valores específicos por ciudad
        print("\n🌡️  Actualizando factores de temperatura por ciudad...")
        ciudades_actualizadas = 0
        
        for ciudad_key, factor in FACTORES_TEMPERATURA.items():
            result = conn.execute(
                text("""
                    UPDATE ciudades 
                    SET "factorTemperatura" = :factor 
                    WHERE key = :ciudad_key
                """),
                {"factor": factor, "ciudad_key": ciudad_key}
            )
            if result.rowcount > 0:
                ciudades_actualizadas += 1
                print(f"  ✓ {ciudad_key}: {factor}")
        
        conn.commit()
        
        # 4. Verificar resultados
        result = conn.execute(text("""
            SELECT COUNT(*) as total,
                   AVG("factorTemperatura") as promedio,
                   MIN("factorTemperatura") as minimo,
                   MAX("factorTemperatura") as maximo
            FROM ciudades
        """))
        stats = result.fetchone()
        
        print(f"\n📈 RESULTADOS DE LA MIGRACIÓN:")
        print(f"  - Total ciudades: {stats[0]}")
        print(f"  - Ciudades actualizadas con factor específico: {ciudades_actualizadas}")
        print(f"  - Factor promedio: {stats[1]:.3f}")
        print(f"  - Factor mínimo: {stats[2]:.3f} (costa caribe)")
        print(f"  - Factor máximo: {stats[3]:.3f} (alta montaña)")
        print(f"\n✅ Migración completada exitosamente")
        print(f"\n💡 Las ciudades no listadas mantendrán el factor default de 0.90")

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN: Agregar factorTemperatura a ciudades")
    print("=" * 60)
    print("\nEste script agregará el campo factorTemperatura a PostgreSQL")
    print("con valores específicos según el clima de cada región.\n")
    
    try:
        migrar_factor_temperatura()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
