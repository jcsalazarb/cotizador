# ✨ NUEVOS PLACEHOLDERS AGREGADOS

## 📊 Placeholders de Valores Acumulados hasta Payback

Se agregaron **3 nuevos placeholders cortos** (máximo 8 letras) para mostrar los valores acumulados hasta alcanzar el punto de retorno de inversión (payback):

### 1️⃣ `{{ACUM_GEN}}` - Acumulado por Generación
- **Longitud**: 8 letras
- **Formato**: `$8,234,567`
- **Descripción**: Suma de todos los ahorros por generación de energía hasta el año del payback
- **Ejemplo**: Si el payback es en el año 3, suma los ahorros por generación de los años 1, 2 y 3

### 2️⃣ `{{ACUM_DED}}` - Acumulado por Deducción
- **Longitud**: 8 letras  
- **Formato**: `$2,500,000`
- **Descripción**: Suma de todos los ahorros por deducción de renta (50% base × 35% tasa) hasta el año del payback
- **Máximo**: 5 años (según legislación colombiana)

### 3️⃣ `{{ACUM_DEP}}` - Acumulado por Depreciación
- **Longitud**: 8 letras
- **Formato**: `$4,500,000`
- **Descripción**: Suma de todos los ahorros por depreciación fiscal (35% de depreciación anual) hasta el año del payback
- **Máximo**: 3 años (según legislación colombiana)

---

## 📐 USO EN POWERPOINT

### Opción 1: Tabla Compacta
```
┌──────────────────────┬──────────────┐
│ Concepto             │ Valor        │
├──────────────────────┼──────────────┤
│ Generación           │ {{ACUM_GEN}} │
│ Deducción Renta      │ {{ACUM_DED}} │
│ Depreciación         │ {{ACUM_DEP}} │
└──────────────────────┴──────────────┘
```

### Opción 2: Cuadros de Texto Pequeños
```
[Generación]
{{ACUM_GEN}}

[Deducción]  
{{ACUM_DED}}

[Depreciación]
{{ACUM_DEP}}
```

### Opción 3: Lista con Viñetas
```
• Ahorro por generación: {{ACUM_GEN}}
• Ahorro por deducción: {{ACUM_DED}}  
• Ahorro por depreciación: {{ACUM_DEP}}
```

---

## 🔢 EJEMPLO REAL

**Sistema de 4.4 kW con inversión de $15,000,000 COP y payback en año 3:**

```
Generación:    $8,234,567
Deducción:     $2,500,000
Depreciación:  $4,500,000
───────────────────────────
TOTAL:        $15,234,567
```

**Suma = Inversión** ✅ (en el año del payback)

---

## 📋 TOTAL DE PLACEHOLDERS ACTUALIZADOS

**Antes**: 28 placeholders  
**Ahora**: **31 placeholders** (28 + 3 nuevos)

---

## ✅ ESTADO

- ✅ Backend actualizado (`server.py`)
- ✅ Documentación actualizada (`PLACEHOLDERS_TEMPLATE.md`)
- ✅ Backend reiniciado automáticamente con `--reload`
- ⏳ **Pendiente**: Actualizar el archivo `Template-PreCotizacion.pptx` manualmente con los nuevos placeholders

---

## 🎯 PRÓXIMO PASO

Abrir el archivo PowerPoint:
```
/Users/jcsalazarb/Documents/GitHub/cotizador/Template/Template-PreCotizacion.pptx
```

Y agregar los placeholders `{{ACUM_GEN}}`, `{{ACUM_DED}}` y `{{ACUM_DEP}}` en la diapositiva de análisis financiero.

---

**Fecha de actualización**: 24 de noviembre de 2025
