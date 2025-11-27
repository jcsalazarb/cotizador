# Guía de Despliegue en Railway.app

## 📋 Requisitos Previos

- ✅ Cuenta de GitHub con repositorio `cotizador`
- ✅ Dominio `nassasolar.com` configurado en Namecheap
- ✅ Correo `comercial@nassasolar.com` activo

## 🚀 Paso 1: Preparar el Repositorio

### 1.1 Verificar archivos de configuración

Asegúrate de tener estos archivos en la raíz del proyecto:

```bash
cotizador/
├── railway.json          # ✅ Configuración de Railway
├── Procfile             # ✅ Definición de proceso
├── nixpacks.toml        # ✅ Instalación de LibreOffice
├── .env.example         # ✅ Plantilla de variables
├── .gitignore          # ✅ Archivos a ignorar
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   ├── .env            # ⚠️ NO subir a Git
│   └── ...
└── Template/
    └── Template-PreCotizacion.pptx
```

### 1.2 Hacer commit y push

```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador

# Verificar estado
git status

# Agregar archivos nuevos
git add railway.json Procfile nixpacks.toml .gitignore .env.example

# Commit
git commit -m "Configuración para despliegue en Railway"

# Push al repositorio
git push origin main
```

## 🎯 Paso 2: Crear Cuenta en Railway

### 2.1 Registro
1. Ve a: https://railway.app
2. Clic en **"Login"** o **"Start a New Project"**
3. Selecciona **"Login with GitHub"**
4. Autoriza Railway para acceder a tus repositorios

### 2.2 Conectar Repositorio
1. En el dashboard, clic en **"New Project"**
2. Selecciona **"Deploy from GitHub repo"**
3. Busca y selecciona: **`jcsalazarb/cotizador`**
4. Railway detectará automáticamente los archivos de configuración

## ⚙️ Paso 3: Configurar Variables de Entorno

### 3.1 En el Dashboard de Railway

1. Selecciona tu proyecto desplegado
2. Ve a la pestaña **"Variables"**
3. Agrega las siguientes variables (una por una):

```bash
SMTP_HOST=mail.privateemail.com
SMTP_PORT=587
SMTP_USER=comercial@nassasolar.com
SMTP_PASS=Lu1sF3rN@ss@
EMAIL_FROM=comercial@nassasolar.com
EMAIL_NASSA=nassasolar.comercial@outlook.com
EMAIL_SUBJECT=PreCotización Nassa Solar
ADMIN_USER=admin
ADMIN_PASS=Lu1sF3rN@ss@
ALLOWED_ORIGINS=*
LIBREOFFICE_PATH=soffice
RATE_LIMIT=10
```

⚠️ **IMPORTANTE**: 
- No uses comillas en los valores
- Railway genera automáticamente `PORT` (no la configures)
- `ALLOWED_ORIGINS=*` permite todos los orígenes (temporal)

### 3.2 Variables Generadas Automáticamente

Railway genera estas variables automáticamente:
- `PORT` - Puerto asignado (variable)
- `RAILWAY_STATIC_URL` - URL pública de tu app

## 🌐 Paso 4: Obtener URL de Railway

Después del despliegue:

1. Ve a **"Settings"** → **"Domains"**
2. Railway te asigna una URL como: `cotizador-production.up.railway.app`
3. **Copia esta URL** - la necesitarás para DNS

## 🔧 Paso 5: Configurar DNS en Namecheap

### 5.1 Configurar Subdominio

1. Inicia sesión en **Namecheap**
2. Ve a **Domain List** → Clic en **nassasolar.com**
3. Pestaña **"Advanced DNS"**
4. Agrega un registro CNAME:

```
Type: CNAME Record
Host: cotizador (o @ para usar nassasolar.com directamente)
Value: cotizador-production.up.railway.app
TTL: Automatic
```

### 5.2 Configurar Dominio Personalizado en Railway

1. En Railway, ve a **"Settings"** → **"Domains"**
2. Clic en **"Custom Domain"**
3. Ingresa: `cotizador.nassasolar.com` (o `nassasolar.com`)
4. Railway te dará instrucciones de verificación
5. Espera propagación DNS (5-30 minutos)

## ✅ Paso 6: Verificar Despliegue

### 6.1 Revisar Logs

En Railway:
1. Ve a la pestaña **"Deployments"**
2. Clic en el despliegue activo
3. Ve a **"View Logs"**
4. Verifica que no haya errores

Deberías ver:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:XXXX
```

### 6.2 Probar Endpoints

Una vez desplegado, prueba:

```bash
# Health check
curl https://cotizador-production.up.railway.app/health

# API de ciudades
curl https://cotizador-production.up.railway.app/api/ciudades

# API de equipos
curl https://cotizador-production.up.railway.app/api/equipos
```

### 6.3 Probar Frontend

1. Abre tu navegador en: `https://cotizador-production.up.railway.app/`
2. Deberías ver el formulario de cotización
3. Prueba generar una cotización completa

## 🔐 Paso 7: Actualizar CORS

Una vez que tengas el dominio funcionando:

1. Ve a **"Variables"** en Railway
2. Actualiza `ALLOWED_ORIGINS`:

```bash
ALLOWED_ORIGINS=https://cotizador.nassasolar.com,https://nassasolar.com
```

3. Railway reiniciará automáticamente

## 📊 Paso 8: Monitoreo

### Uso de Recursos

Railway **Plan Gratuito**:
- $5 USD de crédito/mes
- ~500 horas de ejecución
- Suficiente para 10-20 cotizaciones/día

### Ver Métricas

En Railway:
1. Pestaña **"Metrics"**
2. Monitorea: CPU, RAM, Network
3. Revisa costos en **"Usage"**

## 🚨 Solución de Problemas

### Error: "Build failed"

**Causa**: Falta `requirements.txt` o error en `nixpacks.toml`

**Solución**:
```bash
# Verificar que requirements.txt tenga todas las dependencias
cd backend
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Actualizar requirements.txt"
git push
```

### Error: "Application failed to respond"

**Causa**: Puerto incorrecto o falta variable de entorno

**Solución**:
1. Verifica que `server.py` use `os.getenv('PORT', 8001)`
2. Verifica que todas las variables estén configuradas

### Error: "LibreOffice not found"

**Causa**: `nixpacks.toml` no instaló LibreOffice correctamente

**Solución**: Verifica que `nixpacks.toml` tenga:
```toml
[phases.setup]
nixPkgs = ["python39", "libreoffice"]
```

### Error: "Email sending failed"

**Causa**: Variables SMTP incorrectas

**Solución**:
1. Verifica credenciales de Namecheap
2. Revisa logs: `"View Logs"` en Railway
3. Prueba correo local primero

## 📝 Comandos Útiles

### Ver logs en tiempo real
En Railway, ve a **"View Logs"** y selecciona **"Live"**

### Forzar redespliegue
1. Ve a **"Deployments"**
2. Clic en **"Redeploy"**

### Rollback a versión anterior
1. Ve a **"Deployments"**
2. Selecciona despliegue anterior
3. Clic en **"Redeploy"**

## 🔄 Actualizar la Aplicación

Cada vez que hagas cambios:

```bash
# Hacer cambios en tu código
# ...

# Commit y push
git add .
git commit -m "Descripción del cambio"
git push origin main

# Railway desplegará automáticamente
```

## 📞 Siguiente Paso: Página Principal

Una vez funcionando el cotizador, necesitarás:

1. **Crear página principal** en `nassasolar.com`
2. **Enlazar cotizador** desde la página principal
3. **Configurar SSL** (Railway lo hace automático)

## 💰 Costos Estimados

### Mes 1-3 (Gratis)
- Railway: $0 (crédito gratuito)
- Namecheap dominio: $9/año (~$0.75/mes)
- Namecheap email: $1.99/mes
- **Total: ~$2.74 USD/mes**

### Después del período gratuito
- Railway puede cobrar ~$5-10/mes según uso
- O migrar a Contabo VPS: €4.99/mes

## ✅ Checklist Final

- [ ] Archivos de configuración creados
- [ ] Repositorio actualizado en GitHub
- [ ] Cuenta Railway creada y conectada
- [ ] Variables de entorno configuradas
- [ ] Despliegue exitoso (logs sin errores)
- [ ] DNS configurado en Namecheap
- [ ] Dominio personalizado funcionando
- [ ] Prueba de cotización completa (PDF+email)
- [ ] CORS actualizado con dominio real

## 🎉 ¡Listo!

Tu sistema de cotizaciones está en producción y accesible desde internet.

**URL de acceso**: `https://cotizador.nassasolar.com` (o la que configuraste)

---

**Soporte**: Si tienes problemas, revisa los logs en Railway o consulta la documentación: https://docs.railway.app
