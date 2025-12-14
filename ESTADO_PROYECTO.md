# 📊 Estado del Proyecto - Sistema de Cotización Solar NASSA

**Última actualización:** 13 de diciembre de 2025  
**Estado:** En desarrollo activo - Funcional en producción  
**URL Producción:** https://web-production-3749b.up.railway.app

---

## 🎯 Resumen Ejecutivo

Sistema de cotización solar fotovoltaico con backend FastAPI y frontend vanilla HTML/JS. Incluye generación automática de presentaciones PowerPoint, conversión a PDF, envío por email y panel CRM para gestión de cotizaciones.

**Stack Tecnológico:**
- **Backend:** FastAPI + Python-PPTX + LibreOffice + PostgreSQL (Railway)
- **Frontend:** HTML/CSS/JS vanilla (sin framework)
- **Despliegue:** Railway (backend + DB) + GitHub Pages potencial para frontend
- **Email:** SMTP (Gmail)

---

## ✅ Funcionalidades Completadas

### 1. Sistema de Cotización (Frontend - `Index.html`)
- ✅ Formulario de captura de datos del cliente
- ✅ Selección de equipos (paneles, inversores, baterías) desde API
- ✅ Cálculo automático de paneles según consumo y HSP
- ✅ Generación de 2 opciones (Ideal y Ajustada a área disponible)
- ✅ Proyección financiera a 25 años:
  - Depreciación acelerada (3 años, 35% beneficio fiscal)
  - Deducción de renta (5 años, 50% base, 35% efectivo)
  - Degradación anual de paneles (1%)
  - Incremento costo energía (5.5%/año)
  - Cálculo de ROI y ahorro acumulado
- ✅ Modal de visualización de resultados completos
- ✅ Almacenamiento en localStorage para CRM interno

### 2. Generación de Documentos (Backend)
- ✅ Relleno automático de PowerPoint template
- ✅ Población de tabla de ahorros (12 años en PPTX)
- ✅ Conversión PPTX → PDF vía LibreOffice CLI
- ✅ Envío por email (PPTX + PDF) a cliente y NASSA
- ✅ Limpieza automática de archivos temporales

### 3. Panel CRM (`backend/static/crm.html`)
**Completado en esta sesión:**

#### 3.1 Sistema de Autenticación
- ✅ Login con usuario y contraseña (HTTP Basic Auth)
- ✅ Validación contra endpoint `/api/admin/dashboard`
- ✅ Dashboard oculto hasta login exitoso
- ✅ Logout funcional
- ✅ Credenciales dinámicas (no hardcodeadas en JS)
- ✅ Todas las llamadas API usan `getAuthHeader()`

**Implementación:**
```javascript
// Archivo: backend/static/crm.html
let authCredentials = null;

function login() {
    authCredentials = btoa(`${username}:${password}`);
    // Valida contra /api/admin/dashboard
}

function getAuthHeader() {
    return { 'Authorization': 'Basic ' + authCredentials };
}
```

#### 3.2 Funcionalidad de Impresión
- ✅ Botón Imprimir funcional
- ✅ Impresión en formato **landscape (horizontal)**
- ✅ Todo el contenido del modal visible (sin truncamiento)
- ✅ Tabla de ahorros completa en una página
- ✅ Preservación de colores y diseño
- ✅ Fuentes optimizadas (7pt tabla, 9pt body)
- ✅ Botones PDF y WhatsApp eliminados

**Estilos de impresión:**
```css
@media print {
    @page {
        size: letter landscape;
        margin: 0.5in 0.3in;
    }
    table th, table td {
        padding: 4px 3px !important;
        font-size: 7pt !important;
    }
}
```

#### 3.3 Visualización de Cotizaciones
- ✅ Modal muestra datos completos desde PostgreSQL
- ✅ Usa `datos_completos` del endpoint `/api/admin/cotizaciones/{id}`
- ✅ Tabs para Opción 1 y Opción 2 (si existe)
- ✅ Pestaña Opción 2 se oculta automáticamente si no hay datos
- ✅ Tabla de ahorros con validación de array

#### 3.4 Mejoras UI/UX
- ✅ Diseño con Tailwind CSS
- ✅ Dashboard con tabs: Dashboard, Buscar, Reportes
- ✅ Búsqueda con filtros (nombre, email, ciudad, estado)
- ✅ Paginación de resultados
- ✅ Indicadores estadísticos

### 4. Base de Datos PostgreSQL (Railway)
- ✅ Modelo `Cotizacion` con SQLAlchemy
- ✅ Campos JSON para `datos_completos`, `opcion1`, `opcion2`
- ✅ Almacenamiento de cliente, sistema, consumo, equipos
- ✅ Estados de cotización y metadata

### 5. API Endpoints
**Públicos:**
- `GET /health` - Health check
- `GET /api/equipos` - Equipos sin precios
- `GET /api/ciudades` - HSP por ciudad
- `POST /api/cotizar` - Generar cotización

**Admin (requieren autenticación):**
- `GET /api/admin/dashboard` - Estadísticas
- `GET /api/admin/cotizaciones/buscar` - Buscar con filtros
- `GET /api/admin/cotizaciones/{id}` - Detalle completo
- `GET /api/admin/reportes/top-ciudades` - Top ciudades
- `GET /api/admin/reportes/estadisticas` - Stats generales
- `GET /api/equipos/precios` - Equipos con precios (admin)
- `GET /crm` - Panel CRM

---

## 🚧 Tareas Pendientes (Por hacer al retomar)

### PRIORIDAD ALTA - Gestión de Usuarios

#### 1. Módulo de Gestión de Usuarios en `admin.html`
**Requerimiento del usuario:** "Debemos crear un módulo que nos permita crear usuarios con niveles de acceso. Este módulo debe crearse en el admin.html por seguridad"

**Tareas:**
- [ ] Crear tabla de usuarios en PostgreSQL
  ```python
  class User(Base):
      id: int
      username: str (unique)
      password_hash: str (bcrypt)
      email: str
      role: str (admin, crm_user, viewer)
      is_active: bool
      created_at: datetime
      last_login: datetime
  ```

- [ ] Endpoints de gestión de usuarios:
  - `POST /api/admin/users` - Crear usuario
  - `GET /api/admin/users` - Listar usuarios
  - `GET /api/admin/users/{id}` - Obtener usuario
  - `PUT /api/admin/users/{id}` - Actualizar usuario
  - `DELETE /api/admin/users/{id}` - Eliminar usuario
  - `PUT /api/admin/users/{id}/password` - Cambiar contraseña

- [ ] UI en `admin.html`:
  - Nueva pestaña "👥 Usuarios"
  - Tabla de usuarios con acciones (Editar, Eliminar)
  - Formulario de creación/edición
  - Selección de rol (dropdown)
  - Toggle de estado activo/inactivo

- [ ] Sistema de roles:
  - **Admin**: Acceso completo (crear usuarios, ver precios, etc.)
  - **CRM User**: Solo acceso a CRM (leer cotizaciones)
  - **Viewer**: Solo visualización (sin editar)

- [ ] Actualizar autenticación:
  - Migrar de credenciales hardcodeadas a base de datos
  - Middleware de autenticación por rol
  - Decorador `@require_role("admin")`
  - Hash de contraseñas con bcrypt
  - Sesiones con tokens (opcional: JWT)

**Archivos a crear/modificar:**
- `backend/models.py` - Agregar modelo `User`
- `backend/auth.py` - Sistema de autenticación mejorado
- `backend/server.py` - Endpoints de usuarios
- `backend/static/admin.html` - UI de gestión de usuarios

### PRIORIDAD MEDIA - Mejoras CRM

#### 2. Exportación de Datos
- [ ] Botón "Exportar a Excel" en CRM
- [ ] Endpoint `GET /api/admin/cotizaciones/export?format=xlsx`
- [ ] Generación de archivo Excel con `openpyxl`
- [ ] Filtros de exportación (fecha, ciudad, estado)

#### 3. Notas y Seguimiento
- [ ] Campo de notas por cotización
- [ ] Historial de cambios de estado
- [ ] Recordatorios/tareas pendientes
- [ ] Último contacto con cliente

#### 4. Dashboard Mejorado
- [ ] Gráficos con Chart.js o similar
- [ ] Tendencias por mes
- [ ] Tasa de conversión
- [ ] Valor promedio de cotización

### PRIORIDAD BAJA - Optimizaciones

#### 5. Performance
- [ ] Cache de equipos y ciudades (Redis opcional)
- [ ] Paginación en backend (limit/offset)
- [ ] Índices en PostgreSQL (ciudad, fecha_creacion, estado)
- [ ] Compresión de respuestas API (gzip)

#### 6. Testing
- [ ] Tests unitarios (pytest)
- [ ] Tests de endpoints (FastAPI TestClient)
- [ ] Tests de generación de PPTX
- [ ] CI/CD con GitHub Actions

#### 7. Documentación
- [ ] Swagger/OpenAPI completo
- [ ] README con instrucciones de instalación
- [ ] Documentación de API
- [ ] Guía de usuario para CRM

---

## 🐛 Bugs Conocidos

Ninguno reportado actualmente. Sistema estable en producción.

---

## 📋 Commits Importantes de Esta Sesión

### Autenticación CRM
```
ad6cc47 - 🔐 Implementar sistema de autenticación en CRM
- Login con validación de credenciales
- Dashboard oculto hasta login exitoso
- getAuthHeader() en todas las llamadas API
```

### Mejoras de Impresión
```
29036c2 - ✨ Mejorar funcionalidad de impresión y UI del modal CRM
- Eliminar botones PDF y WhatsApp
- Mejorar estilos de impresión

b424ad2 - 🐛 Corregir funcionalidad de impresión en CRM
- Usar ID correcto (modalResultado)
- Validaciones y logs de debugging

d0c746d - 🖨️ Mejorar significativamente impresión del modal CRM
- Estilos @media print mejorados
- Expansión completa de contenido

f2bca7d - 📄 Ajustar tabla de ahorros para impresión landscape
- Orientación horizontal
- Fuentes reducidas (7pt tabla)
- Tabla completa visible
```

---

## 🔧 Configuración del Entorno

### Variables de Entorno (`.env`)
```bash
# Admin (hardcodeado - MIGRAR A DB)
ADMIN_USER=admin
ADMIN_PASS=Lu1sF3rN@ss@

# Email SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_NASSA=nassasolar@example.com

# LibreOffice
LIBREOFFICE_PATH=soffice  # o ruta completa en macOS

# API
ALLOWED_ORIGINS=*
RATE_LIMIT=10

# Database (Railway automático)
DATABASE_URL=postgresql://...
```

### Instalación Local (macOS)
```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# LibreOffice (para PDF)
brew install --cask libreoffice

# Ejecutar
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend
```bash
# Desde raíz del proyecto
python3 -m http.server 8000
# Abrir http://localhost:8000
```

---

## 📁 Estructura de Archivos Clave

```
cotizador/
├── Index.html                 # Frontend principal de cotización
├── backend/
│   ├── server.py             # FastAPI server (5000+ líneas)
│   ├── requirements.txt      # Dependencias Python
│   ├── config/
│   │   ├── equipos.json      # Catálogo de equipos con PRECIOS
│   │   └── ciudades.json     # HSP por ciudad
│   ├── static/
│   │   ├── crm.html          # Panel CRM (1400+ líneas)
│   │   ├── admin.html        # Panel Admin (por mejorar)
│   │   └── images/
│   └── templates/
├── Template/
│   └── Template-PreCotizacion.pptx  # Template con TABLA_AHORROS
└── ESTADO_PROYECTO.md        # Este archivo
```

---

## 🔑 Credenciales de Acceso

### CRM / Admin
- **Usuario:** admin
- **Contraseña:** Lu1sF3rN@ss@
- **URL CRM:** https://web-production-3749b.up.railway.app/crm
- **URL Admin:** https://web-production-3749b.up.railway.app/admin

**⚠️ IMPORTANTE:** Migrar a sistema de usuarios en base de datos (tarea pendiente)

---

## 📊 Datos de Configuración

### Cálculos Financieros
- **Depreciación:** 3 años, 35% beneficio fiscal
- **Deducción renta:** 5 años, 50% base, 35% efectivo
- **Degradación anual:** 1% producción paneles
- **Primer año:** Solo 50% generación
- **Incremento energía:** 5.5%/año
- **IVA:** 19% (aplica a baterías, soportería, instalación, materiales)

### Costos Adicionales por Panel
- **Soportería:** 180,000 COP
- **Instalación:** 250,000 COP
- **Materiales:** 150,000 COP

### HSP por Ciudad (ejemplos)
- Santa Marta: 5.6
- Barranquilla: 5.2
- Cartagena: 5.3
- Bogotá: 4.5
- Default: 5.0

---

## 🚀 Próximos Pasos al Retomar

1. **Revisar este documento** para refrescar contexto
2. **Verificar producción:** https://web-production-3749b.up.railway.app/health
3. **Priorizar:** Comenzar con módulo de gestión de usuarios en admin.html
4. **Crear rama:** `git checkout -b feature/user-management`
5. **Modelo de datos:** Diseñar tabla `users` en PostgreSQL
6. **Endpoints:** Implementar CRUD de usuarios
7. **UI:** Nueva tab "Usuarios" en admin.html
8. **Testing:** Probar roles y permisos
9. **Migración:** Cambiar auth de hardcoded a DB

---

## 📝 Notas Técnicas Importantes

### PowerPoint Template
- **Nombre tabla:** `TABLA_AHORROS` (o busca por headers "año" + "ahorro")
- **Estructura:** 13 rows (1 header + 12 datos)
- **Placeholders:** `{{NOMBRE}}`, `{{CAPACIDAD_INSTALADA}}`, etc.
- **Columnas tabla:** año, valor_kwh, produccion, generacion, depreciacion, deduccion, costo, ahorro, acumulado, roi

### Impresión CRM
- **Orientación:** Landscape (horizontal)
- **Márgenes:** 0.5in vertical, 0.3in horizontal
- **Fuente tabla:** 7pt celdas, 7.5pt headers
- **ID modal:** `modalResultado` (NO modalDetalle)
- **ID contenido:** `contenidoResultado`

### PostgreSQL Railway
- **Endpoint datos completos:** `/api/admin/cotizaciones/{id}`
- **Estructura:** `data.cotizacion.datos_completos` contiene JSON frontend
- **Campos opción:** `opcion1`, `opcion2` (puede ser null)

---

## 🤝 Decisiones de Diseño

### ¿Por qué vanilla JS y no React?
- Simplicidad del proyecto
- No requiere build process
- Fácil deployment sin bundler
- Cliente puede modificar fácilmente

### ¿Por qué PostgreSQL y no MongoDB?
- Datos estructurados y relacionales
- Railway ofrece PostgreSQL integrado
- Transacciones y consistencia
- Mejor para reportes y agregaciones

### ¿Por qué PowerPoint y no PDF directo?
- Cliente necesita editar presentaciones
- Template visual más flexible
- LibreOffice hace conversión a PDF
- Envío de ambos formatos al cliente

---

## 📞 Soporte y Recursos

- **Repositorio:** github.com/jcsalazarb/cotizador
- **Producción:** https://web-production-3749b.up.railway.app
- **Railway Dashboard:** https://railway.app (requiere login)
- **Email configurado:** Gmail SMTP

---

## ✨ Logros de Esta Sesión

1. ✅ Sistema de autenticación completo en CRM
2. ✅ Impresión funcional con formato landscape
3. ✅ Tabla de ahorros visible completa en PDF
4. ✅ Eliminación de botones innecesarios (PDF, WhatsApp)
5. ✅ Pestaña Opción 2 condicional
6. ✅ Validaciones y logs de debugging
7. ✅ Despliegue exitoso a Railway

**Estado actual:** Sistema 100% funcional en producción, listo para mejoras de gestión de usuarios.

---

_Última modificación: 13 de diciembre de 2025_  
_Próxima sesión: Implementar gestión de usuarios y roles_
