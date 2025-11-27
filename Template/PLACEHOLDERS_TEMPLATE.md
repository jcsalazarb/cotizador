# 📋 PLACEHOLDERS DEL TEMPLATE POWERPOINT

## ✅ LISTA COMPLETA DE ETIQUETAS QUE BUSCA EL BACKEND

El archivo `Template-PreCotizacion.pptx` debe contener estos placeholders (etiquetas) **EXACTAMENTE** como se muestran aquí (con dobles llaves y MAYÚSCULAS):

**Total: 32 placeholders** - ⚡ **TODOS con máximo 8 letras**

### 📊 INFORMACIÓN GENERAL
```
{{COT_ID}}   → ID único de la cotización (ej: "NASSA-1732483200")
{{FECHA}}    → Fecha de la cotización (ej: "2025-11-24")
```

### 👤 DATOS DEL CLIENTE
```
{{NOMBRE}}   → Nombre completo del cliente
{{EMAIL}}    → Correo electrónico
{{TELEFONO}} → Número de teléfono/WhatsApp
{{CIUDAD}}   → Ciudad del cliente
{{DIRECC}}   → Dirección completa
{{NIC}}      → Número de Identificación del Cliente (NIC)
```

### ⚡ CONSUMO ENERGÉTICO
```
{{CONSUMO}}  → Consumo mensual (ej: "450 kWh")
{{FACTURA}}  → Valor de la factura (ej: "$350,000 COP")
{{VAL_KWH}}  → Valor por kWh (ej: "$778 COP")
{{HSPC}}     → Hora Solar Pico (HSP) usada en el cálculo (ej: "5.6")
{{PCTDIA}}   → % consumo en horas de día (ej: "60%")
```

### 🏠 CARACTERÍSTICAS DEL INMUEBLE
```
{{VIVIENDA}} → Tipo de vivienda (Casa, Apartamento, Local, Empresa)
{{SIS_ELEC}} → Sistema eléctrico (Monofásico, Bifásico, Trifásico)
{{TIPO_FV}}  → Tipo de sistema FV (ongrid, offgrid, hibrido_incluido, hibrido_opcional)
{{NPISOS}}   → Número de pisos (ej: "1", "2")
{{AREA}}     → Área disponible en m2 (ej: "24.5")
```

### 🔧 EQUIPAMIENTO
```
{{N_PANEL}}  → Cantidad de paneles (ej: "8")
{{M_PANEL}}  → Modelo del panel (ej: "Panel Solar 550W Monocristalino")
{{N_INVER}}  → Cantidad de inversores (ej: "1")
{{M_INVER}}  → Modelo del inversor (ej: "Inversor Híbrido 5kW")
{{N_BATER}}  → Cantidad de baterías (ej: "1" o " " si no hay batería)
{{M_BATER}}  → Modelo de la batería (ej: "Batería 10kWh" o " " si no hay batería)
```

**⚠️ NOTA IMPORTANTE SOBRE BATERÍAS:**
- Si el sistema NO incluye baterías (ongrid), `{{N_BATER}}` y `{{M_BATER}}` mostrarán un espacio en blanco " "
- Si el sistema SÍ incluye baterías (offgrid, hibrido_incluido), mostrarán "1" y el modelo respectivamente
- Esto permite que el template funcione tanto para sistemas con como sin baterías

### 📈 ESPECIFICACIONES TÉCNICAS
```
{{CAP_KW}}   → Capacidad instalada (ej: "4.40 kW")
{{GEN_MES}}  → Generación mensual (ej: "600 kWh")
```

### 💰 ANÁLISIS FINANCIERO
```
{{INVER}}    → Inversión total del sistema (ej: "$15,000,000 COP")
{{SUBTOT}}   → Subtotal antes de IVA (ej: "$12,605,042 COP")
{{AHO_MES}}  → Ahorro mensual en energía (ej: "$467,100 COP")
{{RETORNO}}  → Tiempo de retorno (ej: "2.7 años")
{{PORC_PR}}  → Porcentaje de producción mensual (ej: "133%")
{{ACUM_GEN}} → Acumulado por generación hasta payback (ej: "$8,234,567")
{{ACUM_DED}} → Acumulado por deducción hasta payback (ej: "$2,500,000")
{{ACUM_DEP}} → Acumulado por depreciación hasta payback (ej: "$4,500,000")
{{TOT_ACUM}} → Total acumulado hasta payback (ej: "$15,234,567 COP")
```

---

## 📊 TABLA DE AHORROS (25 AÑOS)

El template también debe contener una **tabla llamada "TABLA_AHORROS"** con los siguientes encabezados:

### Opción 1: Nombre de tabla definido
La tabla debe tener el nombre "TABLA_AHORROS" en PowerPoint (click derecho > propiedades).

### Opción 2: Encabezados detectables
Si no tiene nombre, el backend buscará una tabla con encabezados que contengan estas palabras:
- **"año"** (o "ano") → Columna del año
- **"valor kwh"** (o "valorkwh", "valor_kwh") → Valor del kWh
- **"producción"** (o "produccion") → Producción anual
- **"generación"** (o "generacion", "ahorro generacion") → Ahorro por generación
- **"depreciación"** (o "depreciacion") → Ahorro por depreciación
- **"deducción"** (o "deduccion") → Ahorro por deducción de renta
- **"costo"** (o "mantenimiento") → Costo de mantenimiento
- **"ahorro"** (o "ahorro total", "total año") → Ahorro total del año
- **"acumulado"** → Ahorro acumulado
- **"roi"** → Retorno de inversión (%)

### Estructura esperada de la tabla:
```
| Año | Valor kWh | Producción | Gen. | Deprec. | Deducción | Mantenim. | Total Año | Acumulado | ROI % |
|-----|-----------|------------|------|---------|-----------|-----------|-----------|-----------|-------|
|  1  |   $778    |  2,904 kWh | $... |   $...  |    $...   |    $...   |    $...   |    $...   | -45%  |
|  2  |   $821    |  5,805 kWh | $... |   $...  |    $...   |    $...   |    $...   |    $...   | -12%  |
| ... |    ...    |     ...    | ...  |   ...   |    ...    |    ...    |    ...    |    ...    |  ...  |
```

⚠️ **IMPORTANTE**: La tabla debe tener al menos **13 filas** (1 encabezado + 12 filas de datos para los primeros 12 años).

---

## 🎨 LOGO DE LA EMPRESA

Para incluir el logo de NASSA Solar en el template:

1. **Insertar logo en PowerPoint**:
   - Insertar → Imagen → seleccionar logo de NASSA Solar
   - Colocar en la posición deseada (esquina superior, encabezado, etc.)
   - El logo se mantendrá en todas las diapositivas donde se coloque

2. **Recomendaciones**:
   - Usar formato PNG con fondo transparente
   - Tamaño recomendado: 150-200px de ancho
   - Ubicaciones típicas:
     - Esquina superior izquierda/derecha
     - Centro del encabezado
     - Pie de página
   - Archivo disponible en: `/assets/images/loggo-Nassa.png`

---

## 📝 EJEMPLO DE USO EN POWERPOINT

### Diapositiva de Equipamiento (ejemplo):

```
╔══════════════════════════════════════════════════════════╗
║  EQUIPAMIENTO DEL SISTEMA SOLAR                          ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Paneles Solares:                                        ║
║  • Cantidad: {{N_PANEL}}                                ║
║  • Modelo: {{M_PANEL}}                                  ║
║                                                          ║
║  Inversor:                                               ║
║  • Cantidad: {{N_INVER}}                                ║
║  • Modelo: {{M_INVER}}                                  ║
║                                                          ║
║  Baterías:                                               ║
║  • Cantidad: {{N_BATER}}                                ║
║  • Modelo: {{M_BATER}}                                  ║
║                                                          ║
║  Capacidad Total: {{CAP_KW}}                            ║
║  Generación Mensual: {{GEN_MES}}                        ║
╚══════════════════════════════════════════════════════════╝
```

**Resultado con batería:**
```
Baterías:
• Cantidad: 1
• Modelo: Batería LiFePO4 10kWh
```

**Resultado sin batería (ongrid):**
```
Baterías:
• Cantidad:  
• Modelo:  
```
(Los campos aparecen vacíos pero la estructura se mantiene)

---

### Diapositiva de Análisis Financiero (ejemplo):

```
╔══════════════════════════════════════════════════════════╗
║  ANÁLISIS FINANCIERO HASTA EL PAYBACK                    ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Inversión Total: {{INVER}}                             ║
║  Tiempo de Retorno: {{RETORNO}}                         ║
║                                                          ║
║  ┌─────────────────────────────────────────────────┐   ║
║  │ AHORROS ACUMULADOS HASTA EL PAYBACK             │   ║
║  ├─────────────────────────────────────────────────┤   ║
║  │ Por Generación:    {{ACUM_GEN}}                 │   ║
║  │ Por Deducción:     {{ACUM_DED}}                 │   ║
║  │ Por Depreciación:  {{ACUM_DEP}}                 │   ║
║  ├─────────────────────────────────────────────────┤   ║
║  │ TOTAL ACUMULADO:   {{TOT_ACUM}}                 │   ║
║  └─────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════╝
```

**Resultado real (ejemplo con sistema de 4.4kW):**
```
┌─────────────────────────────────────────────────┐
│ AHORROS ACUMULADOS HASTA EL PAYBACK             │
├─────────────────────────────────────────────────┤
│ Por Generación:    $8,234,567                   │
│ Por Deducción:     $2,500,000                   │
│ Por Depreciación:  $4,500,000                   │
├─────────────────────────────────────────────────┤
│ TOTAL ACUMULADO:   $15,234,567 COP              │
└─────────────────────────────────────────────────┘
```

⚡ **NOTA:** TODOS los placeholders tienen máximo 8 letras para caber en cuadros de texto pequeños.

---

### Diapositiva de Cliente (ejemplo):

```
╔══════════════════════════════════════════════════════════╗
║  DATOS DEL CLIENTE                                       ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Nombre:    {{NOMBRE}}                                  ║
║  Email:     {{EMAIL}}                                   ║
║  Teléfono:  {{TELEFONO}}                                ║
║  NIC:       {{NIC}}                                     ║
║  Ciudad:    {{CIUDAD}}                                  ║
║  Dirección: {{DIRECC}}                                  ║
║                                                          ║
║  Consumo Mensual: {{CONSUMO}}                           ║
║  Valor Factura:   {{FACTURA}}                           ║
║  Valor kWh:       {{VAL_KWH}}                           ║
╚══════════════════════════════════════════════════════════╝
```

## 🔍 VERIFICACIÓN DEL TEMPLATE

### Checklist antes de usar el template:

- [ ] Todos los placeholders están escritos EXACTAMENTE como se muestran (dobles llaves, MAYÚSCULAS)
- [ ] La tabla de ahorros tiene nombre "TABLA_AHORROS" O encabezados detectables
- [ ] La tabla tiene al menos 13 filas (1 header + 12 datos)
- [ ] El logo de NASSA Solar está insertado en el template
- [ ] No hay espacios extras dentro de los placeholders (❌ `{{ NOMBRE }}` ✅ `{{NOMBRE}}`)
- [ ] Los placeholders están en cuadros de texto editables, no en imágenes

### Cómo probar:
1. Abrir el template en PowerPoint
2. Buscar (Ctrl+F / Cmd+F) por "{{" para encontrar todos los placeholders
3. Verificar que cada uno está en la lista de arriba
4. Hacer clic derecho en la tabla → Propiedades → verificar nombre "TABLA_AHORROS"

---

## 📄 UBICACIÓN DEL TEMPLATE

```
/Users/jcsalazarb/Documents/GitHub/cotizador/Template/Template-PreCotizacion.pptx
```

⚠️ El nombre del archivo debe ser **exactamente** `Template-PreCotizacion.pptx` (con guion y "C" mayúscula en Cotizacion).

---

## 🐛 TROUBLESHOOTING

### "Template PPTX no encontrado"
- Verificar que el archivo existe en la ruta correcta
- Verificar el nombre exacto del archivo (case-sensitive en macOS)

### "No se encontró la tabla TABLA_AHORROS"
- Verificar el nombre de la tabla en PowerPoint
- Alternativamente, asegurarse de que los encabezados contienen las palabras clave

### "Placeholders no se reemplazan"
- Verificar que no hay espacios dentro de las llaves: `{{NOMBRE}}` ✅ vs `{{ NOMBRE }}` ❌
- Verificar que están en MAYÚSCULAS
- Verificar que están en cuadros de texto editables, no en grupos o imágenes

---

## 📞 CONTACTO

Si tienes dudas sobre los placeholders, revisa el código en:
`backend/server.py` líneas 350-376 (función `build_placeholders`)
