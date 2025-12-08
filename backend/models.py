"""
Modelos SQLAlchemy para la base de datos PostgreSQL
Sistema de Cotización Solar NASSA
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, JSON, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Base para los modelos
Base = declarative_base()

# ==================== MODELOS ====================

class Panel(Base):
    __tablename__ = "paneles"
    
    id = Column(String(50), primary_key=True)
    nombre = Column(String(200), nullable=False)
    capacidad = Column(Float, nullable=False)  # Watts
    precio = Column(Float, nullable=False)  # COP
    descripcion = Column(Text, nullable=False)
    eficienciaPanel = Column(Float, default=0.90)
    area = Column(Float, default=2.0)  # m² - Área del panel
    default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Inversor(Base):
    __tablename__ = "inversores"
    
    id = Column(String(50), primary_key=True)
    nombre = Column(String(200), nullable=False)
    capacidad = Column(Float, nullable=False)  # Watts
    precio = Column(Float, nullable=False)  # COP
    descripcion = Column(Text, nullable=False)
    eficiencia = Column(Float, default=0.90)
    sistemaElectrico = Column(JSON, nullable=False)  # ["monofasico", "bifasico", "trifasico"]
    
    # Nuevos campos para MICRO/STRING
    tipo = Column(String(20), default="STRING")  # "MICRO" o "STRING"
    paneles_por_inversor = Column(Integer, default=0)  # Solo para MICRO
    sobredimensionamiento = Column(Float, default=0.40)  # Solo para STRING
    
    default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Bateria(Base):
    __tablename__ = "baterias"
    
    id = Column(String(50), primary_key=True)
    nombre = Column(String(200), nullable=False)
    capacidad = Column(Float, nullable=False)  # Wh
    precio = Column(Float, nullable=False)  # COP
    descripcion = Column(Text, nullable=False)
    default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Ciudad(Base):
    __tablename__ = "ciudades"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)  # "santa_marta", "barranquilla"
    nombre = Column(String(200), nullable=False)  # "Santa Marta", "Barranquilla"
    hsp = Column(Float, nullable=False)  # Horas Solar Pico
    factorTemperatura = Column(Float, default=0.90)  # Factor de temperatura (0.84-0.95)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Parametro(Base):
    __tablename__ = "parametros"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    seccion = Column(String(100), nullable=False)  # "costos_instalacion", "parametros_fiscales", etc.
    data = Column(JSON, nullable=False)  # Todo el bloque de datos
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Consecutivo(Base):
    __tablename__ = "consecutivos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ano_actual = Column(Integer, nullable=False)
    ultimo_consecutivo = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Estadistica(Base):
    __tablename__ = "estadisticas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    total_cotizaciones = Column(Integer, default=0)
    total_email_enviados = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== CONFIGURACIÓN DE BASE DE DATOS ====================

def get_database_url():
    """Obtener URL de conexión desde variables de entorno"""
    # Railway proporciona DATABASE_URL automáticamente
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        # Fallback para desarrollo local
        database_url = (
            f"postgresql://{os.getenv('PGUSER', 'postgres')}:"
            f"{os.getenv('PGPASSWORD', 'postgres')}@"
            f"{os.getenv('PGHOST', 'localhost')}:"
            f"{os.getenv('PGPORT', '5432')}/"
            f"{os.getenv('PGDATABASE', 'cotizador')}"
        )
    
    return database_url


def create_db_engine():
    """Crear engine de SQLAlchemy"""
    database_url = get_database_url()
    engine = create_engine(database_url, echo=False)
    return engine


def get_db_session():
    """Obtener sesión de base de datos"""
    engine = create_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def init_database():
    """Inicializar base de datos (crear tablas)"""
    engine = create_db_engine()
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada correctamente")


# ==================== FUNCIÓN DE MIGRACIÓN ====================

def migrate_from_json():
    """
    Migrar datos existentes de archivos JSON a PostgreSQL
    Esta función se ejecuta UNA SOLA VEZ después de configurar PostgreSQL
    """
    import json
    from pathlib import Path
    
    print("🔄 Iniciando migración desde JSON a PostgreSQL...")
    
    # Rutas de archivos JSON
    BASE_DIR = Path(__file__).parent
    CONFIG_DIR = BASE_DIR / "config"
    
    session = get_db_session()
    
    try:
        # 1. MIGRAR EQUIPOS
        equipos_file = CONFIG_DIR / "equipos.json"
        if equipos_file.exists():
            with open(equipos_file, "r", encoding="utf-8") as f:
                equipos = json.load(f)
            
            # Paneles
            for panel_data in equipos.get("paneles", []):
                panel = Panel(**panel_data)
                session.merge(panel)  # merge = insert or update
            print(f"✅ Migrados {len(equipos.get('paneles', []))} paneles")
            
            # Inversores
            for inv_data in equipos.get("inversores", []):
                # Mapear tipo_sistema → sistemaElectrico
                if "tipo_sistema" in inv_data:
                    tipo_sistema = inv_data.pop("tipo_sistema")
                    # Convertir string a lista (formato esperado por el modelo)
                    inv_data["sistemaElectrico"] = [tipo_sistema]
                
                inversor = Inversor(**inv_data)
                session.merge(inversor)
            print(f"✅ Migrados {len(equipos.get('inversores', []))} inversores")
            
            # Baterías
            for bat_data in equipos.get("baterias", []):
                bateria = Bateria(**bat_data)
                session.merge(bateria)
            print(f"✅ Migradas {len(equipos.get('baterias', []))} baterías")
        
        # 2. MIGRAR CIUDADES
        ciudades_file = CONFIG_DIR / "ciudades.json"
        if ciudades_file.exists():
            with open(ciudades_file, "r", encoding="utf-8") as f:
                ciudades = json.load(f)
            
            for key, data in ciudades.items():
                if key != "default":
                    ciudad = Ciudad(
                        key=key,
                        nombre=data.get("nombre", key.replace("_", " ").title()),
                        hsp=data["hsp"]
                    )
                    session.merge(ciudad)
            print(f"✅ Migradas {len(ciudades) - 1} ciudades")
        
        # 3. MIGRAR PARÁMETROS
        parametros_file = CONFIG_DIR / "parametros.json"
        if parametros_file.exists():
            with open(parametros_file, "r", encoding="utf-8") as f:
                parametros = json.load(f)
            
            for seccion, data in parametros.items():
                param = Parametro(seccion=seccion, data=data)
                session.add(param)
            print(f"✅ Migrados {len(parametros)} bloques de parámetros")
        
        # 4. MIGRAR CONSECUTIVO
        consecutivo_file = CONFIG_DIR / "consecutivo.json"
        if consecutivo_file.exists():
            with open(consecutivo_file, "r", encoding="utf-8") as f:
                consecutivo_data = json.load(f)
            
            consecutivo = Consecutivo(
                ano_actual=consecutivo_data["ano_actual"],
                ultimo_consecutivo=consecutivo_data["ultimo_consecutivo"]
            )
            session.add(consecutivo)
            print("✅ Migrado consecutivo")
        
        # 5. MIGRAR ESTADÍSTICAS
        estadisticas_file = CONFIG_DIR / "estadisticas.json"
        if estadisticas_file.exists():
            with open(estadisticas_file, "r", encoding="utf-8") as f:
                stats_data = json.load(f)
            
            stats = Estadistica(
                total_cotizaciones=stats_data.get("total_cotizaciones", 0),
                total_email_enviados=stats_data.get("total_email_enviados", 0)
            )
            session.add(stats)
            print("✅ Migradas estadísticas")
        
        session.commit()
        print("🎉 ¡Migración completada exitosamente!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error en migración: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    # Este bloque ya no se usa - usar migrate_to_postgres.py en su lugar
    print("⚠️ Usar migrate_to_postgres.py para migración inicial")
    print("⚠️ Este archivo solo proporciona modelos y funciones auxiliares")
