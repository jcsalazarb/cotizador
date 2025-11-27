# 📧 CONFIGURAR EMAIL DE GMAIL PARA ENVÍO AUTOMÁTICO

## ⚠️ PROBLEMA ACTUAL

El sistema está generando cotizaciones correctamente, pero los emails no se están enviando debido a credenciales incorrectas de Gmail.

Error actual:
```
⚠️ Error email: (535, b'5.7.8 Username and Password not accepted')
```

---

## ✅ SOLUCIÓN: CREAR CONTRASEÑA DE APLICACIÓN EN GMAIL

### Paso 1: Habilitar Verificación en 2 Pasos

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. En el menú lateral, selecciona **"Seguridad"**
3. Busca la sección **"Verificación en 2 pasos"**
4. Si no está activada, haz clic en **"Activar"** y sigue los pasos
5. Completa la configuración con tu teléfono

### Paso 2: Crear Contraseña de Aplicación

1. Una vez activada la verificación en 2 pasos, regresa a **"Seguridad"**
2. Busca **"Contraseñas de aplicaciones"** (al final de la sección de verificación en 2 pasos)
3. Haz clic en **"Contraseñas de aplicaciones"**
4. Puede que te pida tu contraseña de Gmail nuevamente
5. En el campo "Nombre de la app", escribe: **"NASSA Solar Cotizador"**
6. Haz clic en **"Crear"**
7. Gmail generará una contraseña de 16 caracteres (sin espacios)
8. **COPIA ESTA CONTRASEÑA** (la verás solo una vez)

### Paso 3: Actualizar el archivo `.env`

1. Abre el archivo `/Users/jcsalazarb/Documents/GitHub/cotizador/backend/.env`
2. Reemplaza la línea de `SMTP_PASS` con la nueva contraseña:

```bash
SMTP_PASS=tu_contraseña_de_16_caracteres_sin_espacios
```

Ejemplo (NO uses esta, usa la que Gmail te generó):
```bash
SMTP_PASS=abcdwxyzefgh1234
```

3. **NO DEJES ESPACIOS** en la contraseña
4. Guarda el archivo

### Paso 4: Reiniciar el Backend

En la terminal, ejecuta:

```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador/backend
source venv/bin/activate
lsof -ti:8001 | xargs kill -9 2>/dev/null
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

---

## 🧪 PROBAR EL EMAIL

1. Abre http://localhost:8000/index_Original_modificado.html
2. Completa el formulario de cotización
3. Envía la cotización
4. Verifica en los logs del backend:
   - ✅ Si ves: `✅ Email enviado a [email]` → Todo funciona
   - ❌ Si ves: `⚠️ Error email: ...` → Revisa los pasos anteriores

5. Revisa tu bandeja de entrada (y carpeta de spam)

---

## 🔍 TROUBLESHOOTING

### "No encuentro Contraseñas de aplicaciones"
- Asegúrate de haber activado la Verificación en 2 pasos primero
- La opción solo aparece DESPUÉS de activar 2FA
- Puede estar en: Cuenta de Google > Seguridad > Verificación en dos pasos > Contraseñas de aplicaciones

### "Sigo sin poder enviar emails"
1. Verifica que copiaste la contraseña completa (16 caracteres)
2. Verifica que no hay espacios en la contraseña en el `.env`
3. Verifica que el email en `SMTP_USER` es correcto: `nassasolarprecotizacion@gmail.com`
4. Reinicia el backend después de cambiar el `.env`

### "La contraseña desapareció"
- Gmail solo muestra la contraseña de aplicación una vez
- Si la perdiste, debes crear una nueva:
  - Ve a Contraseñas de aplicaciones
  - Elimina la anterior
  - Crea una nueva

### "¿Puedo usar mi contraseña normal de Gmail?"
- ❌ NO, Gmail ya no permite usar contraseñas normales para aplicaciones
- ✅ DEBES usar una contraseña de aplicación

---

## 📱 VERIFICACIÓN RÁPIDA

Tu archivo `.env` debe verse así:

```bash
# SMTP (usar contraseña de aplicación de Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=nassasolarprecotizacion@gmail.com
SMTP_PASS=abcdwxyzefgh1234
EMAIL_FROM=nassasolarprecotizacion@gmail.com
EMAIL_NASSA=jcsalazarb@icloud.com
```

Donde `SMTP_PASS` es la contraseña de 16 caracteres que Gmail te dio (sin espacios).

---

## ✅ CUANDO FUNCIONE

Una vez que el email funcione, verás en los logs del backend:

```
✅ Email enviado a cliente@email.com
INFO: 127.0.0.1:XXXXX - "POST /api/cotizar HTTP/1.1" 200 OK
```

Y el cliente recibirá un email con:
- **Asunto:** "Cotización NASSA Solar - [ID]"
- **Adjunto:** PDF con la cotización completa
- **CC:** jcsalazarb@icloud.com (copia para NASSA)

---

## 🔐 SEGURIDAD

- La contraseña de aplicación es SOLO para este proyecto
- Si la compartes accidentalmente, puedes revocarla en Gmail
- Gmail te permite crear múltiples contraseñas de aplicación
- Nunca subas el archivo `.env` a GitHub (ya está en `.gitignore`)

---

## 📞 CONTACTO

Si después de seguir estos pasos sigue sin funcionar:
1. Verifica que el email `nassasolarprecotizacion@gmail.com` existe
2. Verifica que tienes acceso a ese email
3. Intenta con otro email de Gmail si es necesario
