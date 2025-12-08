# Solución: Inversores y Campo Default Faltante

**Fecha**: 4 de diciembre de 2025  
**Problemas reportados**: 2  
**Status**: ✅ RESUELTO

---

## 📋 Problemas Identificados

### Problema 1: Inversores no se activan hasta modificar Sistema Eléctrico
**Síntoma**: Al cargar la página, la sección de inversores permanece vacía hasta que el usuario manualmente cambia el valor del campo "Sistema Eléctrico".

**Causa raíz**: 
- El `init()` del frontend llamaba `cargarEquipos(null)` 
- Con `sistemaElectrico=null`, el código intencionalmente NO cargaba inversores
- Esto fue diseñado así para evitar mostrar inversores incompatibles antes de seleccionar el sistema
- Sin embargo, cuando se aplicaban valores por defecto, los inversores nunca se cargaban

### Problema 2: Campo `default` faltante en equipos.json
**Síntoma**: No todos los equipos en `equipos.json` tienen el campo `default`, lo que podría causar inconsistencias en la selección automática.

**Riesgo**:
```python
# Si un equipo no tiene "default", esto falla:
if equipo["default"]:  # KeyError si no existe el campo
    ...

# Solución correcta:
if equipo.get("default", False):  # Retorna False si no existe
    ...
```

---

## ✅ Soluciones Implementadas

### Solución 1: Agregar campo `default` a TODOS los equipos

**Archivo**: `backend/config/equipos.json`

Se agregó `"default": false` a todos los equipos que no lo tenían:
- ✅ 6 paneles actualizados (panel2-panel8, excepto panel1 que ya tenía `"default": true`)
- ✅ 8 inversores actualizados (inv2-inv9, excepto inv1 que ya tenía `"default": true`)
- ✅ 6 baterías actualizadas (bat2-bat7, excepto bat1 que ya tenía `"default": true`)

**Total**: 20 equipos actualizados

**Estado actual**:
```json
✅ Paneles:     7 equipos (1 default: panel1)
✅ Inversores:  9 equipos (1 default: inv1 - monofásico)
✅ Baterías:    7 equipos (1 default: bat1)
```

---

### Solución 2: Cargar inversores al inicio con sistema default

**Archivo**: `backend/static/index.html`

#### Cambio en `DOMContentLoaded`:

**ANTES**:
```javascript
// Cargar equipos iniciales con inversores ocultos
await cargarEquipos(null);  // ❌ No carga inversores
```

**DESPUÉS**:
```javascript
// FIX #2 y #4: Cargar equipos CON el sistema eléctrico default
const selectSistemaElectrico = document.getElementById('sistemaElectrico');
const sistemaElectricoDefault = selectSistemaElectrico ? selectSistemaElectrico.value : 'bifasico';

console.log(`🔧 Cargando inversores para sistema default: ${sistemaElectricoDefault}`);
await cargarEquipos(sistemaElectricoDefault);  // ✅ Carga inversores compatibles
```

#### Cambio en `aplicarValoresDefault`:

**ANTES**:
```javascript
if (defaults.sistemaElectrico) {
    selectSistemaElectrico.value = defaults.sistemaElectrico;
    // FIX #2 y #4: Cargar inversores compatibles automáticamente
    await cargarEquipos(defaults.sistemaElectrico);  // ❌ Carga duplicada
}
```

**DESPUÉS**:
```javascript
if (defaults.sistemaElectrico) {
    selectSistemaElectrico.value = defaults.sistemaElectrico;
    // NOTA: Los inversores se cargarán en DOMContentLoaded después de aplicar defaults
}
```

**Resultado**: Los inversores se cargan **UNA SOLA VEZ** con el sistema eléctrico correcto.

---

### Solución 3: Mejorar algoritmo de selección de defaults

**Archivo**: `backend/server.py`

#### Mejoras en `obtener_equipos_defaults()`:

1. **Documentación clara del algoritmo de 4 niveles**:
```python
"""
Algoritmo de selección (4 niveles de prioridad):
    1. Equipo marcado como default=True y compatible con sistema_electrico
    2. Primer equipo compatible (si no hay default para ese tipo)
    3. Equipo marcado como default=True (ignorando compatibilidad)
    4. Primer equipo disponible (fallback final)
"""
```

2. **Manejo robusto de defaults faltantes**:
```python
# Siempre usar .get("default", False) en lugar de ["default"]
panel_default = next((p for p in equipos["paneles"] if p.get("default", False)), None)

# Mensajes de advertencia claros
if not panel_default:
    panel_default = equipos["paneles"][0] if equipos["paneles"] else None
    if panel_default:
        print(f"⚠️ No hay panel default, usando primer disponible: {panel_default.get('id')}")
```

3. **Logs de debugging mejorados**:
```python
# NIVEL 1: Default + compatible
# NIVEL 2: Primer compatible (⚠️ 1 advertencia)
print(f"⚠️ No hay inversor default para {sistema_electrico}, buscando primer compatible...")

# NIVEL 3: Default sin compatibilidad (⚠️⚠️ 2 advertencias)
print(f"⚠️⚠️ No hay inversores compatibles con {sistema_electrico}, usando default general...")

# NIVEL 4: Fallback final (⚠️⚠️⚠️ 3 advertencias)
print(f"⚠️⚠️⚠️ Usando primer inversor disponible como fallback: {inversor_default.get('id')}")
```

---

## 🧪 Validación de la Solución

### Test 1: Script de validación automática

```bash
cd backend
python validate_defaults.py
```

**Resultado**:
```
✅ Sistema MONOFASICO: 4 inversores (1 default: inv1)
⚠️ Sistema BIFASICO: 3 inversores (0 defaults) → Usa NIVEL 2 (primer compatible)
⚠️ Sistema TRIFASICO: 2 inversores (0 defaults) → Usa NIVEL 2 (primer compatible)

✅ Paneles: 7 equipos (1 default: panel1)
✅ Baterías: 7 equipos (1 default: bat1)

📊 RESUMEN: 2 advertencias (bifásico/trifásico sin default)
```

### Test 2: Frontend local

1. **Abrir**: http://localhost:8000
2. **Verificar**:
   - ✅ HSP se calcula automáticamente (Fix #1)
   - ✅ Inversores aparecen inmediatamente (Fix #2)
   - ✅ Sistema eléctrico: "Bifásico" (default aplicado)
   - ✅ 3 inversores bifásicos visibles: inv2, inv5, inv9

### Test 3: API Backend

```bash
# Test health
curl http://localhost:8001/health
# ✅ {"status":"ok"}

# Test valores default
curl http://localhost:8001/api/valores-default
# ✅ {"sistemaElectrico":"bifasico", ...}

# Test equipos filtrados
curl "http://localhost:8001/api/equipos?sistemaElectrico=bifasico"
# ✅ 3 inversores bifásicos
```

---

## 📊 Impacto de los Cambios

| Aspecto | Antes | Después |
|---------|-------|---------|
| **UX al cargar página** | Inversores vacíos ❌ | Inversores visibles ✅ |
| **Consistencia de datos** | 20 equipos sin `default` ⚠️ | Todos tienen `default` ✅ |
| **Robustez del algoritmo** | Posibles KeyError ⚠️ | `.get()` seguro ✅ |
| **Logs de debugging** | Básicos | Detallados (4 niveles) ✅ |
| **Validación automática** | Manual | Script + documentación ✅ |

---

## 🔧 Configuración Recomendada

Para optimizar el sistema, el administrador debería marcar 1 default por tipo de sistema eléctrico:

### Estado Actual (Producción)
```
✅ Monofásico:  inv1 (default)
⚠️ Bifásico:    Sin default → Usa inv2 (primer compatible)
⚠️ Trifásico:   Sin default → Usa inv3 (primer compatible)
```

### Configuración Óptima Sugerida
```
✅ Monofásico:  inv1 (default) ← Ya configurado
➕ Bifásico:    inv2 (sugerido como default)
➕ Trifásico:   inv3 (sugerido como default)
```

**Cómo hacerlo**:
1. Acceder al panel admin: `/admin`
2. Sección "Inversores"
3. Marcar como default:
   - `inv2` (Huawei 5kW Bifásico)
   - `inv3` (SMA 10kW Trifásico)

---

## 📚 Archivos Modificados

| Archivo | Líneas | Tipo de Cambio |
|---------|--------|----------------|
| `backend/config/equipos.json` | 20 equipos | Agregar campo `default: false` |
| `backend/static/index.html` | ~1042-1047 | Cargar inversores al inicio |
| `backend/static/index.html` | ~391-398 | Eliminar carga duplicada |
| `backend/server.py` | 158-226 | Mejorar algoritmo + logs |

**Total**: 3 archivos, ~100 líneas modificadas

---

## 🚀 Próximos Pasos

### Inmediato (Producción)
- [x] Validar sintaxis local
- [x] Probar flujo completo local
- [ ] Commit + Push a GitHub
- [ ] Verificar auto-deploy Railway
- [ ] Confirmar en producción

### Opcional (Mejora continua)
- [ ] Marcar defaults para bifásico/trifásico en panel admin
- [ ] Re-ejecutar `validate_defaults.py` para confirmar 0 advertencias
- [ ] Agregar tests automatizados para flujo de defaults

---

## 🎯 Respuesta a tu Pregunta

> "Si el administrador selecciona un inversor default por cada tipo de sistema eléctrico, ¿cómo se manejaría este caso?"

**Respuesta**: 

El sistema ya está preparado para ese caso óptimo. Cuando agregues defaults para bifásico y trifásico:

1. **NIVEL 1 activado**: El algoritmo encontrará el inversor `default=true` + `tipo_sistema=bifasico`
2. **Sin advertencias**: Los logs no mostrarán `⚠️`
3. **Validación limpia**: `validate_defaults.py` mostrará 0 advertencias
4. **UX consistente**: Siempre se seleccionará el mismo inversor por defecto para cada tipo de sistema

**Actualmente** (sin defaults marcados):
- Bifásico → **NIVEL 2**: Usa `inv2` (primer compatible) ⚠️
- Trifásico → **NIVEL 2**: Usa `inv3` (primer compatible) ⚠️

**Con defaults marcados**:
- Bifásico → **NIVEL 1**: Usa `inv2` (default explícito) ✅
- Trifásico → **NIVEL 1**: Usa `inv3` (default explícito) ✅

**No hay riesgo de inconsistencia** porque:
- Todos los equipos ahora tienen el campo `default` (true o false)
- El algoritmo usa `.get("default", False)` → nunca KeyError
- Hay 4 niveles de fallback → siempre se selecciona algo

---

## ✅ Checklist de Verificación

- [x] Campo `default` agregado a todos los equipos (20 equipos)
- [x] Frontend carga inversores al inicio
- [x] HSP se calcula automáticamente (Fix previo)
- [x] Algoritmo robusto con 4 niveles de prioridad
- [x] Logs detallados con emojis de advertencia
- [x] Script de validación funcional
- [x] Tests locales exitosos (health, defaults, equipos)
- [x] Sintaxis validada (`py_compile` OK)
- [ ] Commit + Push pendiente
- [ ] Deploy a Railway pendiente

---

**Nota**: Las advertencias actuales (bifásico/trifásico sin default) son **informativas**, no errores. El sistema funciona correctamente usando el NIVEL 2 del algoritmo (primer compatible).
