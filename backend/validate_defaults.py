#!/usr/bin/env python3
"""
Script de validación para equipos.json
Verifica coherencia de defaults y tipos de sistema

Uso:
    python validate_defaults.py
"""

import json
import sys
from pathlib import Path
from collections import Counter

def load_equipos():
    """Cargar equipos.json"""
    equipos_path = Path(__file__).parent / "config" / "equipos.json"
    
    if not equipos_path.exists():
        print(f"❌ ERROR: No se encontró {equipos_path}")
        sys.exit(1)
    
    with open(equipos_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_inversores(inversores):
    """Validar configuración de inversores"""
    print("\n🔍 Validando Inversores...")
    print("="*60)
    
    errores = []
    advertencias = []
    
    # 1. Verificar que todos tienen tipo_sistema
    sin_tipo = [inv for inv in inversores if 'tipo_sistema' not in inv]
    if sin_tipo:
        errores.append(f"❌ {len(sin_tipo)} inversor(es) sin campo 'tipo_sistema'")
        for inv in sin_tipo:
            print(f"   - {inv['id']}: {inv['nombre']}")
    
    # 2. Contar defaults por tipo de sistema
    tipos_validos = ['monofasico', 'bifasico', 'trifasico']
    defaults_por_tipo = {}
    
    for tipo in tipos_validos:
        inversores_tipo = [inv for inv in inversores if inv.get('tipo_sistema') == tipo]
        defaults_tipo = [inv for inv in inversores_tipo if inv.get('default', False)]
        
        defaults_por_tipo[tipo] = {
            'total': len(inversores_tipo),
            'defaults': len(defaults_tipo),
            'ids_default': [inv['id'] for inv in defaults_tipo]
        }
    
    # 3. Validar coherencia de defaults
    for tipo, stats in defaults_por_tipo.items():
        print(f"\n📊 Sistema {tipo.upper()}:")
        print(f"   Total inversores: {stats['total']}")
        print(f"   Defaults: {stats['defaults']}")
        
        if stats['total'] == 0:
            advertencias.append(f"⚠️ No hay inversores para sistema {tipo}")
        elif stats['defaults'] == 0:
            advertencias.append(f"⚠️ No hay default para sistema {tipo}")
        elif stats['defaults'] > 1:
            errores.append(f"❌ {stats['defaults']} defaults para sistema {tipo}")
            print(f"   IDs con default: {', '.join(stats['ids_default'])}")
        else:
            print(f"   ✅ Configuración correcta: {stats['ids_default'][0]}")
    
    # 4. Verificar defaults con tipo incorrecto
    print(f"\n🔍 Validando coherencia de defaults...")
    defaults_globales = [inv for inv in inversores if inv.get('default', False)]
    
    for inv_default in defaults_globales:
        tipo = inv_default.get('tipo_sistema')
        if tipo not in tipos_validos:
            errores.append(f"❌ Default {inv_default['id']} tiene tipo_sistema inválido: {tipo}")
    
    return errores, advertencias

def validate_paneles(paneles):
    """Validar configuración de paneles"""
    print("\n🔍 Validando Paneles...")
    print("="*60)
    
    errores = []
    advertencias = []
    
    defaults = [p for p in paneles if p.get('default', False)]
    
    print(f"   Total paneles: {len(paneles)}")
    print(f"   Defaults: {len(defaults)}")
    
    if len(defaults) == 0:
        advertencias.append("⚠️ No hay panel marcado como default")
    elif len(defaults) > 1:
        advertencias.append(f"⚠️ {len(defaults)} paneles marcados como default")
        print(f"   IDs: {', '.join([p['id'] for p in defaults])}")
    else:
        print(f"   ✅ Default: {defaults[0]['id']}")
    
    # Verificar eficiencia
    sin_eficiencia = [p for p in paneles if 'eficienciaPanel' not in p]
    if sin_eficiencia:
        advertencias.append(f"⚠️ {len(sin_eficiencia)} panel(es) sin eficienciaPanel (usará 1.0)")
    
    return errores, advertencias

def validate_baterias(baterias):
    """Validar configuración de baterías"""
    print("\n🔍 Validando Baterías...")
    print("="*60)
    
    errores = []
    advertencias = []
    
    defaults = [b for b in baterias if b.get('default', False)]
    
    print(f"   Total baterías: {len(baterias)}")
    print(f"   Defaults: {len(defaults)}")
    
    if len(defaults) == 0:
        advertencias.append("⚠️ No hay batería marcada como default")
    elif len(defaults) > 1:
        advertencias.append(f"⚠️ {len(defaults)} baterías marcadas como default")
    else:
        print(f"   ✅ Default: {defaults[0]['id']}")
    
    return errores, advertencias

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🔧 NASSA Solar - Validador de Defaults")
    print("="*60)
    
    # Cargar equipos
    try:
        equipos = load_equipos()
    except Exception as e:
        print(f"\n❌ ERROR cargando equipos.json: {e}")
        sys.exit(1)
    
    # Validar cada categoría
    errores_inv, adv_inv = validate_inversores(equipos['inversores'])
    errores_pan, adv_pan = validate_paneles(equipos['paneles'])
    errores_bat, adv_bat = validate_baterias(equipos['baterias'])
    
    # Consolidar resultados
    todos_errores = errores_inv + errores_pan + errores_bat
    todas_advertencias = adv_inv + adv_pan + adv_bat
    
    # Mostrar resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE VALIDACIÓN")
    print("="*60)
    
    if todos_errores:
        print(f"\n❌ ERRORES CRÍTICOS ({len(todos_errores)}):")
        for error in todos_errores:
            print(f"   {error}")
    
    if todas_advertencias:
        print(f"\n⚠️  ADVERTENCIAS ({len(todas_advertencias)}):")
        for adv in todas_advertencias:
            print(f"   {adv}")
    
    if not todos_errores and not todas_advertencias:
        print("\n✅ ¡Todo OK! Configuración coherente")
        print("   - Defaults correctamente configurados")
        print("   - Tipos de sistema válidos")
        print("   - Sin conflictos detectados")
    
    # Recomendaciones
    if todos_errores or todas_advertencias:
        print("\n📘 RECOMENDACIONES:")
        print("   1. Revisa ADMIN_GUIDE_DEFAULTS.md para mejores prácticas")
        print("   2. Usa el panel admin para marcar/desmarcar defaults")
        print("   3. Asegúrate de tener UN default por tipo de sistema")
        print("   4. Verifica que todos los inversores tengan 'tipo_sistema'")
    
    print("\n" + "="*60 + "\n")
    
    # Exit code
    sys.exit(1 if todos_errores else 0)

if __name__ == "__main__":
    main()
