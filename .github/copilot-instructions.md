# NASSA Solar Quotation System - AI Agent Instructions

## Architecture Overview

This is a **solar photovoltaic quotation system** with a Python FastAPI backend and vanilla HTML/JS frontend. The system calculates solar panel installations, generates PowerPoint presentations, converts them to PDF, and emails quotations to customers.

**Tech Stack**: FastAPI + Python-PPTX + LibreOffice (for PDF conversion) + vanilla HTML/CSS/JS

## Critical Components

### Backend (`backend/server.py`)
- **FastAPI server** on port 5000
- **Security**: HTTP Basic Auth for admin endpoints, rate limiting (10 req/min), CORS middleware
- **Core calculation**: `calcular_cotizacion()` - computes solar panel count, costs, ROI, 25-year savings projections
- **PowerPoint workflow**: Fills `Template-Precottizacion.pptx` → calls LibreOffice CLI → generates PDF → emails both files
- **Key calculations**: 
  - Panel count based on HSP (Horas Solar Pico), consumption, panel efficiency (90%)
  - 25-year financial model: depreciation (3 years, 35% tax benefit), rent deductions (5 years, 50% base, 35% effective)
  - Annual degradation (1%), first year only 50% generation, cost/kWh increase (5.5%/year)

### Configuration Files
- `config/equipos.json`: Equipment catalog with prices (panels, inverters, batteries). **Prices are PRIVATE** - admin endpoint only.
- `config/ciudades.json`: HSP values per Colombian city (Santa Marta: 5.6, Barranquilla: 5.2, etc.)

### Frontend (`Index.html`)
- **Embedded JavaScript** (no separate `.js` files) - all logic in `<script>` tag at bottom
- Fetches equipment/cities from API, submits quotation form via POST `/api/cotizar`
- **Modal CRM**: Stores quotation data in `localStorage` for follow-up calls
- API base URL: `const API_BASE_URL = 'http://127.0.0.1:5000/api'`

## Essential Workflows

### Running the System

**Backend (macOS)**:
```bash
cd backend
source venv/bin/activate  # Create with: python3 -m venv venv
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 5000 --reload
# OR: python server.py
```

**Frontend**:
```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador
python3 -m http.server 8000
# Open http://localhost:8000
```

**LibreOffice Requirement**: Must be installed for PDF conversion
```bash
brew install --cask libreoffice  # macOS
# Path: /Applications/LibreOffice.app/Contents/MacOS/soffice
```

### Environment Variables (`.env`)
```bash
ADMIN_USER=admin
ADMIN_PASS=changeme
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_NASSA=nassasolar@example.com
LIBREOFFICE_PATH=soffice  # or full path
ALLOWED_ORIGINS=*
RATE_LIMIT=10
```

## Critical Patterns

### PowerPoint Table Population
The template **must** have a table named `TABLA_AHORROS` with 13 rows (1 header + 12 data rows). If table name doesn't exist, the system searches for tables with headers containing "año" and "ahorro". The `fill_ahorros_table_in_ppt()` function:
1. Normalizes headers (removes accents, spaces, special chars)
2. Maps columns by detecting keywords: "ano", "valorkwh", "produccion", "generacion", "depreciacion", "deduccion", "costo", "ahorro", "acumulado", "roi"
3. Fills first 12 years of 25-year projection

### Data Flow
1. Frontend form → POST `/api/cotizar` with validated Pydantic model `CotizarRequest`
2. Backend calculates full 25-year projection
3. Fills PowerPoint template with placeholders (`{{NOMBRE}}`, `{{CAPACIDAD_INSTALADA}}`, etc.)
4. LibreOffice CLI converts PPTX → PDF
5. Emails PDF + PPTX to customer (with CC to NASSA)
6. Returns JSON summary (first 10 years only)

### Equipment Pricing Model
- Panels: ~180k-220k COP per unit (450W-550W)
- Inverters: ~1.5M-2.2M COP (3kW-5kW)
- Batteries: ~4.5M-8.5M COP (5kWh-10kWh)
- Additional costs: Soportería (180k/panel), Instalación (250k/panel), Materiales (150k/panel)
- IVA (19%) applies to batteries, soportería, installation, materials (NOT panels/inverters)

## Project-Specific Conventions

- **No external frontend build tools**: All HTML/CSS/JS is inline or in `<script>` tags
- **Spanish language**: All variables, comments, error messages are in Spanish
- **Colombian currency**: COP (pesos colombianos), format with commas: `${value:,.0f}`
- **System types**: `ongrid`, `offgrid`, `hibrido_incluido`, `hibrido_opcional` - batteries required for offgrid/hibrido_incluido
- **HSP lookup**: City names normalized to lowercase, spaces→underscores. Fallback to `"default": {"hsp": 5.0}`
- **File paths**: All use `os.path.join()` for cross-platform compatibility

## Common Debugging Points

- **LibreOffice not found**: Check `LIBREOFFICE_PATH` env var or install via brew
- **Email failures**: Generate quotation continues even if email fails (try/except)
- **Template table not found**: Verify table has "TABLA_AHORROS" name OR headers with "año" + "ahorro"
- **Equipment not found**: IDs must match exactly: `panel1`, `inv2`, `bat1` (case-sensitive)
- **Rate limit**: Default 10 requests/minute per IP, configurable via `RATE_LIMIT`

## Key Files Reference

- `backend/server.py`: All backend logic (no separate modules)
- `backend/config/equipos.json`: Equipment catalog (update prices here)
- `backend/config/ciudades.json`: HSP database for Colombia
- `Template/Template-Precottizacion.pptx`: PowerPoint template with `TABLA_AHORROS` table
- `Index.html`: Main frontend (self-contained, no build step)

## Testing Endpoints

```bash
# Public endpoints
curl http://localhost:5000/health
curl http://localhost:5000/api/equipos  # No prices
curl http://localhost:5000/api/ciudades

# Admin endpoints (require Basic Auth)
curl -u admin:changeme http://localhost:5000/api/equipos/precios
curl -u admin:changeme http://localhost:5000/api/template/download
```

## Important Notes

- **PowerPoint conversion is synchronous**: Can take 30-90 seconds (subprocess timeout)
- **Temp files auto-cleanup**: PPTX and PDF deleted after email sent
- **CRM data**: Frontend stores last quotation in `localStorage.quoteCRM` for phone follow-ups
- **Multiple HTML files**: `Index.html` is primary, others are experiments/backups - ignore them
- **No tests**: This is a production system without test coverage
