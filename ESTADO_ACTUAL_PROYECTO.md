# 📸 ESTADO ACTUAL DEL PROYECTO - SNAPSHOT PARA PRUEBAS
**Fecha**: 5 de diciembre de 2025, 10:35 (Colombia)  
**Commit actual**: f4f03e5 (compatibilidad formato ciudades.json)  
**Rama**: main  
**Ambiente de pruebas**: https://web-production-3749b.up.railway.app/

---

## 🎯 PROPÓSITO DE ESTE DOCUMENTO
Este archivo documenta el estado EXACTO del proyecto antes de iniciar pruebas con testers externos. Si necesitas reanudar el trabajo después de 12+ horas, **LEE ESTE ARCHIVO PRIMERO** para evitar modificar archivos incorrectos.

---

## 🚨 ÚLTIMO CAMBIO CRÍTICO (5 dic 2025, 10:30)

### Bug Solucionado: Admin Panel no cargaba ciudades
**Problema**: El panel de administración (admin.html) no podía cargar la lista de ciudades debido a incompatibilidad de formato en `ciudades.json`.

**Causa Raíz**:
- Backend esperaba: `{"ciudad": {"nombre": "X", "hsp": 5.2}}`
- JSON tenía: `{"ciudad": 5.2}`
- Admin.html intentaba leer `.nombre` y `.hsp` → `undefined`

**Solución Aplicada** (Opción B - Mantener nuevo formato):
1. ✅ Convertido `ciudades.json` al formato objeto completo
2. ✅ Agregado compatibilidad en frontend para ambos formatos
3. ✅ Creado backup del formato anterior (`ciudades_backup.json`)
4. ✅ Creado script de conversión (`convertir_ciudades.py`)

**Archivos Modificados**:
- `backend/config/ciudades.json` (160 ciudades → formato objeto)
- `backend/static/index.html` (compatibilidad líneas 290-301, 425-445)
- `backend/config/ciudades_backup.json` (NUEVO - backup formato antiguo)
- `backend/convertir_ciudades.py` (NUEVO - script conversión)

**Commit**: f4f03e5 - "Fix: Compatibilidad frontend con nuevo formato ciudades.json"

**Estado**: ✅ DESPLEGADO EN PRODUCCIÓN (Railway) - Verificado funcionando

---

## 📂 ESTRUCTURA DE ARCHIVOS CORRECTA

### ✅ ARCHIVOS ACTIVOS (NO TOCAR SIN RAZÓN)

#### Backend (Python FastAPI)
```
backend/server.py                    ← SERVIDOR PRINCIPAL (2254 líneas)
backend/requirements.txt             ← Dependencias Python
backend/.env                         ← Variables de entorno (NO en Git)
```

#### Frontend (HTML/CSS/JS)
```
backend/static/index.html            ← FRONTEND PRINCIPAL (1086 líneas)
backend/static/admin.html            ← Panel administrador
backend/static/styles.css            ← Estilos Tailwind
```

#### Configuración y Datos
```
backend/config/equipos.json          ← Catálogo equipos (TODOS tienen "default")
backend/config/ciudades.json         ← 160 ciudades (FORMATO OBJETO: {nombre, hsp})
backend/config/ciudades_backup.json  ← Backup formato antiguo (números directos)
backend/config/parametros.json       ← Configuración sistema
backend/datos/estadisticas.json      ← Tracking de cotizaciones
backend/convertir_ciudades.py        ← Script conversión formatos ciudades
```

#### Templates PowerPoint
```
Template/Template-PreCotizacion.pptx   ← Template principal (43 MB)
Template/Template-PreCotizacion2.pptx  ← Template alternativo (43 MB)
```

### ❌ ARCHIVOS OBSOLETOS (IGNORAR)
```
Index.html                           ← VIEJO - No usar
Index2.html                          ← Experimento - No usar
indexcanva.html                      ← Experimento - No usar
indexcanva2.html                     ← Experimento - No usar
index_Original.html                  ← Backup - No usar
index_Original_modificado.html       ← Backup - No usar
frontend/index frontend.html         ← Obsoleto - No usar
frontend/index_Canva_Original.html   ← Obsoleto - No usar
```

---

## 🔧 CAMBIOS RECIENTES IMPLEMENTADOS (Últimas 24 horas)

### Fix 1: Inversores Visibles en Carga Inicial
**Problema**: Inversores no aparecían hasta cambiar manualmente "Sistema Eléctrico"  
**Archivo**: `backend/static/index.html` (líneas 1037-1046)  
**Solución**: Cambió `cargarEquipos(null)` por `cargarEquipos(sistemaElectricoDefault)`  
**Estado**: ✅ Desplegado y funcionando  

### Fix 2: Campo "default" en Equipos
**Problema**: 20 equipos sin campo "default" en equipos.json  
**Archivo**: `backend/config/equipos.json`  
**Solución**: Agregado `"default": false` a 6 paneles, 8 inversores, 6 baterías  
**Estado**: ✅ Todos los 23 equipos tienen el campo  

### Fix 3: Algoritmo Inteligente de Defaults
**Problema**: Lógica de fallback deficiente  
**Archivo**: `backend/server.py` (líneas 158-226, función `obtener_equipos_defaults`)  
**Solución**: Algoritmo de 4 niveles de prioridad  
**Estado**: ✅ Implementado con warnings en logs  

### Fix 4: Templates PowerPoint Actualizados
**Problema**: Templates desactualizados en repositorio  
**Archivos**: `Template/Template-PreCotizacion.pptx`, `Template/Template-PreCotizacion2.pptx`  
**Solución**: Subidos templates de 43 MB cada uno  
**Estado**: ✅ Commit e07c429  

### Fix 5: Formato Ciudades.json - Admin Panel
**Problema**: Admin panel no cargaba ciudades (incompatibilidad formato)  
**Archivos**: `backend/config/ciudades.json`, `backend/static/index.html`  
**Solución**: Convertido a formato objeto `{nombre, hsp}` + compatibilidad frontend  
**Estado**: ✅ Commit f4f03e5 - DESPLEGADO EN PRODUCCIÓN  

---

## 📋 FORMATO ACTUAL DE DATOS

### Ciudades (`ciudades.json`)
**Formato NUEVO** (desde 5 dic 2025):
```json
{
  "santa_marta": {
    "nombre": "Santa Marta",
    "hsp": 5.6
  },
  "default": {
    "hsp": 4.5
  }
}
```

**Backup formato antiguo**: Guardado en `ciudades_backup.json`

**Compatibilidad**: Frontend maneja ambos formatos automáticamente:
- Si encuentra `.nombre` → lo usa
- Si encuentra `.hsp` → lo usa
- Si solo encuentra número → lo usa como HSP directo

---

## 📊 ESTADO DE EQUIPOS DEFAULT

### Paneles Solares (7 total)
```
panel1: default=true  ← JA Solar JAM72S30 550W (Default activo)
panel2: default=false ← Jinko Tiger Neo 580W
panel3: default=false ← Longi Hi-MO 6 575W
panel5: default=false ← Canadian Solar HiKu7 590W
panel6: default=false ← Trina Solar Vertex S+ 585W
panel7: default=false ← Risen Energy Titan 595W
panel8: default=false ← Phono Solar PS-M6 560W
```

### Inversores (9 total)
```
inv1: default=true, tipo_sistema="monofasico"   ← Growatt MIC 3000TL-X (Default monofásico)
inv2: default=false, tipo_sistema="bifasico"    ← Growatt MIN 3600TL-XH
inv3: default=false, tipo_sistema="trifasico"   ← Growatt MAX 60KTL3-X LV
inv4: default=false, tipo_sistema="monofasico"  ← Solis 3.6kW
inv5: default=false, tipo_sistema="bifasico"    ← Solis 5kW
inv6: default=false, tipo_sistema="monofasico"  ← Huawei SUN2000-3KTL-L1
inv7: default=false, tipo_sistema="monofasico"  ← Fronius Primo 3.0-1
inv8: default=false, tipo_sistema="trifasico"   ← SMA Sunny Tripower 5.0
inv9: default=false, tipo_sistema="bifasico"    ← Goodwe GW4200-XS
```

### Baterías (7 total)
```
bat1: default=true  ← BYD Battery-Box Premium LVS 8.0 (Default activo)
bat2: default=false ← Pylontech US3000C 3.5kWh
bat3: default=false ← Huawei LUNA2000-5kWh
bat4: default=false ← LG Chem RESU10H 9.8kWh
bat5: default=false ← Tesla Powerwall 2 13.5kWh
bat6: default=false ← Sonnen Batterie eco 8 8kWh
bat7: default=false ← Enphase Encharge 10T 10.5kWh
```

**⚠️ IMPORTANTE**: Los sistemas bifásico y trifásico NO tienen inversores con `default=true`. El algoritmo usa **NIVEL 2** (primer compatible disponible) para estos sistemas.

---

## 🚀 HISTORIAL DE COMMITS (Últimos 4)

```bash
e07c429 (HEAD -> main) - chore: Update PowerPoint templates (4 dic, 17:20)
0580fa5 - debug: Add equipos-file endpoint for troubleshooting (4 dic, 15:45)
470c8c0 - chore: Trigger Railway redeploy (4 dic, 15:30)
4647bb8 - fix: Load inversores on page load + add default field (4 dic, 14:20)
```

**Comando para ver historial completo**:
```bash
git log --oneline --graph --all -20
```

---

## 🔍 ENDPOINTS DE DIAGNÓSTICO

### Endpoint de Salud
```bash
curl https://web-production-3749b.up.railway.app/health
```
**Respuesta esperada**: `{"status": "ok", "timestamp": "..."}`

### Endpoint de Debug (TEMPORAL)
```bash
curl https://web-production-3749b.up.railway.app/debug/equipos-file
```
**Respuesta esperada**:
```json
{
  "file_hash": "164341ab",
  "paneles": {"total": 7, "con_campo_default": 7},
  "inversores": {"total": 9, "con_campo_default": 9},
  "baterias": {"total": 7, "con_campo_default": 7}
}
```

### Endpoint Público de Equipos
```bash
curl https://web-production-3749b.up.railway.app/api/equipos
```
**⚠️ NOTA**: Este endpoint NO devuelve el campo "default" (filtrado por seguridad). Es comportamiento correcto.

---

## 📝 CHECKLIST DE PRUEBAS PARA TESTERS

### Prueba 1: Inversores Visibles en Carga Inicial ✅
1. Abrir https://web-production-3749b.up.railway.app/
2. **SIN TOCAR NADA**, verificar que el select "Inversores" muestra 3 opciones
3. Sistema por defecto debe ser "Bifásico"
4. **Resultado esperado**: Ver inversores inmediatamente

### Prueba 2: Cambio de Sistema Eléctrico ✅
1. Cambiar "Sistema Eléctrico" a "Monofásico"
2. **Resultado esperado**: Select de inversores se actualiza con inversores monofásicos
3. Cambiar a "Trifásico"
4. **Resultado esperado**: Select se actualiza con inversores trifásicos

### Prueba 3: HSP por Ciudad ✅
1. Seleccionar ciudad "Santa Marta"
2. **Resultado esperado**: HSP = 5.6 (visible en campo o usado en cálculos)
3. Seleccionar ciudad "Bogotá"
4. **Resultado esperado**: HSP = 4.5

### Prueba 4: Generación de Cotización 📧
1. Llenar formulario completo:
   - Nombre: "Juan Pérez"
   - Email: "juan@example.com"
   - Consumo: 500 kWh/mes
   - Ciudad: Santa Marta
   - Sistema: Bifásico
   - Tipo: On-Grid
2. Enviar cotización
3. **Resultado esperado**: 
   - Mensaje "Cotización enviada exitosamente"
   - Email recibido con PDF adjunto
   - PowerPoint adjunto (opcional)

### Prueba 5: Panel de Administración 🔐
1. Abrir https://web-production-3749b.up.railway.app/admin.html
2. Login: `admin` / `changeme` (o credenciales del .env)
3. Verificar que se muestran precios de equipos
4. **Resultado esperado**: Tabla con precios visibles (NO en API pública)

---

## 🛠️ COMANDOS PARA RETOMAR TRABAJO

### 1. Verificar Estado del Repositorio
```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador
git status
git log --oneline -5
```

### 2. Verificar Archivos Correctos
```bash
# Frontend correcto (1086 líneas)
wc -l backend/static/index.html

# Backend correcto (2254 líneas)
wc -l backend/server.py

# Equipos con defaults (debe mostrar 23 "default")
grep -c '"default"' backend/config/equipos.json
```

### 3. Verificar Commit Actual
```bash
git log -1 --pretty=format:"%H %s"
# Esperado: e07c429... chore: Update PowerPoint templates
```

### 4. Ver Cambios Locales (si los hay)
```bash
git diff backend/static/index.html
git diff backend/server.py
git diff backend/config/equipos.json
```

---

## 🚨 PROBLEMAS CONOCIDOS Y SOLUCIONES

### Problema: "Railway no despliega cambios"
**Causa**: Confusión - el endpoint `/api/equipos` filtra "default" por diseño de seguridad  
**Solución**: Usar `/debug/equipos-file` para verificar el archivo real  
**Estado**: Resuelto - Railway SÍ está desplegado correctamente  

### Problema: "Inversores no aparecen"
**Causa**: Era un bug - llamada a `cargarEquipos(null)`  
**Solución**: Ya corregido en commit 4647bb8  
**Estado**: ✅ Funcionando  

### Problema: "KeyError: 'default'"
**Causa**: 20 equipos sin campo "default"  
**Solución**: Ya agregado a todos en commit 4647bb8  
**Estado**: ✅ Corregido  

### Problema: "Templates desactualizados"
**Causa**: Modificaciones locales no subidas a GitHub  
**Solución**: Subidos en commit e07c429 (43 MB cada uno)  
**Estado**: ✅ Actualizados  

---

## 📞 INFORMACIÓN DE CONTACTO Y DESPLIEGUE

### Railway
- **URL**: https://web-production-3749b.up.railway.app/
- **Auto-deploy**: Activado desde branch `main`
- **Tiempo de deploy**: 1-2 minutos después de push
- **Logs**: Accesibles desde Railway dashboard

### GitHub
- **Repositorio**: https://github.com/jcsalazarb/cotizador
- **Branch**: main
- **Último commit**: e07c429 (4 dic, 17:20)

### Entorno Local
- **Backend**: Puerto 8001 (uvicorn con --reload)
- **Frontend**: Puerto 8000 (python -m http.server)
- **Comando backend**:
  ```bash
  cd backend && source venv/bin/activate && uvicorn server:app --host 0.0.0.0 --port 8001 --reload
  ```
- **Comando frontend**:
  ```bash
  cd /Users/jcsalazarb/Documents/GitHub/cotizador && python3 -m http.server 8000
  ```

---

## 🎓 INSTRUCCIONES PARA CLAUDE (REANUDAR TRABAJO)

### Si necesitas modificar código después de las pruebas:

1. **PRIMERO**: Lee este archivo completo (`ESTADO_ACTUAL_PROYECTO.md`)
2. **SEGUNDO**: Verifica el commit actual con `git log -1`
3. **TERCERO**: Confirma que estás editando los archivos correctos:
   - ✅ Frontend: `backend/static/index.html`
   - ✅ Backend: `backend/server.py`
   - ✅ Equipos: `backend/config/equipos.json`
   - ❌ NO: `Index.html` (raíz)
   - ❌ NO: `frontend/index frontend.html`

4. **CUARTO**: Si hay reportes de bugs de los testers:
   - Lee el contexto de los fixes recientes en `RESUMEN_FIXES.md`
   - Lee la guía de administración en `ADMIN_GUIDE_DEFAULTS.md`
   - Verifica que el bug no esté ya corregido

5. **QUINTO**: Antes de hacer cambios, ejecuta:
   ```bash
   # Ver si hay cambios sin commitear
   git status
   
   # Ver últimos commits
   git log --oneline -10
   
   # Verificar archivos correctos
   ls -lh backend/static/index.html backend/server.py backend/config/equipos.json backend/config/ciudades.json
   ```

6. **SEXTO**: Después de hacer cambios:
   - Prueba localmente primero
   - Commit con mensaje descriptivo
   - Push a main (Railway auto-deploya)
   - Espera 2 minutos y verifica `/health`

---

## 📚 DOCUMENTACIÓN RELACIONADA

- `RESUMEN_FIXES.md` - Resumen ejecutivo de los fixes implementados
- `ADMIN_GUIDE_DEFAULTS.md` - Guía para administradores sobre defaults
- `TESTING_FIXES.md` - Plan de pruebas detallado
- `SOLUCION_INVERSORES_DEFAULTS.md` - Documentación técnica de la solución
- `.github/copilot-instructions.md` - Instrucciones para agentes AI

---

## ✅ VALIDACIÓN DE ESTADO

**Últimos commits**:
```
f4f03e5 - Fix: Compatibilidad frontend con nuevo formato ciudades.json (5 dic 2025, 10:30)
e07c429 - Feature: Templates actualizados (4 dic 2025, 17:20)
```

**Hash de archivos críticos** (para verificar integridad):
```bash
# Ejecutar en terminal para validar
md5 backend/config/equipos.json
# Esperado: 164341ab (primeros 8 caracteres)

wc -l backend/static/index.html
# Esperado: 1089 líneas (aumentó por código compatibilidad)

wc -l backend/server.py
# Esperado: 2254 líneas

# NUEVO: Verificar formato ciudades
head -5 backend/config/ciudades.json
# Debe mostrar formato objeto: {"ciudad": {"nombre": "X", "hsp": Y}}
```

**Verificación en Producción**:
```bash
# Health check
curl https://web-production-3749b.up.railway.app/health

# Verificar formato ciudades
curl https://web-production-3749b.up.railway.app/api/ciudades | head -20
# Debe mostrar formato objeto
```

**Último cambio válido**: 5 de diciembre de 2025, 10:30 (commit f4f03e5)

---

## 🔐 SEGURIDAD Y PRIVACIDAD

- **Precios**: Solo visibles en `/api/equipos/precios` (requiere Basic Auth)
- **Admin**: Usuario/contraseña en archivo `.env` (NO en Git)
- **SMTP**: Credenciales en `.env` (NO en Git)
- **Endpoint público** (`/api/equipos`): **NO** devuelve precios ni campo "default"
- **Endpoint debug** (`/debug/equipos-file`): Temporal, eliminar en producción final

---

**🎯 OBJETIVO DE ESTE DOCUMENTO**: Garantizar continuidad del proyecto después de interrupciones largas (12+ horas) sin perder contexto ni modificar archivos incorrectos.

**📅 ÚLTIMA ACTUALIZACIÓN**: 5 de diciembre de 2025, 10:35 - Agregado Fix #5 (formato ciudades)

**📅 PRÓXIMA REVISIÓN**: Después de completar pruebas con testers.
