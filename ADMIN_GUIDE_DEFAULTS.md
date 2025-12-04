# 📘 Guía del Administrador - Configuración de Defaults Coherentes

## Sistema de Defaults Inteligente - NASSA Solar

---

## 🎯 Objetivo

Garantizar que los equipos marcados como "default" sean **coherentes** con el tipo de sistema eléctrico seleccionado, evitando errores en cotizaciones automáticas.

---

## 🔧 Cómo Funciona el Sistema

### Flujo de Selección Automática (Cuando usuario elige "Selección Manual = NO")

```
Usuario selecciona Sistema Eléctrico: "Bifásico"
            ↓
Sistema busca inversores en este orden:
            ↓
[1] ¿Hay inversor marcado "default" Y tipo_sistema="bifasico"?
    ├─ SÍ → ✅ Usa ese inversor
    └─ NO → Continúa a [2]
            ↓
[2] ¿Hay ALGÚN inversor con tipo_sistema="bifasico"?
    ├─ SÍ → ✅ Usa el PRIMERO de la lista
    └─ NO → Continúa a [3]
            ↓
[3] ¿Hay inversor marcado "default" (sin restricción de tipo)?
    ├─ SÍ → ⚠️ Usa ese (posible incompatibilidad)
    └─ NO → Continúa a [4]
            ↓
[4] Usa el PRIMER inversor disponible (cualquier tipo)
    └─ ⚠️ Riesgo alto de incompatibilidad
```

---

## ✅ Configuración Recomendada

### Opción A: **Default por Tipo de Sistema** (MEJOR)

Si tienes inversores diferentes para cada sistema:

```json
// equipos.json
{
  "inversores": [
    {
      "id": "inv1",
      "nombre": "Inversor Monofásico 3kW",
      "tipo_sistema": "monofasico",
      "default": true  ← Marcar como default
    },
    {
      "id": "inv2",
      "nombre": "Inversor Bifásico 5kW",
      "tipo_sistema": "bifasico",
      "default": true  ← Marcar como default
    },
    {
      "id": "inv3",
      "nombre": "Inversor Trifásico 10kW",
      "tipo_sistema": "trifasico",
      "default": true  ← Marcar como default
    }
  ]
}
```

**Ventajas**:
- ✅ Máxima coherencia
- ✅ Sistema siempre encuentra default compatible
- ✅ Cotizaciones automáticas 100% confiables

**Pasos en Panel Admin**:
1. Ve a **Admin → Inversores**
2. Para CADA tipo de sistema, marca UN inversor como default
3. Verifica que cada default tenga `tipo_sistema` correcto

---

### Opción B: **Default Universal** (Alternativa)

Si solo tienes inversores de un tipo o quieres usar uno general:

```json
{
  "inversores": [
    {
      "id": "inv_universal",
      "nombre": "Inversor Híbrido Universal",
      "tipo_sistema": "bifasico",  ← El más común en Colombia
      "default": true
    },
    {
      "id": "inv2",
      "nombre": "Otro Inversor Bifásico",
      "tipo_sistema": "bifasico"
    }
  ]
}
```

**Ventajas**:
- ✅ Más simple de gestionar
- ✅ Funciona si todos tus proyectos son similares
- ⚠️ Puede no ser óptimo para todos los casos

**Pasos en Panel Admin**:
1. Marca como default el inversor **más común** en tus proyectos
2. Asegúrate que su `tipo_sistema` coincida con el default de frontend

---

## ❌ Configuraciones a EVITAR

### ❌ Caso 1: Default incompatible

```json
{
  "inversores": [
    {
      "id": "inv_trifasico",
      "tipo_sistema": "trifasico",
      "default": true  ← DEFAULT
    }
  ]
}
```

**Problema**: Si usuario selecciona "bifásico", sistema usará inversor trifásico (incompatible).

**Solución**: Agregar inversor bifásico y marcarlo como default también.

---

### ❌ Caso 2: Sin defaults

```json
{
  "inversores": [
    {
      "id": "inv1",
      "tipo_sistema": "monofasico"
      // Sin default: false
    },
    {
      "id": "inv2",
      "tipo_sistema": "bifasico"
      // Sin default: false
    }
  ]
}
```

**Problema**: Sistema usa PRIMER inversor de la lista (puede ser incompatible).

**Solución**: Marcar al menos uno como default (preferiblemente uno por tipo).

---

### ❌ Caso 3: Múltiples defaults del mismo tipo

```json
{
  "inversores": [
    {
      "id": "inv1",
      "tipo_sistema": "bifasico",
      "default": true  ← DEFAULT 1
    },
    {
      "id": "inv2",
      "tipo_sistema": "bifasico",
      "default": true  ← DEFAULT 2
    }
  ]
}
```

**Problema**: Sistema usa el PRIMERO que encuentre (comportamiento impredecible).

**Solución**: Solo un default por tipo de sistema.

---

## 🔍 Verificación de Configuración

### Checklist para Admin

- [ ] **Cada tipo de sistema** (monofásico, bifásico, trifásico) tiene **AL MENOS 1 inversor** en catálogo
- [ ] **Cada tipo de sistema** tiene **MÁXIMO 1 inversor** marcado como default
- [ ] El campo `tipo_sistema` de cada inversor es correcto
- [ ] El inversor default más común coincide con el default del frontend (`bifasico`)

### Cómo Verificar

1. **Panel Admin** → **Inversores**
2. Filtra por cada tipo de sistema
3. Verifica que haya **exactamente 1** con badge "⭐ DEFAULT"
4. Si no lo hay, márcalo usando botón "⭐ Marcar Default"

---

## 🧪 Testing de Coherencia

### Test 1: Default Coherente

**Setup**:
```json
inv_bifasico: { tipo_sistema: "bifasico", default: true }
```

**Pasos**:
1. Frontend → Sistema Eléctrico: "Bifásico"
2. Selección Manual: "NO"
3. Generar cotización

**Esperado**: ✅ Usa `inv_bifasico`

---

### Test 2: Default Incoherente

**Setup**:
```json
inv_trifasico: { tipo_sistema: "trifasico", default: true }
// NO hay inversor bifásico default
```

**Pasos**:
1. Frontend → Sistema Eléctrico: "Bifásico"
2. Selección Manual: "NO"
3. Generar cotización

**Esperado**: 
- ⚠️ Backend log: `No hay inversor default para bifasico, buscando primer compatible...`
- ✅ Sistema usa PRIMER inversor bifásico disponible (ignora default trifásico)

---

### Test 3: Sin Compatibles

**Setup**:
```json
// Solo inversores trifásicos en catálogo
inv_trifasico: { tipo_sistema: "trifasico", default: true }
```

**Pasos**:
1. Frontend → Sistema Eléctrico: "Bifásico"
2. Selección Manual: "NO"
3. Generar cotización

**Esperado**: 
- ⚠️ Backend log: `No hay inversores compatibles con bifasico, usando default general...`
- ⚠️ Sistema usa inversor trifásico (INCOMPATIBLE pero funcional)
- 📧 Email se envía con advertencia en logs

---

## 📊 Dashboard de Coherencia (Futuro)

### Métricas Sugeridas

```
Coherencia de Defaults: 100%
├─ Monofásico: ✅ 1 default compatible
├─ Bifásico: ✅ 1 default compatible
└─ Trifásico: ✅ 1 default compatible

Cobertura de Sistemas: 100%
├─ Monofásico: 3 inversores (1 default)
├─ Bifásico: 5 inversores (1 default)
└─ Trifásico: 2 inversores (1 default)

Fallbacks Detectados (últimos 30 días):
├─ Nivel 2 (primer compatible): 2 veces
└─ Nivel 3 (default general): 0 veces
```

---

## 🚨 Alertas Automáticas (Recomendación)

El sistema debería enviar alertas cuando:

1. ❌ **Sin default para un tipo**: "No hay inversor default para bifásico"
2. ⚠️ **Múltiples defaults**: "2 inversores bifásicos marcados como default"
3. ⚠️ **Fallback usado**: "Sistema usó nivel 2/3 para seleccionar inversor"
4. 🔴 **Incompatibilidad**: "Inversor trifásico usado para sistema bifásico"

---

## 📞 Soporte

Si detectas comportamiento inesperado:

1. **Revisa logs del backend** en Railway/consola
2. **Busca mensajes** que empiecen con:
   - `🔧 Selección automática de equipos`
   - `⚠️ No hay inversor default para...`
3. **Verifica equipos.json** en Panel Admin
4. **Contacta desarrollo** con logs completos

---

## 🔗 Referencias

- **Código fuente**: `backend/server.py` → función `obtener_equipos_defaults()`
- **Testing**: `TESTING_FIXES.md` → FIX #3 y #4
- **Panel Admin**: `http://localhost:8000/admin` (requiere credenciales)

---

Última actualización: 4 de diciembre de 2025
