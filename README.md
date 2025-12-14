# ☀️ NASSA Solar - Sistema de Cotización Fotovoltaica

**Estado:** ✅ Funcional en producción  
**URL:** https://web-production-3749b.up.railway.app  
**Última actualización:** 13 de diciembre de 2025

Sistema web de cotización automatizada para instalaciones de paneles solares fotovoltaicos en Colombia. Incluye generación de presentaciones PowerPoint, conversión a PDF, envío por email y panel CRM administrativo.

---

## 📚 Documentación

**Para retomar desarrollo, leer en este orden:**

1. **[QUICK_START.md](QUICK_START.md)** - ⚡ Inicio rápido (5 minutos)
2. **[ESTADO_PROYECTO.md](ESTADO_PROYECTO.md)** - 📊 Estado completo y contexto
3. **[TODO.md](TODO.md)** - ✅ Próxima tarea: Gestión de usuarios
4. **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - 🤖 Contexto para AI

---

## 🌟 Características

### Sistema de Cotización
- ✅ Cálculo automático basado en consumo, ubicación (HSP) y tipo de sistema
- ✅ 2 opciones: Ideal y Ajustada a área disponible
- ✅ Proyección financiera 25 años con ROI, depreciación y deducciones fiscales
- ✅ Soporte para sistemas: On-grid, Off-grid, Híbridos
- ✅ Selección de equipos (paneles, inversores, baterías)
- ✅ Generación automática de PowerPoint personalizado
- ✅ Conversión PPTX → PDF vía LibreOffice
- ✅ Envío por email (PDF + PPTX) al cliente y NASSA

### Panel CRM (NUEVO - Dic 2025)
- ✅ **Sistema de autenticación** con login y logout
- ✅ Visualización de cotizaciones desde PostgreSQL
- ✅ Búsqueda con filtros (nombre, email, ciudad, estado)
- ✅ Paginación de resultados
- ✅ **Impresión optimizada** en formato landscape
- ✅ Tabla de ahorros completa visible (7pt fuente)
- ✅ Estadísticas y reportes
- ✅ Pestaña Opción 2 condicional (solo si existe)

### Pendiente (Alta Prioridad)
- ⚠️ Módulo de gestión de usuarios en admin.html
- ⚠️ Sistema de roles (admin, crm_user, viewer)
- ⚠️ Migración de credenciales hardcoded a base de datos

---

## 🏗️ Arquitectura

### Stack Tecnológico
- **Backend**: FastAPI + Python-PPTX + LibreOffice
- **Base de Datos**: PostgreSQL 15 (Railway)
- **Frontend**: HTML/CSS/JS vanilla (Tailwind CSS)
- **Email**: SMTP (Gmail)
- **Hosting**: Railway (backend + DB)

### Estructura del Proyecto
```
cotizador/
├── ESTADO_PROYECTO.md         ⭐ Estado completo
├── TODO.md                     ⭐ Próxima tarea
├── QUICK_START.md              ⭐ Inicio rápido
├── Index.html                  Frontend cotización
├── backend/
│   ├── server.py              FastAPI (5000+ líneas)
│   ├── requirements.txt       
│   ├── config/
│   │   ├── equipos.json       Catálogo equipos (PRECIOS)
│   │   └── ciudades.json      HSP por ciudad
│   └── static/
│       ├── crm.html           Panel CRM (1400+ líneas)
│       └── admin.html         Panel Admin
├── Template/
│   └── Template-PreCotizacion.pptx
└── .github/
    └── copilot-instructions.md
```

---

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.9+
- PostgreSQL 15+ (local) o Railway (producción)
- LibreOffice (para conversión PDF)

### Instalación Local

1. **Clonar repositorio**
```bash
git clone https://github.com/jcsalazarb/cotizador.git
cd cotizador/backend
```

2. **Crear entorno virtual**
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
Crear archivo `.env` en `backend/`:
```bash
# PostgreSQL (Railway o local)
DATABASE_URL=postgresql://user:pass@host:5432/database

# Autenticación Admin
ADMIN_USER=admin
ADMIN_PASS=your_secure_password

# SMTP (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_NASSA=nassasolar@example.com

# LibreOffice
LIBREOFFICE_PATH=soffice  # o ruta completa

# Seguridad
ALLOWED_ORIGINS=*
RATE_LIMIT=10
```

5. **Instalar LibreOffice** (para PDF)
```bash
# macOS
brew install --cask libreoffice

# Ubuntu/Debian
sudo apt-get install libreoffice

# Windows: Descargar de libreoffice.org
```

6. **Ejecutar migraciones** (primera vez)
```bash
python migrate_to_postgres.py
```

7. **Iniciar servidor**
```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

8. **Abrir frontend**
```bash
# En otra terminal
cd ..
python3 -m http.server 8000
```

Acceder a:
- Frontend: http://localhost:8000
- Admin Panel: http://localhost:8000/backend/static/admin.html
- API Docs: http://localhost:8001/docs

## 📊 Base de Datos

### Modelos (SQLAlchemy)

#### Panel
```python
id: String (PK)              # "panel1"
nombre: String               # "Panel 550W Monocristalino"
capacidad: Float             # 550 (Watts)
precio: Float                # 220000 (COP)
area: Float                  # 2.79 (m²)
eficienciaPanel: Float       # 0.90
default: Boolean             # True/False
```

#### Inversor
```python
id: String (PK)              # "inv1"
nombre: String               # "Inversor 5kW MICRO"
capacidad: Float             # 5000 (Watts)
precio: Float                # 2200000 (COP)
eficiencia: Float            # 0.97
tipo: String                 # "MICRO" o "STRING"
paneles_por_inversor: Int    # 4 (solo MICRO)
sobredimensionamiento: Float # 0.40 (solo STRING)
sistemaElectrico: JSON       # ["bifasico", "trifasico"]
default: Boolean
```

#### Bateria
```python
id: String (PK)              # "bat1"
nombre: String               # "Batería Litio 10kWh"
capacidad: Float             # 10000 (Wh)
precio: Float                # 8500000 (COP)
default: Boolean
```

#### Ciudad
```python
key: String (PK)             # "santa_marta"
nombre: String               # "Santa Marta"
hsp: Float                   # 5.6 (Horas Solar Pico)
departamento: String         # "Magdalena"
```

#### Parametro
```python
id: Integer (PK, autoincrement)
seccion: String (unique)     # "costos_instalacion"
data: JSON                   # { campo1: valor1, ... }
```

Secciones de parámetros:
- `costos_instalacion`: Soportería, instalación, materiales, mantenimiento
- `parametros_fiscales`: IVA, depreciación, deducción de renta
- `parametros_proyeccion`: Años, degradación panel, incremento kWh/año
- `parametros_sistema`: Factor área, eficiencias, umbrales
- `tabla_legalizacion`: 6 rangos de capacidad con costos
- `inversores_defaults`: Configuración por defecto MICRO/STRING

## 🔌 API Endpoints

### Públicos
- `GET /health` - Health check
- `GET /api/equipos` - Listado de equipos (sin precios)
- `GET /api/ciudades` - Ciudades con HSP
- `GET /api/valores-default` - Valores por defecto del formulario
- `POST /api/cotizar` - Generar cotización
- `POST /api/enviar-cotizacion` - Generar PDF y enviar email

### Admin (requiere autenticación)
- `GET /api/equipos/precios` - Equipos con precios
- `GET/PUT /api/admin/parametros` - Configuración
- `GET/POST/PUT/DELETE /api/admin/paneles` - CRUD paneles
- `GET/POST/PUT/DELETE /api/admin/inversores` - CRUD inversores
- `GET/POST/PUT/DELETE /api/admin/baterias` - CRUD baterías
- `GET/POST/PUT/DELETE /api/admin/ciudades` - CRUD ciudades
- `PUT /api/admin/{equipo}/{id}/default` - Marcar como default

### Debug
- `GET /api/diagnostico-postgres` - Verificar estado PostgreSQL

## 🧮 Lógica de Cotización

### Tipos de Sistema
1. **On-Grid**: Sin baterías, conectado a red
2. **Off-Grid**: Con baterías, autónomo
3. **Híbrido Incluido**: Baterías incluidas en cotización
4. **Híbrido Opcional**: Baterías opcionales

### Cálculo de Paneles

#### Inversores MICRO
```python
numeroInversores = ceil(numeroPaneles_inicial / paneles_por_inversor)
numeroPaneles = numeroInversores * paneles_por_inversor  # Redondeo
```

#### Inversores STRING
```python
capacidad_efectiva = capacidad_inversor * (1 + sobredimensionamiento)
numeroInversores = ceil(capacidadInstalada / capacidad_efectiva)
```

### Proyección Financiera (25 años)

**Ahorros anuales**:
- **Generación**: `producción_anual * valorKwh * (1 + incremento)^año * (1 - degradación)^año`
- **Depreciación fiscal**: `(subtotal / 3 años) * 35%` (solo primeros 3 años)
- **Deducción de renta**: `(subtotal * 50% * 35%) / 5 años` (solo primeros 5 años)
- **Mantenimiento**: `-capacidadInstalada * costoMant * (1 + incremento)^año`

**Tiempo de retorno**: Año donde `ahorroAcumulado >= valorTotalSistema`

### Legalización

Costos según capacidad instalada (6 rangos):
- 0-5 kW: $2,500,000
- 5-10 kW: $3,500,000
- 10-30 kW: $4,500,000
- 30-100 kW: $6,000,000
- 100-500 kW: $8,000,000
- +500 kW: $10,000,000

## 📧 Generación de PDF

1. **Llenar template PPTX** con python-pptx
2. **Convertir a PDF** con LibreOffice CLI
3. **Enviar por email** con SMTP
4. **Cleanup** de archivos temporales

Placeholders en template:
- `{{NOMBRE}}`, `{{EMAIL}}`, `{{TELEFONO}}`
- `{{CAPACIDAD_INSTALADA}}`, `{{NUMERO_PANELES}}`
- `{{VALOR_TOTAL_SISTEMA}}`, `{{AHORRO_MENSUAL}}`
- Tabla `TABLA_AHORROS` con 12 filas (años 1-12)

## 🔐 Seguridad

- **Rate limiting**: 10 req/min por IP
- **HTTP Basic Auth**: Endpoints admin
- **CORS**: Configurab le via `ALLOWED_ORIGINS`
- **Input validation**: Pydantic models
- **SQL injection**: Protegido por SQLAlchemy ORM

## 🚢 Deployment

### Railway (Producción)
1. Conectar repositorio GitHub
2. Configurar variables de entorno
3. Push a `main` → auto-deploy (~90 seg)

### Variables de Entorno Railway
```bash
DATABASE_URL=postgresql://...  # Provisto por Railway
ADMIN_USER=admin
ADMIN_PASS=<contraseña_segura>
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<tu_email>
SMTP_PASS=<app_password_gmail>
EMAIL_FROM=<tu_email>
EMAIL_NASSA=nassasolar@example.com
LIBREOFFICE_PATH=soffice
ALLOWED_ORIGINS=*
RATE_LIMIT=10
```

## 📈 Datos del Sistema

- **160 ciudades** colombianas con HSP
- **7 paneles** (450W-550W)
- **9 inversores** (3kW-5kW, MICRO/STRING)
- **7 baterías** (5kWh-10kWh)
- **6 secciones** de parámetros configurables

## 🐛 Troubleshooting

### Error: LibreOffice not found
```bash
# macOS
brew install --cask libreoffice
export LIBREOFFICE_PATH=/Applications/LibreOffice.app/Contents/MacOS/soffice

# Linux
sudo apt-get install libreoffice
```

### Error: PostgreSQL connection failed
```bash
# Verificar DATABASE_URL en .env
# Verificar que PostgreSQL esté corriendo
psql $DATABASE_URL -c "SELECT 1;"
```

### Error: Email no enviado
- Verificar app password de Gmail (no contraseña normal)
- Habilitar "Acceso de apps menos seguras" si es necesario
- Revisar logs del servidor para detalles

### Verificar migración PostgreSQL
```bash
curl https://web-production-3749b.up.railway.app/api/diagnostico-postgres
```

## 📝 Changelog

### v2.0.0 (8 dic 2025) - Migración PostgreSQL ✅
- Migración completa de JSON a PostgreSQL
- 27 endpoints funcionando con BD
- Sistema de cotización en tiempo real
- Panel admin con CRUD completo
- Documentación actualizada

### v1.5.0 - Features MICRO/STRING
- Lógica diferenciada para inversores
- Tabla de legalización por rangos
- Consecutivo thread-safe
- Campo % ahorro energía

### v1.0.0 - Release inicial
- Sistema de cotización básico
- Generación de PDF
- Envío por email

## 👥 Contribuir

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Propietario: NASSA Solar  
Uso interno exclusivo

## 📞 Contacto

NASSA Solar  
Email: nassasolar@example.com  
Tel: (057) 313 690 9723  
Web: www.nassasolar.com

---

**Última actualización**: 8 de diciembre de 2025  
**Versión**: 2.0.0 (PostgreSQL)
