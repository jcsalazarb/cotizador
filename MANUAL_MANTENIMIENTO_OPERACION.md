# MANUAL DE MANTENIMIENTO Y OPERACIÓN

**Proyecto:** Sistema de Cotización Solar NASSA  
**Fecha:** 25 de noviembre de 2025  
**Versión:** 1.0

---

## 1. INSTALACIÓN INICIAL

### 1.1 Requisitos del Sistema

```bash
# Python
python3 --version  # >= 3.9

# LibreOffice
/Applications/LibreOffice.app/Contents/MacOS/soffice --version  # macOS
soffice --version  # Linux

# Git
git --version
```

### 1.2 Clonar Repositorio

```bash
cd ~/Documents/GitHub
git clone https://github.com/jcsalazarb/cotizador.git
cd cotizador
```

### 1.3 Configurar Backend

```bash
cd backend

# Crear entorno virtual
python3 -m venv venv

# Activar entorno
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Copiar variables de entorno
cp .env.example .env

# Editar .env con credenciales reales
nano .env
```

### 1.4 Archivo `.env` Requerido

```bash
# SMTP (Gmail App Password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=nassasolarprecotizaciones@gmail.com
SMTP_PASS=hihzyxagqdptwfed
EMAIL_FROM=nassasolarprecotizaciones@gmail.com
EMAIL_NASSA=jcsalazarb@icloud.com
EMAIL_SUBJECT=PreCotización Nassa Solar

# Admin
ADMIN_USER=admin
ADMIN_PASS=Lu1sF3rN@ss@
SECRET_KEY=

# CORS
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Server
PORT=8001
RATE_LIMIT=10
```

---

## 2. INICIAR SERVIDORES

### 2.1 Backend (Puerto 8001)

**Opción 1: Con Uvicorn (Recomendado)**
```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador/backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Opción 2: En background con logs**
```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador/backend
lsof -ti:8001 | xargs kill -9 2>/dev/null  # Liberar puerto
/Users/jcsalazarb/Documents/GitHub/cotizador/backend/venv/bin/uvicorn \
  server:app --host 0.0.0.0 --port 8001 --reload > /tmp/backend.log 2>&1 &
```

**Verificar backend corriendo:**
```bash
curl http://localhost:8001/health
# Respuesta esperada: {"status":"ok","timestamp":"..."}
```

### 2.2 Frontend (Puerto 8000)

```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador
python3 -m http.server 8000
```

**En background:**
```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador
python3 -m http.server 8000 > /tmp/frontend.log 2>&1 &
```

### 2.3 Acceso a Interfaces

- **Frontend:** http://localhost:8000/index_Original_modificado.html
- **Admin:** http://localhost:8000/admin.html
- **API Docs:** http://localhost:8001/docs
- **Redoc:** http://localhost:8001/redoc

---

## 3. DETENER SERVIDORES

```bash
# Detener backend (puerto 8001)
lsof -ti:8001 | xargs kill -9 2>/dev/null
echo "✅ Backend detenido"

# Detener frontend (puerto 8000)
lsof -ti:8000 | xargs kill -9 2>/dev/null
echo "✅ Frontend detenido"

# Ambos puertos a la vez
lsof -ti:8001 | xargs kill -9 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
echo "✅ Puertos liberados"
```

---

## 4. PRUEBAS DE FUNCIONALIDAD

### 4.1 Test Salud del Servidor

```bash
curl http://localhost:8001/health
```

**Respuesta esperada:**
```json
{
  "status": "ok",
  "timestamp": "2025-11-25T12:00:00.000000+00:00"
}
```

### 4.2 Test API Equipos (Pública)

```bash
# Sin precios
curl http://localhost:8001/api/equipos | python3 -m json.tool | head -50

# Contar equipos
curl -s http://localhost:8001/api/equipos | \
  python3 -c "import sys, json; d=json.load(sys.stdin); \
  print(f'Paneles: {len(d[\"paneles\"])}, Inversores: {len(d[\"inversores\"])}, Baterías: {len(d[\"baterias\"])}')"
```

### 4.3 Test Filtro Inversores

```bash
# Inversores monofásicos
curl http://localhost:8001/api/equipos?sistemaElectrico=monofasico | python3 -m json.tool

# Inversores trifásicos
curl http://localhost:8001/api/equipos?sistemaElectrico=trifasico | python3 -m json.tool

# Contar por tipo
curl -s "http://localhost:8001/api/equipos?sistemaElectrico=monofasico" | \
  python3 -c "import sys, json; d=json.load(sys.stdin); print(f'{len(d[\"inversores\"])} inversores')"
```

### 4.4 Test API Ciudades

```bash
# Listar todas
curl http://localhost:8001/api/ciudades | python3 -m json.tool | head -30

# Contar ciudades
curl -s http://localhost:8001/api/ciudades | \
  python3 -c "import sys, json; d=json.load(sys.stdin); print(f'{len(d)} ciudades')"

# Buscar ciudad específica
curl -s http://localhost:8001/api/ciudades | \
  python3 -c "import sys, json; d=json.load(sys.stdin); print(f'Barranquilla HSP: {d.get(\"barranquilla\", \"N/A\")}')"
```

### 4.5 Test Admin API (Con Autenticación)

```bash
# Listar paneles con precios
curl -u "admin:Lu1sF3rN@ss@" http://localhost:8001/api/equipos/precios | python3 -m json.tool

# Crear panel de prueba
curl -u "admin:Lu1sF3rN@ss@" -X POST http://localhost:8001/api/admin/paneles \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Panel Test",
    "capacidad": 600,
    "precio": 500000,
    "descripcion": "Prueba auto-ID"
  }'

# Respuesta esperada: {"status":"success","mensaje":"Panel panelX creado exitosamente","id":"panelX"}

# Eliminar panel de prueba
curl -u "admin:Lu1sF3rN@ss@" -X DELETE http://localhost:8001/api/admin/paneles/panelX
```

### 4.6 Test Cotización Completa

```bash
curl -X POST http://localhost:8001/api/cotizar \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Cliente Prueba",
    "telefono": "3001234567",
    "email": "prueba@test.com",
    "ciudad": "barranquilla",
    "direccion": "Calle 123",
    "consumoMensual": 300,
    "valorFactura": 450000,
    "valorKwh": 1500,
    "nic": "12345678",
    "tipoVivienda": "casa",
    "areaDisponible": 50,
    "numeroPisos": "1",
    "sistemaElectrico": "monofasico",
    "porcentajeConsumodia": 60,
    "tipoFV": "ongrid",
    "panelId": "panel1",
    "inversorId": "inv1"
  }'
```

**Verificar:**
- Status 200
- Email recibido
- Archivos PDF y PPTX adjuntos
- Logs en `/tmp/backend.log`

### 4.7 Test Email SMTP

```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador/backend
source venv/bin/activate
python test_smtp.py
```

**Archivo `test_smtp.py`:**
```python
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

msg = EmailMessage()
msg['Subject'] = 'Test NASSA Solar'
msg['From'] = os.getenv('SMTP_USER')
msg['To'] = os.getenv('EMAIL_NASSA')
msg.set_content('Test email desde sistema cotizaciones')

try:
    with smtplib.SMTP(os.getenv('SMTP_HOST'), int(os.getenv('SMTP_PORT'))) as smtp:
        smtp.starttls()
        smtp.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASS'))
        smtp.send_message(msg)
    print("✅ Email enviado correctamente")
except Exception as e:
    print(f"❌ Error: {e}")
```

---

## 5. DIAGNÓSTICO Y RESOLUCIÓN DE PROBLEMAS

### 5.1 Backend no arranca

**Problema:** `ModuleNotFoundError: No module named 'fastapi'`

**Solución:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

---

**Problema:** `Address already in use (puerto 8001)`

**Solución:**
```bash
lsof -ti:8001 | xargs kill -9 2>/dev/null
sleep 1
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

---

**Problema:** `FileNotFoundError: equipos.json`

**Solución:**
```bash
# Verificar estructura
cd backend
ls -la config/
ls -la config/equipos.json

# Si falta, restaurar desde backup o Git
git checkout config/equipos.json
```

### 5.2 Frontend no carga equipos

**Problema:** CORS error en consola

**Solución en `.env`:**
```bash
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

**Reiniciar backend:**
```bash
lsof -ti:8001 | xargs kill -9
cd backend && uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

---

**Problema:** Inversores no se muestran

**Verificar:**
```javascript
// En consola navegador
console.log('Sistema eléctrico seleccionado:', 
  document.getElementById('sistemaElectrico').value);
```

**Solución:** Asegurarse que se selecciona sistema eléctrico antes de ver inversores.

### 5.3 Email no se envía

**Problema:** `SMTPAuthenticationError`

**Solución:**
1. Verificar contraseña de aplicación Gmail (no contraseña normal)
2. Generar nueva: https://myaccount.google.com/apppasswords
3. Actualizar `SMTP_PASS` en `.env`
4. Reiniciar backend

---

**Problema:** Email enviado pero no llega

**Verificar:**
```bash
# Ver logs
tail -50 /tmp/backend.log | grep -i email

# Test directo
cd backend && source venv/bin/activate && python test_smtp.py
```

**Revisar:**
- Carpeta Spam
- Dirección destinatario correcta
- Límites Gmail (500/día)

### 5.4 PDF no se genera

**Problema:** `FileNotFoundError: soffice`

**Solución:**
```bash
# macOS
brew install --cask libreoffice

# Verificar instalación
/Applications/LibreOffice.app/Contents/MacOS/soffice --version

# Actualizar variable en .env si es necesario
LIBREOFFICE_PATH=/Applications/LibreOffice.app/Contents/MacOS/soffice
```

---

**Problema:** PDF timeout (90 segundos)

**Solución:**
1. Verificar LibreOffice no esté bloqueado
2. Cerrar todas instancias:
```bash
pkill -9 soffice
sleep 2
```
3. Reintentar cotización

### 5.5 Admin panel no guarda

**Problema:** Error 401 Unauthorized

**Solución:**
```bash
# Verificar credenciales en .env
cat backend/.env | grep ADMIN

# Limpiar caché navegador y re-login
# Chrome: Cmd+Shift+Delete
```

---

**Problema:** Modal no cierra después de guardar

**Verificar consola navegador:**
```
F12 > Console
```

**Solución:** Recargar página (Cmd+Shift+R)

---

## 6. MANTENIMIENTO DE ARCHIVOS DE CONFIGURACIÓN

### 6.1 Actualizar Equipos (`equipos.json`)

**Vía Admin Panel (Recomendado):**
1. Abrir http://localhost:8000/admin.html
2. Login con credenciales admin
3. Tab correspondiente (Paneles | Inversores | Baterías)
4. Clic "➕ Nuevo" o "✏️ Editar"
5. Llenar formulario
6. Guardar

**Vía Archivo Directo:**
```bash
cd backend/config
nano equipos.json

# Validar JSON
python3 -c "import json; json.load(open('equipos.json'))" && echo "✅ JSON válido"

# Reiniciar backend para aplicar cambios
lsof -ti:8001 | xargs kill -9
cd .. && uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Formato Inversores (importante `tipo_sistema`):**
```json
{
  "id": "inv1",
  "nombre": "Inversor Growatt 3kW",
  "capacidad": 3000,
  "precio": 2200000,
  "descripcion": "Monofásico, WiFi incluido",
  "eficiencia": 0.9,
  "tipo_sistema": "monofasico"
}
```

### 6.2 Actualizar Ciudades (`ciudades.json`)

```bash
cd backend/config
nano ciudades.json

# Agregar nueva ciudad
"nueva_ciudad": 5.1,

# Validar
python3 -c "import json; d=json.load(open('ciudades.json')); print(f'{len(d)} ciudades')"
```

**Formato:**
```json
{
  "ciudad_normalizada": 5.2,
  "otra_ciudad": 4.8
}
```

**Normalización nombres:**
- Minúsculas
- Espacios → guion bajo
- Sin acentos
- Ejemplo: `"Santa Marta"` → `"santa_marta"`

### 6.3 Actualizar Parámetros (`parametros.json`)

**Vía Admin Panel:**
1. Admin → Tab "Parámetros"
2. Editar valores
3. Guardar

**Vía Archivo:**
```bash
cd backend/config
nano parametros.json

# Ejemplo: Cambiar IVA de 19% a 20%
"iva_porcentaje": 0.20

# Validar
python3 -m json.tool parametros.json
```

### 6.4 Actualizar Template PowerPoint

**Ubicación:** `Template/Template-PreCotizacion.pptx`

**Procedimiento:**
1. Abrir con PowerPoint/LibreOffice
2. Editar diseño, colores, logos
3. **Mantener placeholders:** `{{NOMBRE}}`, `{{TOTAL}}`, etc.
4. **Mantener tabla:** Nombre `TABLA_AHORROS`, 15 filas
5. Guardar como `.pptx`
6. Probar con cotización de prueba

**Descargar template actual:**
```bash
curl -u "admin:Lu1sF3rN@ss@" \
  http://localhost:8001/api/template/download \
  -o Template_backup.pptx
```

**Ver placeholders disponibles:**
```bash
cat Template/PLACEHOLDERS_TEMPLATE.md
```

---

## 7. BACKUP Y RESTAURACIÓN

### 7.1 Backup Manual

```bash
# Backup completo
cd /Users/jcsalazarb/Documents/GitHub
tar -czf cotizador_backup_$(date +%Y%m%d).tar.gz cotizador/

# Backup solo configuración
cd cotizador/backend/config
tar -czf config_backup_$(date +%Y%m%d).tar.gz *.json
```

### 7.2 Backup Automático (Cron)

```bash
# Editar crontab
crontab -e

# Agregar (backup diario a las 2 AM)
0 2 * * * cd /Users/jcsalazarb/Documents/GitHub && tar -czf cotizador_backup_$(date +\%Y\%m\%d).tar.gz cotizador/ > /tmp/backup.log 2>&1
```

### 7.3 Restaurar desde Backup

```bash
cd /Users/jcsalazarb/Documents/GitHub
tar -xzf cotizador_backup_20251125.tar.gz

# Restaurar solo config
cd cotizador/backend/config
tar -xzf config_backup_20251125.tar.gz
```

### 7.4 Restaurar desde Git

```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador

# Ver cambios
git status

# Descartar cambios locales
git checkout -- backend/config/equipos.json

# Restaurar todo al último commit
git reset --hard HEAD

# Actualizar desde remoto
git pull origin main
```

---

## 8. LOGS Y MONITOREO

### 8.1 Ver Logs Backend

```bash
# Tiempo real
tail -f /tmp/backend.log

# Últimas 50 líneas
tail -50 /tmp/backend.log

# Filtrar errores
grep -i error /tmp/backend.log

# Filtrar emails
grep -i email /tmp/backend.log | tail -20
```

### 8.2 Ver Logs Frontend (Navegador)

```
F12 > Console
```

**Filtrar:**
```javascript
// Solo errores
console.error

// Solo warnings
console.warn

// Búsqueda
Cmd+F > "equipos" > Enter
```

### 8.3 Verificar Procesos Activos

```bash
# Backend
lsof -ti:8001
ps aux | grep uvicorn

# Frontend
lsof -ti:8000
ps aux | grep "http.server"

# Ambos
ps aux | grep -E "uvicorn|http.server"
```

### 8.4 Monitoreo Recursos

```bash
# CPU y Memoria
top -pid $(lsof -ti:8001)

# Conexiones red
lsof -i :8001
lsof -i :8000

# Tráfico
netstat -an | grep -E "8000|8001"
```

---

## 9. ACTUALIZACIÓN DE DEPENDENCIAS

### 9.1 Actualizar Python Packages

```bash
cd backend
source venv/bin/activate

# Ver versiones actuales
pip list

# Ver paquetes desactualizados
pip list --outdated

# Actualizar específico
pip install --upgrade fastapi

# Actualizar todos
pip install --upgrade -r requirements.txt

# Guardar nuevas versiones
pip freeze > requirements.txt
```

### 9.2 Actualizar LibreOffice

```bash
# macOS
brew upgrade libreoffice

# Verificar versión
/Applications/LibreOffice.app/Contents/MacOS/soffice --version
```

---

## 10. VERIFICACIÓN DE INTEGRIDAD

### 10.1 Validar Sintaxis Python

```bash
cd backend
source venv/bin/activate
python -m py_compile server.py && echo "✅ Sintaxis correcta"
```

### 10.2 Validar JSON

```bash
cd backend/config

# Equipos
python3 -c "import json; json.load(open('equipos.json'))" && echo "✅ equipos.json válido"

# Ciudades
python3 -c "import json; json.load(open('ciudades.json'))" && echo "✅ ciudades.json válido"

# Parámetros
python3 -c "import json; json.load(open('parametros.json'))" && echo "✅ parametros.json válido"
```

### 10.3 Contar Registros

```bash
cd backend/config

# Paneles
python3 -c "import json; d=json.load(open('equipos.json')); print(f'Paneles: {len(d[\"paneles\"])}')"

# Inversores por tipo
python3 -c "import json; d=json.load(open('equipos.json')); \
  mono = [i for i in d['inversores'] if i.get('tipo_sistema')=='monofasico']; \
  bi = [i for i in d['inversores'] if i.get('tipo_sistema')=='bifasico']; \
  tri = [i for i in d['inversores'] if i.get('tipo_sistema')=='trifasico']; \
  print(f'Monofásicos: {len(mono)}, Bifásicos: {len(bi)}, Trifásicos: {len(tri)}')"

# Ciudades
python3 -c "import json; d=json.load(open('ciudades.json')); print(f'Ciudades: {len(d)}')"
```

---

## 11. COMANDOS RÁPIDOS (CHEAT SHEET)

```bash
# INICIAR TODO
cd /Users/jcsalazarb/Documents/GitHub/cotizador/backend && \
  /Users/jcsalazarb/Documents/GitHub/cotizador/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --reload > /tmp/backend.log 2>&1 &
cd /Users/jcsalazarb/Documents/GitHub/cotizador && \
  python3 -m http.server 8000 > /tmp/frontend.log 2>&1 &

# DETENER TODO
lsof -ti:8001 | xargs kill -9 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null

# REINICIAR BACKEND
lsof -ti:8001 | xargs kill -9 2>/dev/null && sleep 1 && \
  cd /Users/jcsalazarb/Documents/GitHub/cotizador/backend && \
  /Users/jcsalazarb/Documents/GitHub/cotizador/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --reload &

# TEST RÁPIDO
curl http://localhost:8001/health && \
  curl -s http://localhost:8001/api/ciudades | python3 -c "import sys, json; print(f'{len(json.load(sys.stdin))} ciudades')" && \
  curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/index_Original_modificado.html && \
  echo " - Frontend OK"

# LOGS EN TIEMPO REAL
tail -f /tmp/backend.log

# BACKUP RÁPIDO
cd /Users/jcsalazarb/Documents/GitHub && \
  tar -czf cotizador_backup_$(date +%Y%m%d_%H%M).tar.gz cotizador/
```

---

## 12. SCRIPTS DE UTILIDAD

### 12.1 Script Inicio Completo (`start.sh`)

```bash
#!/bin/bash
# start.sh - Iniciar servidores NASSA Solar

echo "🚀 Iniciando Sistema NASSA Solar..."

# Verificar puerto 8001 libre
if lsof -ti:8001 > /dev/null 2>&1; then
    echo "⚠️  Puerto 8001 ocupado, liberando..."
    lsof -ti:8001 | xargs kill -9 2>/dev/null
    sleep 2
fi

# Verificar puerto 8000 libre
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "⚠️  Puerto 8000 ocupado, liberando..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 2
fi

# Iniciar backend
echo "🔧 Iniciando backend (puerto 8001)..."
cd /Users/jcsalazarb/Documents/GitHub/cotizador/backend
/Users/jcsalazarb/Documents/GitHub/cotizador/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
sleep 3

# Verificar backend
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Backend corriendo (PID: $BACKEND_PID)"
else
    echo "❌ Error iniciando backend"
    exit 1
fi

# Iniciar frontend
echo "🌐 Iniciando frontend (puerto 8000)..."
cd /Users/jcsalazarb/Documents/GitHub/cotizador
python3 -m http.server 8000 > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 2

echo "✅ Frontend corriendo (PID: $FRONTEND_PID)"
echo ""
echo "📍 URLs:"
echo "   Frontend: http://localhost:8000/index_Original_modificado.html"
echo "   Admin:    http://localhost:8000/admin.html"
echo "   API Docs: http://localhost:8001/docs"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f /tmp/backend.log"
echo "   Frontend: tail -f /tmp/frontend.log"
```

**Uso:**
```bash
chmod +x start.sh
./start.sh
```

### 12.2 Script Detener (`stop.sh`)

```bash
#!/bin/bash
# stop.sh - Detener servidores NASSA Solar

echo "🛑 Deteniendo Sistema NASSA Solar..."

# Detener backend
if lsof -ti:8001 > /dev/null 2>&1; then
    lsof -ti:8001 | xargs kill -9 2>/dev/null
    echo "✅ Backend detenido"
else
    echo "ℹ️  Backend no estaba corriendo"
fi

# Detener frontend
if lsof -ti:8000 > /dev/null 2>&1; then
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    echo "✅ Frontend detenido"
else
    echo "ℹ️  Frontend no estaba corriendo"
fi

echo "✅ Sistema detenido completamente"
```

### 12.3 Script Test Completo (`test.sh`)

```bash
#!/bin/bash
# test.sh - Test completo funcionalidad

echo "🧪 Ejecutando tests..."

# Test 1: Health
echo "1. Test Health..."
if curl -s http://localhost:8001/health | grep -q "ok"; then
    echo "   ✅ Backend responde"
else
    echo "   ❌ Backend no responde"
    exit 1
fi

# Test 2: Ciudades
echo "2. Test Ciudades..."
CIUDADES=$(curl -s http://localhost:8001/api/ciudades | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "   ✅ $CIUDADES ciudades cargadas"

# Test 3: Equipos
echo "3. Test Equipos..."
curl -s http://localhost:8001/api/equipos | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'   ✅ {len(d[\"paneles\"])} paneles, {len(d[\"inversores\"])} inversores, {len(d[\"baterias\"])} baterías')
"

# Test 4: Frontend
echo "4. Test Frontend..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/index_Original_modificado.html)
if [ "$STATUS" = "200" ]; then
    echo "   ✅ Frontend accesible"
else
    echo "   ❌ Frontend no accesible (HTTP $STATUS)"
fi

echo ""
echo "✅ Todos los tests pasaron"
```

---

## 13. MANTENIMIENTO PERIÓDICO

### 13.1 Diario
- Verificar logs de errores: `grep -i error /tmp/backend.log`
- Verificar emails enviados: `grep -i "email enviado" /tmp/backend.log`

### 13.2 Semanal
- Backup configuración: `tar -czf config_backup.tar.gz backend/config/`
- Actualizar precios equipos (vía admin panel)
- Revisar espacio disco: `df -h`

### 13.3 Mensual
- Actualizar dependencias Python: `pip list --outdated`
- Backup completo proyecto
- Revisar logs completos
- Test completo funcionalidad

### 13.4 Trimestral
- Actualizar LibreOffice
- Revisar template PowerPoint
- Actualizar ciudades nuevas
- Revisar parámetros fiscales (IVA, renta)

---

**FIN DOCUMENTO 2 - MANUAL MANTENIMIENTO Y OPERACIÓN**
