# ⚡ GUÍA RÁPIDA DE PLACEHOLDERS (8 LETRAS MÁXIMO)

## 🎯 RESUMEN VISUAL

```
┌─────────────────────────────────────────────────────────────┐
│                   32 PLACEHOLDERS TOTALES                   │
│              ⚡ TODOS CON MÁXIMO 8 LETRAS ⚡                │
└─────────────────────────────────────────────────────────────┘

📊 INFORMACIÓN GENERAL (2)
  {{COT_ID}}    → ID cotización
  {{FECHA}}     → Fecha

👤 DATOS DEL CLIENTE (6)
  {{NOMBRE}}    → Nombre completo
  {{EMAIL}}     → Email
  {{TELEFONO}}  → Teléfono
  {{CIUDAD}}    → Ciudad
  {{DIRECC}}    → Dirección
  {{NIC}}       → ⭐ NUEVO: Número Identificación Cliente

⚡ CONSUMO ENERGÉTICO (3)
  {{CONSUMO}}   → Consumo mensual (kWh)
  {{FACTURA}}   → Valor factura ($)
  {{VAL_KWH}}   → Valor por kWh ($)

🏠 CARACTERÍSTICAS INMUEBLE (3)
  {{VIVIENDA}}  → Tipo vivienda
  {{SIS_ELEC}}  → Sistema eléctrico
  {{TIPO_FV}}   → Tipo sistema fotovoltaico

🔧 EQUIPAMIENTO (6)
  {{N_PANEL}}   → Número de paneles
  {{M_PANEL}}   → Modelo panel
  {{N_INVER}}   → Número inversores
  {{M_INVER}}   → Modelo inversor
  {{N_BATER}}   → Número baterías (o " ")
  {{M_BATER}}   → Modelo batería (o " ")

📈 ESPECIFICACIONES TÉCNICAS (2)
  {{CAP_KW}}    → Capacidad instalada (kW)
  {{GEN_MES}}   → Generación mensual (kWh)

💰 ANÁLISIS FINANCIERO (10)
  {{INVER}}     → Inversión total
  {{SUBTOT}}    → Subtotal sin IVA
  {{AHO_MES}}   → Ahorro mensual
  {{RETORNO}}   → Años de retorno
  {{PORC_PR}}   → % producción
  {{ACUM_GEN}}  → Acum. generación
  {{ACUM_DED}}  → Acum. deducción
  {{ACUM_DEP}}  → Acum. depreciación
  {{TOT_ACUM}}  → Total acumulado
```

---

## 📝 PLANTILLA LISTA PARA COPIAR/PEGAR

### Cliente + Consumo
```
Nombre:    {{NOMBRE}}
Email:     {{EMAIL}}
Teléfono:  {{TELEFONO}}
NIC:       {{NIC}}
Ciudad:    {{CIUDAD}}
Dirección: {{DIRECC}}

Consumo:   {{CONSUMO}}
Factura:   {{FACTURA}}
Valor kWh: {{VAL_KWH}}
```

### Sistema Fotovoltaico
```
Tipo Sistema:     {{TIPO_FV}}
Tipo Vivienda:    {{VIVIENDA}}
Sistema Eléctrico: {{SIS_ELEC}}

Paneles:     {{N_PANEL}} x {{M_PANEL}}
Inversores:  {{N_INVER}} x {{M_INVER}}
Baterías:    {{N_BATER}} x {{M_BATER}}

Capacidad:   {{CAP_KW}}
Generación:  {{GEN_MES}}
```

### Análisis Financiero
```
Inversión Total: {{INVER}}
Subtotal (s/IVA): {{SUBTOT}}

Ahorro Mensual:  {{AHO_MES}}
Tiempo Retorno:  {{RETORNO}}
Producción:      {{PORC_PR}}

┌─────────────────────────────┐
│ AHORROS HASTA EL PAYBACK    │
├─────────────────────────────┤
│ Generación:     {{ACUM_GEN}}│
│ Deducción:      {{ACUM_DED}}│
│ Depreciación:   {{ACUM_DEP}}│
├─────────────────────────────┤
│ TOTAL:          {{TOT_ACUM}}│
└─────────────────────────────┘
```

---

## 🎨 DISEÑO COMPACTO (Ideal para tablas)

```
┌────────┬───────────┐
│ Campo  │ Valor     │
├────────┼───────────┤
│ NIC    │ {{NIC}}   │
│ Ciudad │ {{CIUDAD}}│
│ kWh/mes│ {{CONSUMO}}│
└────────┴───────────┘

┌────────┬────────────┐
│ Equipo │ Cantidad   │
├────────┼────────────┤
│ Panel  │ {{N_PANEL}}│
│ Inver. │ {{N_INVER}}│
│ Bater. │ {{N_BATER}}│
└────────┴────────────┘

┌────────┬─────────────┐
│ Ahorro │ Monto       │
├────────┼─────────────┤
│ Gen.   │ {{ACUM_GEN}}│
│ Ded.   │ {{ACUM_DED}}│
│ Depr.  │ {{ACUM_DEP}}│
└────────┴─────────────┘
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

Antes de usar el template actualizado:

- [ ] Todos los placeholders tienen máximo 8 letras
- [ ] No hay espacios dentro de las llaves: `{{NOMBRE}}` ✅
- [ ] El nuevo campo `{{NIC}}` está agregado
- [ ] Los placeholders antiguos fueron reemplazados
- [ ] La tabla TABLA_AHORROS existe (o encabezados detectables)
- [ ] El logo de NASSA está insertado
- [ ] Probaste buscar "{{" para verificar todos los placeholders

---

## 🚀 QUICK START

1. **Abrir template** `Template-PreCotizacion.pptx`
2. **Buscar y reemplazar** (Ctrl+H / Cmd+H):
   - Ver lista completa en `MAPEO_PLACEHOLDERS.md`
3. **Agregar** cuadro de texto con `{{NIC}}`
4. **Guardar** y probar con una cotización de prueba

---

## 📱 PARA CUADROS PEQUEÑOS

Si el cuadro de texto es muy pequeño, usa solo el valor sin etiqueta:

```
❌ Evitar:
┌──────────────────────┐
│ NIC: {{NIC}}         │  ← Muy largo
└──────────────────────┘

✅ Mejor:
┌──────────┐
│ {{NIC}}  │  ← Solo valor
└──────────┘
```

---

## 🔢 LONGITUDES EXACTAS

```
3 letras: NIC
5 letras: FECHA, EMAIL, INVER
6 letras: COT_ID, NOMBRE, CIUDAD, DIRECC, CAP_KW, SUBTOT
7 letras: CONSUMO, FACTURA, VAL_KWH, TIPO_FV, N_PANEL, M_PANEL,
          N_INVER, M_INVER, N_BATER, M_BATER, GEN_MES, AHO_MES,
          RETORNO, PORC_PR
8 letras: TELEFONO, VIVIENDA, SIS_ELEC, ACUM_GEN, ACUM_DED,
          ACUM_DEP, TOT_ACUM
```

---

**💡 TIP**: Todos los placeholders son más cortos que antes, lo que facilita el diseño de templates compactos y profesionales.

---

**Versión**: 2.0 - Placeholders cortos  
**Fecha**: 24 de noviembre de 2025
