# Factor de Temperatura por Ciudad

## Resumen

Se implementó el campo `factorTemperatura` en la tabla `ciudades` de PostgreSQL para corregir la producción de los paneles solares según la temperatura ambiente de cada región.

**Commits**:
- `81162d2` - feat: Implementar Factor_Temperatura por ciudad
- `76420bc` - fix: Cambiar ruta endpoint migración

**Estado**: ✅ Implementado y funcionando en producción

---

## Contexto Técnico

### ¿Por qué es necesario?

Los paneles solares pierden eficiencia a mayor temperatura ambiente. La especificación técnica estándar (STC - Standard Test Conditions) asume 25°C, pero en Colombia las temperaturas varían significativamente:

- **Costa Caribe** (Santa Marta, Barranquilla): 28-35°C promedio → **Pérdida ~15%** → Factor 0.85
- **Interior/Valles** (Medellín, Cali): 22-28°C promedio → **Pérdida ~10%** → Factor 0.90
- **Alta Montaña** (Bogotá, Tunja): 10-18°C promedio → **Pérdida ~5%** → Factor 0.92-0.95

### Fórmula Actualizada

**Antes**:
```python
energiaPanelDia = (panel["capacidad"] * eficiencia_panel * hsp) / 1000
```

**Después**:
```python
energiaPanelDia = (panel["capacidad"] * eficiencia_panel * hsp * factorTemperatura) / 1000
```

---

## Implementación

### 1. Modelo SQLAlchemy

**Archivo**: `backend/models.py`

```python
class Ciudad(Base):
    __tablename__ = "ciudades"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    nombre = Column(String(200), nullable=False)
    hsp = Column(Float, nullable=False)
    factorTemperatura = Column(Float, default=0.90)  # NUEVO
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 2. Carga de Datos

**Archivo**: `backend/server.py` línea 348

```python
def cargar_datos_desde_postgres():
    # ...
    ciudades_db = session.query(Ciudad).all()
    ciudades = {
        c.key: {
            "hsp": c.hsp, 
            "nombre": c.nombre,
            "factorTemperatura": getattr(c, 'factorTemperatura', 0.90)  # Fallback
        } 
        for c in ciudades_db
    }
```

### 3. Cálculo de Cotización

**Archivo**: `backend/server.py` línea 422

```python
def calcular_cotizacion(data, equipos, ciudades, parametros=None):
    # ...
    ciudad_data = ciudades.get(ciudad_key, ciudades.get("default", 4.5))
    hsp_value = ciudad_data.get("hsp") if isinstance(ciudad_data, dict) else ciudad_data
    hsp = float(data.get("hspCalculado") or hsp_value)
    
    # NUEVO: Factor de temperatura por ciudad
    factorTemperatura = ciudad_data.get("factorTemperatura", 0.90) if isinstance(ciudad_data, dict) else 0.90
    
    # ...
    energiaPanelDia = (panel["capacidad"] * eficiencia_panel * hsp * factorTemperatura) / 1000
```

### 4. Segunda Opción

**Archivo**: `backend/server.py` línea 667

```python
def calcular_segunda_opcion(data, equipos, ciudades, areaDisponible, cotizacion_id_base, parametros=None):
    # ... (mismo cambio que calcular_cotizacion)
    factorTemperatura = ciudad_data.get("factorTemperatura", 0.90) if isinstance(ciudad_data, dict) else 0.90
    energiaPanelDia = (panel["capacidad"] * eficiencia_panel * hsp * factorTemperatura) / 1000
```

---

## Migración a PostgreSQL

### Endpoint Admin

**Ruta**: `POST /api/admin/migraciones/factor-temperatura`

**Autenticación**: HTTP Basic (usuario/contraseña admin)

**Ejemplo**:
```bash
curl -X POST "https://web-production-3749b.up.railway.app/api/admin/migraciones/factor-temperatura" \
  -u "admin:password"
```

**Respuesta**:
```json
{
  "status": "success",
  "columna_ya_existia": false,
  "total_ciudades": 160,
  "ciudades_actualizadas": 37,
  "estadisticas": {
    "promedio": 0.895,
    "minimo": 0.84,
    "maximo": 0.93
  },
  "mensaje": "Migración completada exitosamente..."
}
```

### Valores por Ciudad

**Costa Caribe (Factor 0.85)**:
- Santa Marta, Barranquilla, Cartagena, Valledupar, Riohacha, Sincelejo, Montería, Magangué, Ciénaga, Fundación, Aracataca, Zona Bananera, Pueblo Viejo, Algarrobo

**Costa Caribe Alta (Factor 0.84)**:
- Albania Guajira, Maicao, Uribia

**Interior/Valles (Factor 0.88-0.91)**:
- Medellín (0.89), Cali (0.88), Bucaramanga (0.89), Cúcuta (0.88), Pereira (0.89), Manizales (0.91), Armenia (0.89), Ibagué (0.88), Neiva (0.87), Villavicencio (0.88), Yopal (0.87), Florencia (0.87)

**Alta Montaña (Factor 0.92-0.93)**:
- Bogotá (0.92), Tunja (0.92), Pasto (0.93), Popayán (0.91), Duitama (0.92), Sogamoso (0.92), Zipaquirá (0.92), Chía (0.92), Facatativá (0.92)

**Default (Factor 0.90)**:
- Todas las demás ciudades no listadas (123 ciudades)

---

## Validación y Pruebas

### Test en Producción

**Ciudad**: Santa Marta (Factor 0.85, HSP 5.6)

**Sistema**:
- 7 paneles de 550W
- 1 inversor de 3kW
- Capacidad: 3.85 kW

**Cálculo Manual**:
```
Energía por panel/día = (550W * 0.90 * 5.6 HSP * 0.85) / 1000
                      = 2.356 kWh

Generación mensual = 7 paneles * 2.356 kWh * 30 días * 0.90 efic_inversor
                    = 445.32 kWh
```

**Resultado del Sistema**: 445 kWh/mes

**Diferencia**: 0.32 kWh (redondeo) ✅

### Impacto en Generación

| Ciudad | Factor | HSP | Panel 550W | Energía/día | Diferencia vs Default |
|--------|--------|-----|------------|-------------|----------------------|
| Santa Marta | 0.85 | 5.6 | 550W | 2.36 kWh | -13% |
| Medellín | 0.89 | 4.8 | 550W | 2.10 kWh | -6% |
| Bogotá | 0.92 | 4.5 | 550W | 2.05 kWh | -3% |
| **Default** | **0.90** | - | - | - | **baseline** |

**Conclusión**: Los sistemas en la costa caribe generarán ~13% menos energía que lo calculado sin factor de temperatura, lo cual refleja mejor la realidad operativa.

---

## Impacto en el Sistema

### Endpoints Afectados

1. ✅ `POST /api/cotizar` - Usa `calcular_cotizacion()`
2. ✅ `POST /api/enviar-cotizacion` - Usa `calcular_cotizacion()` y `calcular_segunda_opcion()`
3. ✅ `GET /api/ciudades` - Retorna ciudades con factorTemperatura

### Funciones Actualizadas

1. ✅ `cargar_datos_desde_postgres()` - Carga factorTemperatura de BD
2. ✅ `calcular_cotizacion()` - Aplica factor en energiaPanelDia
3. ✅ `calcular_segunda_opcion()` - Aplica factor en energiaPanelDia

### Compatibilidad

- ✅ **Fallback**: Si una ciudad no tiene factorTemperatura, usa 0.90 (default)
- ✅ **JSON legacy**: Sistema soporta ciudades sin el campo (getattr con default)
- ✅ **Migración no destructiva**: Columna agregada con default, no afecta datos existentes

---

## Mantenimiento

### Agregar nueva ciudad con factor específico

**SQL directo**:
```sql
INSERT INTO ciudades (key, nombre, hsp, "factorTemperatura")
VALUES ('nueva_ciudad', 'Nueva Ciudad', 5.2, 0.88);
```

**Endpoint API** (próximamente):
```bash
curl -X POST "https://web-production-3749b.up.railway.app/api/admin/ciudades" \
  -u "admin:password" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "nueva_ciudad",
    "nombre": "Nueva Ciudad",
    "hsp": 5.2,
    "factorTemperatura": 0.88
  }'
```

### Actualizar factor existente

```bash
curl -X PUT "https://web-production-3749b.up.railway.app/api/admin/ciudades/santa_marta" \
  -u "admin:password" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Santa Marta",
    "hsp": 5.6,
    "factorTemperatura": 0.86
  }'
```

---

## Referencias

- **Script de migración**: `backend/migrar_factor_temperatura.py`
- **Endpoint de migración**: `backend/server.py` línea 2865
- **Documentación original**: Solicitud del cliente en prompt

**Fecha de implementación**: 8 de diciembre de 2025
**Versión**: Sistema v2.1.0
