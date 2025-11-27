# 📝 ACTUALIZAR TEMPLATE PPTX - Instrucciones

## ⚠️ Problema Detectado

De los **35 placeholders** definidos en el sistema, **17 están presentes** en el Template PPTX actual.

**18 placeholders NO están en el template** y por eso no se reemplazan con sus valores.

**✅ Actualización**: El backend ahora detecta y reemplaza placeholders dentro de objetos **SmartArt**.

---

## 📋 Placeholders que FALTAN en el Template

Debes agregar estos placeholders manualmente en `Template/Template-PreCotizacion.pptx`:

### 📧 Datos del Cliente (5 faltantes)
- `{{CIUDAD}}` - Ciudad del cliente
- `{{DIRECC}}` - Dirección completa
- `{{CONSUMO}}` - Consumo mensual en kWh
- `{{FACTURA}}` - Valor de la factura mensual
- `{{VAL_KWH}}` - Valor del kWh

### ⚡ Características del Sistema (1 faltante)
- `{{SIS_ELEC}}` - Sistema eléctrico (monofásico/trifásico)

### 🔧 Equipamiento (6 faltantes)
- `{{N_PANEL}}` - Número de paneles
- `{{M_PANEL}}` - Modelo del panel
- `{{N_INVER}}` - Número de inversores
- `{{M_INVER}}` - Modelo del inversor
- `{{N_BATER}}` - Número de baterías
- `{{M_BATER}}` - Modelo de la batería

### 💰 Financiero (2 faltantes)
- `{{SUBTOT}}` - Subtotal antes de IVA
- `{{AHO_MES}}` - Ahorro mensual

### 🏠 Inmueble (4 faltantes)
- `{{NPISOS}}` - Número de pisos del edificio
- `{{HSPC}}` - HSP calculado (Horas Solar Pico)
- `{{AREA}}` - Área disponible en m²
- `{{PCTDIA}}` - % de consumo durante el día

---

## ✅ Placeholders que SÍ están en el Template (17)

Estos ya están correctamente configurados:

1. `{{COT_ID}}` - ID de cotización
2. `{{FECHA}}` - Fecha de cotización
3. `{{NOMBRE}}` - Nombre del cliente
4. `{{EMAIL}}` - Email del cliente ✨
5. `{{TELEFONO}}` - Teléfono del cliente ✨
6. `{{VIVIENDA}}` - Tipo de vivienda
7. `{{TIPO_FV}}` - Tipo de sistema FV
8. `{{NIC}}` - Número de identificación del contador
9. `{{CAP_KW}}` - Capacidad instalada en kW
10. `{{GEN_MES}}` - Generación mensual en kWh
11. `{{INVER}}` - Inversión total
12. `{{RETORNO}}` - Tiempo de retorno
13. `{{PORC_PR}}` - % de producción mensual
14. `{{ACUM_GEN}}` - Acumulado por generación
15. `{{ACUM_DEP}}` - Acumulado por depreciación
16. `{{ACUM_DED}}` - Acumulado por deducción
17. `{{TOT_ACUM}}` - Total acumulado

✨ = Detectados después de agregar soporte para SmartArt

---

## ⚠️ Placeholder Extra en Template

Hay 1 placeholder en el template que NO está definido en el código:

- `{{tipo_ edif}}` - Parece ser un error de escritura. Deberías:
  - **Opción 1**: Eliminarlo del template si no se usa
  - **Opción 2**: Reemplazarlo por `{{VIVIENDA}}` si era eso lo que querías

---

## 🛠️ Cómo Actualizar el Template

### Paso 1: Abrir el Template
1. Abre `Template/Template-PreCotizacion.pptx` en PowerPoint
2. Identifica dónde quieres mostrar cada dato faltante

### Paso 2: Agregar Placeholders
Para cada placeholder faltante:

1. **Inserta un cuadro de texto** donde quieras que aparezca el dato
2. **Escribe el placeholder exacto** (con las dobles llaves)
3. **Formatea el texto** (fuente, tamaño, color, alineación)

**Ejemplo**: Si quieres mostrar el email del cliente:
```
Email: {{EMAIL}}
```

**Ejemplo**: Si quieres mostrar equipamiento:
```
Sistema Solar Fotovoltaico
- Paneles: {{N_PANEL}} x {{M_PANEL}}
- Inversores: {{N_INVER}} x {{M_INVER}}
- Baterías: {{N_BATER}} x {{M_BATER}}
```

**Ejemplo**: Si quieres mostrar datos del inmueble:
```
Datos del Inmueble:
- Ciudad: {{CIUDAD}}
- Dirección: {{DIRECC}}
- Pisos: {{NPISOS}}
- Área disponible: {{AREA}} m²
- Sistema eléctrico: {{SIS_ELEC}}
```

### Paso 3: Formato Sugerido por Diapositiva

#### 📄 Diapositiva 1 - Información General
Ya tienes: `{{COT_ID}}`, `{{FECHA}}`, `{{NOMBRE}}`, `{{VIVIENDA}}`

**Agregar**:
```
Cliente: {{NOMBRE}}
Email: {{EMAIL}}
Teléfono: {{TELEFONO}}
Ciudad: {{CIUDAD}}
Dirección: {{DIRECC}}
Tipo de vivienda: {{VIVIENDA}}
```

#### ⚡ Diapositiva 2 - Análisis Energético
Ya tienes: `{{NIC}}`, `{{TIPO_FV}}`, `{{CAP_KW}}`, `{{GEN_MES}}`, `{{INVER}}`, `{{RETORNO}}`, `{{PORC_PR}}`

**Agregar**:
```
Consumo Actual:
- Consumo mensual: {{CONSUMO}}
- Factura promedio: {{FACTURA}}
- Costo por kWh: {{VAL_KWH}}
- Ahorro mensual: {{AHO_MES}}

Sistema Instalado:
- Paneles: {{N_PANEL}} unidades {{M_PANEL}}
- Inversores: {{N_INVER}} unidades {{M_INVER}}
- Baterías: {{N_BATER}} unidades {{M_BATER}}
- Capacidad total: {{CAP_KW}}
- Sistema eléctrico: {{SIS_ELEC}}

Datos del Inmueble:
- Pisos: {{NPISOS}}
- HSP: {{HSPC}} horas
- Área disponible: {{AREA}} m²
- Consumo diurno: {{PCTDIA}}

Inversión:
- Total: {{INVER}}
- Subtotal (sin IVA): {{SUBTOT}}
```

### Paso 4: Verificar Dimensiones de Página

**IMPORTANTE**: El template actual tiene formato **vertical** (7.5" x 10")

Para **formato Carta horizontal** (11" x 8.5"):
1. Ve a **Diseño → Tamaño de diapositiva → Configuración personalizada**
2. Configura:
   - Ancho: **11 pulgadas** (27.94 cm)
   - Alto: **8.5 pulgadas** (21.59 cm)
3. Elige **Maximizar** cuando pregunte cómo ajustar el contenido

### Paso 5: Guardar
1. Guarda el archivo como `Template-PreCotizacion.pptx`
2. **Cierra PowerPoint completamente** (importante para que el backend lo pueda leer)

---

## 🧪 Verificar Cambios

Después de actualizar el template, ejecuta:

```bash
cd /Users/jcsalazarb/Documents/GitHub/cotizador/backend
source venv/bin/activate
python comparar_placeholders.py
```

Deberías ver:
- **Coinciden: 35** (todos los placeholders)
- **Faltantes en template: 0**

---

## 📐 Verificar Dimensiones

```bash
python diagnostico_template.py
```

Deberías ver:
```
📐 DIMENSIONES DE PÁGINA:
   Ancho:  11.00 pulgadas
   Alto:   8.50 pulgadas
   ✅ Formato: Carta horizontal
```

---

## 🚀 Probar Cotización

Una vez actualizado el template:
1. Ve a: http://localhost:8000/index_Original_modificado.html
2. Genera una cotización
3. Verifica que **todos los placeholders** se reemplacen correctamente
4. Verifica que el **PDF tenga formato Carta**

---

## 💡 Tips

1. **Nombres exactos**: Los placeholders deben tener el nombre EXACTO (mayúsculas, dobles llaves)
2. **Espacios**: No agregues espacios dentro de `{{ }}`, usa `{{NOMBRE}}` no `{{ NOMBRE }}`
3. **Formato**: Puedes formatear el texto alrededor del placeholder
4. **Tablas**: Los placeholders funcionan en cuadros de texto y en celdas de tablas
5. **Backup**: Guarda una copia del template original antes de modificar

---

## 🔧 Placeholder Extra Detectado

El template tiene `{{tipo_ edif}}` (con espacio y guion bajo) que no existe en el código.

**Solución recomendada**:
1. Busca `{{tipo_ edif}}` en el template
2. Reemplázalo por `{{VIVIENDA}}` si se refiere al tipo de edificio
3. O elimínalo si no se usa

---

**Creado**: 24 de noviembre de 2025  
**Sistema**: NASSA Solar - Cotizador Automático
