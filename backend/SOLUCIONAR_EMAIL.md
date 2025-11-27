# 🔧 SOLUCIÓN: Error de Email SMTP

## ❌ Problema Actual
```
Error: (535, b'5.7.8 Username and Password not accepted')
```

La contraseña de aplicación actual en `.env` ya no es válida.

## ✅ Solución: Generar Nueva Contraseña de Aplicación

### Paso 1: Verificar verificación en 2 pasos
1. Ve a: https://myaccount.google.com/security
2. Busca "Verificación en 2 pasos"
3. Si **NO está activada**, actívala siguiendo las instrucciones de Google

### Paso 2: Crear contraseña de aplicación
1. Ve a: https://myaccount.google.com/apppasswords
2. Inicia sesión con `nassasolarprecotizacion@gmail.com`
3. En "Selecciona la app", elige **"Otro (nombre personalizado)"**
4. Escribe el nombre: **"NASSA Solar Cotizador"** (o el que prefieras)
5. Haz clic en **"Generar"**
6. Google te mostrará una contraseña de 16 caracteres como: `abcd efgh ijkl mnop`

### Paso 3: Copiar contraseña (IMPORTANTE)
⚠️ **COPIA LA CONTRASEÑA SIN ESPACIOS**: `abcdefghijklmnop`

- ✅ Correcto: `abcdefghijklmnop` (16 caracteres sin espacios)
- ❌ Incorrecto: `abcd efgh ijkl mnop` (con espacios)

### Paso 4: Actualizar archivo .env
1. Abre el archivo: `/Users/jcsalazarb/Documents/GitHub/cotizador/backend/.env`
2. Busca la línea: `SMTP_PASS=cqyguejzsbbaosvk`
3. Reemplaza con la nueva contraseña (SIN ESPACIOS):
   ```
   SMTP_PASS=abcdefghijklmnop
   ```
4. Guarda el archivo

### Paso 5: Reiniciar el backend
```bash
# Matar proceso actual
lsof -ti:8001 | xargs kill -9 2>/dev/null

# Reiniciar backend
cd /Users/jcsalazarb/Documents/GitHub/cotizador/backend
nohup /Users/jcsalazarb/Documents/GitHub/cotizador/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --reload > /tmp/backend.log 2>&1 &
```

### Paso 6: Probar conexión SMTP
```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador/backend
/Users/jcsalazarb/Documents/GitHub/cotizador/backend/venv/bin/python test_smtp.py
```

Deberías ver:
```
✅ SMTP CONFIGURADO CORRECTAMENTE
```

### Paso 7: Probar envío de email completo
1. Abre el frontend: http://localhost:8000/index_Original_modificado.html
2. Genera una cotización
3. Verifica que llegue el email al destinatario

---

## 🔍 Verificar Logs en Tiempo Real
```bash
tail -f /tmp/backend.log
```

Busca líneas como:
- ✅ `✅ Email enviado a usuario@example.com` (éxito)
- ❌ `⚠️ Error email: ...` (error)

---

## 📧 Configuración Actual
- **Usuario SMTP**: nassasolarprecotizacion@gmail.com
- **Host**: smtp.gmail.com
- **Puerto**: 587
- **TLS**: Habilitado
- **Email CC**: jcsalazarb@icloud.com

---

## 🐛 Troubleshooting

### Problema: "Username and Password not accepted"
- ✅ Genera una nueva contraseña de aplicación
- ✅ Verifica que NO tenga espacios
- ✅ Verifica que la verificación en 2 pasos esté activa

### Problema: "Application-specific password required"
- ✅ No uses la contraseña normal de Gmail
- ✅ Debes usar una contraseña de aplicación generada

### Problema: Email no llega
1. Verifica los logs: `tail -f /tmp/backend.log`
2. Revisa la carpeta de Spam del destinatario
3. Verifica que el email destino sea correcto

### Problema: Backend no reinicia
```bash
# Ver procesos en puerto 8001
lsof -ti:8001

# Matar proceso
kill -9 $(lsof -ti:8001)

# Ver logs de error
cat /tmp/backend.log | grep -i error
```

---

## ℹ️ Nota sobre el Nombre de la Aplicación
El nombre "NASSA Solar Cotizador" (o el que elijas) es solo para identificar la contraseña en tu cuenta de Google. No afecta el funcionamiento del sistema. Puedes usar cualquier nombre descriptivo que te ayude a recordar para qué es esa contraseña.
