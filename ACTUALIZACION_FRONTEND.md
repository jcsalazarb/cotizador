# Actualización del Frontend para Filtrado de Inversores

## Cambio Implementado

Se agregó el campo `tipo_sistema` a los inversores para filtrar automáticamente según el sistema eléctrico del cliente.

### Valores posibles:
- `"monofasico"` - Para inversores monofásicos
- `"bifasico"` - Para inversores bifásicos  
- `"trifasico"` - Para inversores trifásicos

## Actualización Requerida en el Frontend

### Antes (sin filtro):
```javascript
fetch('http://127.0.0.1:8001/api/equipos')
    .then(response => response.json())
    .then(data => {
        // Mostrar todos los inversores
        poblarInversores(data.inversores);
    });
```

### Después (con filtro):
```javascript
// Esperar a que el usuario seleccione el sistema eléctrico
const sistemaElectrico = document.getElementById('sistemaElectrico').value;

// Hacer petición con filtro
fetch(`http://127.0.0.1:8001/api/equipos?sistemaElectrico=${sistemaElectrico}`)
    .then(response => response.json())
    .then(data => {
        // Mostrar solo inversores compatibles
        poblarInversores(data.inversores);
    });
```

## Implementación Recomendada

### 1. Agregar listener al campo de sistema eléctrico:

```javascript
document.getElementById('sistemaElectrico').addEventListener('change', function() {
    const sistemaElectrico = this.value;
    
    // Recargar inversores filtrados
    fetch(`${API_BASE_URL}/api/equipos?sistemaElectrico=${sistemaElectrico}`)
        .then(response => response.json())
        .then(data => {
            const selectInversor = document.getElementById('inversor');
            selectInversor.innerHTML = '<option value="">Seleccione un inversor...</option>';
            
            data.inversores.forEach(inversor => {
                const option = document.createElement('option');
                option.value = inversor.id;
                option.textContent = `${inversor.nombre} - ${inversor.capacidad}W`;
                selectInversor.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error cargando inversores:', error);
        });
});
```

### 2. Deshabilitar selección de inversor hasta que se elija sistema eléctrico:

```javascript
// Al cargar la página
document.getElementById('inversor').disabled = true;

// En el listener del sistema eléctrico
document.getElementById('sistemaElectrico').addEventListener('change', function() {
    if (this.value) {
        document.getElementById('inversor').disabled = false;
        // ... cargar inversores filtrados
    } else {
        document.getElementById('inversor').disabled = true;
    }
});
```

### 3. Agregar validación:

```javascript
function validarFormulario() {
    const sistemaElectrico = document.getElementById('sistemaElectrico').value;
    const inversor = document.getElementById('inversor').value;
    
    if (!sistemaElectrico) {
        alert('Por favor seleccione el tipo de sistema eléctrico');
        return false;
    }
    
    if (!inversor) {
        alert('Por favor seleccione un inversor compatible');
        return false;
    }
    
    return true;
}
```

## Flujo Completo Actualizado

```javascript
// 1. Cargar equipos iniciales (paneles y baterías sin filtro)
async function cargarEquiposIniciales() {
    const response = await fetch(`${API_BASE_URL}/api/equipos`);
    const data = await response.json();
    
    // Poblar paneles
    poblarSelect('panel', data.paneles);
    
    // Poblar baterías
    poblarSelect('bateria', data.baterias);
    
    // Inversores se cargarán después de seleccionar sistema eléctrico
}

// 2. Listener para sistema eléctrico
document.getElementById('sistemaElectrico').addEventListener('change', async function() {
    const sistemaElectrico = this.value;
    
    if (!sistemaElectrico) {
        document.getElementById('inversor').disabled = true;
        document.getElementById('inversor').innerHTML = '<option value="">Primero seleccione sistema eléctrico</option>';
        return;
    }
    
    try {
        // Cargar inversores filtrados
        const response = await fetch(`${API_BASE_URL}/api/equipos?sistemaElectrico=${sistemaElectrico}`);
        const data = await response.json();
        
        const selectInversor = document.getElementById('inversor');
        selectInversor.disabled = false;
        selectInversor.innerHTML = '<option value="">Seleccione un inversor...</option>';
        
        if (data.inversores.length === 0) {
            selectInversor.innerHTML = '<option value="">No hay inversores compatibles</option>';
            selectInversor.disabled = true;
            alert(`No hay inversores disponibles para sistema ${sistemaElectrico}`);
            return;
        }
        
        data.inversores.forEach(inversor => {
            const option = document.createElement('option');
            option.value = inversor.id;
            option.textContent = `${inversor.nombre} - ${inversor.capacidad/1000}kW`;
            selectInversor.appendChild(option);
        });
        
        console.log(`✅ Cargados ${data.inversores.length} inversores para sistema ${sistemaElectrico}`);
        
    } catch (error) {
        console.error('Error cargando inversores:', error);
        alert('Error al cargar inversores compatibles');
    }
});

// 3. Helper para poblar selects
function poblarSelect(selectId, items) {
    const select = document.getElementById(selectId);
    select.innerHTML = '<option value="">Seleccione...</option>';
    
    items.forEach(item => {
        const option = document.createElement('option');
        option.value = item.id;
        option.textContent = `${item.nombre} - ${item.capacidad}W`;
        select.appendChild(option);
    });
}
```

## Ejemplo de HTML Actualizado

```html
<div class="form-group">
    <label for="sistemaElectrico">Tipo de Sistema Eléctrico *</label>
    <select id="sistemaElectrico" name="sistemaElectrico" required>
        <option value="">Seleccione...</option>
        <option value="monofasico">Monofásico</option>
        <option value="bifasico">Bifásico</option>
        <option value="trifasico">Trifásico</option>
    </select>
</div>

<div class="form-group">
    <label for="inversor">Inversor Compatible *</label>
    <select id="inversor" name="inversor" required disabled>
        <option value="">Primero seleccione sistema eléctrico</option>
    </select>
    <small style="color: #666;">
        💡 Los inversores se filtran automáticamente según su sistema eléctrico
    </small>
</div>
```

## Testing

### Probar endpoint con curl:

```bash
# Sin filtro (todos los inversores)
curl http://localhost:8001/api/equipos

# Con filtro monofásico
curl "http://localhost:8001/api/equipos?sistemaElectrico=monofasico"

# Con filtro trifásico
curl "http://localhost:8001/api/equipos?sistemaElectrico=trifasico"
```

### Verificar en navegador:

1. Abrir consola del navegador (F12)
2. Seleccionar sistema eléctrico
3. Ver en Network tab la petición con parámetro `?sistemaElectrico=...`
4. Verificar que solo aparecen inversores compatibles

## Notas Importantes

- ✅ El filtrado ocurre en el backend, es seguro
- ✅ Los inversores sin `tipo_sistema` no se mostrarán
- ✅ El panel de admin permite editar el `tipo_sistema` de cada inversor
- ✅ Compatible con sistemas legacy (sin romper frontend actual)
- ⚠️ Actualizar TODOS los inversores en `equipos.json` con su `tipo_sistema`
- ⚠️ Validar que el frontend NO permita enviar cotización sin inversor

## Soporte

Si necesitas ayuda adicional:
1. Revisar `/backend/API_ADMIN.md` para gestión de equipos
2. Usar `admin.html` para actualizar inversores existentes
3. Verificar logs del backend en terminal
