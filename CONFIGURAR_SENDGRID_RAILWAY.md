# 🚀 Configurar SendGrid en Railway - PASO A PASO

## ❗ PROBLEMA ACTUAL

Los correos **NO están llegando** aunque el sistema dice "enviado exitosamente".

**Causa**: Railway bloquea puertos SMTP (465, 587) → Los intentos de envío generan timeout pero el código no lo detecta correctamente.

## ✅ SOLUCIÓN: Usar SendGrid API

SendGrid funciona porque usa **API REST** (no puertos SMTP bloqueados).

---

## 📋 PASO 1: Obtener API Key de SendGrid

### 1.1 Acceder a SendGrid Dashboard
```
URL: https://app.sendgrid.com/
```

1. Inicia sesión con tu cuenta de SendGrid
2. Si no tienes cuenta, crea una gratis en https://signup.sendgrid.com/

### 1.2 Crear API Key

1. En el menú lateral izquierdo, ve a **Settings** → **API Keys**
   
   URL directa: https://app.sendgrid.com/settings/api_keys

2. Click en botón **"Create API Key"** (arriba a la derecha)

3. Configuración de la API Key:
   ```
   Nombre: Railway NASSA Solar Production
   
   Permisos: 
   ✅ Full Access (recomendado)
   
   O si prefieres permisos limitados:
   ✅ Mail Send - Full Access
   ✅ Mail Settings - Read Access (opcional)
   ```

4. Click **"Create & View"**

5. **⚠️ IMPORTANTE**: Copia la API Key inmediatamente
   ```
   Formato: SG.xxxxxxxxxxxxxxxxxxxx.yyyyyyyyyyyyyyyyyyyy
   ```
   
   **⚠️ Solo se muestra UNA VEZ** - Guárdala en lugar seguro

---

## 📋 PASO 2: Verificar Dominio en SendGrid (Si no está verificado)

### Estado Actual del DNS
Según diagnóstico previo, **todos los registros DNS están correctos**:

```
✅ url9576.nassasolar.com → sendgrid.net
✅ 57594379.nassasolar.com → sendgrid.net  
✅ em3280.nassasolar.com → u57594379.wl130.sendgrid.net
✅ s1._clavededominio.nassasolar.com → s1.domainkey.u57594379.wl130.sendgrid.net
✅ s2._clavededominio.nassasolar.com → s2.domainkey.u57594379.wl130.sendgrid.net
✅ _dmarc.nassasolar.com → v=DMARC1; p=rechazar;
```

### 2.1 Verificar Dominio

1. Ve a **Settings** → **Sender Authentication**
   
   URL: https://app.sendgrid.com/settings/sender_auth

2. Encuentra `nassasolar.com` en la lista

3. Click en **"Verify"**

4. **Si el botón no funciona** (problema conocido):
   
   **Opción A**: Esperar 24-48 horas (propagación DNS)
   
   **Opción B**: Intentar en navegador incógnito/privado
   
   **Opción C**: Contactar soporte SendGrid con screenshots del DNS

5. **Alternativa temporal**: Usar **Single Sender Verification**
   ```
   Settings → Sender Authentication → Single Sender Verification
   
   Email: comercial@nassasolar.com
   
   SendGrid enviará email de confirmación → Click en link
   ```

---

## 📋 PASO 3: Configurar Variables en Railway

### 3.1 Acceder a Railway Dashboard

```
URL: https://railway.app/
Proyecto: cotizador (web-production-3749b)
```

1. Selecciona tu proyecto "cotizador"
2. Click en el servicio "web-production-3749b"
3. Ve a la pestaña **"Variables"**

### 3.2 Agregar Variables de Entorno

Click en **"+ New Variable"** y agrega las siguientes (una por una):

#### Variable 1: SENDGRID_API_KEY
```
Key:   SENDGRID_API_KEY
Value: SG.xxxxxxxxxxxxxxxxxxxx.yyyyyyyyyyyyyyyyyyyy
       (pegar la API Key de SendGrid)
```

#### Variable 2: EMAIL_FROM
```
Key:   EMAIL_FROM
Value: comercial@nassasolar.com
```

#### Variable 3: EMAIL_NASSA (opcional - CC)
```
Key:   EMAIL_NASSA
Value: comercial@nassasolar.com
```

#### Variable 4: Verificar EMAIL_NASSA no esté duplicada
Si ya existe EMAIL_NASSA con otro valor, **actualízala** a:
```
comercial@nassasolar.com
```

### 3.3 Guardar y Esperar Redespliegue

- Railway **redesplegará automáticamente** al agregar variables
- Espera 2-3 minutos
- Verifica que el estado sea **"Deployed"**

---

## 📋 PASO 4: Probar Envío de Email

### 4.1 Generar Cotización de Prueba

1. Ve a: https://web-production-3749b.up.railway.app/

2. Llena el formulario con:
   ```
   Email: TU_EMAIL_REAL@gmail.com (usa tu email para recibir prueba)
   Nombre: Prueba SendGrid
   Otros campos: Datos válidos de prueba
   ```

3. Genera cotización

### 4.2 Verificar Logs en Railway

1. En Railway Dashboard, ve a la pestaña **"Deployments"**
2. Click en el deployment más reciente
3. Ve a **"View Logs"**
4. Busca:
   ```
   ✅ Email enviado exitosamente via SendGrid a TU_EMAIL@gmail.com
   ```

### 4.3 Revisar Email

1. Revisa tu bandeja de entrada
2. **Si no aparece**, revisa carpeta **"Spam/Correo no deseado"**
3. El email debe tener:
   - ✅ Header y Footer anaranjados
   - ✅ Resumen de cotización
   - ✅ PDF(s) adjunto(s)
   - ✅ Botón de WhatsApp

---

## 🔍 TROUBLESHOOTING

### Problema 1: "SENDGRID_API_KEY no configurada"

**Logs muestran**:
```
❌ SENDGRID_API_KEY no configurada en variables de entorno
⚠️ SendGrid no configurado, usando SMTP como fallback
```

**Solución**: Verifica que la variable esté en Railway y escrita exactamente como:
```
SENDGRID_API_KEY
```
(sin espacios, respetando mayúsculas)

### Problema 2: Email no llega (SendGrid configurado)

**Posibles causas**:

1. **Dominio no verificado en SendGrid**
   - Ve a Sender Authentication
   - Verifica estado del dominio
   - Usa Single Sender como alternativa temporal

2. **Email en Spam**
   - Revisa carpeta de spam/correo no deseado
   - Marca como "No es spam"

3. **API Key sin permisos**
   - Ve a SendGrid → API Keys
   - Verifica que tenga "Mail Send - Full Access"

4. **Límite de SendGrid alcanzado**
   - Cuenta Free: 100 emails/día
   - Ve a Dashboard → Usage para verificar

### Problema 3: Error "Invalid API Key"

**Logs muestran**:
```
❌ Error SENDGRID: HTTP Error 401: UNAUTHORIZED
```

**Solución**:
1. La API Key puede estar mal copiada
2. Genera una nueva API Key en SendGrid
3. Actualiza SENDGRID_API_KEY en Railway
4. Railway redesplegará automáticamente

### Problema 4: Timeout en Railway Logs

**Logs muestran**:
```
⚠️ Timeout (15s) conectando a mail.privateemail.com:587
```

**Causa**: SendGrid no está configurado, el sistema está usando SMTP como fallback

**Solución**: Completar PASO 3 (configurar SENDGRID_API_KEY)

---

## ✅ VERIFICACIÓN FINAL

### Checklist de Configuración Correcta

- [ ] API Key creada en SendGrid
- [ ] API Key agregada a Railway como `SENDGRID_API_KEY`
- [ ] `EMAIL_FROM=comercial@nassasolar.com` en Railway
- [ ] Railway redesplegado (status "Deployed")
- [ ] Dominio verificado en SendGrid (o Single Sender configurado)
- [ ] Cotización de prueba generada
- [ ] Email recibido con header/footer anaranjados
- [ ] PDF adjunto abierto correctamente

### Variables Finales en Railway

```bash
# SendGrid
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxx.yyyyyyyyyyyyyyyyyyyy
EMAIL_FROM=comercial@nassasolar.com
EMAIL_NASSA=comercial@nassasolar.com

# PostgreSQL (ya configuradas)
DATABASE_URL=postgresql://postgres:...
POSTGRES_HOST=postgres.railway.internal
POSTGRES_PORT=5432
POSTGRES_DB=railway
POSTGRES_USER=postgres
POSTGRES_PASSWORD=MGWnPMjdsaRqjqrXENndaLMeDWuEEbKn

# SMTP (opcional - solo para desarrollo local)
SMTP_HOST=mail.privateemail.com
SMTP_PORT=587
SMTP_USER=nassasolarprecotizacion@gmail.com
SMTP_PASS=(tu contraseña)

# Otros
ADMIN_USER=admin
ADMIN_PASS=(tu contraseña)
ALLOWED_ORIGINS=*
RATE_LIMIT=10
```

---

## 📧 Contacto de Soporte

**Si persisten problemas**:

1. **SendGrid Support**: https://support.sendgrid.com/
2. **Railway Support**: https://help.railway.app/
3. **Logs detallados**: Railway Dashboard → Deployments → View Logs

---

## 🎉 Resultado Esperado

Después de completar todos los pasos:

1. ✅ Usuario genera cotización
2. ✅ Sistema muestra "Cotización generada y email enviado exitosamente"
3. ✅ Cliente recibe email en 10-30 segundos
4. ✅ Email tiene diseño profesional (anaranjado)
5. ✅ PDF(s) adjunto(s) correctamente
6. ✅ NO hay errores en logs de Railway

---

**Fecha**: 12 de diciembre de 2025  
**Proyecto**: NASSA Solar - Sistema de Cotización  
**Versión**: v2.0 con PostgreSQL + SendGrid
