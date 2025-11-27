# 🚀 PASOS RÁPIDOS PARA DESPLEGAR EN RAILWAY

## ✅ YA COMPLETADO

- [x] Archivos de configuración creados (railway.json, Procfile, nixpacks.toml)
- [x] Repositorio actualizado en GitHub
- [x] Correo corporativo comercial@nassasolar.com configurado
- [x] Pruebas de envío de email exitosas

## 📋 SIGUIENTE: DESPLIEGUE EN RAILWAY (15 minutos)

### 1️⃣ Crear Cuenta Railway (2 min)
```
1. Ir a: https://railway.app
2. Clic "Login with GitHub"
3. Autorizar Railway
```

### 2️⃣ Conectar Repositorio (2 min)
```
1. Dashboard → "New Project"
2. "Deploy from GitHub repo"
3. Seleccionar: jcsalazarb/cotizador
4. Railway detectará automáticamente la configuración
```

### 3️⃣ Configurar Variables de Entorno (5 min)
```
En Railway → Pestaña "Variables" → Agregar:

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

⚠️ **COPIAR Y PEGAR** cada línea sin comillas adicionales

### 4️⃣ Obtener URL (1 min)
```
1. Railway desplegará automáticamente
2. Ir a "Settings" → "Domains"
3. Copiar URL: cotizador-production-XXXX.up.railway.app
```

### 5️⃣ Configurar DNS en Namecheap (5 min)
```
1. Namecheap → Domain List → nassasolar.com
2. Advanced DNS → Add New Record
3. Type: CNAME
   Host: cotizador
   Value: [URL de Railway sin https://]
   TTL: Automatic
4. Save
```

### 6️⃣ Verificar Funcionamiento
```bash
# Abrir navegador:
https://cotizador-production-XXXX.up.railway.app

# Probar cotización completa
# Verificar que llegue email
```

## 🎯 URLs FINALES

- **Temporal Railway**: `https://cotizador-production-XXXX.up.railway.app`
- **Dominio Personalizado**: `https://cotizador.nassasolar.com` (después de DNS)

## 💰 COSTOS

- Railway: **$0** primeros 3 meses ($5 crédito/mes)
- Dominio: **$9/año** (ya pagado)
- Email: **$1.99/mes** (ya configurado)

**Total mensual: ~$2 USD**

## 📞 SOPORTE

Si algo falla:
1. Revisar logs en Railway → "Deployments" → "View Logs"
2. Verificar variables de entorno (no comillas extras)
3. Consultar: GUIA_RAILWAY_DEPLOYMENT.md

## ✨ DESPUÉS DEL DESPLIEGUE

- [ ] Probar cotización completa
- [ ] Verificar recepción de emails
- [ ] Crear página principal nassasolar.com
- [ ] Enlazar cotizador desde la página principal
- [ ] Actualizar ALLOWED_ORIGINS con dominio real

---

**Tiempo estimado total: 15-20 minutos**
**Siguiente paso**: Ir a https://railway.app y comenzar 🚀
