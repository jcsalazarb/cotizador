#!/usr/bin/env python3
"""
Script para convertir ciudades.json del formato antiguo al nuevo formato.

Formato antiguo: {"ciudad_key": 4.7}
Formato nuevo: {"ciudad_key": {"nombre": "Nombre Ciudad", "hsp": 4.7}}
"""

import json
import os

def convertir_formato():
    """Convierte el formato de ciudades.json"""
    
    # Rutas
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ciudades_file = os.path.join(script_dir, 'config', 'ciudades.json')
    backup_file = os.path.join(script_dir, 'config', 'ciudades_backup.json')
    
    # Leer archivo actual
    print(f"📖 Leyendo: {ciudades_file}")
    with open(ciudades_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Total ciudades: {len(data)}")
    
    # Verificar si ya está en el nuevo formato
    primera_ciudad = next(iter(data.items()))
    ciudad_key, ciudad_data = primera_ciudad
    
    if isinstance(ciudad_data, dict) and 'hsp' in ciudad_data:
        print("ℹ️  El archivo ya está en el nuevo formato. No se requiere conversión.")
        return
    
    print("🔄 Convirtiendo al nuevo formato...")
    
    # Crear backup
    print(f"💾 Creando backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Convertir formato
    nuevo_data = {}
    for ciudad_key, hsp_value in data.items():
        if ciudad_key == "default":
            # Mantener el default como está
            nuevo_data[ciudad_key] = {"hsp": hsp_value}
        else:
            # Convertir ciudad_key a nombre legible
            nombre = ciudad_key.replace("_", " ").title()
            nuevo_data[ciudad_key] = {
                "nombre": nombre,
                "hsp": hsp_value
            }
    
    # Guardar nuevo formato
    print(f"💾 Guardando nuevo formato en: {ciudades_file}")
    with open(ciudades_file, 'w', encoding='utf-8') as f:
        json.dump(nuevo_data, f, ensure_ascii=False, indent=2)
    
    print("\n✅ CONVERSIÓN COMPLETADA")
    print(f"   - Backup guardado en: {backup_file}")
    print(f"   - Nuevo formato en: {ciudades_file}")
    print(f"   - Total ciudades convertidas: {len(nuevo_data)}")
    
    # Mostrar ejemplo
    print("\n📋 Ejemplo de conversión:")
    primera_nueva = next(iter(nuevo_data.items()))
    print(f"   Antes: \"{primera_nueva[0]}\": {data[primera_nueva[0]]}")
    print(f"   Después: \"{primera_nueva[0]}\": {json.dumps(primera_nueva[1], ensure_ascii=False)}")

if __name__ == "__main__":
    convertir_formato()
