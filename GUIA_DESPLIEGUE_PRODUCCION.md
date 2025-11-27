# GUÍA DE DESPLIEGUE EN PRODUCCIÓN - Servidor NASSA

**Proyecto:** Sistema de Cotización Solar  
**Fecha:** 25 de noviembre de 2025  
**Versión:** 1.0

---

## 1. REQUISITOS DEL SERVIDOR

### 1.1 Especificaciones Mínimas

```
- CPU: 2 cores
- RAM: 4 GB
- Disco: 20 GB SSD
- SO: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- Red: IP pública con dominio
- Puertos: 80 (HTTP), 443 (HTTPS)
```

### 1.2 Software Requerido

```bash
- Python 3.9+
- Nginx 1.18+
- LibreOffice 7.0+
- Certbot (Let's Encrypt SSL)
- Supervisor / Systemd
- Git
```

---

## 2. CONFIGURACIÓN INICIAL DEL SERVIDOR

### 2.1 Actualizar Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 2.2 Instalar Dependencias

```bash
# Python y pip
sudo apt install python3 python3-pip python3-venv -y

# Nginx
sudo apt install nginx -y

# LibreOffice (headless)
sudo apt install libreoffice --no-install-recommends -y

# Git
sudo apt install git -y

# Certbot (SSL)
sudo apt install certbot python3-certbot-nginx -y

# Supervisor (gestión procesos)
sudo apt install supervisor -y
```

### 2.3 Crear Usuario Aplicación

```bash
sudo adduser --system --group --home /opt/nassa nassa
sudo su - nassa
```

---

## 3. DESPLIEGUE DE LA APLICACIÓN

### 3.1 Clonar Repositorio

```bash
cd /opt/nassa
git clone https://github.com/jcsalazarb/cotizador.git
cd cotizador
```

### 3.2 Configurar Backend

```bash
cd backend

# Crear entorno virtual
python3 -m venv venv

# Activar entorno
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Copiar y configurar .env
cp .env.example .env
nano .env
```

### 3.3 Archivo `.env` para Producción

```bash
# SMTP (Gmail App Password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=nassasolarprecotizaciones@gmail.com
SMTP_PASS=AQUI_CONTRASEÑA_APLICACION
EMAIL_FROM=nassasolarprecotizaciones@gmail.com
EMAIL_NASSA=contacto@nassasolar.com
EMAIL_SUBJECT=PreCotización Nassa Solar

# Admin (CAMBIAR CONTRASEÑA SEGURA)
ADMIN_USER=admin_nassa
ADMIN_PASS=CONTRASEÑA_SUPER_SEGURA_AQUI_2024!

# Secret Key (Generar uno nuevo)
SECRET_KEY=GENERAR_SECRET_KEY_ALEATORIA_64_CARACTERES

# CORS (Dominio producción)
ALLOWED_ORIGINS=https://cotizador.nassasolar.com,https://www.nassasolar.com

# Server
PORT=8001
RATE_LIMIT=50

# LibreOffice Path
LIBREOFFICE_PATH=/usr/bin/soffice
```

**Generar SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 3.4 Permisos

```bash
sudo chown -R nassa:nassa /opt/nassa/cotizador
sudo chmod 600 /opt/nassa/cotizador/backend/.env
sudo chmod +x /opt/nassa/cotizador/backend/venv/bin/*
```

---

## 4. CONFIGURACIÓN SUPERVISOR (Backend)

### 4.1 Archivo Supervisor

```bash
sudo nano /etc/supervisor/conf.d/nassa-backend.conf
```

**Contenido:**
```ini
[program:nassa-backend]
command=/opt/nassa/cotizador/backend/venv/bin/uvicorn server:app --host 127.0.0.1 --port 8001 --workers 2
directory=/opt/nassa/cotizador/backend
user=nassa
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/nassa/backend.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PATH="/opt/nassa/cotizador/backend/venv/bin",HOME="/opt/nassa",LANG="es_CO.UTF-8",LC_ALL="es_CO.UTF-8"
```

### 4.2 Crear Directorio Logs

```bash
sudo mkdir -p /var/log/nassa
sudo chown nassa:nassa /var/log/nassa
```

### 4.3 Activar Supervisor

```bash
# Recargar configuración
sudo supervisorctl reread
sudo supervisorctl update

# Iniciar backend
sudo supervisorctl start nassa-backend

# Verificar estado
sudo supervisorctl status nassa-backend
```

### 4.4 Comandos Supervisor

```bash
# Ver logs
sudo tail -f /var/log/nassa/backend.log

# Reiniciar
sudo supervisorctl restart nassa-backend

# Detener
sudo supervisorctl stop nassa-backend

# Estado
sudo supervisorctl status
```

---

## 5. CONFIGURACIÓN NGINX

### 5.1 Archivo Configuración Nginx

```bash
sudo nano /etc/nginx/sites-available/nassa-cotizador
```

**Contenido:**
```nginx
# Upstream backend
upstream nassa_backend {
    server 127.0.0.1:8001 fail_timeout=10s max_fails=3;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name cotizador.nassasolar.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name cotizador.nassasolar.com;
    
    # SSL Certificates (configurar después con certbot)
    ssl_certificate /etc/letsencrypt/live/cotizador.nassasolar.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cotizador.nassasolar.com/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Logs
    access_log /var/log/nginx/nassa-access.log;
    error_log /var/log/nginx/nassa-error.log;
    
    # Max upload size (para PDFs grandes)
    client_max_body_size 20M;
    
    # Frontend (archivos estáticos)
    root /opt/nassa/cotizador;
    index index_Original_modificado.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    # API Backend (proxy)
    location /api/ {
        proxy_pass http://nassa_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 90s;
        proxy_read_timeout 90s;
    }
    
    # Docs API (opcional, comentar para ocultar en producción)
    location ~ ^/(docs|redoc|openapi.json) {
        proxy_pass http://nassa_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Protección con IP (opcional)
        # allow 190.XXX.XXX.XXX;  # IP oficina NASSA
        # deny all;
    }
    
    # Admin Panel (protección adicional)
    location /admin.html {
        # Limitar por IP (opcional)
        # allow 190.XXX.XXX.XXX;  # IP oficina NASSA
        # deny all;
        
        try_files $uri =404;
    }
    
    # Cache archivos estáticos
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Denegar acceso a archivos sensibles
    location ~ /\. {
        deny all;
    }
    
    location ~ \.env$ {
        deny all;
    }
    
    location ~ \.git {
        deny all;
    }
}
```

### 5.2 Activar Sitio

```bash
# Crear symlink
sudo ln -s /etc/nginx/sites-available/nassa-cotizador /etc/nginx/sites-enabled/

# Eliminar default (opcional)
sudo rm /etc/nginx/sites-enabled/default

# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

---

## 6. CONFIGURAR SSL (HTTPS)

### 6.1 Obtener Certificado Let's Encrypt

```bash
# Crear directorio certbot
sudo mkdir -p /var/www/certbot

# Solicitar certificado
sudo certbot --nginx -d cotizador.nassasolar.com
```

**Seguir prompts:**
- Email: contacto@nassasolar.com
- Aceptar términos: Yes
- Compartir email: No (opcional)
- Redirect HTTP → HTTPS: Yes (opción 2)

### 6.2 Renovación Automática

```bash
# Test renovación
sudo certbot renew --dry-run

# Configurar cron (ya incluido por certbot)
sudo crontab -l | grep certbot
# Debe mostrar: 0 0,12 * * * certbot renew --quiet
```

### 6.3 Verificar SSL

```bash
# Test online
https://www.ssllabs.com/ssltest/analyze.html?d=cotizador.nassasolar.com

# Verificar certificado local
sudo certbot certificates
```

---

## 7. CONFIGURACIÓN DNS

### 7.1 Registros DNS Necesarios

**En panel de dominio (ej: GoDaddy, Cloudflare):**

```
Tipo    Nombre              Valor                   TTL
A       cotizador           190.XXX.XXX.XXX         3600
CNAME   www.cotizador       cotizador.nassasolar.com 3600
```

### 7.2 Verificar Propagación

```bash
# Linux/macOS
dig cotizador.nassasolar.com

# Verificar desde múltiples locaciones
https://www.whatsmydns.net/#A/cotizador.nassasolar.com
```

**Esperar 1-48 horas para propagación completa.**

---

## 8. ACTUALIZAR FRONTEND (API URL)

### 8.1 Modificar URL Backend

```bash
sudo nano /opt/nassa/cotizador/index_Original_modificado.html
```

**Cambiar:**
```javascript
// De:
const API_BASE_URL = 'http://localhost:8001/api';

// A:
const API_BASE_URL = 'https://cotizador.nassasolar.com/api';
```

### 8.2 Modificar Admin Panel

```bash
sudo nano /opt/nassa/cotizador/admin.html
```

**Cambiar:**
```javascript
// De:
const API_BASE_URL = 'http://localhost:8001/api';

// A:
const API_BASE_URL = 'https://cotizador.nassasolar.com/api';
```

### 8.3 Actualizar .env Backend

```bash
sudo nano /opt/nassa/cotizador/backend/.env
```

**Actualizar:**
```bash
ALLOWED_ORIGINS=https://cotizador.nassasolar.com
```

**Reiniciar backend:**
```bash
sudo supervisorctl restart nassa-backend
```

---

## 9. FIREWALL (UFW)

### 9.1 Configurar Firewall

```bash
# Habilitar UFW
sudo ufw enable

# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Denegar acceso directo a backend (solo desde localhost)
# Puerto 8001 NO debe estar expuesto

# Ver reglas
sudo ufw status numbered
```

### 9.2 Protección Adicional (Fail2ban)

```bash
# Instalar
sudo apt install fail2ban -y

# Configurar
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
```

**Agregar:**
```ini
[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https"]
logpath = /var/log/nginx/*error.log
findtime = 600
bantime = 3600
maxretry = 10
```

**Activar:**
```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
sudo fail2ban-client status
```

---

## 10. MONITOREO Y LOGS

### 10.1 Logs Backend

```bash
# Tiempo real
sudo tail -f /var/log/nassa/backend.log

# Errores
sudo grep -i error /var/log/nassa/backend.log | tail -50

# Últimas 100 líneas
sudo tail -100 /var/log/nassa/backend.log
```

### 10.2 Logs Nginx

```bash
# Access log
sudo tail -f /var/log/nginx/nassa-access.log

# Error log
sudo tail -f /var/log/nginx/nassa-error.log

# Estadísticas
sudo awk '{print $1}' /var/log/nginx/nassa-access.log | sort | uniq -c | sort -nr | head -20
```

### 10.3 Monitoreo Recursos

```bash
# CPU y RAM
htop

# Espacio disco
df -h

# Uso backend
ps aux | grep uvicorn

# Conexiones activas
sudo netstat -tunlp | grep -E "80|443|8001"
```

### 10.4 Configurar Alertas (Opcional)

```bash
# Instalar monit
sudo apt install monit -y

# Configurar
sudo nano /etc/monit/conf.d/nassa
```

**Contenido:**
```
check process nassa-backend with pidfile /var/run/supervisor/nassa-backend.pid
    start program = "/usr/bin/supervisorctl start nassa-backend"
    stop program = "/usr/bin/supervisorctl stop nassa-backend"
    if cpu > 80% for 5 cycles then alert
    if memory > 80% for 5 cycles then alert
    
check host nassa-web with address 127.0.0.1
    if failed port 8001 protocol http request "/health" then alert
```

---

## 11. BACKUP EN PRODUCCIÓN

### 11.1 Script Backup Automático

```bash
sudo nano /opt/nassa/backup.sh
```

**Contenido:**
```bash
#!/bin/bash
# Backup automático NASSA Solar

DATE=$(date +%Y%m%d_%H%M)
BACKUP_DIR="/opt/nassa/backups"
APP_DIR="/opt/nassa/cotizador"

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Backup configuración
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
    $APP_DIR/backend/config/*.json \
    $APP_DIR/backend/.env \
    $APP_DIR/Template/*.pptx

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /var/log/nassa/

# Eliminar backups > 30 días
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

# Enviar a S3/Dropbox/Drive (opcional)
# aws s3 cp $BACKUP_DIR/config_$DATE.tar.gz s3://nassa-backups/

echo "✅ Backup completado: $DATE"
```

**Hacer ejecutable:**
```bash
sudo chmod +x /opt/nassa/backup.sh
```

### 11.2 Cron Backup Diario

```bash
sudo crontab -e
```

**Agregar:**
```cron
# Backup diario a las 3 AM
0 3 * * * /opt/nassa/backup.sh >> /var/log/nassa/backup.log 2>&1
```

---

## 12. ACTUALIZACIÓN DE LA APLICACIÓN

### 12.1 Procedimiento Actualización

```bash
# 1. Conectar al servidor
ssh usuario@cotizador.nassasolar.com

# 2. Cambiar a usuario nassa
sudo su - nassa

# 3. Ir al directorio
cd /opt/nassa/cotizador

# 4. Backup actual
cp backend/.env /tmp/env_backup
tar -czf /tmp/app_backup_$(date +%Y%m%d).tar.gz .

# 5. Pull cambios
git pull origin main

# 6. Restaurar .env (si se sobrescribió)
cp /tmp/env_backup backend/.env

# 7. Actualizar dependencias (si cambió requirements.txt)
cd backend
source venv/bin/activate
pip install --upgrade -r requirements.txt

# 8. Reiniciar backend
sudo supervisorctl restart nassa-backend

# 9. Verificar
curl https://cotizador.nassasolar.com/api/health

# 10. Ver logs
sudo tail -f /var/log/nassa/backend.log
```

### 12.2 Rollback (si falla)

```bash
# Restaurar desde backup
cd /opt/nassa
tar -xzf /tmp/app_backup_YYYYMMDD.tar.gz -C cotizador/

# Reiniciar
sudo supervisorctl restart nassa-backend
```

---

## 13. CHECKLIST PRE-PRODUCCIÓN

```
☐ Servidor con IP pública configurada
☐ Dominio apuntando a IP (DNS propagado)
☐ Python 3.9+ instalado
☐ Nginx instalado y configurado
☐ LibreOffice instalado
☐ SSL (HTTPS) configurado y funcionando
☐ Firewall (UFW) activado (puertos 22, 80, 443)
☐ Fail2ban configurado
☐ Supervisor instalado y backend corriendo
☐ Logs rotando correctamente
☐ Backup automático configurado
☐ Variables .env producción configuradas:
    ☐ SMTP credenciales válidas
    ☐ ADMIN_PASS cambiada (segura)
    ☐ SECRET_KEY generada
    ☐ ALLOWED_ORIGINS con dominio producción
    ☐ LIBREOFFICE_PATH correcto
☐ Frontend URLs actualizadas (API_BASE_URL)
☐ Admin URLs actualizadas
☐ Test cotización completa:
    ☐ Formulario funciona
    ☐ PDF se genera
    ☐ Email se envía
☐ Admin panel accesible y funcional
☐ Monitoreo configurado (opcional)
☐ Documentación actualizada con IPs/dominios
☐ Equipo NASSA capacitado en uso
```

---

## 14. CONTACTO TÉCNICO

**En caso de problemas en producción:**

- **Email:** soporte@nassasolar.com
- **Repositorio:** https://github.com/jcsalazarb/cotizador
- **Logs:** `/var/log/nassa/backend.log`
- **Status:** `sudo supervisorctl status`
- **Restart:** `sudo supervisorctl restart nassa-backend`

---

**FIN DOCUMENTO 3 - GUÍA DESPLIEGUE PRODUCCIÓN**
