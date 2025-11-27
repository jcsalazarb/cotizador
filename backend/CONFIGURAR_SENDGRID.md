HAY# 📧 Configuración de SendGrid para NASSA Solar

## ✅ ¿Por qué SendGrid?

- **100 emails/día GRATIS** para siempre
- **No requiere contraseñas de aplicación** (usa API Key)
- **Más confiable** que Gmail SMTP para producción
- **Dashboards** con estadísticas de envíos
- **HTML emails** con mejor formato

---

## 🚀 Configuración Paso a Paso

### 1. Crear cuenta en SendGrid

1. Ve a: https://signup.sendgrid.com/
2. Completa el formulario:
   - Email: `nassasolarprecotizacion@gmail.com` (o el que prefieras)
   - Nombre: NASSA Solar
   - Empresa: NASSA Solar
3. **Verifica tu email** (importante)

### 2. Crear API Key

1. Una vez dentro de SendGrid, ve a: **Settings → API Keys**
   - O directamente: https://app.sendgrid.com/settings/api_keys

2. Haz clic en **"Create API Key"**

3. Configuración:
   - **Nombre**: "NASSA Solar Production"
   - **Permisos**: Selecciona **"Full Access"**
   - Haz clic en **"Create & View"**

4. **COPIA LA API KEY** inmediatamente (solo se muestra una vez)
   - Formato: `SG.xxxxxxxxxxxxx...` (empieza con SG.)
   - Guárdala en un lugar seguro

### 3. Verificar Sender Identity (Remitente)

**Importante**: SendGrid requiere que verifiques el email desde el que enviarás.

#### Opción A: Single Sender Verification (Recomendado para empezar)

1. Ve a: **Settings → Sender Authentication → Verify a Single Sender**
   - O: https://app.sendgrid.com/settings/sender_auth/senders

2. Completa el formulario:
   - **From Name**: NASSA Solar
   - **From Email Address**: `nassasolarprecotizacion@gmail.com`
   - **Reply To**: `nassasolarprecotizacion@gmail.com`
   - **Company Address**: Dirección de NASSA Solar
   - **Company City**: Tu ciudad
   - **Company Country**: Colombia

3. Haz clic en **"Create"**

4. **Verifica tu email**:
   - SendGrid enviará un email a `nassasolarprecotizacion@gmail.com`
   - Abre el email y haz clic en el enlace de verificación
   - ✅ El estado cambiará a "Verified"

#### Opción B: Domain Authentication (Más profesional)

Si tienes dominio propio (ej: @nassasolar.com):
1. Ve a: **Settings → Sender Authentication → Authenticate Your Domain**
2. Sigue las instrucciones para agregar registros DNS
3. Más info: https://docs.sendgrid.com/ui/account-and-settings/how-to-set-up-domain-authentication

### 4. Actualizar archivo .env

Edita `/Users/jcsalazarb/Documents/GitHub/cotizador/backend/.env`:

```bash
# SendGrid (Método preferido)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM=nassasolarprecotizacion@gmail.com
EMAIL_NASSA=jcsalazarb@icloud.com

# SMTP (Fallback - opcional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=nassasolarprecotizacion@gmail.com
SMTP_PASS=hihzyxagqdptwfed
```

**Importante**: 
- `EMAIL_FROM` debe ser el email que verificaste en SendGrid
- `SENDGRID_API_KEY` debe empezar con `SG.`

### 5. Reiniciar el backend

```bash
# Matar proceso actual
lsof -ti:8001 | xargs kill -9

# Reiniciar
cd /Users/jcsalazarb/Documents/GitHub/cotizador/backend
nohup /Users/jcsalazarb/Documents/GitHub/cotizador/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --reload > /tmp/backend.log 2>&1 &
```

### 6. Probar envío

Genera una cotización desde el frontend y verifica:

1. **Logs del backend**:
   ```bash
   tail -f /tmp/backend.log
   ```
   
   Deberías ver:
   ```
   ✅ Email enviado vía SendGrid a usuario@example.com
   ```

2. **Dashboard de SendGrid**:
   - Ve a: https://app.sendgrid.com/email_activity
   - Verás estadísticas de tus emails (enviados, abiertos, clicks, etc.)

3. **Bandeja de entrada**:
   - Verifica el email del cliente
   - Verifica el CC a `jcsalazarb@icloud.com`

---

## 🔄 Cómo funciona el Sistema Inteligente

El backend ahora tiene **3 funciones**:

1. **`enviar_email()`** - SMTP Gmail (método anterior)
2. **`enviar_email_sendgrid()`** - SendGrid API (nuevo)
3. **`enviar_email_inteligente()`** - Función principal que:
   - ✅ **Intenta SendGrid primero** (si `SENDGRID_API_KEY` existe)
   - ⚠️ Si falla, **usa SMTP como fallback**

**Ventaja**: Puedes tener ambos configurados y el sistema elegirá automáticamente el que funcione.

---

## 📊 Límites y Costos

### Plan Gratuito (Free Tier)
- **100 emails/día** = **3,000 emails/mes**
- Válido para siempre
- Sin tarjeta de crédito
- Suficiente para empezar

### Plan Essentials ($19.95/mes)
- **50,000 emails/mes**
- **40,000 contactos**
- Soporte por email

### Plan Pro ($89.95/mes)
- **100,000 emails/mes**
- Todos los features
- Soporte prioritario

**Recomendación**: Empieza con el plan gratuito. 100 emails/día son suficientes para ~3 cotizaciones diarias.

---

## 🐛 Troubleshooting

### Error: "Sender email must be verified"
**Solución**: Ve a Settings → Sender Authentication y verifica el email remitente.

### Error: "API Key not found" o "Unauthorized"
**Solución**:
1. Verifica que la API Key esté correcta en `.env`
2. Verifica que empiece con `SG.`
3. Crea una nueva API Key si es necesario

### Error: "The from address does not match a verified Sender Identity"
**Solución**: El email en `EMAIL_FROM` debe coincidir exactamente con el verificado en SendGrid.

### Emails no llegan
**Chequear**:
1. Dashboard de SendGrid: https://app.sendgrid.com/email_activity
2. Carpeta de Spam del destinatario
3. Logs del backend: `tail -f /tmp/backend.log`

### Backend sigue usando SMTP
**Solución**: Verifica que `SENDGRID_API_KEY` esté en `.env` y que reiniciaste el backend.

---

## 📧 Formato de Email

El nuevo sistema envía emails en **HTML** con mejor formato:

- ✅ Logo y colores de NASSA Solar
- ✅ Tabla con resumen de la cotización
- ✅ Diseño responsive (se ve bien en móvil)
- ✅ PDF adjunto
- ✅ CC automático a EMAIL_NASSA

---

## ✅ Checklist de Configuración

- [ ] Cuenta creada en SendGrid
- [ ] Email verificado en SendGrid
- [ ] API Key creada (empieza con SG.)
- [ ] Single Sender verificado (email remitente)
- [ ] `SENDGRID_API_KEY` agregada al `.env`
- [ ] `EMAIL_FROM` coincide con el verificado
- [ ] Backend reiniciado
- [ ] Email de prueba enviado exitosamente

---

## 📞 Soporte

- **SendGrid Docs**: https://docs.sendgrid.com/
- **SendGrid Support**: https://support.sendgrid.com/
- **SendGrid Status**: https://status.sendgrid.com/

---

**Creado para**: NASSA Solar  
**Fecha**: 24 de noviembre de 2025
