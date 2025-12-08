🎯 RESPUESTAS A TUS PREGUNTAS:
1️⃣ PANEL DE ADMINISTRACIÓN:
Credenciales:

Funciones disponibles:

✅ Ver/editar parámetros del sistema (costos, fiscales, proyección, nuevos: eficiencias, factor área, umbral)
✅ Gestionar equipos (paneles, inversores, baterías) con precios
✅ Descargar templates
2️⃣ PROBLEMA DE LISTAS INVISIBLES:
Causa probable: Extensión del navegador o configuración CSS que sobrescribe los estilos

Solución implementada:

✅ Agregué !important a todos los estilos de <option> para forzar visibilidad
✅ Duplicé propiedades (background + background-color) para mayor compatibilidad
✅ Agregué display:block y line-height explícitos
✅ Creé página de diagnóstico para el tester
🧪 PÁGINA DE DIAGNÓSTICO PARA EL TESTER:
URL:
https://web-production-3749b.up.railway.app/test-select.html

Qué hace esta página:
✅ Muestra 3 listas desplegables de prueba
✅ Detecta información del navegador (User Agent, zoom, resolución)
✅ Da instrucciones para solucionar problemas
✅ Botón de diagnóstico para verificar que las listas funcionan

Instrucciones para el tester:
Abrir https://web-production-3749b.up.railway.app/test-select.html
Hacer clic en cada lista y verificar si ve las opciones
Si NO ve las opciones:
Hacer Ctrl+Shift+R (hard refresh)
Verificar zoom al 100%
Desactivar extensiones (AdBlock, Dark Mode, etc.)
Probar en modo incógnito
Verificar que no tenga "Forzar modo oscuro" activado en Chrome

🔍 POSIBLES CAUSAS DEL PROBLEMA:
Extensión de modo oscuro (invierte colores, puede ocultar opciones)
Zoom del navegador menor al 100%
Caché antiguo (necesita hard refresh)
Configuración de accesibilidad de Chrome (Alto contraste, etc.)
Flag experimental de Chrome activado
Windows de alto contraste (si está en Windows)

📸 PIDE AL TESTER:
Si después del deploy (en 2-3 min) sigue con el problema:

Screenshot del test-select.html mostrando:
    Una lista desplegable abierta
    La información del navegador al final de la página
Abrir Consola del navegador (F12):
    Ir a pestaña "Console"
    Copiar cualquier error que aparezca
Probar en modo incógnito:
    Chrome: Ctrl+Shift+N (Windows) o Cmd+Shift+N (Mac)      
    Si funciona en incógnito → problema es una extensión

⏱️ DEPLOYMENT:

Tú pruebas: https://web-production-3749b.up.railway.app/
Tester prueba: https://web-production-3749b.up.railway.app/test-select.html
Admin pruebas: https://web-production-3749b.up.railway.app/admin

COMMITS DE LOS DOS ULTIMOS DIAS
VIERNES 28 NOVIEMBRE 2025 (HOY - 14 commits)
59dd956 | 22:01 | Fix: Mejorar visibilidad select con important y test de diagnostico
04dc91e | 18:39 | Fix: Mejorar visibilidad de opciones en dropdowns (select)
d5a0d9b | 18:27 | Feature: Parametrizar variables del sistema (eficiencias, factor área, umbral 2da opción)
333311c | 17:23 | Fix: Corregir título 'Cotizador Nassa Solar - Energía Renovable' y usar logo local
1e44f8a | 16:58 | Update: Templates actualizados con formato Roboto y ajustes visuales
2cc1f91 | 15:11 | Fix: 1) TABLA_AHORROS fuente 7pt, 2) Mismo ID base para opción 1 y 2, 3) Preservar Roboto
4db51da | 13:49 | Fix: Corregir nombres de parámetros en calcular_segunda_opcion()
f73d151 | 13:28 | Debug: Capturar error de opción 2 en diagnóstico JSON
b40d9e9 | 13:19 | Debug: Agregar diagnóstico detallado de segunda opción en respuesta JSON
48329f7 | 13:12 | Update: Template1y2 con cambio de fuentes y tamaño shapes anidados
f03b44e | 12:28 | Merge: Sincronizar fix INV8→inv9 (Railway) + fix formato Arial 9pt (local)
6c0d2d5 | 11:29 | Fix: Aplicar formato Arial 9pt consistente en TABLA_AHORROS
1d3be27 | 11:20 | Change ID from 'INV8' to 'inv9' in equipos.json
504a7de | 09:53 | Agregar Template-PreCotizacion2.pptx para opción 2 (forzado)
3a07a51 | 09:48 | Implementar soporte para dos templates independientes (Opción 1 y 2)

🗓️ JUEVES 27 NOVIEMBRE 2025 (AYER - 31 commits)

5db5af1 | 22:56 | Fix: Preservar formato en TABLA_AHORROS y actualizar logo email
fe3c170 | 22:49 | Update: Template con cambio de fuentes y tamaño shapes anidados
a18b91e | 22:24 | Fix DEFINITIVO: Reemplazo simple sin modificar formatos
8c0ab74 | 22:24 | Update: Template con cambio de fuentes y tamaño shapes anidados
a55b7dc | 22:20 | Update: Template con cambio de fuentes y tamaño shapes anidados
7310878 | 21:42 | Fix: Corregir error '_Run' object has no attribute '_element'
504b026 | 21:32 | Fix: Preservar formato de fuentes y alineación en placeholders
95e96d5 | 21:02 | Update: Template con desagrupar shapes anidados
993d054 | 20:07 | Simplificar reemplazo de placeholders - enfoque run por run
d7d79ae | 19:45 | Fix CRÍTICO: Eliminar procesamiento duplicado de shapes
b7aacbe | 19:44 | Update: Template con desagrupar shapes anidados
15fa822 | 17:51 | Fix: Eliminar duplicación de placeholders y mejorar logging
d414a36 | 16:36 | Debug: Agregar log de areaDisponible antes de enviar
de4b86e | 16:00 | Debug: Logs extensivos para diagnosticar segunda opción
df9bf85 | 15:42 | Debug: Agregar logs detallados para diagnóstico de duplicación
59e5244 | 15:10 | Fix: Generación independiente de PDFs con templates frescos
f48d736 | 14:47 | Fix: Capturar FormData ANTES de deshabilitar inputs
ff9b33e | 14:36 | Fix: Corrección error de sintaxis en línea 27
d51e445 | 14:09 | Feature: Segunda opción de cotización ajustada a área disponible
ff7a47b | 14:02 | Update: Template con {{AREA_REQ}} y fuentes corregidas
2dddc3c | 13:18 | Update: Template con {{AREA_REQ}} y fuentes corregidas
352f6d4 | 13:07 | Feature: Cálculo de área requerida + Mejoras UX frontend
67c58ff | 11:47 | Fix: Zona horaria Colombia (UTC-5) + Mejorar reemplazo placeholders PPTX
66eb4a9 | 09:39 | fix: Convertir IDs de equipos a minúsculas para validación backend
b5c69ee | 09:29 | fix: Mejorar logging de errores 422 en frontend
c93e4cd | 08:44 | fix: Usar puerto 465 (SMTP_SSL) como prioridad para Railway
0e9bd41 | 02:48 | fix: Cambiar API_BASE_URL de localhost a window.location.origin para Railway
b5ec467 | 02:36 | fix: Corregir rutas del logo a /static/images/loggo-Nassa.png
f2c0717 | 02:36 | feat: Agregar template PowerPoint Template-PreCotizacion.pptx (44MB)
f229ae5 | 02:15 | feat: Agregar archivos de configuración JSON (equipos, ciudades, parametros)
282380f | 02:05 | Fix: Agregar email-validator requerido por Pydantic EmailStr
f1d63c3 | 01:47 | Fix: Actualizar startCommand en railway.json para usar /opt/venv
859c1a3 | 01:39 | Fix: Crear virtual environment para instalar dependencias en Railway