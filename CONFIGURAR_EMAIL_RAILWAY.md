# 📧 Configurar Email en Railway - Solución Definitiva

## 🔴 Problema Actual
Railway **bloquea los puertos 465 y 587** (SMTP tradicional), por eso Namecheap no funciona.

## ✅ Solución: Usar Gmail o SendGrid

---

## 🟢 OPCIÓN 1: Gmail (Recomendado - Más Fácil)

### Ventajas:
- ✅ Funciona en Railway (puerto 587 de Gmail suele estar permitido)
- ✅ 500 emails/día gratis
- ✅ Configuración rápida (5 minutos)
- ✅ No requiere tarjeta de crédito

### Pasos:

#### 1. Crear Contraseña de Aplicación en Gmail

1. Ve a https://myaccount.google.com/
2. Click en "Seguridad" (Security)
3. Activa "Verificación en dos pasos" si no está activa
4. Busca "Contraseñas de aplicaciones" (App passwords)
5. Selecciona:
   - App: **Correo** (Mail)
   - Dispositivo: **Otro** (Other) → Escribe: "NASSA Solar Railway"
6. Click "Generar"
7. **COPIA LA CONTRASEÑA** (16 caracteres sin espacios)

#### 2. Configurar Variables en Railway

Ve a tu proyecto en Railway → Variables → Add Variables:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASS=xxxx xxxx xxxx xxxx    # Pega la contraseña de aplicación (16 caracteres)
EMAIL_FROM=tu_email@gmail.com
EMAIL_NASSA=nassasolar.comercial@outlook.com
EMAIL_SUBJECT=Cotización Sistema Solar Fotovoltaico - NASSA Solar
```

**IMPORTANTE:** Reemplaza:
- `tu_email@gmail.com` con tu Gmail real
- `xxxx xxxx xxxx xxxx` con la contraseña de aplicación que copiaste

#### 3. Guardar y Esperar Redeploy

Railway redesplegará automáticamente (~2 minutos). Después, prueba enviar una cotización.

---

## 🟦 OPCIÓN 2: SendGrid (Alternativa Profesional)

### Ventajas:
- ✅ 100 emails/día gratis (sin tarjeta de crédito)
- ✅ No usa puertos SMTP (API REST)
- ✅ Tracking de emails (aperturas, clicks)
- ✅ Mejor deliverability

### Pasos:

#### 1. Crear Cuenta SendGrid

1. Ve a https://signup.sendgrid.com/
2. Completa el formulario:
   - Email: tu email real
   - Password: (crea una contraseña segura)
3. Verifica tu email
4. Login en https://app.sendgrid.com/

#### 2. Generar API Key

1. Ve a Settings → API Keys
2. Click "Create API Key"
3. Nombre: `NASSA Solar Production`
4. Permisos: **Full Access** (o mínimo "Mail Send")
5. Click "Create & View"
6. **COPIA LA API KEY** (empieza con `SG.`)
7. Guárdala en un lugar seguro (no la volverás a ver)

#### 3. Verificar Sender Identity

1. Ve a Settings → Sender Authentication
2. Click "Verify a Single Sender"
3. Completa:
   - From Name: `NASSA Solar`
   - From Email: `tu_email@gmail.com` (o el que uses)
   - Reply To: `comercial@nassasolar.com`
   - Dirección: (tu dirección real)
4. Click "Create"
5. Revisa tu email y verifica el sender

#### 4. Configurar Variables en Railway

Ve a Railway → Variables → Add Variables:

```bash
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM=tu_email@gmail.com    # El email verificado en paso 3
EMAIL_NASSA=nassasolar.comercial@outlook.com
EMAIL_SUBJECT=Cotización Sistema Solar Fotovoltaico - NASSA Solar
```

**IMPORTANTE:** 
- Usa el email EXACTO que verificaste en SendGrid
- El sistema automáticamente usará SendGrid si `SENDGRID_API_KEY` existe

#### 5. Guardar y Esperar Redeploy

Railway redesplegará automáticamente (~2 minutos).

---

## 🧪 Probar la Configuración

### Desde Railway:

1. Espera que termine el redeploy
2. Ve a https://web-production-3749b.up.railway.app/
3. Llena el formulario de cotización
4. Usa tu email personal para recibir la prueba
5. Click "Generar Cotización"

### Verificar Logs:

1. Railway Dashboard → Tu proyecto → Deployments
2. Click en el último deployment → View Logs
3. Busca mensajes como:
   - `✅ Email enviado via puerto 587 (STARTTLS)` ← Gmail funcionando
   - `✅ Email enviado via SendGrid` ← SendGrid funcionando
   - `⚠️ Fallo puerto 465: ...` ← Esperado (puerto bloqueado)
   - `⚠️ Gmail SMTP falló: ... Intentando SendGrid...` ← Fallback activado

---

## 🎯 ¿Cuál Elegir?

| Característica | Gmail | SendGrid |
|---------------|-------|----------|
| Facilidad Setup | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Emails/día | 500 | 100 |
| Deliverability | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Tracking | ❌ | ✅ |
| Costo | Gratis | Gratis |
| Railway Compatible | ✅ (probablemente) | ✅ (100%) |

**Recomendación:** Empieza con **Gmail** (más fácil). Si no funciona, usa **SendGrid** (garantizado que funciona en Railway).

---

## 🔧 Solución de Problemas

### Gmail no funciona:
```
⚠️ Fallo puerto 587: [Errno 111] Connection refused
```
**Solución:** Railway también bloquea Gmail. Usa SendGrid (Opción 2).

### SendGrid no funciona:
```
❌ SendGrid también falló: 403 Forbidden
```
**Solución:** Verifica que hayas verificado el "Sender Identity" (paso 3 de SendGrid).

### Email llega a spam:
**Solución:** 
- Gmail: Normal en primeros envíos, mejora con el tiempo
- SendGrid: Configura SPF/DKIM records (Settings → Sender Authentication → Domain Authentication)

### No llega ningún email:
**Solución:**
1. Verifica variables en Railway Dashboard
2. Revisa logs para ver el error exacto
3. Prueba con otro email (a veces Gmail bloquea)

---

## 📝 Resumen de Variables Requeridas

### Para Gmail:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_gmail@gmail.com
SMTP_PASS=contraseña_aplicacion_16_caracteres
EMAIL_FROM=tu_gmail@gmail.com
EMAIL_NASSA=nassasolar.comercial@outlook.com
```

### Para SendGrid:
```
SENDGRID_API_KEY=SG.tu_api_key_aqui
EMAIL_FROM=tu_email_verificado@domain.com
EMAIL_NASSA=nassasolar.comercial@outlook.com
```

### Opcionales (ya tienen default):
```
EMAIL_SUBJECT=Cotización Sistema Solar Fotovoltaico - NASSA Solar
```

---

## 🚀 Después de Configurar

Una vez que funcione el email, el sistema está **100% productivo**:

✅ Frontend servido desde Railway  
✅ Backend procesando cotizaciones  
✅ PDF generado con LibreOffice  
✅ Emails enviados automáticamente  
✅ Copias a nassasolar.comercial@outlook.com  

**Siguiente paso:** Configurar dominio personalizado `cotizador.nassasolar.com` (ver `GUIA_DESPLIEGUE_PRODUCCION.md`).
