# DOCUMENTACIÓN FUNCIONAL - Sistema de Cotización Solar NASSA

**Fecha:** 25 de noviembre de 2025  
**Versión:** 1.0  
**Empresa:** NASSA Solar

---

## 1. DESCRIPCIÓN GENERAL

Sistema web para generar cotizaciones de instalaciones solares fotovoltaicas. Calcula dimensionamiento, costos, ROI y genera presentaciones en PowerPoint/PDF que se envían por email.

**Stack Tecnológico:**
- Backend: Python 3.9 + FastAPI
- Frontend: HTML5 + Vanilla JavaScript + TailwindCSS
- Base de Datos: JSON (equipos.json, ciudades.json, parametros.json)
- Generación Documentos: python-pptx + LibreOffice
- Email: SMTP (Gmail)

---

## 2. BACKEND (`backend/server.py`)

### 2.1 Arquitectura
- **Framework:** FastAPI (puerto 8001)
- **Servidor:** Uvicorn con hot-reload
- **Líneas de código:** ~1161 líneas

### 2.2 Endpoints Principales

#### **Endpoints Públicos:**
```
GET  /health                    - Estado del servidor
GET  /api/equipos               - Catálogo (sin precios)
GET  /api/equipos?sistemaElectrico=X - Inversores filtrados
GET  /api/ciudades              - HSP por ciudad
POST /api/cotizar               - Generar cotización
```

#### **Endpoints Admin (HTTP Basic Auth):**
```
GET    /api/equipos/precios           - Catálogo completo con precios
GET    /api/admin/paneles             - Listar paneles
POST   /api/admin/paneles             - Crear panel (ID auto-generado)
PUT    /api/admin/paneles/{id}        - Actualizar panel
DELETE /api/admin/paneles/{id}        - Eliminar panel
GET    /api/admin/inversores          - Listar inversores
POST   /api/admin/inversores          - Crear inversor
PUT    /api/admin/inversores/{id}     - Actualizar inversor
DELETE /api/admin/inversores/{id}     - Eliminar inversor
GET    /api/admin/baterias            - Listar baterías
POST   /api/admin/baterias            - Crear batería
PUT    /api/admin/baterias/{id}       - Actualizar batería
DELETE /api/admin/baterias/{id}       - Eliminar batería
GET    /api/admin/parametros          - Obtener parámetros sistema
PUT    /api/admin/parametros          - Actualizar parámetros
GET    /api/template/download         - Descargar template PPTX
```

### 2.3 Cálculos Core

**Dimensionamiento:**
```python
# Número de paneles
paneles_necesarios = ceil((consumo_mensual * 30) / (hsp * capacidad_panel * 0.9))

# Proyección 25 años
- Año 1: 50% de generación (factor_primer_ano)
- Degradación: 2% anual
- Incremento kWh: 3.5% anual
- Depreciación: 3 años (35% impuesto renta)
- Deducción renta: 5 años (50% base, 35% efectivo)
```

**Costos Totales:**
```python
subtotal = (paneles * precio_panel) + (inversores * precio_inv) + (baterias * precio_bat)
soporteria = paneles * 180000
instalacion = paneles * 250000
materiales = paneles * 190000
iva = (soporteria + instalacion + materiales + baterias) * 0.19
total = subtotal + soporteria + instalacion + materiales + iva
```

### 2.4 Flujo de Cotización

1. Validar datos con Pydantic
2. Calcular dimensionamiento (HSP, paneles, inversores)
3. Proyección financiera 25 años
4. Llenar template PowerPoint (`Template-PreCotizacion.pptx`)
5. Convertir PPTX → PDF con LibreOffice CLI
6. Enviar email con PDF + PPTX adjuntos
7. Eliminar archivos temporales
8. Retornar resumen JSON (10 años)

### 2.5 Seguridad Backend

- **HTTP Basic Auth** para endpoints admin
- **Rate Limiting:** 10 req/min por IP (configurable)
- **CORS:** Dominios permitidos en `ALLOWED_ORIGINS`
- **Validación Pydantic:** Tipos, rangos, patrones regex
- **Secrets:** Variables de entorno en `.env`

---

## 3. FRONTEND (`index_Original_modificado.html`)

### 3.1 Características
- **Tecnología:** HTML5 + JavaScript vanilla (sin frameworks)
- **CSS:** TailwindCSS vía CDN
- **Tamaño:** ~872 líneas
- **Puerto:** 8000 (Python HTTP server)

### 3.2 Funcionalidades

**Formulario de Cotización:**
- Datos cliente (nombre, teléfono, email, dirección)
- Parámetros técnicos (consumo, ciudad, NIC, tipo vivienda)
- Selección sistema eléctrico (monofásico/bifásico/trifásico)
- Filtrado dinámico de inversores según sistema
- Selección equipos (panel, inversor, batería opcional)

**Validaciones Frontend:**
```javascript
- Email formato válido
- Teléfono 7-20 dígitos
- Consumo > 50 kWh
- Porcentaje consumo día 0-100%
- Sistema FV requerido (ongrid/offgrid/híbrido)
- Inversores ocultos hasta seleccionar sistema eléctrico
```

**Modal CRM:**
- Almacena última cotización en `localStorage`
- Facilita seguimiento telefónico
- Persiste entre sesiones

### 3.3 Comunicación Backend

```javascript
const API_BASE_URL = 'http://localhost:8001/api';

// Carga inicial: sin inversores
await cargarEquipos(null);

// Al seleccionar sistema eléctrico
await cargarEquipos(sistemaElectrico); // Filtra inversores

// Envío cotización
fetch(`${API_BASE_URL}/cotizar`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(datos)
});
```

---

## 4. PANEL DE ADMINISTRACIÓN (`admin.html`)

### 4.1 Acceso
- URL: `http://localhost:8000/admin.html`
- Autenticación: HTTP Basic Auth
- Usuario/Contraseña: Definidos en `.env`

### 4.2 Funcionalidades

**Gestión de Equipos:**
- CRUD completo paneles (7 registros)
- CRUD completo inversores (8 registros)
- CRUD completo baterías (7 registros)
- IDs auto-generados (panel1, inv1, bat1...)
- Validación tipo_sistema inversores

**Gestión de Parámetros:**
- Costos instalación (soportería, instalación, materiales)
- Parámetros fiscales (IVA, renta, depreciación)
- Parámetros proyección (degradación, años)

**UI/UX:**
- Sistema de tabs (Paneles | Inversores | Baterías | Parámetros)
- Modales para crear/editar
- Notificaciones flotantes (success/error)
- Confirmación antes de eliminar
- Recarga automática de listas

### 4.3 Seguridad Admin

- IDs no editables (generados por backend)
- Validación campos requeridos
- Confirmación eliminaciones
- Precios privados (no expuestos en API pública)
- Logout manual

---

## 5. BASES DE DATOS (JSON)

### 5.1 `equipos.json`
```json
{
  "paneles": [
    {
      "id": "panel1",
      "nombre": "Panel Canadian Solar 550W",
      "capacidad": 550,
      "precio": 850000,
      "descripcion": "...",
      "eficienciaPanel": 0.9
    }
  ],
  "inversores": [
    {
      "id": "inv1",
      "nombre": "Inversor Growatt 3kW",
      "capacidad": 3000,
      "precio": 2200000,
      "eficiencia": 0.9,
      "tipo_sistema": "monofasico"
    }
  ],
  "baterias": [...]
}
```

**Tipos Sistema:**
- `monofasico` (5 inversores)
- `bifasico` (1 inversor)
- `trifasico` (2 inversores)

### 5.2 `ciudades.json`
```json
{
  "santa_marta": 5.6,
  "barranquilla": 5.2,
  "bogota": 4.2,
  ...
}
```
- 163 ciudades colombianas
- Valor: HSP (Horas Solar Pico)

### 5.3 `parametros.json`
```json
{
  "costos_instalacion": {
    "soporteria_por_panel": 180000,
    "instalacion_por_panel": 250000,
    "materiales_por_panel": 190000,
    "mantenimiento_anual_por_kw": 160000
  },
  "parametros_fiscales": {
    "iva_porcentaje": 0.19,
    "impuesto_renta_porcentaje": 0.35,
    "deduccion_renta_base_porcentaje": 0.5,
    "anos_deduccion": 5,
    "anos_depreciacion": 3
  },
  "parametros_proyeccion": {
    "degradacion_anual_panel": 0.02,
    "factor_primer_ano": 0.4,
    "incremento_anual_kwh": 0.035,
    "anos_proyeccion": 30
  }
}
```

---

## 6. TEMPLATE POWERPOINT

### 6.1 Archivo
- **Ubicación:** `Template/Template-PreCotizacion.pptx`
- **Slides:** 6-8 diapositivas
- **Formato:** PowerPoint 2016+ (.pptx)

### 6.2 Placeholders
```
{{NOMBRE}}                  - Nombre cliente
{{TELEFONO}}                - Teléfono
{{EMAIL}}                   - Email
{{CIUDAD}}                  - Ciudad
{{DIRECCION}}               - Dirección
{{CONSUMO_MENSUAL}}         - Consumo kWh/mes
{{VALOR_FACTURA}}           - Valor factura COP
{{CAPACIDAD_INSTALADA}}     - kWp total
{{PANELES_CANTIDAD}}        - Número paneles
{{PANELES_MODELO}}          - Modelo panel
{{INVERSORES_MODELO}}       - Modelo inversor
{{BATERIAS_MODELO}}         - Modelo batería (opcional)
{{TIPO_FV}}                 - On-Grid/Off-Grid/Híbrido
{{SUBTOT}}                  - Subtotal COP
{{SOPORTERIA}}              - Costo soportería
{{INSTALACION}}             - Costo instalación
{{MATERIALES}}              - Costo materiales
{{IVA}}                     - IVA COP
{{TOTAL}}                   - Total COP
{{AHORRO_MES_1}}            - Ahorro mensual año 1
{{AHORRO_ANUAL_1}}          - Ahorro anual año 1
{{ROI_SIMPLE}}              - ROI simple años
{{PAYBACK}}                 - Payback años
```

### 6.3 Tabla TABLA_AHORROS
- Nombre tabla: `TABLA_AHORROS`
- Filas: 15 (1 header + 14 datos)
- Detección automática de filas
- Columnas: Año, Valor kWh, Producción, Generación, Depreciación, Deducción, Costo sin solar, Ahorro, Acumulado, ROI

---

## 7. GENERACIÓN PDF

### 7.1 Proceso
1. Backend llena template PPTX con datos
2. Guarda PPTX temporal en `/tmp/`
3. Ejecuta LibreOffice CLI:
   ```bash
   soffice --headless --convert-to pdf --outdir /tmp/ archivo.pptx
   ```
4. Genera PDF en mismo directorio
5. Adjunta ambos archivos a email

### 7.2 Requisitos
- **LibreOffice** instalado en sistema
- macOS: `/Applications/LibreOffice.app/Contents/MacOS/soffice`
- Linux: `/usr/bin/soffice` o `/usr/bin/libreoffice`
- Windows: `C:\Program Files\LibreOffice\program\soffice.exe`

### 7.3 Timeout
- Conversión: 90 segundos máximo
- Si falla: Envía solo PPTX

---

## 8. SISTEMA DE EMAIL

### 8.1 Configuración SMTP
```python
SMTP_HOST = smtp.gmail.com
SMTP_PORT = 587 (STARTTLS)
SMTP_USER = nassasolarprecotizaciones@gmail.com
SMTP_PASS = [Contraseña de aplicación Gmail]
```

### 8.2 Flujo Email
1. Crear mensaje con asunto personalizado
2. Cuerpo HTML con datos cliente
3. Adjuntar PDF y PPTX
4. Enviar a cliente (TO)
5. CC a NASSA (jcsalazarb@icloud.com)
6. Log resultado (éxito/error)

### 8.3 Plantilla Email
```html
Asunto: PreCotización Nassa Solar - {NOMBRE}

Estimado {NOMBRE},

Adjuntamos su precotización solar con:
- Capacidad: {CAPACIDAD_INSTALADA} kWp
- Inversión: ${TOTAL:,.0f} COP
- Ahorro mensual estimado: ${AHORRO_MES_1:,.0f}
- Retorno inversión: {ROI_SIMPLE} años

Archivos adjuntos:
- Precotizacion_{NOMBRE}_{TIMESTAMP}.pdf
- Precotizacion_{NOMBRE}_{TIMESTAMP}.pptx

Saludos,
Equipo NASSA Solar
```

---

## 9. SEGURIDAD GENERAL

### 9.1 Autenticación
- Admin: HTTP Basic Auth
- Variables: `ADMIN_USER`, `ADMIN_PASS` en `.env`
- No hay usuarios finales (cotización pública)

### 9.2 Autorización
- Endpoints públicos: Equipos (sin precios), ciudades, cotización
- Endpoints privados: CRUD equipos, parámetros, template

### 9.3 Protecciones
- **Rate Limiting:** 10 req/min por IP
- **CORS:** Solo dominios permitidos
- **Validación:** Pydantic en todos los endpoints
- **Secrets:** `.env` excluido de Git (`.gitignore`)
- **IDs auto-generados:** Admin no controla IDs

### 9.4 Datos Sensibles
- Precios equipos (solo admin)
- Credenciales SMTP
- Credenciales admin
- Secret key (futuro JWT)

---

## 10. RESTRICCIONES Y LIMITACIONES

### 10.1 Técnicas
- Python 3.9+ requerido
- LibreOffice obligatorio para PDF
- Gmail SMTP (contraseña de aplicación)
- Sin base de datos relacional
- Sin transacciones ACID
- Archivos JSON thread-unsafe

### 10.2 Funcionales
- 1 panel/inversor por cotización
- Batería opcional
- Solo Colombia (163 ciudades)
- Proyección fija 25-30 años
- Template PPTX manual
- Sin historial cotizaciones

### 10.3 Escalabilidad
- Rate limit 10 req/min (ajustable)
- Sin queue de emails
- Conversión PDF síncrona (90s timeout)
- JSON en memoria (límite ~10MB)
- Sin balanceo de carga

### 10.4 UX
- Sin registro usuarios
- Sin login cliente
- Sin dashboard
- Sin edición cotizaciones
- Sin comparación cotizaciones

---

## 11. DEPENDENCIAS

### 11.1 Python (requirements.txt)
```
fastapi==0.104.1          # Framework web
uvicorn==0.24.0           # Servidor ASGI
python-dotenv==1.0.0      # Variables entorno
pydantic==2.5.0           # Validación datos
python-pptx==0.6.21       # Manipulación PowerPoint
python-docx==0.8.11       # (No usado actualmente)
reportlab==4.0.7          # (No usado actualmente)
sendgrid==6.12.5          # (No usado actualmente)
```

### 11.2 Sistema
- Python 3.9+
- LibreOffice 7.0+
- macOS 10.15+ / Ubuntu 20.04+ / Windows 10+

### 11.3 Navegadores (Frontend)
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## 12. ESTRUCTURA DE ARCHIVOS

```
cotizador/
├── backend/
│   ├── server.py                    # Backend principal (1161 líneas)
│   ├── requirements.txt             # Dependencias Python
│   ├── .env                         # Variables entorno (no Git)
│   ├── .env.example                 # Plantilla variables
│   ├── config/
│   │   ├── equipos.json            # Catálogo equipos
│   │   ├── ciudades.json           # HSP ciudades
│   │   └── parametros.json         # Parámetros sistema
│   └── venv/                       # Entorno virtual Python
├── Template/
│   ├── Template-PreCotizacion.pptx  # Template PowerPoint
│   └── *.md                         # Guías placeholders
├── index_Original_modificado.html   # Frontend principal (872 líneas)
├── admin.html                       # Panel admin (1057 líneas)
└── README.md                        # (Este archivo futuro)
```

---

## 13. FLUJO COMPLETO DE OPERACIÓN

```
1. Usuario abre frontend (puerto 8000)
2. Frontend carga ciudades y equipos (sin inversores)
3. Usuario llena formulario
4. Usuario selecciona sistema eléctrico → Carga inversores filtrados
5. Usuario selecciona panel, inversor, batería (opcional)
6. Usuario envía formulario
7. Backend valida datos (Pydantic)
8. Backend calcula dimensionamiento y proyección 25 años
9. Backend llena template PPTX con 40+ placeholders
10. Backend llena tabla TABLA_AHORROS (15 filas)
11. Backend convierte PPTX → PDF (LibreOffice CLI, 90s timeout)
12. Backend envía email con PDF + PPTX adjuntos
13. Backend elimina archivos temporales
14. Backend retorna resumen JSON (10 primeros años)
15. Frontend muestra resultado en modal
16. Frontend guarda datos en localStorage (CRM)
```

---

## 14. MONEDA Y FORMATO

- **Moneda:** COP (Pesos colombianos)
- **Formato números:** `1.234.567` (punto miles, sin decimales)
- **Formato moneda:** `$1,234,567 COP` o `$1.234.567`
- **IVA:** 19%
- **Idioma:** Español (Colombia)

---

## 15. CONTACTO Y SOPORTE

- **Empresa:** NASSA Solar
- **Email cotizaciones:** nassasolarprecotizaciones@gmail.com
- **Email seguimiento:** jcsalazarb@icloud.com
- **WhatsApp:** +57 313 690 9723
- **Repositorio:** GitHub (privado)

---

**FIN DOCUMENTO 1 - DOCUMENTACIÓN FUNCIONAL**
