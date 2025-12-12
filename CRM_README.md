# 📊 Sistema CRM - NASSA Solar

Panel de gestión de cotizaciones fotovoltaicas con dashboard, búsqueda, reportes y exportación.

## 🚀 Acceso

- **Panel CRM**: https://web-production-3749b.up.railway.app/crm
- **Credenciales**: `admin` / `Lu1sF3rN@ss@`

## ✨ Funcionalidades

### 📊 Dashboard

**Métricas en Tiempo Real:**
- Total de cotizaciones (históricas, mes actual, año actual)
- Emails enviados y tasa de conversión
- Promedios del sistema (paneles, capacidad, valor, ROI, ahorro mensual)
- Top 5 ciudades con más cotizaciones
- Equipos más populares (paneles e inversores)
- Últimas 10 cotizaciones con estado

**Endpoint:** `GET /api/admin/dashboard`

```bash
curl -u admin:PASSWORD https://tu-dominio.com/api/admin/dashboard
```

**Respuesta:**
```json
{
  "status": "success",
  "timestamp": "2025-12-12T...",
  "resumen": {
    "total_cotizaciones": 150,
    "cotizaciones_mes": 23,
    "cotizaciones_anio": 150,
    "emails_enviados": 120,
    "tasa_conversion": 80.0
  },
  "promedios": {
    "paneles": 15.5,
    "capacidad_kw": 9.5,
    "valor_total": 55000000,
    "tiempo_retorno_anos": 3.2,
    "ahorro_mensual": 850000
  },
  "top_ciudades": [...],
  "equipos_populares": {...},
  "cotizaciones_recientes": [...]
}
```

### 🔍 Búsqueda de Cotizaciones

**Filtros Disponibles:**
- Nombre del cliente (búsqueda parcial)
- Email (búsqueda parcial)
- Teléfono (búsqueda parcial)
- Ciudad (búsqueda exacta)
- Rango de fechas (desde/hasta)
- Estado de email (enviado/no enviado)
- Paginación (50 por página, max 200)

**Endpoint:** `GET /api/admin/cotizaciones/buscar`

**Parámetros:**
- `nombre`: string (opcional)
- `email`: string (opcional)
- `telefono`: string (opcional)
- `ciudad`: string (opcional)
- `fecha_desde`: YYYY-MM-DD (opcional)
- `fecha_hasta`: YYYY-MM-DD (opcional)
- `email_enviado`: true/false (opcional)
- `pagina`: int (default: 1)
- `por_pagina`: int (default: 50, max: 200)

**Ejemplos:**

```bash
# Buscar por nombre
curl -u admin:PASSWORD "https://tu-dominio.com/api/admin/cotizaciones/buscar?nombre=Juan"

# Buscar por ciudad y estado
curl -u admin:PASSWORD "https://tu-dominio.com/api/admin/cotizaciones/buscar?ciudad=Barranquilla&email_enviado=true"

# Buscar por rango de fechas
curl -u admin:PASSWORD "https://tu-dominio.com/api/admin/cotizaciones/buscar?fecha_desde=2025-01-01&fecha_hasta=2025-12-31"
```

**Respuesta:**
```json
{
  "status": "success",
  "resultados": [
    {
      "id": "NASSA-2025-0001",
      "fecha_creacion": "2025-12-12T...",
      "nombre": "Juan Pérez",
      "email": "juan@example.com",
      "telefono": "+57 3001234567",
      "ciudad": "Barranquilla",
      "tipo_sistema_fv": "ongrid",
      "consumo_mensual": 500,
      "num_paneles": 10,
      "capacidad_instalada": "6.15 kW",
      "valor_total": 35000000,
      "tiempo_retorno": 3.5,
      "email_enviado": true,
      "fecha_envio_email": "2025-12-12T...",
      "tiene_opcion2": false,
      "num_opciones": 1
    }
  ],
  "paginacion": {
    "pagina_actual": 1,
    "por_pagina": 50,
    "total_resultados": 150,
    "total_paginas": 3
  },
  "filtros_aplicados": {...}
}
```

### 👁️ Detalle de Cotización

**Endpoint:** `GET /api/admin/cotizaciones/{cotizacion_id}`

```bash
curl -u admin:PASSWORD https://tu-dominio.com/api/admin/cotizaciones/NASSA-2025-0001
```

**Respuesta:**
```json
{
  "status": "success",
  "cotizacion": {
    "id": "NASSA-2025-0001",
    "fecha_creacion": "2025-12-12T...",
    "cliente": {
      "nombre": "Juan Pérez",
      "email": "juan@example.com",
      "telefono": "+57 3001234567",
      "direccion": "Calle 123 #45-67",
      "ciudad": "Barranquilla",
      "nic": "123456789"
    },
    "sistema": {
      "tipo_vivienda": "casa",
      "sistema_electrico": "monofasico",
      "tipo_sistema_fv": "ongrid"
    },
    "consumo": {
      "consumo_mensual": 500,
      "valor_factura": 550000,
      "valor_kwh": 1100,
      "porcentaje_consumo_dia": 60,
      "hsp_calculado": 5.2,
      "area_disponible": 50
    },
    "equipos": {
      "panel": {"id": "panel1", "nombre": "Panel 615W Monocristalino"},
      "inversor": {"id": "inv1", "nombre": "Inversor 5kW"}
    },
    "opcion1": {
      "num_paneles": 10,
      "capacidad_instalada": 6.15,
      "area_requerida": 25.5,
      "valor_total": 35000000,
      "ahorro_mensual": 850000,
      "tiempo_retorno": 3.5
    },
    "opcion2": null,
    "estado": {
      "email_enviado": true,
      "fecha_envio_email": "2025-12-12T...",
      "num_opciones": 1
    },
    "metadata": {...},
    "datos_completos": {...}
  }
}
```

### 📈 Reportes

#### Top Ciudades

**Endpoint:** `GET /api/admin/reportes/top-ciudades`

**Parámetros:**
- `limit`: int (default: 10, max: 50)

```bash
curl -u admin:PASSWORD "https://tu-dominio.com/api/admin/reportes/top-ciudades?limit=10"
```

**Respuesta:**
```json
{
  "status": "success",
  "reporte": "Top Ciudades",
  "timestamp": "2025-12-12T...",
  "resultados": [
    {
      "ciudad": "Barranquilla",
      "total_cotizaciones": 45,
      "valor_total_acumulado": 1850000000,
      "capacidad_promedio_kw": 8.5,
      "total_paneles": 650
    },
    {
      "ciudad": "Santa Marta",
      "total_cotizaciones": 38,
      "valor_total_acumulado": 1650000000,
      "capacidad_promedio_kw": 9.2,
      "total_paneles": 580
    }
  ]
}
```

#### Estadísticas Generales

**Endpoint:** `GET /api/admin/reportes/estadisticas`

```bash
curl -u admin:PASSWORD https://tu-dominio.com/api/admin/reportes/estadisticas
```

**Respuesta:**
```json
{
  "status": "success",
  "timestamp": "2025-12-12T...",
  "estadisticas_generales": {
    "total_cotizaciones": 150,
    "promedio_paneles": 15.5,
    "promedio_capacidad_kw": 9.5,
    "promedio_valor": 55000000,
    "promedio_tiempo_retorno_anos": 3.2,
    "valor_total_mercado": 8250000000,
    "valor_min": 10000000,
    "valor_max": 150000000
  },
  "adopcion_opcion2": {
    "cotizaciones_con_opcion2": 45,
    "porcentaje": 30.0
  },
  "por_tipo_sistema": [
    {"tipo": "ongrid", "cantidad": 120},
    {"tipo": "hibrido_incluido", "cantidad": 20},
    {"tipo": "offgrid", "cantidad": 10}
  ],
  "por_tipo_vivienda": [
    {"tipo": "casa", "cantidad": 100},
    {"tipo": "apartamento", "cantidad": 30},
    {"tipo": "empresa", "cantidad": 20}
  ]
}
```

### 💾 Exportación de Datos

**Endpoint:** `GET /api/admin/reportes/export`

**Parámetros:**
- `fecha_desde`: YYYY-MM-DD (opcional)
- `fecha_hasta`: YYYY-MM-DD (opcional)
- `formato`: "csv" o "json" (default: csv)

**Ejemplos:**

```bash
# Exportar todo en CSV
curl -u admin:PASSWORD "https://tu-dominio.com/api/admin/reportes/export?formato=csv" -o cotizaciones.csv

# Exportar rango de fechas en JSON
curl -u admin:PASSWORD "https://tu-dominio.com/api/admin/reportes/export?formato=json&fecha_desde=2025-01-01&fecha_hasta=2025-12-31" -o cotizaciones.json

# Exportar mes actual
curl -u admin:PASSWORD "https://tu-dominio.com/api/admin/reportes/export?formato=csv&fecha_desde=2025-12-01" -o diciembre.csv
```

**Formato CSV:**
```csv
ID,Fecha,Nombre,Email,Teléfono,Ciudad,Consumo (kWh/mes),Num Paneles,Capacidad (kW),Valor Total,Ahorro Mensual,Tiempo Retorno (años),Email Enviado,Tiene Opción 2
NASSA-2025-0001,2025-12-12 10:30,Juan Pérez,juan@example.com,+57 3001234567,Barranquilla,500,10,6.15,35000000,850000,3.5,Sí,No
```

**Formato JSON:**
```json
{
  "status": "success",
  "total": 150,
  "datos": [
    {
      "id": "NASSA-2025-0001",
      "fecha_creacion": "2025-12-12T10:30:00",
      "nombre": "Juan Pérez",
      "email": "juan@example.com",
      "telefono": "+57 3001234567",
      "ciudad": "Barranquilla",
      "consumo_mensual": 500,
      "num_paneles": 10,
      "capacidad_instalada": 6.15,
      "valor_total": 35000000,
      "ahorro_mensual": 850000,
      "tiempo_retorno": 3.5,
      "email_enviado": true,
      "tiene_opcion2": false
    }
  ]
}
```

## 🔐 Autenticación

Todos los endpoints CRM requieren **HTTP Basic Authentication**:

```bash
# Con curl
curl -u admin:PASSWORD https://tu-dominio.com/api/admin/dashboard

# Con header explícito
curl -H "Authorization: Basic YWRtaW46TGExc0YzckZAc3NAQGw=" https://tu-dominio.com/api/admin/dashboard

# Desde JavaScript (frontend)
const authHeader = 'Basic ' + btoa('admin:PASSWORD');
fetch('/api/admin/dashboard', {
    headers: {
        'Authorization': authHeader
    }
});
```

## 📊 Panel Web (crm.html)

Interfaz visual completa con:

### Features de la UI:
- ✅ Dashboard con tarjetas interactivas (hover effect)
- ✅ Gráficos de estadísticas en tiempo real
- ✅ Búsqueda avanzada con múltiples filtros
- ✅ Paginación de resultados
- ✅ Modal de detalle con información completa
- ✅ Botones de exportación (CSV/JSON)
- ✅ Diseño responsive (móvil, tablet, desktop)
- ✅ Tailwind CSS para estilos modernos
- ✅ Estados visuales (enviado ✓, pendiente ⏳)

### Tabs del Panel:
1. **📊 Dashboard** - Métricas y cotizaciones recientes
2. **🔍 Buscar** - Filtros avanzados y resultados paginados
3. **📈 Reportes** - Top ciudades, estadísticas, exportación

### Acceso Directo:
```
https://web-production-3749b.up.railway.app/crm
```

## 🎯 Casos de Uso

### 1. Seguimiento de Ventas
```bash
# Ver cotizaciones pendientes de email
curl -u admin:PASSWORD "https://tu-dominio.com/api/admin/cotizaciones/buscar?email_enviado=false"

# Ver cotizaciones de este mes
curl -u admin:PASSWORD "https://tu-dominio.com/api/admin/cotizaciones/buscar?fecha_desde=2025-12-01"
```

### 2. Análisis de Mercado
```bash
# Top ciudades con más demanda
curl -u admin:PASSWORD "https://tu-dominio.com/api/admin/reportes/top-ciudades?limit=20"

# Estadísticas completas
curl -u admin:PASSWORD "https://tu-dominio.com/api/admin/reportes/estadisticas"
```

### 3. Exportación para Excel
```bash
# Descargar todas las cotizaciones
curl -u admin:PASSWORD "https://tu-dominio.com/api/admin/reportes/export?formato=csv" -o cotizaciones_completas.csv

# Abrir con Excel y analizar
```

### 4. Búsqueda de Cliente
```bash
# Por nombre
curl -u admin:PASSWORD "https://tu-dominio.com/api/admin/cotizaciones/buscar?nombre=Juan"

# Por email
curl -u admin:PASSWORD "https://tu-dominio.com/api/admin/cotizaciones/buscar?email=juan@example.com"

# Obtener detalle completo
curl -u admin:PASSWORD "https://tu-dominio.com/api/admin/cotizaciones/NASSA-2025-0001"
```

## 🔧 Configuración

El CRM utiliza la misma configuración del backend:

```env
# Autenticación Admin
ADMIN_USER=admin
ADMIN_PASS=Lu1sF3rN@ss@

# PostgreSQL (Railway)
DATABASE_URL=postgresql://...
```

## 📝 Notas Técnicas

### Base de Datos
- Tabla: `cotizaciones` (40+ campos)
- Índices recomendados:
  ```sql
  CREATE INDEX idx_cotizaciones_email ON cotizaciones(email);
  CREATE INDEX idx_cotizaciones_ciudad ON cotizaciones(ciudad);
  CREATE INDEX idx_cotizaciones_fecha ON cotizaciones(fecha_creacion);
  CREATE INDEX idx_cotizaciones_email_enviado ON cotizaciones(email_enviado);
  ```

### Performance
- Búsquedas paginadas (max 200 por página)
- Queries optimizadas con SQLAlchemy
- Caching de resultados (opcional, agregar Redis)

### Seguridad
- Basic Auth en todos los endpoints admin
- CORS configurado para dominios permitidos
- Rate limiting (10 req/min por IP)
- Credenciales en variables de entorno

## 🚀 Roadmap Futuro

Ideas para mejorar el CRM:

1. **Gráficos Visuales**
   - Chart.js o Recharts para líneas de tendencia
   - Gráfico de barras por ciudad
   - Gráfico circular por tipo de sistema

2. **Notificaciones**
   - Alertas de nuevas cotizaciones (WebSocket)
   - Email diario con resumen
   - Notificaciones push

3. **Análisis Avanzado**
   - Predicción de ventas (ML)
   - Análisis de cohortes
   - Segmentación de clientes

4. **Integración CRM Externo**
   - Sincronización con Salesforce
   - Integración con HubSpot
   - Webhooks para eventos

5. **Más Reportes**
   - Reporte de ROI promedio por ciudad
   - Análisis de equipos más rentables
   - Tasa de adopción de Opción 2 por región

## 🐛 Troubleshooting

### Error 401 Unauthorized
```bash
# Verificar credenciales
echo -n "admin:Lu1sF3rN@ss@" | base64
# Debe retornar: YWRtaW46THUxc0YzckZAc3NAQGw=
```

### Error 500 Database
```bash
# Verificar conexión PostgreSQL
curl -u admin:PASSWORD https://tu-dominio.com/api/admin/verificar-postgres
```

### No hay datos en dashboard
```bash
# Verificar que existan cotizaciones
curl -u admin:PASSWORD "https://tu-dominio.com/api/admin/cotizaciones/buscar"
```

## 📞 Soporte

Para consultas sobre el CRM:
- Email: nassasolar@example.com
- GitHub: https://github.com/jcsalazarb/cotizador

---

**Última actualización**: 12 de diciembre de 2025
**Versión**: 1.0.0
**Autor**: NASSA Solar Development Team
