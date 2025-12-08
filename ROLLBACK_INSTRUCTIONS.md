# 🔄 Instrucciones de Rollback

## ⚠️ Si algo sale mal con PostgreSQL

Este documento explica cómo regresar al sistema JSON estable en caso de problemas.

---

## 📍 Puntos de Restauración Creados

### **Tag: v1.0-json-stable**
- **Commit**: ddf0dd3
- **Fecha**: 6 de diciembre 2025
- **Estado**: Sistema JSON con flush/fsync funcionando
- **Incluye**: 
  - Admin panel completo con nuevos parámetros
  - Tabla de legalización
  - Campos MICRO/STRING inversores
  - Fix persistencia equipos.json

### **Branch: backup-json-system**
- **Mismo estado que el tag**
- **Uso**: Referencia permanente del código estable

---

## 🚨 Opciones de Rollback (de más rápida a más completa)

### **Opción 1: Railway Rollback (30 segundos)**

**Cuándo usar**: Problema en producción, necesitas arreglarlo YA

**Pasos**:
1. Ir a: https://railway.app/project/tu-proyecto
2. Click en "Deployments"
3. Buscar deployment con tag `v1.0-json-stable`
4. Click "Redeploy"

**Resultado**: Railway vuelve a versión estable sin tocar Git

---

### **Opción 2: Revertir Último Commit (2 minutos)**

**Cuándo usar**: El último cambio causó el problema

```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador

# Ver últimos commits
git log --oneline -5

# Revertir último commit (crea nuevo commit que deshace cambios)
git revert HEAD

# Push (Railway auto-deploya)
git push origin main
```

**✅ Ventaja**: No destruye historial
**✅ Seguro**: Puede revertirse nuevamente si te equivocas

---

### **Opción 3: Regresar al Tag v1.0-json-stable (5 minutos)**

**Cuándo usar**: Múltiples commits fallaron, necesitas volver al estado 100% estable

```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador

# Ver tags disponibles
git tag -l

# Regresar al tag estable
git reset --hard v1.0-json-stable

# Forzar push (CUIDADO: sobrescribe historial remoto)
git push origin main --force

# Verificar en Railway que auto-deploye
```

**⚠️ Advertencia**: Borra commits posteriores al tag
**✅ Garantía**: Estado 100% probado y funcional

---

### **Opción 4: Restaurar desde Branch Backup (5 minutos)**

**Cuándo usar**: Alternativa a la Opción 3

```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador

# Ver branches disponibles
git branch -a

# Regresar al branch backup
git reset --hard origin/backup-json-system

# Forzar push
git push origin main --force
```

---

### **Opción 5: Checkout a Commit Específico (avanzado)**

**Cuándo usar**: Sabes exactamente qué commit quieres

```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador

# Ver historial completo
git log --oneline --graph --all

# Regresar a commit específico
git reset --hard ddf0dd3

# Forzar push
git push origin main --force
```

---

## 🧪 Rollback con Testing Previo (Recomendado)

Si tienes tiempo, prueba antes de forzar en producción:

```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador

# 1. Crear branch temporal
git checkout -b test-rollback

# 2. Regresar al estado estable en este branch
git reset --hard v1.0-json-stable

# 3. Probar localmente
cd backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# 4. Si funciona bien, aplicar a main
git checkout main
git reset --hard v1.0-json-stable
git push origin main --force

# 5. Limpiar branch temporal
git branch -D test-rollback
```

---

## 📊 Comparación de Opciones

| Opción | Velocidad | Afecta Historial | Requiere --force | Riesgo |
|--------|-----------|------------------|------------------|--------|
| Railway Redeploy | ⚡⚡⚡ 30s | No | No | Bajo |
| git revert | ⚡⚡ 2min | No (agrega) | No | Muy Bajo |
| git reset tag | ⚡ 5min | Sí (borra) | Sí | Medio |
| git reset branch | ⚡ 5min | Sí (borra) | Sí | Medio |
| git reset commit | ⚡ 5min | Sí (borra) | Sí | Medio |

---

## ⚠️ Antes de Hacer Rollback

### **1. Diagnosticar el problema**
```bash
# Ver logs de Railway
railway logs

# Ver estado actual
git log --oneline -5
git status
```

### **2. Crear backup del estado actual** (por si acaso)
```bash
git branch backup-antes-rollback
git push origin backup-antes-rollback
```

### **3. Notificar** (si trabajan más personas)
- Avisar en equipo que harás rollback
- Esperar confirmación antes de `--force`

---

## 🎯 Rollback Recomendado para PostgreSQL

Si la migración a PostgreSQL falla:

```bash
# 1. Railway rollback inmediato (mientras arreglas)
# Dashboard → Deployments → Redeploy v1.0-json-stable

# 2. En tu máquina local
cd /Users/jcsalazarb/Documents/GitHub/cotizador

# 3. Crear branch para investigar qué falló
git checkout -b debug-postgresql
git add .
git commit -m "WIP: Estado fallido PostgreSQL para debugging"
git push origin debug-postgresql

# 4. Regresar main al estado estable
git checkout main
git reset --hard v1.0-json-stable
git push origin main --force

# 5. Railway auto-deploya versión estable
# 6. Investigar problema en branch debug-postgresql
# 7. Cuando esté arreglado, merge desde debug-postgresql
```

---

## 📞 Contactos de Emergencia

Si no funciona ningún rollback:

1. **Repositorio GitHub**: https://github.com/jcsalazarb/cotizador
2. **Railway Project**: https://railway.app/project/tu-proyecto
3. **Backup local**: `/Users/jcsalazarb/Documents/GitHub/cotizador`

---

## ✅ Verificación Post-Rollback

Después de hacer rollback, verifica:

```bash
# 1. Ver commit actual
git log --oneline -1

# 2. Verificar archivos críticos
ls -la backend/config/equipos.json
ls -la backend/server.py

# 3. Probar localmente
cd backend
source venv/bin/activate
uvicorn server:app --port 8001

# 4. Verificar en producción
curl https://web-production-3749b.up.railway.app/health

# 5. Abrir admin panel
# https://web-production-3749b.up.railway.app/admin.html
```

---

## 🔒 Prevención de Futuros Problemas

1. **Siempre crear tag antes de cambios grandes**:
   ```bash
   git tag -a v1.x-descripcion -m "Mensaje"
   git push origin v1.x-descripcion
   ```

2. **Commits pequeños y testeables**:
   - NO: 1 commit gigante con todo
   - SÍ: 5 commits pequeños, cada uno testeable

3. **Testing local exhaustivo**:
   - Probar TODOS los endpoints antes de push
   - Usar Postman/Insomnia para testing

4. **Railway staging environment** (opcional):
   - Crear segundo proyecto Railway "cotizador-staging"
   - Probar ahí primero, luego producción

---

## 📝 Log de Rollbacks

Documenta aquí si haces rollback:

```
| Fecha | Razón | Opción Usada | Commit Original | Resultado |
|-------|-------|--------------|-----------------|-----------|
| (vacío) | - | - | - | - |
```

---

## 🎓 Referencias

- **Git Reset vs Revert**: https://www.atlassian.com/git/tutorials/resetting-checking-out-and-reverting
- **Railway Deployments**: https://docs.railway.app/deploy/deployments
- **Git Force Push**: https://git-scm.com/docs/git-push#Documentation/git-push.txt---force

---

**Última actualización**: 6 de diciembre 2025  
**Versión estable actual**: v1.0-json-stable (commit ddf0dd3)
