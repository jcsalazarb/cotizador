# 📋 TODO - Sistema de Cotización NASSA Solar

**Última actualización:** 13 de diciembre de 2025

---

## 🔥 PRÓXIMA SESIÓN - Implementar Gestión de Usuarios

### Checklist de Inicio
- [ ] Leer `ESTADO_PROYECTO.md` para refrescar contexto
- [ ] Verificar producción: `curl https://web-production-3749b.up.railway.app/health`
- [ ] Crear rama: `git checkout -b feature/user-management`
- [ ] Levantar ambiente local (backend puerto 8001, frontend puerto 8000)

---

## 🎯 Fase 1: Modelo de Datos (1-2 horas)

### Base de Datos
- [ ] Crear modelo `User` en SQLAlchemy
  ```python
  # backend/models.py o backend/auth.py
  class User(Base):
      __tablename__ = 'users'
      id = Column(Integer, primary_key=True)
      username = Column(String, unique=True, nullable=False)
      email = Column(String, unique=True, nullable=False)
      password_hash = Column(String, nullable=False)
      role = Column(String, default='crm_user')  # admin, crm_user, viewer
      is_active = Column(Boolean, default=True)
      created_at = Column(DateTime, default=datetime.utcnow)
      last_login = Column(DateTime, nullable=True)
  ```

- [ ] Agregar dependencia: `pip install bcrypt`
- [ ] Crear migración manual o usar Alembic (opcional)
- [ ] Script para crear usuario admin inicial
  ```python
  # backend/create_admin.py
  import bcrypt
  from models import User, get_db
  
  def create_admin():
      hashed = bcrypt.hashpw('Lu1sF3rN@ss@'.encode(), bcrypt.gensalt())
      admin = User(
          username='admin',
          email='admin@nassasolar.com',
          password_hash=hashed.decode(),
          role='admin'
      )
      # guardar en DB
  ```

### Testing BD
- [ ] Ejecutar script de creación de admin
- [ ] Verificar tabla en Railway PostgreSQL
- [ ] Probar login con nuevo usuario

---

## 🎯 Fase 2: Backend - Endpoints (2-3 horas)

### Autenticación Mejorada
- [ ] Crear archivo `backend/auth.py`
- [ ] Función `verify_password(plain, hashed)`
- [ ] Función `get_password_hash(password)`
- [ ] Función `authenticate_user(username, password)`
- [ ] Decorador `@require_role("admin")` para endpoints

### Endpoints de Usuarios
- [ ] `POST /api/admin/users` - Crear usuario
  - Validar username único
  - Hash de password
  - Solo admin puede crear
  
- [ ] `GET /api/admin/users` - Listar todos
  - Ocultar password_hash en response
  - Solo admin
  
- [ ] `GET /api/admin/users/{id}` - Obtener uno
  - Solo admin
  
- [ ] `PUT /api/admin/users/{id}` - Actualizar
  - No permitir cambio de role si no es admin
  - Solo admin
  
- [ ] `DELETE /api/admin/users/{id}` - Eliminar
  - No permitir eliminar último admin
  - Solo admin
  
- [ ] `PUT /api/admin/users/{id}/password` - Cambiar contraseña
  - Admin puede cambiar cualquiera
  - Usuario puede cambiar la suya

### Migrar Autenticación
- [ ] Actualizar `auth_admin` dependency en server.py
- [ ] Cambiar de credenciales hardcoded a DB
- [ ] Agregar campo `last_login` al hacer login
- [ ] Testing de endpoints con Postman/curl

---

## 🎯 Fase 3: Frontend - UI en admin.html (2-3 horas)

### Nueva Pestaña "Usuarios"
- [ ] Copiar estructura de tabs existentes
- [ ] Crear tab "👥 Usuarios"
- [ ] Diseño con Tailwind CSS (mismo estilo que CRM)

### Tabla de Usuarios
- [ ] Columnas: ID, Username, Email, Role, Estado, Último Login, Acciones
- [ ] Botón "Crear Usuario" (abre modal)
- [ ] Acciones por fila:
  - ✏️ Editar
  - 🔑 Cambiar Contraseña
  - 🗑️ Eliminar (con confirmación)
  - 🔄 Activar/Desactivar

### Modal Crear/Editar Usuario
- [ ] Campos: Username, Email, Password, Confirmar Password, Role (select)
- [ ] Validación frontend:
  - Username mínimo 3 caracteres
  - Email válido
  - Password mínimo 8 caracteres
  - Passwords coinciden
- [ ] Toggle "Activo/Inactivo"

### JavaScript
- [ ] Función `cargarUsuarios()` - GET /api/admin/users
- [ ] Función `crearUsuario()` - POST /api/admin/users
- [ ] Función `editarUsuario(id)` - PUT /api/admin/users/{id}
- [ ] Función `eliminarUsuario(id)` - DELETE /api/admin/users/{id}
- [ ] Función `cambiarPassword(id)` - PUT /api/admin/users/{id}/password
- [ ] Usar `getAuthHeader()` para autenticación

---

## 🎯 Fase 4: Sistema de Roles (1-2 horas)

### Definir Permisos
```javascript
const ROLES = {
    admin: {
        can: ['create_users', 'edit_users', 'delete_users', 'view_prices', 'export_data']
    },
    crm_user: {
        can: ['view_quotations', 'search_quotations', 'view_reports']
    },
    viewer: {
        can: ['view_quotations']
    }
}
```

### Backend
- [ ] Middleware de roles en server.py
- [ ] Proteger endpoints según rol
- [ ] Endpoint `/api/admin/equipos/precios` solo para admin
- [ ] Endpoint `/api/admin/users` solo para admin

### Frontend
- [ ] Mostrar/ocultar elementos según rol del usuario
- [ ] Almacenar rol en `sessionStorage` después del login
- [ ] Función `hasPermission(action)` en JavaScript

---

## 🎯 Fase 5: Testing & Deploy (1 hora)

### Testing Local
- [ ] Crear usuario admin
- [ ] Crear usuario CRM
- [ ] Crear usuario viewer
- [ ] Probar login con cada rol
- [ ] Verificar permisos (admin ve todo, otros limitados)
- [ ] Probar CRUD completo de usuarios
- [ ] Cambiar contraseñas
- [ ] Activar/desactivar usuarios
- [ ] Intentar eliminar último admin (debe fallar)

### Deploy a Railway
- [ ] Commit cambios: `git commit -m "feat: Sistema de gestión de usuarios con roles"`
- [ ] Push a main: `git push origin main`
- [ ] Verificar despliegue en Railway
- [ ] Ejecutar script de creación de admin en producción
- [ ] Probar login en https://web-production-3749b.up.railway.app/admin

### Documentación
- [ ] Actualizar `ESTADO_PROYECTO.md`
- [ ] Agregar capturas de pantalla (opcional)
- [ ] Documentar credenciales de usuarios de prueba
- [ ] Marcar como completado en TODO.md

---

## 📝 Mejoras Futuras (Post User Management)

### CRM Enhancements
- [ ] Exportar a Excel
- [ ] Notas por cotización
- [ ] Historial de cambios de estado
- [ ] Recordatorios/tareas
- [ ] Último contacto con cliente

### Dashboard Mejorado
- [ ] Gráficos con Chart.js
- [ ] Tendencias mensuales
- [ ] Tasa de conversión
- [ ] Valor promedio de cotización
- [ ] Comparativa entre ciudades

### Performance
- [ ] Cache de equipos y ciudades
- [ ] Paginación en backend
- [ ] Índices en PostgreSQL
- [ ] Compresión gzip

### Testing
- [ ] Tests unitarios con pytest
- [ ] Tests de endpoints
- [ ] Tests de generación PPTX
- [ ] CI/CD con GitHub Actions

### Seguridad
- [ ] JWT tokens en lugar de Basic Auth
- [ ] Rate limiting por usuario
- [ ] Logs de auditoría
- [ ] 2FA (opcional)

---

## 📌 Notas Importantes

### Credenciales Actuales (Hardcoded)
```
Usuario: admin
Password: Lu1sF3rN@ss@
```
**⚠️ ELIMINAR después de migrar a DB**

### URLs de Referencia
- **Producción:** https://web-production-3749b.up.railway.app
- **CRM:** /crm
- **Admin:** /admin
- **API Docs:** /docs (Swagger)

### Comandos Útiles
```bash
# Levantar backend
cd backend && source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Verificar salud
curl http://localhost:8001/health

# Ver logs Railway
railway logs

# Conectar a DB Railway
railway connect
```

---

## ✅ Criterios de Aceptación

El sistema de gestión de usuarios estará completo cuando:

1. ✅ Tabla `users` existe en PostgreSQL con todos los campos
2. ✅ Admin puede crear/editar/eliminar usuarios
3. ✅ Contraseñas hasheadas con bcrypt
4. ✅ Roles funcionan (admin, crm_user, viewer)
5. ✅ Login usa base de datos (no hardcoded)
6. ✅ Permisos aplicados en backend y frontend
7. ✅ UI funcional en admin.html
8. ✅ No se puede eliminar último admin
9. ✅ Desplegado en Railway
10. ✅ Documentación actualizada

---

_Estimado total: 8-12 horas de desarrollo_  
_Prioridad: ALTA - Base para futuras mejoras de seguridad_
