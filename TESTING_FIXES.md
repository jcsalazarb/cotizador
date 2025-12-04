# 🧪 Testing de Fixes - 4 Problemas Detectados

## Fecha: 4 de diciembre de 2025

---

## ✅ **FIX #1: HSP no se actualiza con ciudad default**

### Problema Original
- Cuando se carga la página, la ciudad default se selecciona pero el campo HSP queda vacío
- Usuario debe cambiar manualmente la ciudad para que se calcule el HSP

### Solución Implementada
**Archivo**: `backend/static/index.html`  
**Línea**: ~343  
**Cambio**:
```javascript
// Aplicar ciudad por defecto
if (defaults.ciudad) {
    const selectCiudad = document.getElementById('ciudad');
    // ... código de selección ...
    // FIX #1: Calcular HSP automáticamente después de seleccionar ciudad
    calcularHSP();
}
```

### Cómo Probar
1. Abrir http://localhost:8000 (o URL de Railway)
2. Esperar a que cargue la página
3. **Verificar**: Campo "HSP Calculado" debe tener valor automáticamente (ej: 5.6 para Santa Marta)
4. ✅ **Esperado**: HSP se calcula sin intervención del usuario

---

## ✅ **FIX #2: Inversores no se cargan al seleccionar "Selección Manual SI"**

### Problema Original
- Al cambiar "Selección Manual" de NO a SI, los inversores no aparecen
- Usuario debe cambiar el "Sistema Eléctrico" para que se carguen inversores

### Solución Implementada
**Archivo**: `backend/static/index.html`  
**Línea**: ~394  
**Cambio**:
```javascript
// Aplicar sistema eléctrico
if (defaults.sistemaElectrico) {
    const selectSistemaElectrico = document.getElementById('sistemaElectrico');
    if (selectSistemaElectrico) {
        selectSistemaElectrico.value = defaults.sistemaElectrico;
        // FIX #2: Cargar inversores compatibles automáticamente
        await cargarEquipos(defaults.sistemaElectrico);
    }
}
```

### Cómo Probar
1. Cargar página (sistema eléctrico default = "bifasico")
2. Seleccionar "¿Seleccionar equipos manualmente?" → **SI**
3. **Verificar**: Sección de inversores debe mostrar inversores compatibles con bifásico
4. ✅ **Esperado**: Inversores visibles inmediatamente sin cambiar sistema eléctrico

---

## ✅ **FIX #3: Coherencia entre inversor default y sistema eléctrico**

### Problema Original
- Si el inversor marcado como "default" en equipos.json no es compatible con el sistema eléctrico seleccionado, el sistema puede fallar o seleccionar un inversor incompatible

### Solución Implementada
**Archivo**: `backend/server.py`  
**Función**: `obtener_equipos_defaults(equipos, sistema_electrico)`  
**Línea**: ~158  

**Lógica de selección inteligente**:
1. **Prioridad 1**: Buscar inversor default compatible con sistema eléctrico
2. **Prioridad 2**: Si no existe, usar primer inversor compatible
3. **Prioridad 3**: Si no hay compatibles, usar default general
4. **Fallback**: Primer inversor disponible

```python
# 1. Buscar inversor default que sea compatible con el sistema eléctrico
inversor_default = next(
    (i for i in equipos["inversores"] 
     if i.get("default", False) and i.get("tipo_sistema") == sistema_electrico),
    None
)

# 2. Si no hay default compatible, buscar el PRIMER inversor compatible
if not inversor_default:
    inversor_default = next(
        (i for i in equipos["inversores"] if i.get("tipo_sistema") == sistema_electrico),
        None
    )
```

### Cómo Probar

**Escenario A: Default coherente**
1. Panel Admin → Inversores → Marcar como default un inversor bifásico
2. Frontend → Seleccionar sistema eléctrico "Bifásico"
3. Selección manual NO → Generar cotización
4. ✅ **Esperado**: Usa el inversor default bifásico

**Escenario B: Default NO coherente**
1. Panel Admin → Inversores → Marcar como default un inversor trifásico
2. Frontend → Seleccionar sistema eléctrico "Bifásico"
3. Selección manual NO → Generar cotización
4. ✅ **Esperado**: Sistema usa el PRIMER inversor bifásico (no el default trifásico)
5. Console log debe mostrar: `⚠️ No hay inversor default para bifasico, buscando primer compatible...`

**Escenario C: Sin compatibles**
1. Panel Admin → Eliminar todos los inversores bifásicos
2. Frontend → Seleccionar sistema eléctrico "Bifásico"
3. Selección manual NO → Generar cotización
4. ✅ **Esperado**: Sistema usa inversor default general o muestra error claro

---

## ✅ **FIX #4: Inversor no seleccionado con Selección Manual NO**

### Problema Original
- Usuario cambia sistema eléctrico con "Selección Manual = NO"
- Sistema muestra mensaje "X inversores cargados" pero no selecciona ninguno
- Cotización falla porque req.inversor = None

### Solución Implementada
**Archivo**: `backend/server.py`  
**Endpoint**: `POST /api/cotizar`  
**Línea**: ~1908  

**Cambio**:
```python
# Si seleccionManual es NO, usar equipos por defecto
if req.seleccionManual == "NO":
    # FIX #4: Pasar sistema eléctrico para selección inteligente de inversor
    defaults = obtener_equipos_defaults(equipos, req.sistemaElectrico)
    req_dict["panel"] = defaults["panel"]
    req_dict["inversor"] = defaults["inversor"]
    
    # Log para debugging
    print(f"🔧 Selección automática de equipos:")
    print(f"   Sistema eléctrico: {req.sistemaElectrico}")
    print(f"   Inversor default: {defaults['inversor']}")
```

### Cómo Probar
1. Llenar formulario con todos los datos obligatorios
2. **"¿Seleccionar equipos manualmente?"** → **NO**
3. **"Sistema Eléctrico"** → Cambiar entre opciones (monofásico, bifásico, trifásico)
4. Click "GENERAR COTIZACIÓN"
5. **Verificar backend logs**: Debe mostrar:
   ```
   🔧 Selección automática de equipos:
      Sistema eléctrico: bifasico
      Panel default: panel1
      Inversor default: inv2  ← DEBE TENER VALOR
   ```
6. ✅ **Esperado**: Cotización se genera exitosamente con inversor compatible

---

## 🎯 Resumen de Cambios

### Frontend (`backend/static/index.html`)
- **2 modificaciones** en función `aplicarValoresDefault()`
- Trigger automático de `calcularHSP()` al aplicar ciudad
- Trigger automático de `cargarEquipos()` al aplicar sistema eléctrico

### Backend (`backend/server.py`)
- **1 función refactorizada**: `obtener_equipos_defaults()` ahora acepta `sistema_electrico`
- **1 endpoint actualizado**: `POST /api/cotizar` pasa sistema eléctrico a defaults
- Lógica inteligente de 4 niveles para selección de inversor

---

## 📋 Checklist de Testing

### Pre-Despliegue (Local)
- [ ] FIX #1: HSP se calcula automáticamente con ciudad default
- [ ] FIX #2: Inversores aparecen al seleccionar "Manual SI"
- [ ] FIX #3: Inversor default coherente con sistema eléctrico
- [ ] FIX #4: Cotización funciona con "Manual NO" y cambio de sistema

### Post-Despliegue (Railway)
- [ ] Verificar endpoint `/api/valores-default` retorna sistemaElectrico
- [ ] Probar flujo completo: carga → selección → cotización → email
- [ ] Verificar logs en Railway para mensajes de selección automática
- [ ] Probar casos edge: sin defaults, sin compatibles, cambios rápidos

---

## 🚨 Casos Edge a Considerar

### Caso 1: Usuario rápido
**Escenario**: Usuario cambia sistema eléctrico múltiples veces rápidamente antes de que terminen de cargar inversores  
**Mitigación**: `cargarEquipos()` es async, última llamada prevalece

### Caso 2: Admin elimina inversores compatibles
**Escenario**: No hay inversores para el sistema eléctrico seleccionado  
**Comportamiento**: Sistema usa default general o primer disponible (fallback)

### Caso 3: Defaults JSON corruptos
**Escenario**: `equipos.json` tiene defaults inválidos o sin `tipo_sistema`  
**Comportamiento**: Sistema usa primer equipo disponible (graceful degradation)

---

## 📊 Métricas de Éxito

✅ **HSP calculado**: 100% de usuarios ven HSP al cargar página  
✅ **Inversores visibles**: 0 clics adicionales necesarios  
✅ **Coherencia**: 100% compatibilidad sistema-inversor  
✅ **Tasa conversión**: Reducción de errores en cotización  

---

## 🔗 Commits Relacionados

- **Commit anterior**: `fcbd8d7` - Feature: Add sistemaElectrico tracking
- **Este commit**: Pendiente - Fix: 4 problemas de UX en selección de equipos
