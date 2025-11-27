# 📂 Nueva Estructura del Proyecto

## ✅ Reorganización Completada

Se ha reorganizado el proyecto para una estructura más profesional y compatible con Railway.

## 🗂️ Estructura Actual

```
cotizador/
├── backend/
│   ├── server.py              # FastAPI backend (ahora sirve archivos estáticos)
│   ├── static/                # ← NUEVO: Frontend público
│   │   ├── index.html         # Página principal de cotización
│   │   ├── admin.html         # Panel administrativo
│   │   ├── css/               # Estilos (si existen)
│   │   ├── js/                # Scripts (si existen)
│   │   └── images/            # Imágenes
│   │       └── loggo-Nassa.png
│   ├── config/
│   │   ├── equipos.json       # Catálogo de equipos
│   │   └── ciudades.json      # HSP por ciudad
│   ├── templates/             # (si usas Jinja2)
│   ├── .env                   # Variables de entorno (NO en Git)
│   ├── requirements.txt       # Dependencias Python
│   └── test_email.py          # Script de prueba de email
├── Template/
│   └── Template-PreCotizacion.pptx  # Plantilla PowerPoint
├── railway.json               # Configuración Railway
├── Procfile                   # Comando de inicio
├── nixpacks.toml              # Instalación LibreOffice
├── .gitignore                 # Archivos ignorados
├── .env.example               # Plantilla de variables
└── *.md                       # Documentación
```

## 🎯 URLs de Acceso

### Local (desarrollo)
- **Frontend**: http://localhost:8001/
- **Admin**: http://localhost:8001/admin
- **API Health**: http://localhost:8001/health
- **API Docs**: http://localhost:8001/docs
- **Equipos**: http://localhost:8001/api/equipos
- **Ciudades**: http://localhost:8001/api/ciudades

### Railway (producción)
- **Frontend**: https://tu-app.up.railway.app/
- **Admin**: https://tu-app.up.railway.app/admin
- **API**: https://tu-app.up.railway.app/api/*

## 🔄 Cambios Realizados

### 1. **Frontend Unificado**
   - ❌ Antes: Múltiples archivos HTML en la raíz
     - `index_Original_modificado.html`
     - `Index.html`
     - `Index2.html`
     - `admin.html`
   - ✅ Ahora: Un solo archivo en `backend/static/`
     - `backend/static/index.html` (cotización)
     - `backend/static/admin.html` (panel admin)

### 2. **Servidor Unificado**
   - ❌ Antes: Dos servidores separados
     - Backend: `uvicorn` en puerto 8001
     - Frontend: `python -m http.server` en puerto 8000
   - ✅ Ahora: Un solo servidor FastAPI en puerto 8001
     - Sirve API y archivos estáticos

### 3. **Archivos Estáticos**
   - FastAPI monta `/static` con `StaticFiles`
   - Ruta raíz `/` sirve `index.html`
   - Ruta `/admin` sirve `admin.html`
   - CSS, JS, imágenes accesibles en `/static/*`

### 4. **Compatibilidad Railway**
   - Railway ejecuta un solo proceso
   - Todo se sirve desde el mismo puerto (`$PORT`)
   - No necesita configurar frontend por separado

## 📝 Código Actualizado en `server.py`

```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Configuración de archivos estáticos
STATIC_DIR = os.path.join(APP_DIR, "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Endpoint raíz sirve index.html
@app.get("/")
def root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"message": "API NASSA Solar", "status": "activo"}

# Endpoint admin sirve admin.html
@app.get("/admin")
def admin_panel():
    admin_path = os.path.join(STATIC_DIR, "admin.html")
    if os.path.exists(admin_path):
        return FileResponse(admin_path, media_type="text/html")
    raise HTTPException(404, "Panel administrativo no encontrado")
```

## 🚀 Cómo Usar

### Desarrollo Local

```bash
# 1. Liberar puerto (si está ocupado)
lsof -ti:8001 | xargs kill -9 2>/dev/null

# 2. Iniciar servidor (desde carpeta backend)
cd backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# 3. Abrir navegador
# Frontend: http://localhost:8001/
# Admin: http://localhost:8001/admin
```

### Despliegue en Railway

```bash
# 1. Commit y push
git add .
git commit -m "Actualización frontend"
git push origin main

# 2. Railway desplegará automáticamente
# - Ejecuta: cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT
# - Sirve frontend en: https://tu-app.up.railway.app/
```

## ⚠️ Archivos Antiguos (Ignorados por Git)

Estos archivos HTML en la raíz ya NO se usan y están en `.gitignore`:
- `/Index.html`
- `/Index2.html`
- `/index_Original.html`
- `/index_Original_modificado.html`
- `/indexcanva.html`
- `/indexcanva2.html`
- `/admin.html` (raíz)
- `/frontend/` (carpeta completa)

**Puedes eliminarlos localmente si quieres** (no afecta el repositorio):
```bash
rm -f Index*.html indexcanva*.html admin.html
rm -rf frontend/
```

## ✅ Ventajas de la Nueva Estructura

1. **Un solo servidor**: No necesitas levantar frontend y backend por separado
2. **URLs limpias**: `/` para cotización, `/admin` para administración
3. **Compatible con Railway**: Un solo proceso, un solo puerto
4. **CORS simplificado**: Mismo dominio para todo
5. **Profesional**: Estructura estándar de aplicaciones web modernas
6. **Fácil despliegue**: Solo ejecutar `uvicorn` y todo funciona

## 🔧 Próximos Pasos

1. ✅ Estructura reorganizada
2. ✅ Código actualizado
3. ✅ Commit realizado
4. ⏳ Push a GitHub: `git push origin main`
5. ⏳ Desplegar en Railway

## 📞 Soporte

Si algo no funciona:
1. Verifica que `backend/static/index.html` exista
2. Revisa logs: `uvicorn` mostrará errores
3. Prueba acceder a: http://localhost:8001/

---

**Esta estructura está lista para producción en Railway** 🚀
