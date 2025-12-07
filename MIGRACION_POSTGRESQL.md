# 🚀 Guía de Migración a PostgreSQL

## ✅ Cambios Ya Realizados

1. **requirements.txt actualizado** con:
   - `psycopg2-binary==2.9.9` (driver PostgreSQL)
   - `sqlalchemy==2.0.23` (ORM)

2. **models.py creado** con:
   - 8 tablas: paneles, inversores, baterias, ciudades, parametros, consecutivos, estadisticas
   - Función `migrate_from_json()` para importar datos existentes
   - Soporte para desarrollo local y Railway

---

## 📋 Pasos para Completar la Migración

### **PASO 1: Instalar PostgreSQL localmente (para testing)**

#### En macOS:
```bash
# Instalar PostgreSQL
brew install postgresql@15

# Iniciar servicio
brew services start postgresql@15

# Crear base de datos de prueba
createdb cotizador
```

#### Agregar a `.env` (desarrollo local):
```bash
# PostgreSQL Local (solo para testing)
DATABASE_URL=postgresql://tu_usuario:tu_password@localhost:5432/cotizador
# O usa las variables individuales:
PGHOST=localhost
PGPORT=5432
PGUSER=postgres
PGPASSWORD=postgres
PGDATABASE=cotizador
```

---

### **PASO 2: Probar migración localmente**

```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador/backend

# Activar entorno virtual
source venv/bin/activate

# Instalar nuevas dependencias
pip install -r requirements.txt

# Ejecutar migración (crear tablas e importar datos)
python models.py
```

**Salida esperada**:
```
✅ Base de datos inicializada correctamente
🔄 Iniciando migración desde JSON a PostgreSQL...
✅ Migrados 9 paneles
✅ Migrados 9 inversores
✅ Migradas 3 baterías
✅ Migradas 15 ciudades
✅ Migrados 6 bloques de parámetros
✅ Migrado consecutivo
✅ Migradas estadísticas
🎉 ¡Migración completada exitosamente!
```

---

### **PASO 3: Actualizar `server.py` para usar PostgreSQL**

Necesitas reemplazar todas las funciones que usan `load_json()` con queries SQLAlchemy.

**Ejemplo - Antes (JSON)**:
```python
def get_paneles_admin():
    data = load_json(EQUIPOS_FILE)
    return data["paneles"]
```

**Ejemplo - Después (PostgreSQL)**:
```python
from models import get_db_session, Panel

def get_paneles_admin():
    session = get_db_session()
    try:
        paneles = session.query(Panel).all()
        return [
            {
                "id": p.id,
                "nombre": p.nombre,
                "capacidad": p.capacidad,
                "precio": p.precio,
                "descripcion": p.descripcion,
                "eficienciaPanel": p.eficienciaPanel,
                "default": p.default
            }
            for p in paneles
        ]
    finally:
        session.close()
```

**Endpoints a actualizar** (aproximadamente 30 funciones):
- ✅ GET /api/equipos
- ✅ GET /api/admin/paneles
- ✅ POST /api/admin/paneles
- ✅ PUT /api/admin/paneles/{id}
- ✅ DELETE /api/admin/paneles/{id}
- ✅ PUT /api/admin/paneles/{id}/default
- (Repetir para inversores, baterías, ciudades, parámetros)

---

### **PASO 4: Configurar PostgreSQL en Railway**

1. **En el dashboard de Railway**:
   - Ir a tu proyecto
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway creará automáticamente la base de datos

2. **Variables de entorno automáticas**:
   Railway añadirá automáticamente:
   ```
   DATABASE_URL=postgresql://user:pass@host.railway.internal:5432/railway
   PGHOST=...
   PGPORT=5432
   PGUSER=postgres
   PGPASSWORD=...
   PGDATABASE=railway
   ```

3. **Inicializar base de datos en Railway**:
   
   Opción A - Desde consola local:
   ```bash
   # Conectarse a Railway
   railway login
   railway link
   
   # Ejecutar migración remota
   railway run python models.py
   ```
   
   Opción B - Agregar a `server.py` (se ejecuta al iniciar):
   ```python
   from models import init_database, migrate_from_json
   
   @app.on_event("startup")
   async def startup_event():
       if os.getenv("DATABASE_URL"):
           print("🔄 Inicializando base de datos...")
           init_database()
           
           # Solo migrar si las tablas están vacías
           session = get_db_session()
           from models import Panel
           if session.query(Panel).count() == 0:
               migrate_from_json()
           session.close()
   ```

---

### **PASO 5: Deploy a Railway**

```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador

# Commit cambios
git add backend/requirements.txt backend/models.py
git commit -m "feat: Migración a PostgreSQL con SQLAlchemy

- Agregado psycopg2-binary y sqlalchemy a requirements.txt
- Creado models.py con 8 tablas (paneles, inversores, baterias, etc)
- Función migrate_from_json() para importar datos existentes
- Soporte para desarrollo local y Railway"

# Push (Railway auto-deploya)
git push origin main
```

---

### **PASO 6: Verificar en Railway**

1. **Ver logs de deployment**:
   - En Railway dashboard → "Deployments" → Click último deploy
   - Buscar: "✅ Base de datos inicializada correctamente"

2. **Conectarse a PostgreSQL desde Railway CLI**:
   ```bash
   railway login
   railway link
   railway run psql $DATABASE_URL
   ```

3. **Verificar datos**:
   ```sql
   -- Ver tablas
   \dt
   
   -- Contar registros
   SELECT COUNT(*) FROM paneles;
   SELECT COUNT(*) FROM inversores;
   SELECT COUNT(*) FROM ciudades;
   
   -- Ver datos
   SELECT id, nombre, precio FROM paneles LIMIT 5;
   ```

---

## 🎯 Ventajas de PostgreSQL

1. **Persistencia garantizada**: Los datos sobreviven reinicios de contenedor
2. **Concurrencia**: Múltiples usuarios pueden modificar datos simultáneamente
3. **Transacciones**: Rollback automático si algo falla
4. **Backups**: Railway hace backups automáticos
5. **Escalabilidad**: Puedes upgradear plan si creces
6. **Queries complejas**: SQL completo disponible

---

## ⚠️ Importante

- **Los archivos JSON seguirán existiendo** como backup, pero no se usarán más
- **La migración es irreversible**: Una vez en PostgreSQL, no regreses a JSON
- **Railway PostgreSQL gratis**: 512MB storage, suficiente para ~100,000 cotizaciones
- **Testing local primero**: Siempre prueba localmente antes de desplegar

---

## 🔄 Siguiente Paso Recomendado

¿Quieres que:
1. **Te ayude a actualizar server.py** para usar PostgreSQL? (3-4 horas de trabajo)
2. **Creemos un script de migración automatizado**?
3. **Probemos la migración localmente primero**?

**Mi recomendación**: Probar localmente primero (#3), luego actualizar server.py (#1).
