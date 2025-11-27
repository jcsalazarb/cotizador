# Cómo Ver Errores del Frontend en el Navegador

## 🔍 Abrir la Consola del Navegador

### Chrome / Edge / Brave
1. Presiona **F12** o **Ctrl+Shift+I** (Windows/Linux) / **Cmd+Option+I** (Mac)
2. Haz clic en la pestaña **Console** (Consola)

### Firefox
1. Presiona **F12** o **Ctrl+Shift+K** (Windows/Linux) / **Cmd+Option+K** (Mac)
2. Ya estarás en la consola

### Safari
1. Primero habilita el menú de desarrollo: Preferencias → Avanzado → Marcar "Mostrar menú Desarrollo"
2. Presiona **Cmd+Option+C**

## 📋 Pasos para Diagnosticar Errores de Cotización

1. **Abre la consola** (F12)
2. **Limpia la consola** (click en el ícono 🚫 o botón "Clear console")
3. **Llena el formulario** completamente
4. **Envía la cotización**
5. **Observa los mensajes** en la consola:
   - ✅ Mensajes en verde/azul = OK
   - ❌ Mensajes en rojo = Error
   - ⚠️ Mensajes en amarillo = Warning

## 🔎 Qué Buscar

### Errores comunes:

**1. Error de Red (Network Error)**
```
Failed to fetch
net::ERR_CONNECTION_REFUSED
```
→ El servidor no está respondiendo

**2. Error 400 (Bad Request)**
```
POST https://... 400 (Bad Request)
```
→ Datos enviados incorrectamente

**3. Error 422 (Validation Error)**
```
{
  "detail": [
    {"loc": ["body", "campo"], "msg": "Field required"}
  ]
}
```
→ Falta algún campo obligatorio

**4. Error 500 (Server Error)**
```
POST https://... 500 (Internal Server Error)
```
→ Error en el backend (revisar logs de Railway)

## 📸 Cómo Compartir el Error

1. **Haz clic derecho** en el mensaje de error
2. **Copy message** / **Copiar mensaje**
3. **Pega** el mensaje completo

O mejor:
1. **Captura de pantalla** de toda la consola con el error visible
2. Comparte la imagen

## 🔧 Verificación Rápida

Ejecuta esto en la consola del navegador para verificar:

```javascript
console.log('API URL:', window.location.origin + '/api');
console.log('Formulario:', document.getElementById('formularioCotizacion'));
```

Debería mostrar:
- API URL: https://web-production-3749b.up.railway.app/api
- Formulario: `<form id="formularioCotizacion">...</form>`

## 📞 Si nada funciona

Envíame:
1. ✅ Captura de la consola con los errores
2. ✅ URL donde estás probando
3. ✅ Datos que ingresaste en el formulario
