# API de Administración - NASSA Solar

## Autenticación
Todos los endpoints de administración requieren autenticación HTTP Basic con las credenciales configuradas en `.env`:
- Usuario: `ADMIN_USER` (default: `admin`)
- Contraseña: `ADMIN_PASS` (default: `changeme`)

**Ejemplo curl:**
```bash
curl -u admin:changeme http://localhost:8001/api/admin/parametros
```

---

## 📋 Gestión de Parámetros de Costos

### GET /api/admin/parametros
Obtiene todos los parámetros de costos, fiscales y de proyección.

**Respuesta:**
```json
{
  "costos_instalacion": {
    "soporteria_por_panel": 180000,
    "instalacion_por_panel": 250000,
    "materiales_por_panel": 150000,
    "mantenimiento_anual_por_kw": 120000
  },
  "parametros_fiscales": {
    "iva_porcentaje": 0.19,
    "impuesto_renta_porcentaje": 0.35,
    "deduccion_renta_base_porcentaje": 0.50,
    "anos_deduccion": 5,
    "anos_depreciacion": 3
  },
  "parametros_proyeccion": {
    "degradacion_anual_panel": 0.01,
    "factor_primer_ano": 0.5,
    "incremento_anual_kwh": 0.055,
    "anos_proyeccion": 25
  }
}
```

### PUT /api/admin/parametros
Actualiza los parámetros de costos.

**Body:**
```json
{
  "costos_instalacion": {...},
  "parametros_fiscales": {...},
  "parametros_proyeccion": {...}
}
```

---

## 🔋 Gestión de Paneles

### GET /api/admin/paneles
Lista todos los paneles con precios.

### POST /api/admin/paneles
Crea un nuevo panel.

**Body:**
```json
{
  "id": "panel8",
  "nombre": "Panel Nuevo 700W",
  "capacidad": 700,
  "precio": 1200000,
  "descripcion": "Nuevo panel de alta eficiencia",
  "eficienciaPanel": 0.90
}
```

### PUT /api/admin/paneles/{panel_id}
Actualiza un panel existente.

**Body:** Mismo formato que POST

### DELETE /api/admin/paneles/{panel_id}
Elimina un panel.

---

## ⚡ Gestión de Inversores

### GET /api/admin/inversores
Lista todos los inversores con precios.

### POST /api/admin/inversores
Crea un nuevo inversor.

**Body:**
```json
{
  "id": "inv9",
  "nombre": "Inversor Nuevo 15kW",
  "capacidad": 15000,
  "precio": 8000000,
  "descripcion": "Inversor trifásico industrial",
  "eficiencia": 0.90
}
```

### PUT /api/admin/inversores/{inversor_id}
Actualiza un inversor existente.

### DELETE /api/admin/inversores/{inversor_id}
Elimina un inversor.

---

## 🔋 Gestión de Baterías

### GET /api/admin/baterias
Lista todas las baterías con precios.

### POST /api/admin/baterias
Crea una nueva batería.

**Body:**
```json
{
  "id": "bat8",
  "nombre": "Batería Nueva 20kWh",
  "capacidad": 20000,
  "precio": 28000000,
  "descripcion": "Batería de litio de alta capacidad"
}
```

### PUT /api/admin/baterias/{bateria_id}
Actualiza una batería existente.

### DELETE /api/admin/baterias/{bateria_id}
Elimina una batería.

---

## 📝 Ejemplos de Uso

### Actualizar precios de soportería e instalación
```bash
curl -u admin:changeme -X PUT http://localhost:8001/api/admin/parametros \
  -H "Content-Type: application/json" \
  -d '{
    "costos_instalacion": {
      "soporteria_por_panel": 200000,
      "instalacion_por_panel": 280000,
      "materiales_por_panel": 170000,
      "mantenimiento_anual_por_kw": 150000
    },
    "parametros_fiscales": {
      "iva_porcentaje": 0.19,
      "impuesto_renta_porcentaje": 0.35,
      "deduccion_renta_base_porcentaje": 0.50,
      "anos_deduccion": 5,
      "anos_depreciacion": 3
    },
    "parametros_proyeccion": {
      "degradacion_anual_panel": 0.01,
      "factor_primer_ano": 0.5,
      "incremento_anual_kwh": 0.055,
      "anos_proyeccion": 25
    }
  }'
```

### Crear nuevo panel
```bash
curl -u admin:changeme -X POST http://localhost:8001/api/admin/paneles \
  -H "Content-Type: application/json" \
  -d '{
    "id": "panel8",
    "nombre": "Panel Solar 700W Premium",
    "capacidad": 700,
    "precio": 1250000,
    "descripcion": "Panel de última generación",
    "eficienciaPanel": 0.90
  }'
```

### Actualizar precio de un panel
```bash
curl -u admin:changeme -X PUT http://localhost:8001/api/admin/paneles/panel1 \
  -H "Content-Type: application/json" \
  -d '{
    "id": "panel1",
    "nombre": "Panel Canadian Solar 550W",
    "capacidad": 550,
    "precio": 900000,
    "descripcion": "Monocristalino, 25 años garantía",
    "eficienciaPanel": 0.90
  }'
```

### Eliminar un equipo
```bash
curl -u admin:changeme -X DELETE http://localhost:8001/api/admin/paneles/panel7
```

---

## ✅ Respuestas

**Éxito:**
```json
{
  "status": "success",
  "mensaje": "Panel panel8 creado exitosamente"
}
```

**Error 400 - ID Duplicado:**
```json
{
  "detail": "Ya existe un panel con ID panel8"
}
```

**Error 404 - No encontrado:**
```json
{
  "detail": "Panel panel99 no encontrado"
}
```

**Error 401 - Credenciales inválidas:**
```json
{
  "detail": "Credenciales inválidas"
}
```

---

## 🔐 Seguridad

1. **NUNCA** expongas estos endpoints públicamente sin HTTPS
2. **CAMBIA** las credenciales por defecto en producción
3. **CONSIDERA** usar un sistema de autenticación más robusto (JWT, OAuth) para producción
4. **BACKUPS**: Haz respaldos de `equipos.json` y `parametros.json` antes de modificarlos

---

## 📚 Documentación Interactiva

Una vez el servidor esté corriendo, visita:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

Ambas interfaces permiten probar los endpoints directamente desde el navegador.
