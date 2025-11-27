# 🔄 MAPEO DE PLACEHOLDERS: ANTIGUOS → NUEVOS

## 📋 Tabla de Conversión

Todos los placeholders han sido rediseñados con **máximo 8 letras** para caber en cuadros de texto pequeños.

| **PLACEHOLDER ANTIGUO**        | **PLACEHOLDER NUEVO** | **Longitud** | **Descripción** |
|--------------------------------|-----------------------|--------------|-----------------|
| `{{COTIZACION_ID}}`            | `{{COT_ID}}`          | 6 letras     | ID de cotización |
| `{{FECHA}}`                    | `{{FECHA}}`           | 5 letras     | ✅ Sin cambio |
| `{{NOMBRE}}`                   | `{{NOMBRE}}`          | 6 letras     | ✅ Sin cambio |
| `{{EMAIL}}`                    | `{{EMAIL}}`           | 5 letras     | ✅ Sin cambio |
| `{{TELEFONO}}`                 | `{{TELEFONO}}`        | 8 letras     | ✅ Sin cambio |
| `{{CIUDAD}}`                   | `{{CIUDAD}}`          | 6 letras     | ✅ Sin cambio |
| `{{DIRECCION}}`                | `{{DIRECC}}`          | 6 letras     | Dirección |
| **N/A (NUEVO)**                | `{{NIC}}`             | 3 letras     | ⭐ Nuevo campo |
| `{{CONSUMO_MENSUAL}}`          | `{{CONSUMO}}`         | 7 letras     | Consumo mensual |
| `{{VALOR_FACTURA}}`            | `{{FACTURA}}`         | 7 letras     | Valor factura |
| `{{VALOR_KWH}}`                | `{{VAL_KWH}}`         | 7 letras     | Valor por kWh |
| `{{TIPO_VIVIENDA}}`            | `{{VIVIENDA}}`        | 8 letras     | Tipo de vivienda |
| `{{SISTEMA_ELECTRICO}}`        | `{{SIS_ELEC}}`        | 8 letras     | Sistema eléctrico |
| `{{TIPO_SISTEMA}}`             | `{{TIPO_FV}}`         | 7 letras     | Tipo sistema FV |
| `{{NUM_PANELES}}`              | `{{N_PANEL}}`         | 7 letras     | Número de paneles |
| `{{PANEL_MODELO}}`             | `{{M_PANEL}}`         | 7 letras     | Modelo panel |
| `{{INVERSORES}}`               | `{{N_INVER}}`         | 7 letras     | Número inversores |
| `{{INVERSOR_MODELO}}`          | `{{M_INVER}}`         | 7 letras     | Modelo inversor |
| `{{NUM_BATERIAS}}`             | `{{N_BATER}}`         | 7 letras     | Número baterías |
| `{{BATERIA_MODELO}}`           | `{{M_BATER}}`         | 7 letras     | Modelo batería |
| `{{CAPACIDAD_INSTALADA_KW}}`   | `{{CAP_KW}}`          | 6 letras     | Capacidad en kW |
| `{{GENERACION_MENSUAL_KWH}}`   | `{{GEN_MES}}`         | 7 letras     | Generación mensual |
| `{{INVERSION_TOTAL}}`          | `{{INVER}}`           | 5 letras     | Inversión total |
| `{{SUBTOTAL_SIN_IVA}}`         | `{{SUBTOT}}`          | 6 letras     | Subtotal sin IVA |
| `{{AHORRO_MENSUAL}}`           | `{{AHO_MES}}`         | 7 letras     | Ahorro mensual |
| `{{RETORNO_ANIOS}}`            | `{{RETORNO}}`         | 7 letras     | Años de retorno |
| `{{PORCENTAJE_PRODUCCION}}`    | `{{PORC_PR}}`         | 7 letras     | % producción |
| `{{ACUM_GEN}}`                 | `{{ACUM_GEN}}`        | 8 letras     | ✅ Sin cambio |
| `{{ACUM_DED}}`                 | `{{ACUM_DED}}`        | 8 letras     | ✅ Sin cambio |
| `{{ACUM_DEP}}`                 | `{{ACUM_DEP}}`        | 8 letras     | ✅ Sin cambio |
| `{{TOTAL_ACUMULADO_PAYBACK}}`  | `{{TOT_ACUM}}`        | 8 letras     | Total acumulado |

---

## 📊 ESTADÍSTICAS

- **Total placeholders**: 32 (31 anteriores + 1 nuevo: `{{NIC}}`)
- **Longitud máxima**: 8 letras
- **Placeholders sin cambio**: 9 (FECHA, NOMBRE, EMAIL, TELEFONO, CIUDAD, ACUM_GEN, ACUM_DED, ACUM_DEP)
- **Placeholders renombrados**: 22
- **Placeholders nuevos**: 1 (`{{NIC}}`)

---

## 🔍 BÚSQUEDA Y REEMPLAZO EN POWERPOINT

Si tienes un template con los nombres antiguos, usa estas reglas de búsqueda/reemplazo:

### 1️⃣ Información General
```
{{COTIZACION_ID}}           →  {{COT_ID}}
```

### 2️⃣ Datos del Cliente
```
{{DIRECCION}}               →  {{DIRECC}}
[Agregar manualmente]       →  {{NIC}}
```

### 3️⃣ Consumo Energético
```
{{CONSUMO_MENSUAL}}         →  {{CONSUMO}}
{{VALOR_FACTURA}}           →  {{FACTURA}}
{{VALOR_KWH}}               →  {{VAL_KWH}}
```

### 4️⃣ Características del Inmueble
```
{{TIPO_VIVIENDA}}           →  {{VIVIENDA}}
{{SISTEMA_ELECTRICO}}       →  {{SIS_ELEC}}
{{TIPO_SISTEMA}}            →  {{TIPO_FV}}
```

### 5️⃣ Equipamiento
```
{{NUM_PANELES}}             →  {{N_PANEL}}
{{PANEL_MODELO}}            →  {{M_PANEL}}
{{INVERSORES}}              →  {{N_INVER}}
{{INVERSOR_MODELO}}         →  {{M_INVER}}
{{NUM_BATERIAS}}            →  {{N_BATER}}
{{BATERIA_MODELO}}          →  {{M_BATER}}
```

### 6️⃣ Especificaciones Técnicas
```
{{CAPACIDAD_INSTALADA_KW}}  →  {{CAP_KW}}
{{GENERACION_MENSUAL_KWH}}  →  {{GEN_MES}}
```

### 7️⃣ Análisis Financiero
```
{{INVERSION_TOTAL}}         →  {{INVER}}
{{SUBTOTAL_SIN_IVA}}        →  {{SUBTOT}}
{{AHORRO_MENSUAL}}          →  {{AHO_MES}}
{{RETORNO_ANIOS}}           →  {{RETORNO}}
{{PORCENTAJE_PRODUCCION}}   →  {{PORC_PR}}
{{TOTAL_ACUMULADO_PAYBACK}} →  {{TOT_ACUM}}
```

---

## ✅ CHECKLIST DE ACTUALIZACIÓN

### Paso 1: Backup
- [ ] Hacer copia de seguridad del `Template-PreCotizacion.pptx` actual

### Paso 2: Búsqueda y Reemplazo
- [ ] Abrir PowerPoint
- [ ] Ctrl+H (Cmd+H en Mac) para abrir "Buscar y reemplazar"
- [ ] Aplicar cada reemplazo de la tabla de arriba
- [ ] Verificar que no quedan placeholders antiguos (buscar "{{")

### Paso 3: Agregar NIC
- [ ] Insertar cuadro de texto para `{{NIC}}` en la diapositiva de datos del cliente

### Paso 4: Verificación
- [ ] Buscar "{{" para encontrar todos los placeholders
- [ ] Verificar que todos tienen máximo 8 letras
- [ ] Verificar que no hay espacios dentro de las llaves: `{{NOMBRE}}` ✅ vs `{{ NOMBRE }}` ❌
- [ ] Guardar el template actualizado

---

## 🎯 VENTAJAS DE LOS NOMBRES CORTOS

✅ **Caben en cuadros de texto pequeños** - No se cortan ni hacen wrap  
✅ **Mejor legibilidad en diseño** - Menos espacio visual ocupado  
✅ **Más fácil de escribir** - Menos caracteres a teclear  
✅ **Menos errores de tipeo** - Nombres más cortos = menos errores  
✅ **Compatible con diseños compactos** - Tablas y gráficos pequeños

---

## 📄 ARCHIVOS ACTUALIZADOS

- ✅ `backend/server.py` - Función `build_placeholders()` actualizada
- ✅ `Template/PLACEHOLDERS_TEMPLATE.md` - Documentación completa actualizada
- ✅ `Template/MAPEO_PLACEHOLDERS.md` - Este archivo (tabla de conversión)
- ⏳ `Template/Template-PreCotizacion.pptx` - **Pendiente de actualización manual**

---

**Fecha de actualización**: 24 de noviembre de 2025  
**Versión**: 2.0 (Nombres cortos de máximo 8 letras)
