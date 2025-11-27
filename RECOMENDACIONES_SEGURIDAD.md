# RECOMENDACIONES DE SEGURIDAD - Sistema NASSA Solar

**Proyecto:** Sistema de Cotización Solar  
**Fecha:** 25 de noviembre de 2025  
**Versión:** 1.0  
**Criticidad:** ALTA

---

## 1. SEGURIDAD DE AUTENTICACIÓN

### 1.1 Credenciales de Administrador

**❌ NO HACER:**
```bash
ADMIN_USER=admin
ADMIN_PASS=admin123
```

**✅ RECOMENDADO:**
```bash
ADMIN_USER=admin_nassa_2024
ADMIN_PASS=N@ss@S0l4r_Pr0d_2024!xZ#mK9pQ
```

**Generador de contraseñas seguras:**
```bash
# Linux/macOS
openssl rand -base64 32

# Python
python3 -c "import secrets, string; chars=string.ascii_letters+string.digits+string.punctuation; print(''.join(secrets.choice(chars) for i in range(32)))"
```

**Requisitos contraseña admin:**
- Mínimo 20 caracteres
- Mayúsculas y minúsculas
- Números
- Símbolos especiales
- NO palabras del diccionario
- NO información personal
- NO reutilizar de otros sistemas

### 1.2 Secret Key

**Generar única y aleatoria:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

**En `.env`:**
```bash
SECRET_KEY=xK8mP2vQ9nR4jL7wE6sA3zD5hF1gT0yU_cN8bV4xQ2pM9kL7jH6fG5dS3aZ1wE0
```

**Nunca** compartir en:
- Repositorios públicos
- Emails
- Chats
- Documentación pública

### 1.3 HTTP Basic Auth

**Limitaciones actuales:**
- Solo protege endpoints `/api/admin/*`
- Credenciales en base64 (reversible)
- No expira sesiones

**Mejoras recomendadas (futuro):**
- Implementar JWT (JSON Web Tokens)
- Tokens con expiración (1 hora)
- Refresh tokens
- Logout funcional

---

## 2. SEGURIDAD DE RED

### 2.1 HTTPS Obligatorio

**Producción SIEMPRE con SSL/TLS:**
```nginx
# Redirigir HTTP → HTTPS
server {
    listen 80;
    return 301 https://$server_name$request_uri;
}
```

**Verificaciones:**
```bash
# Test SSL
curl -I https://cotizador.nassasolar.com

# Debe retornar: HTTP/2 200
# NO: HTTP/1.1 200 (inseguro)
```

**Evitar:**
- Certificados autofirmados en producción
- SSL v3 / TLS 1.0 (vulnerables)
- Certificados expirados

### 2.2 CORS Restrictivo

**❌ PELIGROSO:**
```python
ALLOWED_ORIGINS=*  # Permite CUALQUIER dominio
```

**✅ SEGURO:**
```python
ALLOWED_ORIGINS=https://cotizador.nassasolar.com,https://www.nassasolar.com
```

**En producción:**
- NUNCA usar `*`
- Solo dominios específicos
- Validar protocolo (https://)
- Sin dominios de desarrollo

### 2.3 Firewall (UFW)

**Configuración mínima:**
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH (cambiar puerto en producción)
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

**CRÍTICO: Puerto 8001 NO debe estar expuesto:**
```bash
# Verificar
sudo ufw status numbered

# NO debe aparecer:
# 8001/tcp   ALLOW   Anywhere
```

### 2.4 Rate Limiting

**Configuración actual:**
```python
RATE_LIMIT=10  # 10 req/min por IP
```

**Producción ajustar según carga:**
```python
RATE_LIMIT=50  # Usuarios reales
# Si hay ataques DDoS, reducir temporalmente a 10
```

**Nginx rate limiting adicional:**
```nginx
limit_req_zone $binary_remote_addr zone=nassa_limit:10m rate=30r/m;

server {
    location /api/cotizar {
        limit_req zone=nassa_limit burst=5 nodelay;
    }
}
```

---

## 3. SEGURIDAD DE DATOS

### 3.1 Validación de Entrada

**Backend valida con Pydantic:**
```python
email: EmailStr  # Formato email válido
telefono: str = Field(..., pattern=r'^\+?[0-9\s\-()]{7,20}$')
consumoMensual: float = Field(..., gt=50, lt=50000)
```

**Nunca confiar en frontend:**
- Frontend puede ser bypasseado
- Validación backend es obligatoria
- Rechazar datos malformados

### 3.2 Inyección SQL

**No aplica (no hay SQL):**
- Sistema usa JSON (no base de datos)
- Sin queries dinámicos
- Sin riesgo inyección SQL

**Futuro (si migran a PostgreSQL/MySQL):**
- Usar ORM (SQLAlchemy)
- Parametrizar queries
- Validar inputs

### 3.3 XSS (Cross-Site Scripting)

**Frontend escapa HTML:**
```javascript
// NUNCA:
element.innerHTML = user_input;

// SIEMPRE:
element.textContent = user_input;
// O usar frameworks con auto-escape (React, Vue)
```

**Sanitización:**
```javascript
function sanitize(text) {
    return text.replace(/[<>\"']/g, '');
}
```

### 3.4 Path Traversal

**Backend valida paths:**
```python
# PELIGRO:
file = open(f"/tmp/{user_filename}")  # Puede ser ../../../etc/passwd

# SEGURO:
import os
safe_path = os.path.basename(user_filename)
file = open(f"/tmp/{safe_path}")
```

**Template PowerPoint:**
- Path fijo: `Template/Template-PreCotizacion.pptx`
- No acepta paths del usuario
- Validar existencia antes de leer

---

## 4. SEGURIDAD DE ARCHIVOS

### 4.1 Permisos Sistema

**Usuario aplicación (nassa):**
```bash
# App files
sudo chown -R nassa:nassa /opt/nassa/cotizador
sudo chmod 755 /opt/nassa/cotizador

# .env (solo lectura owner)
sudo chmod 600 /opt/nassa/cotizador/backend/.env

# Logs (escritura owner)
sudo chown nassa:nassa /var/log/nassa
sudo chmod 755 /var/log/nassa
```

**NUNCA:**
```bash
chmod 777 /opt/nassa/cotizador  # ❌ Todos pueden leer/escribir
chmod 644 backend/.env          # ❌ Otros pueden leer secretos
```

### 4.2 Archivos Temporales

**Limpiar después de usar:**
```python
# Backend server.py ya lo hace
try:
    os.remove(temp_pptx)
    os.remove(temp_pdf)
except:
    pass
```

**Verificar periódicamente:**
```bash
# Ver archivos temporales viejos
find /tmp -name "*PreCotizacion*" -mtime +1 -ls

# Eliminar > 24 horas
find /tmp -name "*PreCotizacion*" -mtime +1 -delete
```

### 4.3 Upload de Archivos

**Actualmente NO hay uploads:**
- Sin formulario de carga
- Sin riesgo de archivos maliciosos

**Si implementan en futuro:**
- Validar tipo MIME
- Escanear con antivirus (ClamAV)
- Limitar tamaño (ej: 5 MB)
- Renombrar archivos (no usar nombre original)
- Almacenar fuera de webroot

---

## 5. SEGURIDAD EMAIL

### 5.1 SMTP Seguro

**Configuración actual:**
```python
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587  # STARTTLS
```

**Verificar:**
- Puerto 587 (TLS) o 465 (SSL)
- NUNCA puerto 25 (sin encripción)
- Contraseña de aplicación (no contraseña Gmail normal)

### 5.2 Prevención Spam

**Headers anti-spam:**
```python
msg['Reply-To'] = 'no-reply@nassasolar.com'
msg['X-Mailer'] = 'NASSA Solar System'
```

**Evitar:**
- Enviar > 500 emails/día (límite Gmail)
- Listas no solicitadas
- Contenido sospechoso (GANA DINERO RÁPIDO)

### 5.3 Validación Email Destinatario

**Backend valida formato:**
```python
email: EmailStr  # Pydantic valida sintaxis
```

**Adicional recomendado:**
- Verificar dominio existe (DNS MX)
- Lista negra dominios temporales (10minutemail, etc.)
- Confirmación double opt-in (futuro)

---

## 6. SEGURIDAD ADMIN PANEL

### 6.1 Restricción por IP

**Nginx configuración:**
```nginx
location /admin.html {
    # Solo oficina NASSA
    allow 190.123.45.67;  # IP pública oficina
    deny all;
    
    try_files $uri =404;
}

location ~ ^/api/admin/ {
    allow 190.123.45.67;
    deny all;
    
    proxy_pass http://nassa_backend;
}
```

**Verificar IP pública oficina:**
```bash
curl https://ipinfo.io/ip
```

### 6.2 VPN (Recomendado)

**Configurar acceso VPN:**
- Instalar WireGuard / OpenVPN
- Admin solo accesible vía VPN
- Bloquear acceso público

### 6.3 Autenticación de Dos Factores (Futuro)

**Implementar 2FA:**
- Google Authenticator
- SMS
- Email con código

---

## 7. SEGURIDAD DATOS SENSIBLES

### 7.1 Precios de Equipos

**✅ Correcta implementación actual:**
```python
# GET /api/equipos (público) - SIN precios
# GET /api/equipos/precios (admin) - CON precios
```

**Verificar:**
```bash
# Público (debe fallar)
curl https://cotizador.nassasolar.com/api/equipos/precios
# Expected: 401 Unauthorized

# Admin (debe funcionar)
curl -u admin:pass https://cotizador.nassasolar.com/api/equipos/precios
```

### 7.2 Datos Clientes

**Actualmente NO se almacenan:**
- Sin base de datos persistente
- Cotizaciones no guardan info cliente
- Solo localStorage navegador (frontend)

**Si implementan persistencia:**
- Cifrar datos sensibles (GDPR)
- Hash contraseñas (bcrypt, argon2)
- Anonimizar datos analítica
- Política de retención (borrar después 90 días)

### 7.3 Logs

**NO registrar datos sensibles:**
```python
# ❌ MAL
logger.info(f"Email: {email}, Contraseña: {password}")

# ✅ BIEN
logger.info(f"Login exitoso: {email}")
```

**Rotar logs:**
```bash
# /etc/logrotate.d/nassa
/var/log/nassa/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
}
```

---

## 8. SEGURIDAD INFRASTRUCTURE

### 8.1 Actualizaciones Sistema

**Semanal:**
```bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

**Críticas inmediatas:**
```bash
sudo apt upgrade --security-only -y
```

### 8.2 Monitoreo Intrusiones

**Fail2ban:**
```bash
sudo apt install fail2ban -y

# Ver intentos bloqueados
sudo fail2ban-client status nginx-limit-req
```

**Revisar logs ataques:**
```bash
sudo tail -f /var/log/nginx/nassa-error.log | grep -i "limit"
```

### 8.3 Backup Encriptado

**Cifrar backups sensibles:**
```bash
# Backup con encripción
tar -czf - /opt/nassa/cotizador/backend/config/ | \
  openssl enc -aes-256-cbc -salt -out backup_encrypted.tar.gz.enc

# Desencriptar
openssl enc -aes-256-cbc -d -in backup_encrypted.tar.gz.enc | \
  tar -xz -C /restore/path/
```

### 8.4 Hardening SSH

```bash
sudo nano /etc/ssh/sshd_config
```

**Configuración segura:**
```
Port 2222                    # Cambiar de 22
PermitRootLogin no
PasswordAuthentication no    # Solo SSH keys
PubkeyAuthentication yes
MaxAuthTries 3
LoginGraceTime 30
```

**Reiniciar SSH:**
```bash
sudo systemctl restart sshd
```

---

## 9. SEGURIDAD LIBRERÍAS

### 9.1 Vulnerabilidades Conocidas

**Escanear dependencias:**
```bash
cd backend
source venv/bin/activate
pip install safety
safety check
```

**Actualizar vulnerables:**
```bash
pip install --upgrade nombre_paquete
pip freeze > requirements.txt
```

### 9.2 Auditoría Regular

**Mensual:**
```bash
# Ver paquetes desactualizados
pip list --outdated

# Actualizar críticos
pip install --upgrade fastapi uvicorn python-pptx
```

### 9.3 Pinning Versiones

**requirements.txt con versiones exactas:**
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
```

**NO usar:**
```
fastapi>=0.100.0  # Puede instalar vulnerable
uvicorn           # Sin versión (peligroso)
```

---

## 10. COMPLIANCE Y PRIVACIDAD

### 10.1 GDPR (Si aplica Europa)

**Obligaciones:**
- Consentimiento explícito
- Derecho al olvido
- Portabilidad datos
- Notificar brechas < 72 horas

**Implementar:**
- Política de privacidad
- Términos y condiciones
- Checkbox "Acepto..."

### 10.2 Ley de Protección Datos Colombia

**Ley 1581 de 2012:**
- Autorización uso datos personales
- Finalidad específica
- Política tratamiento datos
- Derechos ARCO (Acceso, Rectificación, Cancelación, Oposición)

**Texto sugerido footer:**
```
"Al enviar este formulario, autorizo a NASSA Solar el tratamiento de 
mis datos personales para fines comerciales según la Ley 1581 de 2012. 
Consulte nuestra Política de Privacidad."
```

---

## 11. PLAN RESPUESTA INCIDENTES

### 11.1 Detección

**Monitorear:**
- Picos tráfico inusual
- Errores 500 masivos
- Logins fallidos repetidos
- Archivos modificados no autorizados

**Alertas:**
```bash
# Email si backend cae
check process nassa-backend with pidfile /var/run/supervisor/nassa-backend.pid
    if failed then alert admin@nassasolar.com
```

### 11.2 Contención

**Si detectan ataque:**
```bash
# 1. Bloquear IP atacante
sudo ufw deny from 123.45.67.89

# 2. Detener backend (si necesario)
sudo supervisorctl stop nassa-backend

# 3. Modo mantenimiento Nginx
sudo nano /etc/nginx/sites-available/nassa-cotizador
# Agregar: return 503;

# 4. Recargar Nginx
sudo nginx -s reload
```

### 11.3 Análisis

**Revisar:**
```bash
# Logs ataque
sudo grep "123.45.67.89" /var/log/nginx/nassa-access.log

# Comandos ejecutados
sudo grep "sudo" /var/log/auth.log

# Archivos modificados recientemente
find /opt/nassa -mtime -1 -type f -ls
```

### 11.4 Recuperación

**Pasos:**
1. Identificar vector ataque
2. Parchear vulnerabilidad
3. Restaurar desde backup limpio
4. Cambiar todas las credenciales
5. Actualizar dependencias
6. Reiniciar servicios
7. Monitorear 48 horas

### 11.5 Lecciones Aprendidas

**Documentar:**
- Fecha/hora incidente
- Vector ataque
- Daños causados
- Acciones tomadas
- Mejoras implementadas

---

## 12. CHECKLIST SEGURIDAD PRE-PRODUCCIÓN

```
☐ Credenciales admin cambiadas (contraseña fuerte 20+ chars)
☐ SECRET_KEY generada (64+ caracteres aleatorios)
☐ HTTPS configurado (SSL válido, no expirado)
☐ CORS restrictivo (solo dominio producción)
☐ Firewall activo (UFW: 22, 80, 443 permitidos, resto bloqueado)
☐ Puerto 8001 NO expuesto públicamente
☐ Fail2ban configurado
☐ Rate limiting activo (50 req/min o ajustado)
☐ SSH hardening (puerto cambiado, solo keys, root deshabilitado)
☐ Permisos archivos correctos (600 .env, 755 app)
☐ Logs rotando (no exceder disco)
☐ Backups automatizados (diarios, cifrados)
☐ Dependencias actualizadas (sin vulnerabilidades conocidas)
☐ Admin panel restringido (IP o VPN)
☐ Endpoints /docs /redoc deshabilitados o protegidos
☐ Email SMTP con TLS (puerto 587/465)
☐ Validación inputs backend (Pydantic)
☐ Headers seguridad (HSTS, X-Frame-Options, CSP)
☐ Monitoreo activo (uptime, errores, ataques)
☐ Plan respuesta incidentes documentado
☐ Política privacidad publicada (GDPR/Ley 1581)
☐ Equipo capacitado (procedimientos seguridad)
☐ Contacto soporte técnico definido
```

---

## 13. RECOMENDACIONES ADICIONALES

### 13.1 Auditoría Externa

**Contratar pentesting:**
- Anual o al lanzar features críticas
- OWASP Top 10
- Pruebas caja negra y gris
- Reporte vulnerabilidades

### 13.2 WAF (Web Application Firewall)

**Cloudflare (gratis):**
- Protección DDoS
- Rate limiting global
- Cache CDN
- SSL universal

**AWS WAF / Azure Firewall (pago):**
- Reglas personalizadas
- Machine learning
- Bloqueo geográfico

### 13.3 Separación Entornos

**Mantener separados:**
```
Desarrollo: http://localhost:8000
Staging:    https://staging.nassasolar.com
Producción: https://cotizador.nassasolar.com
```

**NUNCA:**
- Probar en producción
- Datos reales en desarrollo
- Credenciales iguales entre entornos

### 13.4 Documentación Segura

**NO incluir en docs públicas:**
- Contraseñas
- Secret keys
- IPs servidores
- Nombres usuarios
- Estructura infraestructura detallada

**Usar:**
- Gestores contraseñas (1Password, Bitwarden)
- Secrets manager (AWS Secrets, HashiCorp Vault)
- Documentación privada (Notion, Confluence privado)

---

## 14. CONTACTOS EMERGENCIA

**Soporte Técnico NASSA:**
- Email: soporte@nassasolar.com
- Teléfono: +57 313 690 9723 (24/7 emergencias)

**Reportar Vulnerabilidad:**
- Email seguro: security@nassasolar.com
- PGP Key: (si aplica)

**Proveedores:**
- Hosting: [Proveedor nombre + soporte]
- SSL: Let's Encrypt / Certificador
- Email: Google Workspace / Proveedor

---

## 15. RECURSOS ADICIONALES

**Documentación:**
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- Nginx Security: https://nginx.org/en/docs/http/ngx_http_ssl_module.html

**Herramientas:**
- SSL Test: https://www.ssllabs.com/ssltest/
- Security Headers: https://securityheaders.com/
- Observatory: https://observatory.mozilla.org/

**Alertas Seguridad:**
- CVE Details: https://www.cvedetails.com/
- Python Security: https://pypi.org/project/safety/

---

**FIN DOCUMENTO 4 - RECOMENDACIONES DE SEGURIDAD**

**CRÍTICO: Revisar y aplicar ANTES de producción. La seguridad es responsabilidad de todos.**
