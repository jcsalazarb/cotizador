Te# Solución al problema de envío de emails en Railway

## 🔴 Problema identificado
Railway **bloquea el puerto 587** (SMTP STARTTLS) por políticas de seguridad contra spam. Esto es común en servicios de hosting gratuitos.

## ✅ Soluciones implementadas (en orden de prioridad)

### Solución 1: Puerto 465 (SMTP_SSL) ⭐ IMPLEMENTADA
El código ahora intenta automáticamente **puerto 465 primero** (SMTP con SSL directo), que Railway generalmente permite.

**Ventajas:**
- No requiere cambios en variables de Railway
- Namecheap soporta puerto 465: `mail.privateemail.com:465`
- Más seguro que STARTTLS

**Configuración actual en Railway:**
```bash
SMTP_HOST=mail.privateemail.com
SMTP_PORT=587  # El código intentará 465 ANTES
SMTP_USER=comercial@nassasolar.com
SMTP_PASS=Lu1sF3rN@ss@
EMAIL_FROM=comercial@nassasolar.com
EMAIL_NASSA=nassasolar.comercial@outlook.com
```

**Si esta solución funciona (la más probable):**
- Verás en los logs: `✅ Email enviado via puerto 465 (SSL)`
- No necesitas hacer nada más

---

### Solución 2: Cambiar SMTP_PORT a 465 manualmente
Si prefieres forzar solo el puerto 465, actualiza la variable en Railway:

1. Ve a Railway → Variables
2. Cambia `SMTP_PORT` de `587` a `465`
3. Guarda (Railway redesplegará automáticamente)

---

### Solución 3: SendGrid API (alternativa sin SMTP)
Si Railway bloquea TODOS los puertos SMTP (raro), usa SendGrid (100 emails/día gratis):

**Pasos:**
1. Crea cuenta en https://sendgrid.com/
2. Genera API Key: Settings → API Keys → Create API Key
3. Añade variable en Railway:
   ```bash
   SENDGRID_API_KEY=SG.tu_api_key_aqui
   ```
4. El código automáticamente usará SendGrid si detecta `SENDGRID_API_KEY`

**Ventajas:**
- No usa puertos SMTP (funciona en cualquier hosting)
- Incluye tracking de emails
- 100 emails/día gratis

---

### Solución 4: Gmail SMTP (puerto 587 alternativo)
Gmail a veces funciona mejor en Railway:

**Pasos:**
1. Crea contraseña de aplicación en Gmail:
   - Google Account → Security → 2-Step Verification → App passwords
2. Actualiza variables en Railway:
   ```bash
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=tu_email@gmail.com
   SMTP_PASS=tu_app_password_16_digitos
   EMAIL_FROM=tu_email@gmail.com
   ```

**Limitación:** 500 emails/día

---

## 📊 Diagnóstico en Railway

### Ver logs en tiempo real:
```bash
# En Railway Dashboard:
1. Click en tu proyecto
2. Click en el deployment
3. Click en "View Logs"
4. Busca mensajes como:
   - "✅ Email enviado via puerto 465"
   - "⚠️ Fallo puerto 587: [Errno 111] Connection refused"
```

### Probar desde Railway directamente:
```bash
# Opción 1: Usar curl desde tu computadora
curl -X POST https://web-production-3749b.up.railway.app/api/cotizar \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test Email",
    "telefono": "3001234567",
    "email": "tu_email@gmail.com",
    "ciudad": "santa_marta",
    "consumoMensual": 300,
    "valorFactura": 450000,
    "valorKwh": 1500,
    "tipoSistemaFV": "ongrid",
    "panel": "panel1",
    "inversor": "inv1"
  }'

# Verifica el resultado y luego revisa los logs de Railway
```

---

## 🎯 Estado actual del sistema

✅ **Código actualizado** (commit c93e4cd):
- Intenta puerto 465 primero (SMTP_SSL)
- Si falla, intenta puerto 587 (STARTTLS)
- Logs detallados de cada intento

✅ **Variables configuradas en Railway**:
- Todas las variables SMTP están correctas
- Esperando redeploy automático (~2 minutos)

⏳ **Siguiente paso**:
1. Espera que Railway termine el redeploy
2. Genera una cotización de prueba desde https://web-production-3749b.up.railway.app/
3. Verifica si llega el email (revisa spam también)
4. Si no funciona, revisa los logs de Railway para ver qué puerto falló

---

## 📝 Mensaje de error típico

Si ves este error en Railway logs:
```
[Errno 111] Connection refused
```
→ El puerto está bloqueado por Railway

Si ves este error:
```
[Errno 113] No route to host
```
→ Railway no permite conexiones salientes a ese servidor

Si ves:
```
Authentication failed (535)
```
→ Credenciales incorrectas (verifica SMTP_PASS)

---

## 🚀 Plan B: Migrar a Contabo VPS

Si Railway bloquea todos los puertos SMTP (improbable):
- Costo: €4.99/mes (Contabo VPS 200GB)
- Sin restricciones de puertos
- Seguir guía: `GUIA_DESPLIEGUE_PRODUCCION.md`

Pero **prueba primero el puerto 465**, debería funcionar! 🎉
