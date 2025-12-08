import os
import json
import time
import tempfile
import shutil
import subprocess
import smtplib
import secrets
import unicodedata
from math import ceil
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, EmailStr, Field, field_validator
from email.message import EmailMessage
from dotenv import load_dotenv
from pptx import Presentation
from pptx.enum.text import PP_ALIGN
from pptx.util import Pt

load_dotenv()

# ========================================
# ⏰ ZONA HORARIA COLOMBIA (UTC-5)
# ========================================
COLOMBIA_TZ = timezone(timedelta(hours=-5))

def now_colombia():
    """Retorna la hora actual en Colombia (UTC-5)"""
    return datetime.now(COLOMBIA_TZ)

# ========================================
# 📁 CONFIGURACIÓN DE RUTAS
# ========================================
APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(APP_DIR, "config")
EQUIPOS_FILE = os.path.join(CONFIG_DIR, "equipos.json")
CIUDADES_FILE = os.path.join(CONFIG_DIR, "ciudades.json")
PARAMETROS_FILE = os.path.join(CONFIG_DIR, "parametros.json")
ESTADISTICAS_FILE = os.path.join(CONFIG_DIR, "estadisticas.json")
CONSECUTIVO_FILE = os.path.join(CONFIG_DIR, "consecutivo.json")
TEMPLATE_DIR = os.path.join(APP_DIR, "..", "Template")
TEMPLATE_PPTX = os.path.join(TEMPLATE_DIR, "Template-PreCotizacion.pptx")
TEMPLATE_PPTX_OP2 = os.path.join(TEMPLATE_DIR, "Template-PreCotizacion2.pptx")

# ========================================
# 🔒 CONFIGURACIÓN DE SEGURIDAD
# ========================================
app = FastAPI(
    title="NASSA Solar API",
    description="API segura para cotizaciones de sistemas fotovoltaicos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ========================================
# 📁 CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS
# ========================================
STATIC_DIR = os.path.join(APP_DIR, "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

security = HTTPBasic()
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "10"))
RATE_WINDOW = 60
request_counts: Dict[str, list] = {}

def rate_limit(request: Request):
    """Rate limiting por IP"""
    ip = request.client.host
    now = time.time()
    arr = request_counts.setdefault(ip, [])
    request_counts[ip] = [t for t in arr if now - t < RATE_WINDOW]
    if len(request_counts[ip]) >= RATE_LIMIT:
        raise HTTPException(429, f"Límite {RATE_LIMIT} req/min excedido")
    request_counts[ip].append(now)

def auth_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Verificar credenciales para endpoints administrativos"""
    u_ok = secrets.compare_digest(credentials.username, os.getenv("ADMIN_USER", "admin"))
    p_ok = secrets.compare_digest(credentials.password, os.getenv("ADMIN_PASS", "changeme"))
    if not (u_ok and p_ok):
        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Basic"}
        )
    return credentials.username

# ========================================
# 🔐 MODELOS CON VALIDACIÓN ROBUSTA
# ========================================
class CotizarRequest(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    telefono: str = Field(..., pattern=r'^\+?[0-9\s\-()]{7,20}$')
    email: EmailStr
    ciudad: str = Field(..., min_length=2, max_length=80)
    direccion: str = Field(..., min_length=5, max_length=200)
    consumoMensual: float = Field(..., gt=50, lt=50000)
    valorFactura: float = Field(..., gt=10000, lt=100000000)
    valorKwh: float = Field(..., gt=100, lt=5000)
    nic: str = Field(..., min_length=5, max_length=25)
    tipoVivienda: str = Field(..., pattern=r'^(casa|apartamento|local|empresa)$')
    areaDisponible: Optional[float] = Field(0, ge=0, lt=20000)
    numeroPisos: Optional[str] = Field("1", pattern=r'^[1-6]$')
    sistemaElectrico: str = Field(..., pattern=r'^(monofasico|bifasico|trifasico)$')
    porcentajeConsumodia: float = Field(..., ge=0, le=100)
    porcentajeAhorroEnergia: float = Field(100.0, ge=10, le=100, description="Porcentaje del consumo que desea cubrir con energía solar")
    tipoSistemaFV: str = Field(..., pattern=r'^(ongrid|offgrid|hibrido_incluido|hibrido_opcional)$')
    hspCalculado: Optional[float] = Field(None, gt=0, lt=9)
    legalizacion: str = Field(..., pattern=r'^(SI|NO)$')
    seleccionManual: str = Field(..., pattern=r'^(SI|NO)$')
    panel: Optional[str] = Field(None, pattern=r'^panel[1-9]\d?$')
    inversor: Optional[str] = Field(None, pattern=r'^inv[1-9]\d?$')
    bateria: Optional[str] = Field(None, pattern=r'^bat[1-9]\d?$')
    identificacion: Optional[str] = Field(None, max_length=20)

    @field_validator("bateria")
    @classmethod
    def validar_bateria(cls, v, info):
        if info.data.get("tipoSistemaFV") in ("offgrid", "hibrido_incluido") and not v:
            raise ValueError("Batería requerida para el tipo de sistema seleccionado")
        return v
    
    @field_validator("panel", "inversor")
    @classmethod
    def validar_equipos_manuales(cls, v, info):
        # Si seleccionManual es SI, panel e inversor son obligatorios
        if info.data.get("seleccionManual") == "SI" and not v:
            raise ValueError("Panel e inversor son requeridos cuando se selecciona manualmente")
        return v

# ========================================
# 📁 FUNCIONES AUXILIARES
# ========================================
def load_json(path: str) -> dict:
    """Cargar archivo JSON con manejo de errores"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(404, f"Archivo no encontrado: {os.path.basename(path)}")
    except json.JSONDecodeError:
        raise HTTPException(500, f"JSON inválido: {os.path.basename(path)}")

def obtener_siguiente_consecutivo() -> str:
    """
    Genera el siguiente número de cotización con formato NASSA-YYYY-#### 
    Usa lock de archivo para evitar duplicados en concurrencia
    """
    import fcntl
    
    consecutivo_file = os.path.join(CONFIG_DIR, "consecutivo.json")
    
    # Abrir con lock exclusivo
    with open(consecutivo_file, "r+", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        
        try:
            data = json.load(f)
            ano_actual = now_colombia().year
            
            # Si cambió el año, resetear consecutivo
            if data.get("ano_actual") != ano_actual:
                data["ano_actual"] = ano_actual
                data["ultimo_consecutivo"] = 0
            
            # Incrementar consecutivo
            data["ultimo_consecutivo"] += 1
            consecutivo = data["ultimo_consecutivo"]
            
            # Escribir de vuelta
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()
            
            # Formatear: NASSA-2025-0001
            cotizacion_id = f"NASSA-{ano_actual}-{consecutivo:04d}"
            return cotizacion_id
            
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def calcular_valor_legalizacion(capacidad_instalada_w: float, parametros: dict) -> float:
    """
    Calcula el costo de legalización según tabla de rangos
    
    Args:
        capacidad_instalada_w: Capacidad en Watts
        parametros: Dict con tabla_legalizacion.rangos
    
    Returns:
        Valor de legalización (no exento de IVA)
    """
    tabla = parametros.get("tabla_legalizacion", {}).get("rangos", [])
    
    for rango in tabla:
        if rango["min"] <= capacidad_instalada_w <= rango["max"]:
            return rango["valor"]
    
    # Fallback: último rango si no encuentra
    return tabla[-1]["valor"] if tabla else 0

def obtener_equipos_defaults(equipos: dict, sistema_electrico: str = None) -> dict:
    """
    Obtener equipos marcados como default en equipos.json
    
    Args:
        equipos: Diccionario con paneles, inversores y baterías
        sistema_electrico: Tipo de sistema eléctrico (monofasico, bifasico, trifasico)
                          Si se proporciona, filtra inversores compatibles
    
    Returns:
        Dict con IDs de panel, inversor y batería por defecto
        
    Algoritmo de selección (4 niveles de prioridad):
        1. Equipo marcado como default=True y compatible con sistema_electrico
        2. Primer equipo compatible (si no hay default para ese tipo)
        3. Equipo marcado como default=True (ignorando compatibilidad)
        4. Primer equipo disponible (fallback final)
    """
    # Panel: Buscar default o primer disponible
    panel_default = next((p for p in equipos["paneles"] if p.get("default", False)), None)
    if not panel_default:
        panel_default = equipos["paneles"][0] if equipos["paneles"] else None
        if panel_default:
            print(f"⚠️ No hay panel default, usando primer disponible: {panel_default.get('id')}")
    
    # Batería: Buscar default o primera disponible
    bateria_default = next((b for b in equipos["baterias"] if b.get("default", False)), None)
    if not bateria_default:
        bateria_default = equipos["baterias"][0] if equipos["baterias"] else None
        if bateria_default:
            print(f"⚠️ No hay batería default, usando primera disponible: {bateria_default.get('id')}")
    
    # FIX #3 y #4: Selección inteligente de inversor según sistema eléctrico
    inversor_default = None
    
    if sistema_electrico:
        # NIVEL 1: Buscar inversor default=True compatible con sistema_electrico
        inversor_default = next(
            (i for i in equipos["inversores"] 
             if i.get("default", False) and i.get("tipo_sistema") == sistema_electrico),
            None
        )
        
        # NIVEL 2: Si no hay default compatible, buscar PRIMER inversor compatible
        if not inversor_default:
            print(f"⚠️ No hay inversor default para {sistema_electrico}, buscando primer compatible...")
            inversor_default = next(
                (i for i in equipos["inversores"] if i.get("tipo_sistema") == sistema_electrico),
                None
            )
            
        # NIVEL 3: Si aún no hay compatible, usar cualquier default (sin importar tipo)
        if not inversor_default:
            print(f"⚠️⚠️ No hay inversores compatibles con {sistema_electrico}, usando default general...")
            inversor_default = next(
                (i for i in equipos["inversores"] if i.get("default", False)),
                None
            )
    else:
        # Sin sistema eléctrico especificado, usar default general
        inversor_default = next((i for i in equipos["inversores"] if i.get("default", False)), None)
    
    # NIVEL 4: Fallback final - primer inversor disponible
    if not inversor_default:
        inversor_default = equipos["inversores"][0] if equipos["inversores"] else None
        if inversor_default:
            print(f"⚠️⚠️⚠️ Usando primer inversor disponible como fallback: {inversor_default.get('id')}")
    
    return {
        "panel": panel_default["id"] if panel_default else None,
        "inversor": inversor_default["id"] if inversor_default else None,
        "bateria": bateria_default["id"] if bateria_default else None
    }

# ========================================
# 🧮 FUNCIÓN DE CÁLCULO
# ========================================
def calcular_cotizacion(data: dict, equipos: dict, ciudades: dict) -> dict:
    """
    Lógica de cálculo de cotización completa con:
    - Porcentaje de ahorro de energía
    - Lógica MICRO vs STRING para inversores
    - Costo de legalización por rangos
    - Consecutivo controlado
    """
    # Cargar parámetros de configuración
    parametros_path = os.path.join(APP_DIR, "config", "parametros.json")
    parametros = load_json(parametros_path)
    
    # Extraer parámetros
    costos = parametros["costos_instalacion"]
    fiscales = parametros["parametros_fiscales"]
    proyeccion = parametros["parametros_proyeccion"]
    parametros_sistema = parametros.get("parametros_sistema", {})
    
    # PUNTO 6: Porcentaje de ahorro de energía (default 100%)
    porcentajeAhorroEnergia = float(data.get("porcentajeAhorroEnergia", parametros_sistema.get("porcentaje_ahorro_default", 100)))
    
    consumoMensual = float(data["consumoMensual"])
    # MODIFICACIÓN CRÍTICA: Consumo objetivo basado en % ahorro
    consumoObjetivo = consumoMensual * (porcentajeAhorroEnergia / 100.0)
    
    valorFactura = float(data["valorFactura"])
    valorKwh = float(data["valorKwh"])
    ciudad_key = data["ciudad"].lower().strip().replace(" ", "_")
    
    # FIX: Compatibilidad con nuevo formato de ciudades.json (objeto con .hsp)
    ciudad_data = ciudades.get(ciudad_key, ciudades.get("default", 4.5))
    hsp_value = ciudad_data.get("hsp") if isinstance(ciudad_data, dict) else ciudad_data
    hsp = float(data.get("hspCalculado") or hsp_value)

    panel = next((x for x in equipos["paneles"] if x["id"] == data["panel"]), None)
    inversor = next((x for x in equipos["inversores"] if x["id"] == data["inversor"]), None)
    bateria = next((x for x in equipos["baterias"] if x["id"] == data.get("bateria")), None) if data.get("bateria") else None
    if not panel or not inversor:
        raise ValueError("Panel o inversor no encontrado")
    
    factorAreaEfectiva = parametros_sistema.get("factor_area_efectiva", 1.2)
    areaPanel = panel.get("area", 2.0)
    eficiencia_panel = panel.get("eficienciaPanel", parametros_sistema.get("eficiencia_panel_default", 1.0))
    eficiencia_inversor = inversor.get("eficiencia", parametros_sistema.get("eficiencia_inversor_default", 1.0))
    
    # CÁLCULO INICIAL de paneles basado en consumo objetivo
    consumoDiario = consumoObjetivo / 30
    energiaPanelDia = (panel["capacidad"] * eficiencia_panel * hsp) / 1000
    numeroPaneles_inicial = int(ceil((consumoDiario * 1.2) / energiaPanelDia))
    
    # PUNTO 5: Lógica de inversores MICRO vs STRING
    tipo_inversor = inversor.get("tipo", "STRING")
    
    if tipo_inversor == "MICRO":
        # MICRO: Basado en paneles por inversor
        paneles_por_inversor = inversor.get("paneles_por_inversor", 4)
        numeroInversores_raw = numeroPaneles_inicial / paneles_por_inversor
        decimal = numeroInversores_raw - int(numeroInversores_raw)
        
        if decimal < 0.5:
            numeroInversores = int(numeroInversores_raw)
        else:
            numeroInversores = int(numeroInversores_raw) + 1
        
        # Recalcular paneles si se redondeó hacia abajo
        numeroPaneles = numeroInversores * paneles_por_inversor
        
    else:  # STRING
        # STRING: Basado en capacidad con sobredimensionamiento
        sobredimensionamiento = inversor.get("sobredimensionamiento", 0.40)
        capacidad_inversor_w = inversor["capacidad"]
        capacidad_efectiva_w = capacidad_inversor_w * (1 + sobredimensionamiento)
        
        # Calcular capacidad instalada inicial
        capacidadInstalada_inicial = (numeroPaneles_inicial * panel["capacidad"]) / 1000  # kW
        
        # Número de inversores necesarios
        numeroInversores = int(ceil((capacidadInstalada_inicial * 1000) / capacidad_efectiva_w))
        
        # Capacidad máxima que pueden manejar los inversores
        capacidad_maxima_sistema = (numeroInversores * capacidad_efectiva_w) / 1000  # kW
        
        # Si la capacidad inicial excede la máxima, ajustar paneles
        if capacidadInstalada_inicial > capacidad_maxima_sistema:
            numeroPaneles = int((capacidad_maxima_sistema * 1000) / panel["capacidad"])
        else:
            numeroPaneles = numeroPaneles_inicial
    
    # RECALCULAR todo con paneles y/o inversores ajustados
    capacidadInstalada = (numeroPaneles * panel["capacidad"]) / 1000  # kW
    generacionMensual = numeroPaneles * energiaPanelDia * 30 * eficiencia_inversor
    generacionAnual = generacionMensual * 12
    areaRequerida = round(numeroPaneles * areaPanel * factorAreaEfectiva, 2)

    # Costos básicos desde parámetros configurables
    soporteria = costos["soporteria_por_panel"]
    instalacion = costos["instalacion_por_panel"]
    materialesAdicionales = costos["materiales_por_panel"]
    mantenimientoAnual = costos["mantenimiento_anual_por_kw"]

    costoPaneles = numeroPaneles * panel.get("precio", 0)
    costoInversores = numeroInversores * inversor.get("precio", 0)
    costoBaterias = bateria.get("precio", 0) if bateria else 0
    costoSoporteria = numeroPaneles * soporteria
    costoInstalacion = numeroPaneles * instalacion
    costoMateriales = numeroPaneles * materialesAdicionales

    # PUNTO 1: Valor de legalización (NO exento de IVA)
    capacidadInstalada_w = capacidadInstalada * 1000
    valorLegalizacion = calcular_valor_legalizacion(capacidadInstalada_w, parametros)
    incluir_legalizacion = data.get("legalizacion", "NO") == "SI"
    costoLegalizacion = valorLegalizacion if incluir_legalizacion else 0
    ivaLegalizacion = costoLegalizacion * fiscales["iva_porcentaje"]

    # Cálculo de costos totales
    subtotalAntesIVA = costoPaneles + costoInversores + costoBaterias + costoSoporteria + costoInstalacion + costoMateriales
    subtotalConLegalizacion = subtotalAntesIVA + costoLegalizacion
    
    # IVA: Equipos + Legalización
    ivaEquipos = (costoBaterias + costoSoporteria + costoInstalacion + costoMateriales) * fiscales["iva_porcentaje"]
    ivaTotal = ivaEquipos + ivaLegalizacion
    
    valorTotalSistema = subtotalConLegalizacion + ivaTotal

    porcentajeProduccionMensual = ((generacionMensual / consumoMensual) * 100) if consumoMensual > 0 else 0
    ahorroMensualEnergia = generacionMensual * valorKwh
    ahorroAnualEnergia = ahorroMensualEnergia * 12

    deduccionRentaBase = subtotalAntesIVA * fiscales["deduccion_renta_base_porcentaje"]
    deduccionRentaEfectiva = deduccionRentaBase * fiscales["impuesto_renta_porcentaje"]
    ahorroAnualDeduccion = (deduccionRentaEfectiva / fiscales["anos_deduccion"])
    depreciacionAnual = subtotalAntesIVA / fiscales["anos_depreciacion"]
    ahorroAnualDepreciacion = depreciacionAnual * fiscales["impuesto_renta_porcentaje"]

    tabla = []
    ahorroAcum = 0
    payback = 0
    alcanzado = False
    costoMantBase = capacidadInstalada * mantenimientoAnual
    acumxgen = acumxdeduc = acumxdepre = 0

    # Usar parámetros configurables para la proyección
    anos_proyeccion = proyeccion["anos_proyeccion"]
    degradacion_anual = proyeccion["degradacion_anual_panel"]
    factor_primer_ano = proyeccion["factor_primer_ano"]
    incremento_anual = proyeccion["incremento_anual_kwh"]
    anos_depreciacion = fiscales["anos_depreciacion"]
    anos_deduccion = fiscales["anos_deduccion"]

    for year in range(1, anos_proyeccion + 1):
        valorKwhAño = valorKwh * ((1 + incremento_anual) ** (year - 1))
        degradacion = ((1 - degradacion_anual) ** (year - 1))
        factorInicio = factor_primer_ano if year == 1 else 1
        prodAnual = generacionAnual * degradacion * factorInicio
        ahorroGeneracion = min(prodAnual * valorKwhAño, valorFactura * 12 * ((1 + incremento_anual) ** (year - 1)))
        ahorroDep = ahorroAnualDepreciacion if year <= anos_depreciacion else 0
        ahorroDed = ahorroAnualDeduccion if year <= anos_deduccion else 0
        costoMant = costoMantBase * ((1 + incremento_anual) ** (year - 1))
        ahorroTotal = ahorroGeneracion + ahorroDep + ahorroDed - costoMant
        ahorroAcum += ahorroTotal
        roi = ((ahorroAcum - valorTotalSistema) / valorTotalSistema) * 100 if valorTotalSistema else 0

        if not alcanzado and ahorroAcum >= valorTotalSistema:
            alcanzado = True
            payback = year

        if not alcanzado or year <= payback:
            acumxgen += ahorroGeneracion
            acumxdeduc += ahorroDed
            acumxdepre += ahorroDep

        tabla.append({
            "año": year,
            "valorKwhAño": round(valorKwhAño),
            "produccionAnual": round(prodAnual),
            "ahorroGeneracion": round(ahorroGeneracion),
            "ahorroDep": round(ahorroDep),
            "ahorroDed": round(ahorroDed),
            "costoMant": round(costoMant),
            "ahorroTotalAño": round(ahorroTotal),
            "ahorroAcumulado": round(ahorroAcum),
            "roi": round(roi, 2)
        })

    TotalAcum = acumxgen + acumxdeduc + acumxdepre
    TotalAcum = acumxgen + acumxdeduc + acumxdepre
    tiempoRetorno = payback or (valorTotalSistema / (ahorroAnualEnergia + ahorroAnualDeduccion + ahorroAnualDepreciacion + 1e-9))

    # PUNTO 3: Generar consecutivo controlado
    cotizacion_id = obtener_siguiente_consecutivo()

    return {
        "fecha": now_colombia().isoformat(),
        "cotizacionId": cotizacion_id,
        "panel": {"id": panel["id"], "nombre": panel["nombre"], "capacidad": panel["capacidad"], "area": areaPanel},
        "inversor": {
            "id": inversor["id"], 
            "nombre": inversor["nombre"], 
            "capacidad": inversor["capacidad"],
            "tipo": tipo_inversor,
            "paneles_por_inversor": inversor.get("paneles_por_inversor") if tipo_inversor == "MICRO" else None,
            "sobredimensionamiento": inversor.get("sobredimensionamiento") if tipo_inversor == "STRING" else None
        },
        "bateria": {"id": bateria["id"], "nombre": bateria["nombre"]} if bateria else None,
        "numeroPaneles": numeroPaneles,
        "numeroInversores": numeroInversores,
        "capacidadInstalada": round(capacidadInstalada, 2),
        "areaRequerida": areaRequerida,
        "areaDisponibleCliente": float(data.get("areaDisponible", 0)),
        "generacionMensual": round(generacionMensual),
        "generacionAnual": round(generacionAnual),
        "porcentajeAhorroEnergia": porcentajeAhorroEnergia,
        "consumoObjetivo": round(consumoObjetivo),
        # PUNTO 2: Desglose detallado de costos para preview
        "desgloseCostos": {
            "costoPaneles": round(costoPaneles),
            "costoInversores": round(costoInversores),
            "costoBaterias": round(costoBaterias),
            "costoSoporteria": round(costoSoporteria),
            "costoInstalacion": round(costoInstalacion),
            "costoMateriales": round(costoMateriales),
            "costoLegalizacion": round(costoLegalizacion),
            "subtotalAntesIVA": round(subtotalAntesIVA),
            "ivaEquipos": round(ivaEquipos),
            "ivaLegalizacion": round(ivaLegalizacion),
            "ivaTotal": round(ivaTotal)
        },
        "valorTotalSistema": round(valorTotalSistema),
        "ahorroMensualEnergia": round(ahorroMensualEnergia),
        "ahorroAnualEnergia": round(ahorroAnualEnergia),
        "tiempoRetorno": round(tiempoRetorno, 1),
        "tablaAhorros": tabla,
        "porcentajeProduccionMensual": round(porcentajeProduccionMensual, 1),
        "subtotalAntesIVA": round(subtotalAntesIVA),
        "deduccionRentaBase": round(deduccionRentaBase),
        "deduccionRentaEfectiva": round(deduccionRentaEfectiva),
        "depreciacionAnual": round(depreciacionAnual),
        "ahorroAnualDepreciacion": round(ahorroAnualDepreciacion),
        "ahorroTotalDepreciacion": round(ahorroAnualDepreciacion * 3),
        "ahorroTotalDeduccion": round(deduccionRentaEfectiva),
        "acumxgen": round(acumxgen),
        "acumxdeduc": round(acumxdeduc),
        "acumxdepre": round(acumxdepre),
        "TotalAcum": round(TotalAcum)
    }

def calcular_segunda_opcion(data: dict, equipos: dict, ciudades: dict, areaDisponible: float, cotizacion_id_base: str) -> dict:
    """
    Calcula cotización ajustada al área disponible del cliente.
    Reduce número de paneles para que quepan en el espacio real.
    Usa la misma lógica MICRO/STRING y legalización que calcular_cotizacion.
    
    Args:
        cotizacion_id_base: ID base (ej: "NASSA-2025-0001") para mantener consistencia
    """
    parametros_path = os.path.join(APP_DIR, "config", "parametros.json")
    parametros = load_json(parametros_path)
    
    costos = parametros["costos_instalacion"]
    fiscales = parametros["parametros_fiscales"]
    proyeccion = parametros["parametros_proyeccion"]
    parametros_sistema = parametros.get("parametros_sistema", {})
    
    # Porcentaje de ahorro
    porcentajeAhorroEnergia = float(data.get("porcentajeAhorroEnergia", parametros_sistema.get("porcentaje_ahorro_default", 100)))
    
    consumoMensual = float(data["consumoMensual"])
    consumoObjetivo = consumoMensual * (porcentajeAhorroEnergia / 100.0)
    valorFactura = float(data["valorFactura"])
    valorKwh = float(data["valorKwh"])
    ciudad_key = data["ciudad"].lower().strip().replace(" ", "_")
    
    ciudad_data = ciudades.get(ciudad_key, ciudades.get("default", 4.5))
    hsp_value = ciudad_data.get("hsp") if isinstance(ciudad_data, dict) else ciudad_data
    hsp = float(data.get("hspCalculado") or hsp_value)

    panel = next((x for x in equipos["paneles"] if x["id"] == data["panel"]), None)
    inversor = next((x for x in equipos["inversores"] if x["id"] == data["inversor"]), None)
    bateria = next((x for x in equipos["baterias"] if x["id"] == data.get("bateria")), None) if data.get("bateria") else None
    
    factorAreaEfectiva = parametros_sistema.get("factor_area_efectiva", 1.2)
    areaPanel = panel.get("area", 2.0)
    
    # CALCULAR NÚMERO MÁXIMO DE PANELES QUE CABEN EN EL ÁREA
    numeroPaneles_max = max(1, int(areaDisponible / (areaPanel * factorAreaEfectiva)))
    
    # Aplicar lógica MICRO/STRING con restricción de área
    eficiencia_panel = panel.get("eficienciaPanel", parametros_sistema.get("eficiencia_panel_default", 1.0))
    eficiencia_inversor = inversor.get("eficiencia", parametros_sistema.get("eficiencia_inversor_default", 1.0))
    energiaPanelDia = (panel["capacidad"] * eficiencia_panel * hsp) / 1000
    
    tipo_inversor = inversor.get("tipo", "STRING")
    
    if tipo_inversor == "MICRO":
        paneles_por_inversor = inversor.get("paneles_por_inversor", 4)
        # Ajustar a múltiplo de paneles_por_inversor que quepa en área
        numeroInversores = numeroPaneles_max // paneles_por_inversor
        if numeroInversores == 0:
            numeroInversores = 1
        numeroPaneles = numeroInversores * paneles_por_inversor
        # Si excede área, reducir un inversor
        if numeroPaneles > numeroPaneles_max:
            numeroInversores = max(1, numeroInversores - 1)
            numeroPaneles = numeroInversores * paneles_por_inversor
    else:  # STRING
        # Usar todos los paneles que quepan
        numeroPaneles = numeroPaneles_max
        sobredimensionamiento = inversor.get("sobredimensionamiento", 0.40)
        capacidad_inversor_w = inversor["capacidad"]
        capacidad_efectiva_w = capacidad_inversor_w * (1 + sobredimensionamiento)
        capacidadInstalada_temp = (numeroPaneles * panel["capacidad"]) / 1000
        numeroInversores = int(ceil((capacidadInstalada_temp * 1000) / capacidad_efectiva_w))
    
    # RECALCULAR con paneles/inversores ajustados
    capacidadInstalada = (numeroPaneles * panel["capacidad"]) / 1000
    generacionMensual = numeroPaneles * energiaPanelDia * 30 * eficiencia_inversor
    generacionAnual = generacionMensual * 12
    areaRequerida = round(numeroPaneles * areaPanel * factorAreaEfectiva, 2)
    
    # Costos con legalización
    soporteria = costos["soporteria_por_panel"]
    instalacion = costos["instalacion_por_panel"]
    materialesAdicionales = costos["materiales_por_panel"]
    mantenimientoAnual = costos["mantenimiento_anual_por_kw"]
    
    costoPaneles = numeroPaneles * panel.get("precio", 0)
    costoInversores = numeroInversores * inversor.get("precio", 0)
    costoBaterias = bateria.get("precio", 0) if bateria else 0
    costoSoporteria = numeroPaneles * soporteria
    costoInstalacion = numeroPaneles * instalacion
    costoMateriales = numeroPaneles * materialesAdicionales
    
    # Legalización (si aplica)
    capacidadInstalada_w = capacidadInstalada * 1000
    valorLegalizacion = calcular_valor_legalizacion(capacidadInstalada_w, parametros)
    incluir_legalizacion = data.get("legalizacion", "NO") == "SI"
    costoLegalizacion = valorLegalizacion if incluir_legalizacion else 0
    ivaLegalizacion = costoLegalizacion * fiscales["iva_porcentaje"]
    
    subtotalAntesIVA = costoPaneles + costoInversores + costoBaterias + costoSoporteria + costoInstalacion + costoMateriales
    subtotalConLegalizacion = subtotalAntesIVA + costoLegalizacion
    ivaEquipos = (costoBaterias + costoSoporteria + costoInstalacion + costoMateriales) * fiscales["iva_porcentaje"]
    ivaTotal = ivaEquipos + ivaLegalizacion
    valorTotalSistema = subtotalConLegalizacion + ivaTotal
    
    porcentajeProduccionMensual = ((generacionMensual / consumoMensual) * 100) if consumoMensual > 0 else 0
    ahorroMensualEnergia = generacionMensual * valorKwh
    ahorroAnualEnergia = ahorroMensualEnergia * 12
    
    # Fiscales
    deduccionRentaBase = subtotalAntesIVA * fiscales["deduccion_renta_base_porcentaje"]
    deduccionRentaEfectiva = deduccionRentaBase * fiscales["impuesto_renta_porcentaje"]
    ahorroAnualDeduccion = (deduccionRentaEfectiva / fiscales["anos_deduccion"])
    depreciacionAnual = subtotalAntesIVA / fiscales["anos_depreciacion"]
    ahorroAnualDepreciacion = depreciacionAnual * fiscales["impuesto_renta_porcentaje"]
    
    # Proyección 30 años - usar nombres correctos
    anos_proyeccion = proyeccion["anos_proyeccion"]
    degradacion_anual = proyeccion["degradacion_anual_panel"]
    factor_primer_ano = proyeccion["factor_primer_ano"]
    incremento_anual = proyeccion["incremento_anual_kwh"]
    anos_depreciacion = fiscales["anos_depreciacion"]
    anos_deduccion = fiscales["anos_deduccion"]
    
    tabla = []
    acumxgen = acumxdeduc = acumxdepre = 0
    ahorroAcum = 0
    payback = None
    costoMantBase = capacidadInstalada * mantenimientoAnual
    alcanzado = False
    
    for year in range(1, anos_proyeccion + 1):
        valorKwhAño = valorKwh * ((1 + incremento_anual) ** (year - 1))
        degradacion = ((1 - degradacion_anual) ** (year - 1))
        factorInicio = factor_primer_ano if year == 1 else 1
        prodAnual = generacionAnual * degradacion * factorInicio
        ahorroGeneracion = min(prodAnual * valorKwhAño, valorFactura * 12 * ((1 + incremento_anual) ** (year - 1)))
        
        ahorroDep = ahorroAnualDepreciacion if year <= anos_depreciacion else 0
        ahorroDed = ahorroAnualDeduccion if year <= anos_deduccion else 0
        costoMant = costoMantBase * ((1 + incremento_anual) ** (year - 1))
        
        ahorroTotal = ahorroGeneracion + ahorroDep + ahorroDed - costoMant
        ahorroAcum += ahorroTotal
        roi = ((ahorroAcum - valorTotalSistema) / valorTotalSistema) * 100 if valorTotalSistema else 0
        
        if not alcanzado and ahorroAcum >= valorTotalSistema:
            alcanzado = True
            payback = year
        
        if not alcanzado or year <= (payback or anos_proyeccion):
            acumxgen += ahorroGeneracion
            acumxdeduc += ahorroDed
            acumxdepre += ahorroDep
        
        tabla.append({
            "año": year,
            "valorKwhAño": round(valorKwhAño),
            "produccionAnual": round(prodAnual),
            "ahorroGeneracion": round(ahorroGeneracion),
            "ahorroDep": round(ahorroDep),
            "ahorroDed": round(ahorroDed),
            "costoMant": round(costoMant),
            "ahorroTotalAño": round(ahorroTotal),
            "ahorroAcumulado": round(ahorroAcum),
            "roi": round(roi, 2)
        })
    
    TotalAcum = acumxgen + acumxdeduc + acumxdepre
    tiempoRetorno = payback or (valorTotalSistema / (ahorroAnualEnergia + ahorroAnualDeduccion + ahorroAnualDepreciacion + 1e-9))
    
    return {
        "fecha": now_colombia().isoformat(),
        "cotizacionId": cotizacion_id_base + "-OP2",  # Usar el mismo ID base con sufijo
        "panel": {"id": panel["id"], "nombre": panel["nombre"], "capacidad": panel["capacidad"], "area": areaPanel},
        "inversor": {
            "id": inversor["id"], 
            "nombre": inversor["nombre"], 
            "capacidad": inversor["capacidad"],
            "tipo": tipo_inversor,
            "paneles_por_inversor": inversor.get("paneles_por_inversor") if tipo_inversor == "MICRO" else None,
            "sobredimensionamiento": inversor.get("sobredimensionamiento") if tipo_inversor == "STRING" else None
        },
        "bateria": {"id": bateria["id"], "nombre": bateria["nombre"]} if bateria else None,
        "numeroPaneles": numeroPaneles,
        "numeroInversores": numeroInversores,
        "capacidadInstalada": round(capacidadInstalada, 2),
        "areaRequerida": areaRequerida,
        "areaDisponibleCliente": areaDisponible,
        "generacionMensual": round(generacionMensual),
        "generacionAnual": round(generacionAnual),
        "porcentajeAhorroEnergia": porcentajeAhorroEnergia,
        "consumoObjetivo": round(consumoObjetivo),
        "desgloseCostos": {
            "costoPaneles": round(costoPaneles),
            "costoInversores": round(costoInversores),
            "costoBaterias": round(costoBaterias),
            "costoSoporteria": round(costoSoporteria),
            "costoInstalacion": round(costoInstalacion),
            "costoMateriales": round(costoMateriales),
            "costoLegalizacion": round(costoLegalizacion),
            "subtotalAntesIVA": round(subtotalAntesIVA),
            "subtotalConLegalizacion": round(subtotalConLegalizacion),
            "ivaEquipos": round(ivaEquipos),
            "ivaLegalizacion": round(ivaLegalizacion),
            "ivaTotal": round(ivaTotal)
        },
        "valorTotalSistema": round(valorTotalSistema),
        "ahorroMensualEnergia": round(ahorroMensualEnergia),
        "ahorroAnualEnergia": round(ahorroAnualEnergia),
        "tiempoRetorno": round(tiempoRetorno, 1),
        "tablaAhorros": tabla,
        "porcentajeProduccionMensual": round(porcentajeProduccionMensual, 1),
        "subtotalAntesIVA": round(subtotalAntesIVA),
        "deduccionRentaBase": round(deduccionRentaBase),
        "deduccionRentaEfectiva": round(deduccionRentaEfectiva),
        "depreciacionAnual": round(depreciacionAnual),
        "ahorroAnualDepreciacion": round(ahorroAnualDepreciacion),
        "ahorroTotalDepreciacion": round(ahorroAnualDepreciacion * 3),
        "ahorroTotalDeduccion": round(deduccionRentaEfectiva),
        "acumxgen": round(acumxgen),
        "acumxdeduc": round(acumxdeduc),
        "acumxdepre": round(acumxdepre),
        "TotalAcum": round(TotalAcum)
    }

# ========================================
# 📄 PROCESAMIENTO DE TEMPLATE PPTX
# ========================================
def _normalize(t: str) -> str:
    """Normaliza texto para comparación de encabezados"""
    if t is None:
        return ""
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii")
    t = t.strip().lower().replace("_", "").replace("-", "").replace(" ", "")
    return t

def _find_table_by_name_or_headers(prs, preferred_name: str = "TABLA_AHORROS"):
    """Busca tabla por nombre o por encabezados"""
    for slide in prs.slides:
        for shape in slide.shapes:
            if getattr(shape, "name", "") == preferred_name and shape.has_table:
                return shape.table
    
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_table:
                table = shape.table
                if table.rows and table.columns:
                    headers = [_normalize(cell.text) for cell in table.rows[0].cells]
                    if any("AÑO" in h or "año" in h for h in headers) and any("Ahorro" in h for h in headers):
                        return table
    return None

def _map_columns_by_header(table):
    """Mapea índices de columnas según encabezados"""
    header_map = {}
    headers = [cell.text.strip() for cell in table.rows[0].cells]  # Sin normalizar para preservar mayúsculas
    
    for idx, h in enumerate(headers):
        h_lower = h.lower().replace(" ", "").replace("_", "").replace("-", "")
        
        if "año" in h_lower:
            header_map["año"] = idx
        elif "valorkwh" in h_lower:
            header_map["valorKwh"] = idx
        elif "producción" in h_lower or "produccion" in h_lower:
            header_map["produccionAnual"] = idx
        elif "generacion" in h_lower or "generación" in h_lower:
            header_map["generacion"] = idx
        elif "depreciacion" in h_lower or "depreciación" in h_lower:
            header_map["depreciacion"] = idx
        elif "deduccion" in h_lower or "deducción" in h_lower:
            header_map["deduccion"] = idx
        elif "costomtto" in h_lower or "costomant" in h_lower:
            header_map["costoMtto"] = idx
        elif "totahorro" in h_lower or "ahorrototal" in h_lower:
            header_map["ahorroAño"] = idx
        elif "acumulado" in h_lower:
            header_map["acumulado"] = idx
        elif h.upper() == "ROI":
            header_map["roi"] = idx
    return header_map

def fill_ahorros_table_in_ppt(prs, tabla_ahorros: list, max_years: int = None):
    """Llena la tabla de ahorros en el PPTX con formato y alineación
    
    Args:
        prs: Presentación de PowerPoint
        tabla_ahorros: Lista con datos de ahorros por año
        max_years: Número máximo de años a llenar (None = detectar automáticamente desde tabla)
    """
    table = _find_table_by_name_or_headers(prs, "TABLA_AHORROS")
    if table is None:
        print("⚠️ No se encontró TABLA_AHORROS en el Template - continuando sin llenar tabla")
        return

    col_map = _map_columns_by_header(table)
    print(f"📊 Columnas detectadas en tabla: {list(col_map.keys())}")
    
    required = {"año", "roi"}
    if not required.issubset(col_map.keys()):
        print(f"⚠️ Encabezados insuficientes. Encontrados: {list(col_map.keys())} - continuando sin llenar tabla")
        return

    # Detectar automáticamente el número de filas disponibles (excluyendo el encabezado)
    filas_disponibles = len(table.rows) - 1  # -1 porque la primera fila es el encabezado
    print(f"📋 Filas disponibles en tabla: {filas_disponibles}")
    
    # Determinar cuántos años llenar: el mínimo entre filas disponibles, datos disponibles y max_years (si se especifica)
    if max_years is None:
        n = min(filas_disponibles, len(tabla_ahorros))
    else:
        n = min(max_years, filas_disponibles, len(tabla_ahorros))
    
    print(f"✍️  Llenando {n} años en la tabla")
    
    for i in range(n):
        row_idx = i + 1
        if row_idx >= len(table.rows):
            break
        
        año_data = tabla_ahorros[i]
        año = año_data.get("año", i + 1)
        
        # Función auxiliar para formatear celdas con formato ARIAL 9pt consistente
        def set_cell_value(col_key, value_text):
            if col_key in col_map:
                cell = table.cell(row_idx, col_map[col_key])
                
                # Aplicar formato Arial 9pt de forma explícita
                if cell.text_frame and cell.text_frame.paragraphs:
                    for paragraph in cell.text_frame.paragraphs:
                        # Si hay runs, usar el primer run
                        if paragraph.runs:
                            # Limpiar texto de todos los runs
                            for run in paragraph.runs:
                                run.text = ""
                            # Poner el nuevo valor en el primer run y aplicar formato
                            first_run = paragraph.runs[0]
                            first_run.text = value_text
                            first_run.font.name = "Arial"
                            first_run.font.size = Pt(7)
                        else:
                            # Si no hay runs, crear uno con formato Arial 7pt
                            run = paragraph.add_run()
                            run.text = value_text
                            run.font.name = "Arial"
                            run.font.size = Pt(7)
                        
                        # Cambiar alineación para columnas numéricas
                        if col_key in ["valorKwh", "produccionAnual", "generacion", "depreciacion", 
                                     "deduccion", "costoMtto", "ahorroAño", "acumulado", "roi"]:
                            paragraph.alignment = PP_ALIGN.RIGHT
                        else:
                            paragraph.alignment = PP_ALIGN.CENTER
        
        # Llenar columnas con valores formateados
        set_cell_value("año", str(año))
        set_cell_value("valorKwh", f"${año_data.get('valorKwhAño', 0):,.0f}")
        set_cell_value("produccionAnual", f"{año_data.get('produccionAnual', 0):,.0f}")  # CORREGIDO: era 'produccionAnual'
        set_cell_value("generacion", f"${año_data.get('ahorroGeneracion', 0):,.0f}")
        set_cell_value("depreciacion", f"${año_data.get('ahorroDep', 0):,.0f}")
        set_cell_value("deduccion", f"${año_data.get('ahorroDed', 0):,.0f}")
        set_cell_value("costoMtto", f"${año_data.get('costoMant', 0):,.0f}")
        set_cell_value("ahorroAño", f"${año_data.get('ahorroTotalAño', 0):,.0f}")
        set_cell_value("acumulado", f"${año_data.get('ahorroAcumulado', 0):,.0f}")
        set_cell_value("roi", f"{año_data.get('roi', 0):.2f}%")

    # Limpiar filas vacías
    for j in range(n + 1, len(table.rows)):
        for c in range(len(table.columns)):
            table.cell(j, c).text = ""

def build_placeholders(req: dict, resultado: dict, opcion: str = "") -> dict:
    """
    Construye diccionario de placeholders - TODOS máximo 8 letras
    opcion: "" para una sola opción, "OPCIÓN 1" o "OPCIÓN 2 - Ajustada a área disponible"
    """
    print(f"   🏗️  Construyendo placeholders para: {opcion if opcion else '(única)'}")
    print(f"      N_PANEL: {resultado['numeroPaneles']}, CAP_KW: {resultado['capacidadInstalada']} kW")
    print(f"      AREA_REQ: {resultado['areaRequerida']} m², INVER: ${resultado['valorTotalSistema']:,.0f}")
    
    # Manejar baterías: si no hay batería, dejar campos en blanco
    num_baterias = "1" if resultado.get("bateria") else " "
    bateria_modelo = resultado["bateria"]["nombre"] if resultado.get("bateria") else " "
    
    # Mapeo de nombres de sistemas a formato correcto
    tipo_sistema_map = {
        "ongrid": "ON GRID",
        "offgrid": "OFF GRID",
        "hibrido_incluido": "HIBRIDO CON BATERIA",
        "hibrido_opcional": "HIBRIDO OPCIONAL BATERIA"
    }
    tipo_sistema_texto = tipo_sistema_map.get(req["tipoSistemaFV"], req["tipoSistemaFV"].upper())
    
    return {
        # Información general (8 letras máx)
        "{{COT_ID}}": resultado["cotizacionId"],
        "{{FECHA}}": resultado["fecha"][:10],
        "{{OPCION}}": opcion,
        
        # Datos del cliente (8 letras máx)
        "{{NOMBRE}}": req["nombre"],
        "{{EMAIL}}": req["email"],
        "{{TELEFONO}}": req["telefono"],
        "{{CIUDAD}}": req["ciudad"],
        "{{DIRECC}}": req["direccion"],
        "{{NIC}}": req.get("nic", "N/A"),
        
        # Consumo energético (8 letras máx)
        "{{CONSUMO}}": f"{req['consumoMensual']:.0f} kWh",
        "{{FACTURA}}": f"${req['valorFactura']:,.0f}",
        "{{VAL_KWH}}": f"${req['valorKwh']:,.0f}",
        
        # Características del inmueble (8 letras máx)
        "{{VIVIENDA}}": req["tipoVivienda"],
        "{{SIS_ELEC}}": req["sistemaElectrico"],
        "{{TIPO_FV}}": tipo_sistema_texto,
        
        # Equipamiento (8 letras máx)
        "{{N_PANEL}}": str(resultado["numeroPaneles"]),
        "{{M_PANEL}}": resultado["panel"]["nombre"],
        "{{N_INVER}}": str(resultado["numeroInversores"]),
        "{{M_INVER}}": resultado["inversor"]["nombre"],
        "{{N_BATER}}": num_baterias,
        "{{M_BATER}}": bateria_modelo,
        
        # Especificaciones técnicas (8 letras máx)
        "{{CAP_KW}}": f"{resultado['capacidadInstalada']} kW",
        "{{GEN_MES}}": f"{resultado['generacionMensual']} kWh",
        "{{AREA_REQ}}": f"{resultado['areaRequerida']} m²",
        
        # Análisis financiero (8 letras máx)
        "{{INVER}}": f"${resultado['valorTotalSistema']:,.0f}",
        "{{SUBTOT}}": f"${resultado['subtotalAntesIVA']:,.0f}",
        "{{AHO_MES}}": f"${resultado['ahorroMensualEnergia']:,.0f}",
        "{{RETORNO}}": f"{resultado['tiempoRetorno']} años",
        "{{PORC_PR}}": f"{resultado['porcentajeProduccionMensual']}%",
        # Condiciones comerciales (NEW)
        "{{COND_COM}}": resultado.get("condicionesComerciales", ""),
        # Campos adicionales solicitados
        "{{NPISOS}}": str(req.get('numeroPisos', '1')),
        "{{HSPC}}": f"{req.get('hspCalculado') if req.get('hspCalculado') is not None else ''}",
        "{{AREA}}": f"{req.get('areaDisponible', '')}",
        "{{PCTDIA}}": f"{req.get('porcentajeConsumodia', '')}%"
    }

def replace_text_in_shape(shape, mapping: dict):
    """Reemplaza texto en un shape individual manejando placeholders divididos entre runs"""
    if not hasattr(shape, 'has_text_frame') or not shape.has_text_frame:
        return
    
    for paragraph in shape.text_frame.paragraphs:
        # PASO 1: Intentar reemplazo simple run por run (caso ideal)
        for run in paragraph.runs:
            if run.text:
                original_text = run.text
                new_text = original_text
                
                # Reemplazar placeholders completos dentro de este run
                for placeholder, value in mapping.items():
                    if placeholder in new_text:
                        new_text = new_text.replace(placeholder, value)
                
                if new_text != original_text:
                    run.text = new_text
        
        # PASO 2: Verificar si quedan placeholders divididos entre runs
        full_text = "".join(r.text for r in paragraph.runs)
        
        # Si hay placeholders en el texto completo pero no fueron reemplazados
        has_unreplaced = any(placeholder in full_text for placeholder in mapping.keys())
        
        if has_unreplaced:
            # Placeholder dividido entre runs - consolidar
            replaced_text = full_text
            for placeholder, value in mapping.items():
                replaced_text = replaced_text.replace(placeholder, value)
            
            if replaced_text != full_text:
                # Necesitamos consolidar: guardar formato del primer run
                if paragraph.runs:
                    first_run = paragraph.runs[0]
                    
                    # Limpiar todos los runs
                    for run in paragraph.runs:
                        run.text = ""
                    
                    # Poner todo el texto en el primer run
                    first_run.text = replaced_text

def replace_shape_text(shape, mapping: dict):
    """Reemplaza texto en shapes con estrategia simple de buscar-y-reemplazar"""
    from pptx.enum.text import PP_ALIGN
    
    replaced_count = 0
    
    # 1. Si tiene text_frame, procesar
    if hasattr(shape, 'has_text_frame') and shape.has_text_frame:
        replace_text_in_shape(shape, mapping)
    
    # 2. Si es tabla, procesar cada celda con enfoque run-by-run
    if hasattr(shape, 'has_table') and shape.has_table:
        for row in shape.table.rows:
            for cell in row.cells:
                # Procesar cada párrafo y run de la celda
                for paragraph in cell.text_frame.paragraphs:
                    # PASO 1: Intentar reemplazo simple run por run
                    for run in paragraph.runs:
                        if run.text:
                            original_text = run.text
                            new_text = original_text
                            
                            # Reemplazar placeholders
                            for k, v in mapping.items():
                                if k in new_text:
                                    new_text = new_text.replace(k, v)
                                    replaced_count += 1
                            
                            # Actualizar solo si hubo cambios
                            if new_text != original_text:
                                run.text = new_text
                    
                    # PASO 2: Verificar placeholders divididos
                    full_text = "".join(r.text for r in paragraph.runs)
                    has_unreplaced = any(placeholder in full_text for placeholder in mapping.keys())
                    
                    if has_unreplaced:
                        # Placeholder dividido - consolidar
                        replaced_text = full_text
                        for k, v in mapping.items():
                            replaced_text = replaced_text.replace(k, v)
                            if k in full_text:
                                replaced_count += 1
                        
                        if replaced_text != full_text and paragraph.runs:
                            # Limpiar todos los runs
                            for run in paragraph.runs:
                                run.text = ""
                            # Poner texto en el primer run
                            paragraph.runs[0].text = replaced_text
                    
                    # Ajustar alineación para placeholders de totales
                    cell_text = "".join(r.text for r in paragraph.runs)
                    # Alinear celdas con valores monetarios a la derecha
                    if '$' in cell_text:
                        paragraph.alignment = PP_ALIGN.RIGHT
    
    return replaced_count

def fill_template_and_convert(req: dict, resultado: dict, opcion: str = "", template_path: str = None) -> tuple:
    """
    Llena template y convierte a PDF
    opcion: "" para una sola opción, "OPCIÓN 1" o "OPCIÓN 2 - Ajustada a área disponible"
    template_path: Ruta al template PPTX (usa TEMPLATE_PPTX por defecto)
    """
    # Usar template especificado o el por defecto
    template_to_use = template_path if template_path else TEMPLATE_PPTX
    
    if not os.path.isfile(template_to_use):
        raise RuntimeError(f"Template PPTX no encontrado: {template_to_use}")
    
    # Crear archivo temporal con nombre único que incluya timestamp
    timestamp_ms = int(datetime.now().timestamp() * 1000)
    opcion_suffix = "_op1" if opcion and "OPCIÓN 1" in opcion else "_op2" if opcion and "OPCIÓN 2" in opcion else ""
    fd_temp, filled_path = tempfile.mkstemp(
        suffix=f"_{timestamp_ms}{opcion_suffix}.pptx",
        prefix="cotizacion_"
    )
    os.close(fd_temp)
    
    # Copiar template original (FRESCO) al archivo temporal
    shutil.copy(template_to_use, filled_path)
    print(f"\n📄 ===== GENERANDO PDF {opcion if opcion else '(ÚNICA OPCIÓN)'} =====")
    print(f"   Template usado: {os.path.basename(template_to_use)}")
    print(f"   Template copiado a: {os.path.basename(filled_path)}")
    print(f"   Paneles: {resultado['numeroPaneles']}")
    print(f"   Capacidad: {resultado['capacidadInstalada']} kW")
    print(f"   Área requerida: {resultado['areaRequerida']} m²")
    print(f"   Valor total: ${resultado['valorTotalSistema']:,.0f}")

    # Cargar presentación desde la copia fresca
    prs = Presentation(filled_path)
    
    # Reemplazar placeholders (pasando el parámetro opcion)
    mapping = build_placeholders(req, resultado, opcion)
    total_replaced = 0
    print(f"🔄 Iniciando reemplazo de placeholders...")
    print(f"   Total de placeholders definidos: {len(mapping)}")
    print(f"   Opción: {opcion if opcion else '(única)'}") 
    
    for slide_idx, slide in enumerate(prs.slides):
        print(f"\n   📄 Procesando diapositiva {slide_idx + 1}...")
        # Procesar cada shape directamente (sin recursión)
        for shape in slide.shapes:
            count = replace_shape_text(shape, mapping)
            total_replaced += count
    
    print(f"\n✅ Total de reemplazos realizados: {total_replaced}")
    
    # Llenar tabla de ahorros (detecta automáticamente el número de filas)
    fill_ahorros_table_in_ppt(prs, resultado["tablaAhorros"])
    
    prs.save(filled_path)
    
    # Convertir a PDF con LibreOffice
    libreoffice_bin = os.getenv("LIBREOFFICE_PATH", "soffice")
    out_dir = tempfile.mkdtemp()
    cmd = [
        libreoffice_bin,
        "--headless",
        "--norestore",
        "--invisible",
        "--convert-to", "pdf",
        "--outdir", out_dir,
        filled_path
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
    if proc.returncode != 0:
        raise RuntimeError(f"LibreOffice error: {proc.stderr.decode('utf-8')}")
    
    pdf_name = os.path.splitext(os.path.basename(filled_path))[0] + ".pdf"
    pdf_path = os.path.join(out_dir, pdf_name)
    if not os.path.isfile(pdf_path):
        raise RuntimeError("Conversión a PDF fallida")
    
    return filled_path, pdf_path

# ========================================
# 📧 ENVÍO DE EMAIL
# ========================================
def enviar_email(destino: str, pdf_path: str, resultado: dict, pptx_path: Optional[str] = None):
    """Enviar email solo con PDF adjunto"""
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")
    EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER)
    EMAIL_NASSA = os.getenv("EMAIL_NASSA", EMAIL_FROM)

    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS, destino]):
        raise RuntimeError("SMTP incompleto")

    msg = EmailMessage()
    msg["Subject"] = f"Cotización NASSA Solar - {resultado['cotizacionId']}"
    msg["From"] = EMAIL_FROM
    msg["To"] = destino
    if EMAIL_NASSA and EMAIL_NASSA != destino:
        msg["Cc"] = EMAIL_NASSA

    cuerpo = f"""
Estimado cliente,

Adjuntamos su cotización personalizada:

📊 RESUMEN:
- ID: {resultado['cotizacionId']}
- Inversión: ${resultado['valorTotalSistema']:,.0f} COP
- Ahorro mensual: ${resultado['ahorroMensualEnergia']:,.0f} COP
- Retorno: {resultado['tiempoRetorno']} años
- Capacidad: {resultado['capacidadInstalada']} kW

Quedamos atentos a sus consultas.

Saludos cordiales,
NASSA SOLAR
Tel: (057) 313 690 9723
www.nassasolar.com
"""
    msg.set_content(cuerpo.strip())

    with open(pdf_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf",
                          filename=f"Cotizacion_{resultado['cotizacionId']}.pdf")

    # Construir lista de destinatarios para send_message
    destinatarios = [destino]
    if EMAIL_NASSA and EMAIL_NASSA != destino:
        destinatarios.append(EMAIL_NASSA)

    # Intentar primero puerto 465 (SSL) y luego 587 (STARTTLS)
    puertos_intentar = [465, SMTP_PORT] if SMTP_PORT != 465 else [465]
    
    for puerto in puertos_intentar:
        try:
            if puerto == 465:
                # Usar SMTP_SSL para puerto 465
                with smtplib.SMTP_SSL(SMTP_HOST, puerto, timeout=60) as server:
                    server.login(SMTP_USER, SMTP_PASS)
                    server.send_message(msg)
                print(f"✅ Email enviado via puerto {puerto} (SSL)")
                break
            else:
                # Usar SMTP con STARTTLS para puerto 587
                with smtplib.SMTP(SMTP_HOST, puerto, timeout=60) as server:
                    server.starttls()
                    server.login(SMTP_USER, SMTP_PASS)
                    server.send_message(msg)
                print(f"✅ Email enviado via puerto {puerto} (STARTTLS)")
                break
        except Exception as e:
            print(f"⚠️ Fallo puerto {puerto}: {str(e)}")
            if puerto == puertos_intentar[-1]:
                raise  # Si es el último puerto, propagar error
    
    # Log detallado de destinatarios
    if EMAIL_NASSA and EMAIL_NASSA != destino:
        print(f"   Destinatarios: {destino} | CC: {EMAIL_NASSA}")
    else:
        print(f"   Destinatario: {destino}")

def enviar_email_sendgrid(destino: str, pdf_paths: list, resultado: dict, num_opciones: int = 1, pptx_path: Optional[str] = None):
    """
    Enviar email usando SendGrid API (alternativa a SMTP)
    pdf_paths: lista de rutas a PDFs (uno o más)
    num_opciones: 1 o 2 opciones de cotización
    """
    import base64
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition, ContentId
    
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "nassasolarprecotizacion@gmail.com")
    EMAIL_NASSA = os.getenv("EMAIL_NASSA", EMAIL_FROM)
    
    if not SENDGRID_API_KEY:
        raise RuntimeError("SENDGRID_API_KEY no configurada en .env")
    
    # Mensaje personalizado según número de opciones
    mensaje_opciones = "Le presentamos 2 propuestas para su análisis" if num_opciones == 2 else "Hemos preparado una propuesta personalizada para tu proyecto solar"
    mensaje_adjunto = "Sus cotizaciones detalladas están adjuntas en formato PDF" if num_opciones == 2 else "Tu cotización detallada está adjunta en formato PDF"
    
    cuerpo_html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cotización NASSA Solar</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px;">
    
    <!-- Contenedor Principal -->
    <div style="max-width: 650px; margin: 0 auto; background: #ffffff; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
        
        <!-- Header con Gradiente -->
        <div style="background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); padding: 40px 30px; text-align: center; position: relative;">
            <img src="cid:logo_nassa" alt="NASSA Solar Logo" style="max-width: 220px; height: auto; margin-bottom: 15px; display: block; margin-left: auto; margin-right: auto;">
            <p style="margin: 0; color: #ffffff; font-size: 18px; font-weight: 700; letter-spacing: 3px; text-shadow: 0 2px 8px rgba(0,0,0,0.3);">
                ENERGÍA INTELIGENTE
            </p>
        </div>
        
        <!-- Contenido -->
        <div style="padding: 40px 30px;">
            
            <!-- Saludo -->
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="color: #1f2937; font-size: 24px; margin: 0 0 10px 0;">
                    ✨ ¡Tu Cotización Está Lista!
                </h2>
                <p style="color: #6b7280; font-size: 16px; margin: 0; line-height: 1.6;">
                    {mensaje_opciones}
                </p>
            </div>
            
            <!-- Tarjeta de Resumen Premium -->
            <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 16px; padding: 25px; margin: 30px 0; border: 3px solid #fbbf24; box-shadow: 0 10px 30px rgba(251, 191, 36, 0.3);">
                <h3 style="color: #92400e; font-size: 20px; margin: 0 0 20px 0; text-align: center; font-weight: 700;">
                    📊 RESUMEN DE TU INVERSIÓN
                </h3>
                
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 2px solid rgba(146, 64, 14, 0.2);">
                            <span style="color: #78350f; font-size: 14px; font-weight: 600;">📋 ID Cotización</span>
                        </td>
                        <td style="padding: 12px 0; text-align: right; border-bottom: 2px solid rgba(146, 64, 14, 0.2);">
                            <span style="color: #92400e; font-size: 16px; font-weight: 700;">{resultado['cotizacionId']}</span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 2px solid rgba(146, 64, 14, 0.2);">
                            <span style="color: #78350f; font-size: 14px; font-weight: 600;">💰 Inversión Total</span>
                        </td>
                        <td style="padding: 12px 0; text-align: right; border-bottom: 2px solid rgba(146, 64, 14, 0.2);">
                            <span style="color: #dc2626; font-size: 20px; font-weight: 800;">${resultado['valorTotalSistema']:,.0f}</span>
                            <span style="color: #92400e; font-size: 14px; font-weight: 600;"> COP</span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 2px solid rgba(146, 64, 14, 0.2);">
                            <span style="color: #78350f; font-size: 14px; font-weight: 600;">💡 Ahorro Mensual</span>
                        </td>
                        <td style="padding: 12px 0; text-align: right; border-bottom: 2px solid rgba(146, 64, 14, 0.2);">
                            <span style="color: #16a34a; font-size: 20px; font-weight: 800;">${resultado['ahorroMensualEnergia']:,.0f}</span>
                            <span style="color: #92400e; font-size: 14px; font-weight: 600;"> COP</span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 2px solid rgba(146, 64, 14, 0.2);">
                            <span style="color: #78350f; font-size: 14px; font-weight: 600;">⏱️ Tiempo de Retorno</span>
                        </td>
                        <td style="padding: 12px 0; text-align: right; border-bottom: 2px solid rgba(146, 64, 14, 0.2);">
                            <span style="color: #2563eb; font-size: 20px; font-weight: 800;">{resultado['tiempoRetorno']}</span>
                            <span style="color: #92400e; font-size: 14px; font-weight: 600;"> años</span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0;">
                            <span style="color: #78350f; font-size: 14px; font-weight: 600;">⚡ Capacidad Instalada</span>
                        </td>
                        <td style="padding: 12px 0; text-align: right;">
                            <span style="color: #7c3aed; font-size: 20px; font-weight: 800;">{resultado['capacidadInstalada']}</span>
                            <span style="color: #92400e; font-size: 14px; font-weight: 600;"> kW</span>
                        </td>
                    </tr>
                </table>
            </div>
            
            <!-- Beneficios -->
            <div style="background: #f0fdf4; border-radius: 12px; padding: 20px; margin: 25px 0; border-left: 5px solid #16a34a;">
                <h4 style="color: #166534; margin: 0 0 15px 0; font-size: 18px;">🌟 Beneficios de tu Sistema Solar</h4>
                <ul style="margin: 0; padding-left: 20px; color: #15803d; line-height: 1.8;">
                    <li style="margin-bottom: 8px;"><strong>Ahorro inmediato</strong> en tu factura de energía</li>
                    <li style="margin-bottom: 8px;"><strong>Protección</strong> contra aumentos de tarifas</li>
                    <li style="margin-bottom: 8px;"><strong>Valorización</strong> de tu propiedad hasta 20%</li>
                    <li style="margin-bottom: 8px;"><strong>Contribución ambiental</strong> reduciendo CO₂</li>
                </ul>
            </div>
            
            <!-- Call to Action -->
            <div style="text-align: center; margin: 35px 0;">
                <!-- Botón como tabla para máxima compatibilidad cross-client -->
                <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="margin: 0 auto;">
                    <tr>
                        <td align="center" style="background: #16a34a; border-radius: 50px; box-shadow: 0 10px 25px rgba(22, 163, 74, 0.4);">
                            <a href="https://wa.me/573136909723?text=Hola,%20me%20interesa%20la%20cotización%20{resultado['cotizacionId']}" 
                               target="_blank"
                               style="background: #16a34a; border: 2px solid #16a34a; color: #ffffff; font-family: 'Segoe UI', Arial, sans-serif; font-size: 18px; font-weight: 700; line-height: 1.5; text-align: center; text-decoration: none; display: block; padding: 18px 45px; border-radius: 50px; -webkit-text-size-adjust: none; mso-hide: all;">
                                <span style="color: #ffffff; text-decoration: none;">💬 Contáctanos por WhatsApp</span>
                            </a>
                        </td>
                    </tr>
                </table>
                <p style="color: #6b7280; font-size: 14px; margin-top: 15px;">
                    O llámanos al <strong style="color: #ea580c;">(057) 313 690 9723</strong>
                </p>
            </div>
            
            <!-- Archivo Adjunto -->
            <div style="background: #eff6ff; border-radius: 12px; padding: 20px; margin: 25px 0; text-align: center; border: 2px dashed #3b82f6;">
                <p style="margin: 0; color: #1e40af; font-size: 16px; font-weight: 600;">
                    📎 {mensaje_adjunto}
                </p>
            </div>
            
        </div>
        
        <!-- Footer -->
        <div style="background: linear-gradient(135deg, #1f2937 0%, #111827 100%); padding: 30px; text-align: center; color: white;">
()            <img src="cid:logo_nassa" alt="NASSA Solar" style="max-width: 32px; height: auto; margin: 0 auto 12px auto; display: block; opacity: 0.9;">
            <h3 style="margin: 0 0 15px 0; font-size: 22px; font-weight: 700; color: #fbbf24;">
                NASSA SOLAR
            </h3>
            <p style="margin: 5px 0; font-size: 14px; color: #d1d5db;">
                Expertos en Energía Solar Fotovoltaica
            </p>
            <p style="margin: 5px 0; font-size: 14px; color: #d1d5db;">
                📞 Tel: (057) 313 690 9723
            </p>
            <p style="margin: 5px 0; font-size: 14px; color: #d1d5db;">
                🌐 www.nassasolar.com
            </p>
            <p style="margin: 15px 0 5px 0; font-size: 14px; color: #d1d5db;">
                📧 comercial@nassasolar.com
            </p>
            
            <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #374151;">
                <p style="margin: 0; font-size: 12px; color: #9ca3af; line-height: 1.6;">
                    Esta cotización tiene una validez de 30 días.<br>
                    Precios sujetos a disponibilidad y condiciones del mercado.
                </p>
            </div>
        </div>
        
    </div>
    
    <!-- Nota de Privacidad -->
    <div style="text-align: center; margin-top: 20px; padding: 0 20px;">
        <p style="color: rgba(255,255,255,0.8); font-size: 12px; margin: 0;">
            Has recibido este email porque solicitaste una cotización en nuestro sitio web.
        </p>
    </div>
    
</body>
</html>
    """
    
    # Leer PDFs y crear attachments
    attachments = []
    for i, pdf_path in enumerate(pdf_paths, 1):
        with open(pdf_path, "rb") as f:
            pdf_data = base64.b64encode(f.read()).decode()
        
        attachment = Attachment()
        attachment.file_content = FileContent(pdf_data)
        
        # Nombre del archivo según número de opciones
        if num_opciones == 1:
            attachment.file_name = FileName(f"Cotizacion_{resultado['cotizacionId']}.pdf")
        else:
            attachment.file_name = FileName(f"Cotizacion_{resultado['cotizacionId']}_Opcion{i}.pdf")
        
        attachment.file_type = FileType("application/pdf")
        attachment.disposition = Disposition("attachment")
        attachments.append(attachment)
    
    # Adjuntar logo de NASSA como inline attachment (CID)
    logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "images", "loggo-Nassa.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_data = base64.b64encode(f.read()).decode()
        
        logo_attachment = Attachment()
        logo_attachment.file_content = FileContent(logo_data)
        logo_attachment.file_name = FileName("logo-nassa.png")
        logo_attachment.file_type = FileType("image/png")
        logo_attachment.disposition = Disposition("inline")
        logo_attachment.content_id = ContentId("logo_nassa")
        attachments.append(logo_attachment)
    
    # Crear mensaje
    message = Mail(
        from_email=EMAIL_FROM,
        to_emails=[destino, EMAIL_NASSA],  # Envía a ambos
        subject=f"Cotización NASSA Solar - {resultado['cotizacionId']}",
        html_content=cuerpo_html
    )
    
    # Agregar todos los attachments
    for attachment in attachments:
        message.add_attachment(attachment)
    
    # Enviar
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)
    
    if response.status_code in [200, 201, 202]:
        print(f"✅ Email enviado vía SendGrid a {destino}")
    else:
        raise RuntimeError(f"SendGrid error: {response.status_code} - {response.body}")

def enviar_email_inteligente(destino: str, pdf_path: str, resultado: dict, pptx_path: Optional[str] = None):
    """Intenta SMTP primero (Gmail funcionando), SendGrid como fallback"""
    # Intentar Gmail SMTP primero (ya está funcionando)
    try:
        enviar_email(destino, pdf_path, resultado, pptx_path)
        return
    except Exception as e:
        print(f"⚠️ Gmail SMTP falló: {e}. Intentando SendGrid...")
        
        # Fallback a SendGrid si está configurado
        if os.getenv("SENDGRID_API_KEY"):
            try:
                enviar_email_sendgrid(destino, pdf_path, resultado, pptx_path)
                return
            except Exception as e2:
                print(f"❌ SendGrid también falló: {e2}")
                raise Exception(f"Error enviando email por ambos métodos: SMTP={e}, SendGrid={e2}")
        else:
            raise e  # Si no hay SendGrid configurado, relanzar error SMTP

# ========================================
# 🌐 ENDPOINTS
# ========================================
@app.get("/", tags=["General"])
def root():
    """Servir página principal"""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {
        "message": "API NASSA Solar - Sistema de Cotización Fotovoltaico",
        "version": "1.0.0",
        "status": "activo"
    }

@app.get("/admin", tags=["General"])
def admin_panel():
    """Servir panel administrativo"""
    admin_path = os.path.join(STATIC_DIR, "admin.html")
    if os.path.exists(admin_path):
        return FileResponse(admin_path, media_type="text/html")
    raise HTTPException(404, "Panel administrativo no encontrado")

@app.get("/health", tags=["General"])
def health():
    return {"status": "ok", "timestamp": now_colombia().isoformat()}

@app.post("/api/admin/migrate-to-postgres", tags=["Admin"], dependencies=[Depends(auth_admin)])
def migrate_to_postgres():
    """
    Endpoint ONE-TIME para migrar datos de JSON a PostgreSQL
    ⚠️ EJECUTAR SOLO UNA VEZ después de crear la base de datos
    """
    try:
        # Verificar que DATABASE_URL exista
        if not os.getenv("DATABASE_URL"):
            raise HTTPException(500, "DATABASE_URL no configurada. Agrega PostgreSQL en Railway.")
        
        # Importar el script de migración
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        
        from migrate_to_postgres import migrate
        
        # Ejecutar migración
        success = migrate()
        
        if success:
            return {
                "status": "success",
                "mensaje": "¡Migración completada exitosamente!",
                "timestamp": now_colombia().isoformat(),
                "siguiente_paso": "Ahora debes actualizar server.py para usar PostgreSQL en lugar de JSON"
            }
        else:
            raise HTTPException(500, "La migración falló. Revisa los logs de Railway.")
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ ERROR EN MIGRACIÓN: {error_trace}")
        raise HTTPException(500, f"Error en migración: {str(e)}")

@app.get("/api/admin/verificar-postgres", tags=["Admin"], dependencies=[Depends(auth_admin)])
def verificar_postgres():
    """
    Endpoint para verificar conteos de registros en PostgreSQL
    """
    try:
        # Verificar que DATABASE_URL exista
        if not os.getenv("DATABASE_URL"):
            raise HTTPException(500, "DATABASE_URL no configurada")
        
        from models import get_db_session, Panel, Inversor, Bateria, Ciudad, Parametro, Consecutivo
        
        session = get_db_session()
        
        try:
            # Contar registros
            paneles_count = session.query(Panel).count()
            inversores_count = session.query(Inversor).count()
            baterias_count = session.query(Bateria).count()
            ciudades_count = session.query(Ciudad).count()
            parametros_count = session.query(Parametro).count()
            consecutivo_count = session.query(Consecutivo).count()
            
            # Muestra de ciudades
            ciudades_muestra = session.query(Ciudad).limit(10).all()
            muestra_data = [
                {
                    "key": c.key,
                    "nombre": c.nombre,
                    "hsp": c.hsp
                }
                for c in ciudades_muestra
            ]
            
            return {
                "status": "success",
                "conteos": {
                    "paneles": paneles_count,
                    "inversores": inversores_count,
                    "baterias": baterias_count,
                    "ciudades": ciudades_count,
                    "parametros": parametros_count,
                    "consecutivos": consecutivo_count
                },
                "muestra_ciudades": muestra_data,
                "timestamp": now_colombia().isoformat()
            }
        finally:
            session.close()
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ ERROR EN VERIFICACIÓN: {error_trace}")
        raise HTTPException(500, f"Error verificando PostgreSQL: {str(e)}")

@app.get("/debug/equipos-file", tags=["Debug"])
def debug_equipos_file():
    """Endpoint temporal para diagnosticar problema con equipos.json"""
    import hashlib
    try:
        with open(EQUIPOS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            data = json.loads(content)
        
        # Hash del archivo para verificar versión
        file_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        
        # Contar equipos con campo default
        paneles_con_default = sum(1 for p in data['paneles'] if 'default' in p)
        inversores_con_default = sum(1 for i in data['inversores'] if 'default' in i)
        baterias_con_default = sum(1 for b in data['baterias'] if 'default' in b)
        
        return {
            "file_path": EQUIPOS_FILE,
            "file_exists": os.path.exists(EQUIPOS_FILE),
            "file_hash": file_hash,
            "file_size": os.path.getsize(EQUIPOS_FILE),
            "file_mtime": os.path.getmtime(EQUIPOS_FILE),
            "paneles": {
                "total": len(data['paneles']),
                "con_campo_default": paneles_con_default
            },
            "inversores": {
                "total": len(data['inversores']),
                "con_campo_default": inversores_con_default
            },
            "baterias": {
                "total": len(data['baterias']),
                "con_campo_default": baterias_con_default
            },
            "sample_inversor": data['inversores'][1] if len(data['inversores']) > 1 else None
        }
    except Exception as e:
        return {"error": str(e), "file_path": EQUIPOS_FILE}

@app.get("/api/equipos", tags=["Equipos"])
def equipos_publicos(sistemaElectrico: str = None):
    """
    Obtiene equipos disponibles (sin precios).
    
    Args:
        sistemaElectrico: Filtra inversores por tipo (monofasico, bifasico, trifasico).
                         Si no se proporciona, devuelve todos los inversores.
    """
    data = load_json(EQUIPOS_FILE)
    
    # Filtrar inversores si se especifica sistema eléctrico
    inversores = data["inversores"]
    if sistemaElectrico:
        sistema_normalizado = sistemaElectrico.lower().strip()
        inversores = [i for i in inversores if i.get("tipo_sistema", "").lower() == sistema_normalizado]
    
    return {
        "paneles": [{k: v for k, v in p.items() if k in ("id", "nombre", "capacidad", "descripcion")} 
                    for p in data["paneles"]],
        "inversores": [{k: v for k, v in i.items() if k in ("id", "nombre", "capacidad", "descripcion", "tipo_sistema")} 
                       for i in inversores],
        "baterias": [{k: v for k, v in b.items() if k in ("id", "nombre", "capacidad", "descripcion")} 
                     for b in data["baterias"]],
    }

@app.get("/api/equipos/precios", tags=["Equipos"], dependencies=[Depends(auth_admin)])
def equipos_con_precios():
    return load_json(EQUIPOS_FILE)

@app.get("/api/ciudades", tags=["Configuración"])
def ciudades():
    return load_json(CIUDADES_FILE)

@app.get("/api/template/status", tags=["Template"])
def template_status():
    return {"available": os.path.isfile(TEMPLATE_PPTX)}

@app.get("/api/template/download", tags=["Template"], dependencies=[Depends(auth_admin)])
def template_download():
    if not os.path.isfile(TEMPLATE_PPTX):
        raise HTTPException(404, "Template no encontrado")
    return FileResponse(TEMPLATE_PPTX, filename=os.path.basename(TEMPLATE_PPTX))

# ========================================
# 🔧 ENDPOINTS DE ADMINISTRACIÓN
# ========================================

# --- GESTIÓN DE PARÁMETROS DE COSTOS ---
@app.get("/api/admin/parametros", tags=["Admin"], dependencies=[Depends(auth_admin)])
def get_parametros():
    """Obtener todos los parámetros de costos y fiscales"""
    parametros_path = os.path.join(APP_DIR, "config", "parametros.json")
    return load_json(parametros_path)

@app.put("/api/admin/parametros", tags=["Admin"], dependencies=[Depends(auth_admin)])
def update_parametros(parametros: dict):
    """Actualizar parámetros de costos y fiscales"""
    parametros_path = os.path.join(APP_DIR, "config", "parametros.json")
    try:
        with open(parametros_path, "w", encoding="utf-8") as f:
            json.dump(parametros, f, ensure_ascii=False, indent=2)
        return {"status": "success", "mensaje": "Parámetros actualizados exitosamente"}
    except Exception as e:
        raise HTTPException(500, f"Error al actualizar parámetros: {e}")

# --- GESTIÓN DE PANELES ---
@app.get("/api/admin/paneles", tags=["Admin"], dependencies=[Depends(auth_admin)])
def get_paneles_admin():
    """Obtener todos los paneles con precios (admin)"""
    data = load_json(EQUIPOS_FILE)
    return data["paneles"]

@app.post("/api/admin/paneles", tags=["Admin"], dependencies=[Depends(auth_admin)])
def create_panel(panel: dict):
    """Crear nuevo panel con ID auto-generado"""
    data = load_json(EQUIPOS_FILE)
    
    # Auto-generar ID: encontrar el próximo disponible
    existing_ids = [p["id"] for p in data["paneles"]]
    counter = 1
    while f"panel{counter}" in existing_ids:
        counter += 1
    panel["id"] = f"panel{counter}"
    
    # Validar campos requeridos (sin ID)
    required = ["nombre", "capacidad", "precio", "descripcion"]
    if not all(k in panel for k in required):
        raise HTTPException(400, f"Campos requeridos: {', '.join(required)}")
    
    # Agregar eficienciaPanel por defecto si no existe (100%)
    if "eficienciaPanel" not in panel:
        panel["eficienciaPanel"] = 1.0
    
    data["paneles"].append(panel)
    
    try:
        with open(EQUIPOS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()  # Forzar escritura al disco
            os.fsync(f.fileno())  # Sincronizar con el sistema de archivos
        
        print(f"✅ Panel {panel['id']} creado y guardado en {EQUIPOS_FILE}")
        return {"status": "success", "mensaje": f"Panel {panel['id']} creado exitosamente", "id": panel["id"]}
    except Exception as e:
        print(f"❌ Error al guardar panel: {e}")
        raise HTTPException(500, f"Error al guardar: {e}")

@app.put("/api/admin/paneles/{panel_id}", tags=["Admin"], dependencies=[Depends(auth_admin)])
def update_panel(panel_id: str, panel: dict):
    """Actualizar panel existente"""
    data = load_json(EQUIPOS_FILE)
    
    idx = next((i for i, p in enumerate(data["paneles"]) if p["id"] == panel_id), None)
    if idx is None:
        raise HTTPException(404, f"Panel {panel_id} no encontrado")
    
    # Mantener el ID original
    panel["id"] = panel_id
    data["paneles"][idx] = panel
    
    try:
        with open(EQUIPOS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        print(f"✅ Panel {panel_id} actualizado en {EQUIPOS_FILE}")
        return {"status": "success", "mensaje": f"Panel {panel_id} actualizado exitosamente"}
    except Exception as e:
        print(f"❌ Error al actualizar panel: {e}")
        raise HTTPException(500, f"Error al guardar: {e}")

@app.delete("/api/admin/paneles/{panel_id}", tags=["Admin"], dependencies=[Depends(auth_admin)])
def delete_panel(panel_id: str):
    """Eliminar panel"""
    data = load_json(EQUIPOS_FILE)
    
    original_length = len(data["paneles"])
    data["paneles"] = [p for p in data["paneles"] if p["id"] != panel_id]
    
    if len(data["paneles"]) == original_length:
        raise HTTPException(404, f"Panel {panel_id} no encontrado")
    
    try:
        with open(EQUIPOS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        print(f"✅ Panel {panel_id} eliminado de {EQUIPOS_FILE}")
        return {"status": "success", "mensaje": f"Panel {panel_id} eliminado exitosamente"}
    except Exception as e:
        print(f"❌ Error al eliminar panel: {e}")
        raise HTTPException(500, f"Error al guardar: {e}")

# --- GESTIÓN DE INVERSORES ---
@app.get("/api/admin/inversores", tags=["Admin"], dependencies=[Depends(auth_admin)])
def get_inversores_admin():
    """Obtener todos los inversores con precios (admin)"""
    data = load_json(EQUIPOS_FILE)
    return data["inversores"]

@app.post("/api/admin/inversores", tags=["Admin"], dependencies=[Depends(auth_admin)])
def create_inversor(inversor: dict):
    """Crear nuevo inversor con ID auto-generado"""
    data = load_json(EQUIPOS_FILE)
    
    # Auto-generar ID: encontrar el próximo disponible
    existing_ids = [i["id"] for i in data["inversores"]]
    counter = 1
    while f"inv{counter}" in existing_ids:
        counter += 1
    inversor["id"] = f"inv{counter}"
    
    # Validar campos requeridos (sin ID)
    required = ["nombre", "capacidad", "precio", "descripcion"]
    if not all(k in inversor for k in required):
        raise HTTPException(400, f"Campos requeridos: {', '.join(required)}")
    
    # Agregar eficiencia por defecto si no existe (100%)
    if "eficiencia" not in inversor:
        inversor["eficiencia"] = 1.0
    
    # Validar tipo_sistema si se proporciona
    if "tipo_sistema" in inversor and inversor["tipo_sistema"] not in ["monofasico", "bifasico", "trifasico"]:
        raise HTTPException(400, "tipo_sistema debe ser: monofasico, bifasico o trifasico")
    
    data["inversores"].append(inversor)
    
    try:
        with open(EQUIPOS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        print(f"✅ Inversor {inversor['id']} creado y guardado en {EQUIPOS_FILE}")
        return {"status": "success", "mensaje": f"Inversor {inversor['id']} creado exitosamente", "id": inversor["id"]}
    except Exception as e:
        print(f"❌ Error al guardar inversor: {e}")
        raise HTTPException(500, f"Error al guardar: {e}")

@app.put("/api/admin/inversores/{inversor_id}", tags=["Admin"], dependencies=[Depends(auth_admin)])
def update_inversor(inversor_id: str, inversor: dict):
    """Actualizar inversor existente"""
    data = load_json(EQUIPOS_FILE)
    
    idx = next((i for i, inv in enumerate(data["inversores"]) if inv["id"] == inversor_id), None)
    if idx is None:
        raise HTTPException(404, f"Inversor {inversor_id} no encontrado")
    
    inversor["id"] = inversor_id
    data["inversores"][idx] = inversor
    
    try:
        with open(EQUIPOS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        print(f"✅ Inversor {inversor_id} actualizado en {EQUIPOS_FILE}")
        return {"status": "success", "mensaje": f"Inversor {inversor_id} actualizado exitosamente"}
    except Exception as e:
        print(f"❌ Error al actualizar inversor: {e}")
        raise HTTPException(500, f"Error al guardar: {e}")

@app.delete("/api/admin/inversores/{inversor_id}", tags=["Admin"], dependencies=[Depends(auth_admin)])
def delete_inversor(inversor_id: str):
    """Eliminar inversor"""
    data = load_json(EQUIPOS_FILE)
    
    original_length = len(data["inversores"])
    data["inversores"] = [i for i in data["inversores"] if i["id"] != inversor_id]
    
    if len(data["inversores"]) == original_length:
        raise HTTPException(404, f"Inversor {inversor_id} no encontrado")
    
    try:
        with open(EQUIPOS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        print(f"✅ Inversor {inversor_id} eliminado de {EQUIPOS_FILE}")
        return {"status": "success", "mensaje": f"Inversor {inversor_id} eliminado exitosamente"}
    except Exception as e:
        print(f"❌ Error al eliminar inversor: {e}")
        raise HTTPException(500, f"Error al guardar: {e}")

# --- GESTIÓN DE BATERÍAS ---
@app.get("/api/admin/baterias", tags=["Admin"], dependencies=[Depends(auth_admin)])
def get_baterias_admin():
    """Obtener todas las baterías con precios (admin)"""
    data = load_json(EQUIPOS_FILE)
    return data["baterias"]

@app.post("/api/admin/baterias", tags=["Admin"], dependencies=[Depends(auth_admin)])
def create_bateria(bateria: dict):
    """Crear nueva batería con ID auto-generado"""
    data = load_json(EQUIPOS_FILE)
    
    # Auto-generar ID: encontrar el próximo disponible
    existing_ids = [b["id"] for b in data["baterias"]]
    counter = 1
    while f"bat{counter}" in existing_ids:
        counter += 1
    bateria["id"] = f"bat{counter}"
    
    # Validar campos requeridos (sin ID)
    required = ["nombre", "capacidad", "precio", "descripcion"]
    if not all(k in bateria for k in required):
        raise HTTPException(400, f"Campos requeridos: {', '.join(required)}")
    
    data["baterias"].append(bateria)
    
    try:
        with open(EQUIPOS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        print(f"✅ Batería {bateria['id']} creada y guardada en {EQUIPOS_FILE}")
        return {"status": "success", "mensaje": f"Batería {bateria['id']} creada exitosamente", "id": bateria["id"]}
    except Exception as e:
        print(f"❌ Error al guardar batería: {e}")
        raise HTTPException(500, f"Error al guardar: {e}")

@app.put("/api/admin/baterias/{bateria_id}", tags=["Admin"], dependencies=[Depends(auth_admin)])
def update_bateria(bateria_id: str, bateria: dict):
    """Actualizar batería existente"""
    data = load_json(EQUIPOS_FILE)
    
    idx = next((i for i, b in enumerate(data["baterias"]) if b["id"] == bateria_id), None)
    if idx is None:
        raise HTTPException(404, f"Batería {bateria_id} no encontrada")
    
    bateria["id"] = bateria_id
    data["baterias"][idx] = bateria
    
    try:
        with open(EQUIPOS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        print(f"✅ Batería {bateria_id} actualizada en {EQUIPOS_FILE}")
        return {"status": "success", "mensaje": f"Batería {bateria_id} actualizada exitosamente"}
    except Exception as e:
        print(f"❌ Error al actualizar batería: {e}")
        raise HTTPException(500, f"Error al guardar: {e}")

@app.delete("/api/admin/baterias/{bateria_id}", tags=["Admin"], dependencies=[Depends(auth_admin)])
def delete_bateria(bateria_id: str):
    """Eliminar batería"""
    data = load_json(EQUIPOS_FILE)
    
    original_length = len(data["baterias"])
    data["baterias"] = [b for b in data["baterias"] if b["id"] != bateria_id]
    
    if len(data["baterias"]) == original_length:
        raise HTTPException(404, f"Batería {bateria_id} no encontrada")
    
    try:
        with open(EQUIPOS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        print(f"✅ Batería {bateria_id} eliminada de {EQUIPOS_FILE}")
        return {"status": "success", "mensaje": f"Batería {bateria_id} eliminada exitosamente"}
    except Exception as e:
        print(f"❌ Error al eliminar batería: {e}")
        raise HTTPException(500, f"Error al guardar: {e}")

# --- GESTIÓN DE EQUIPOS DEFAULT ---
@app.put("/api/admin/paneles/{panel_id}/default", tags=["Admin"], dependencies=[Depends(auth_admin)])
def set_panel_default(panel_id: str):
    """Marcar un panel como default (desmarca los demás)"""
    data = load_json(EQUIPOS_FILE)
    
    # Verificar que existe el panel
    panel = next((p for p in data["paneles"] if p["id"] == panel_id), None)
    if not panel:
        raise HTTPException(404, f"Panel {panel_id} no encontrado")
    
    # Desmarcar todos los paneles como default
    for p in data["paneles"]:
        p["default"] = False
    
    # Marcar el seleccionado como default
    panel["default"] = True
    
    try:
        with open(EQUIPOS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        print(f"✅ Panel {panel_id} marcado como default en {EQUIPOS_FILE}")
        return {"status": "success", "mensaje": f"Panel {panel_id} marcado como default"}
    except Exception as e:
        print(f"❌ Error al marcar panel default: {e}")
        raise HTTPException(500, f"Error al guardar: {e}")

@app.put("/api/admin/inversores/{inversor_id}/default", tags=["Admin"], dependencies=[Depends(auth_admin)])
def set_inversor_default(inversor_id: str):
    """Marcar un inversor como default (desmarca los demás)"""
    data = load_json(EQUIPOS_FILE)
    
    # Verificar que existe el inversor
    inversor = next((i for i in data["inversores"] if i["id"] == inversor_id), None)
    if not inversor:
        raise HTTPException(404, f"Inversor {inversor_id} no encontrado")
    
    # Desmarcar todos los inversores como default
    for i in data["inversores"]:
        i["default"] = False
    
    # Marcar el seleccionado como default
    inversor["default"] = True
    
    try:
        with open(EQUIPOS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        print(f"✅ Inversor {inversor_id} marcado como default en {EQUIPOS_FILE}")
        return {"status": "success", "mensaje": f"Inversor {inversor_id} marcado como default"}
    except Exception as e:
        print(f"❌ Error al marcar inversor default: {e}")
        raise HTTPException(500, f"Error al guardar: {e}")

@app.put("/api/admin/baterias/{bateria_id}/default", tags=["Admin"], dependencies=[Depends(auth_admin)])
def set_bateria_default(bateria_id: str):
    """Marcar una batería como default (desmarca las demás)"""
    data = load_json(EQUIPOS_FILE)
    
    # Verificar que existe la batería
    bateria = next((b for b in data["baterias"] if b["id"] == bateria_id), None)
    if not bateria:
        raise HTTPException(404, f"Batería {bateria_id} no encontrada")
    
    # Desmarcar todas las baterías como default
    for b in data["baterias"]:
        b["default"] = False
    
    # Marcar la seleccionada como default
    bateria["default"] = True
    
    try:
        with open(EQUIPOS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        print(f"✅ Batería {bateria_id} marcada como default en {EQUIPOS_FILE}")
        return {"status": "success", "mensaje": f"Batería {bateria_id} marcada como default"}
    except Exception as e:
        print(f"❌ Error al marcar batería default: {e}")
        raise HTTPException(500, f"Error al guardar: {e}")

# --- GESTIÓN DE CIUDADES ---
@app.get("/api/admin/ciudades", tags=["Admin"], dependencies=[Depends(auth_admin)])
def get_ciudades_admin():
    """Obtener todas las ciudades con HSP (admin)"""
    data = load_json(CIUDADES_FILE)
    # Convertir dict a lista para mejor manejo en frontend
    ciudades_list = []
    for ciudad_key, ciudad_data in data.items():
        if ciudad_key != "default":
            ciudades_list.append({
                "key": ciudad_key,
                "nombre": ciudad_data.get("nombre", ciudad_key.replace("_", " ").title()),
                "hsp": ciudad_data.get("hsp", 5.0)
            })
    return ciudades_list

@app.post("/api/admin/ciudades", tags=["Admin"], dependencies=[Depends(auth_admin)])
def create_ciudad(ciudad: dict):
    """Crear nueva ciudad con HSP"""
    data = load_json(CIUDADES_FILE)
    
    # Validar campos requeridos
    if "nombre" not in ciudad or "hsp" not in ciudad:
        raise HTTPException(400, "Campos requeridos: nombre, hsp")
    
    # Normalizar nombre para key (lowercase, underscores)
    ciudad_key = ciudad["nombre"].lower().replace(" ", "_").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    
    # Verificar que no existe
    if ciudad_key in data:
        raise HTTPException(400, f"La ciudad {ciudad['nombre']} ya existe")
    
    # Agregar ciudad
    data[ciudad_key] = {
        "nombre": ciudad["nombre"],
        "hsp": float(ciudad["hsp"])
    }
    
    try:
        with open(CIUDADES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return {"status": "success", "mensaje": f"Ciudad {ciudad['nombre']} creada exitosamente", "key": ciudad_key}
    except Exception as e:
        raise HTTPException(500, f"Error al guardar: {e}")

@app.put("/api/admin/ciudades/{ciudad_key}", tags=["Admin"], dependencies=[Depends(auth_admin)])
def update_ciudad(ciudad_key: str, ciudad: dict):
    """Actualizar ciudad existente"""
    data = load_json(CIUDADES_FILE)
    
    if ciudad_key not in data:
        raise HTTPException(404, f"Ciudad {ciudad_key} no encontrada")
    
    if ciudad_key == "default":
        raise HTTPException(400, "No se puede modificar la ciudad 'default'")
    
    # Validar campos
    if "hsp" in ciudad:
        data[ciudad_key]["hsp"] = float(ciudad["hsp"])
    if "nombre" in ciudad:
        data[ciudad_key]["nombre"] = ciudad["nombre"]
    
    try:
        with open(CIUDADES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return {"status": "success", "mensaje": f"Ciudad {ciudad_key} actualizada exitosamente"}
    except Exception as e:
        raise HTTPException(500, f"Error al guardar: {e}")

@app.delete("/api/admin/ciudades/{ciudad_key}", tags=["Admin"], dependencies=[Depends(auth_admin)])
def delete_ciudad(ciudad_key: str):
    """Eliminar ciudad"""
    data = load_json(CIUDADES_FILE)
    
    if ciudad_key not in data:
        raise HTTPException(404, f"Ciudad {ciudad_key} no encontrada")
    
    if ciudad_key == "default":
        raise HTTPException(400, "No se puede eliminar la ciudad 'default'")
    
    del data[ciudad_key]
    
    try:
        with open(CIUDADES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return {"status": "success", "mensaje": f"Ciudad {ciudad_key} eliminada exitosamente"}
    except Exception as e:
        raise HTTPException(500, f"Error al guardar: {e}")

# --- SISTEMA DE TRACKING Y VALORES POR DEFECTO ---
@app.post("/api/track-seleccion", tags=["Analytics"])
async def track_seleccion(request: Request):
    """Registrar selecciones de una cotización para análisis de frecuencia (sin autenticación)"""
    try:
        data = await request.json()
        
        # Cargar estadísticas existentes
        if os.path.exists(ESTADISTICAS_FILE):
            estadisticas = load_json(ESTADISTICAS_FILE)
        else:
            estadisticas = {"cotizaciones": []}
        
        # Agregar nuevo registro con timestamp
        registro = {
            "timestamp": now_colombia().isoformat(),
            "ciudad": data.get("ciudad", ""),
            "tipoSistemaFV": data.get("tipoSistemaFV", ""),
            "tipo_propiedad": data.get("tipo_propiedad", ""),
            "legalizacion": data.get("legalizacion", ""),
            "seleccionManual": data.get("seleccionManual", ""),
            "sistemaElectrico": data.get("sistemaElectrico", ""),
            "porcentajeConsumodia": data.get("porcentajeConsumodia", 50)
        }
        
        estadisticas["cotizaciones"].append(registro)
        
        # Guardar (limitamos a las últimas 500 cotizaciones para no saturar)
        if len(estadisticas["cotizaciones"]) > 500:
            estadisticas["cotizaciones"] = estadisticas["cotizaciones"][-500:]
        
        with open(ESTADISTICAS_FILE, "w", encoding="utf-8") as f:
            json.dump(estadisticas, f, ensure_ascii=False, indent=2)
        
        return {"status": "success", "mensaje": "Selección registrada"}
    except Exception as e:
        # No fallar si hay error en tracking (no es crítico)
        print(f"Error en tracking: {e}")
        return {"status": "error", "mensaje": str(e)}

@app.get("/api/valores-default", tags=["Analytics"])
def get_valores_default():
    """Obtener valores más frecuentes de los últimos 30 días (público, sin autenticación)"""
    try:
        if not os.path.exists(ESTADISTICAS_FILE):
            # Valores por defecto fijos si no hay estadísticas
            return {
                "ciudad": "santa_marta",
                "tipoSistemaFV": "ongrid",
                "tipo_propiedad": "residencial",
                "legalizacion": "SI",
                "seleccionManual": "NO",
                "sistemaElectrico": "bifasico",
                "porcentajeConsumodia": 50,
                "source": "defaults"
            }
        
        estadisticas = load_json(ESTADISTICAS_FILE)
        cotizaciones = estadisticas.get("cotizaciones", [])
        
        if not cotizaciones:
            # Valores por defecto fijos
            return {
                "ciudad": "santa_marta",
                "tipoSistemaFV": "ongrid",
                "tipo_propiedad": "residencial",
                "legalizacion": "SI",
                "seleccionManual": "NO",
                "sistemaElectrico": "bifasico",
                "porcentajeConsumodia": 50,
                "source": "defaults"
            }
        
        # Filtrar últimos 30 días
        fecha_limite = now_colombia() - timedelta(days=30)
        cotizaciones_recientes = []
        
        for cot in cotizaciones:
            try:
                timestamp = datetime.fromisoformat(cot["timestamp"])
                if timestamp >= fecha_limite:
                    cotizaciones_recientes.append(cot)
            except:
                continue
        
        # Si no hay datos recientes, usar todos los datos disponibles
        if not cotizaciones_recientes:
            cotizaciones_recientes = cotizaciones[-50:]  # Últimas 50
        
        # Calcular frecuencias
        from collections import Counter
        
        ciudades = Counter([c.get("ciudad", "") for c in cotizaciones_recientes if c.get("ciudad")])
        tipos_sistema = Counter([c.get("tipoSistemaFV", "") for c in cotizaciones_recientes if c.get("tipoSistemaFV")])
        tipos_propiedad = Counter([c.get("tipo_propiedad", "") for c in cotizaciones_recientes if c.get("tipo_propiedad")])
        legalizaciones = Counter([c.get("legalizacion", "") for c in cotizaciones_recientes if c.get("legalizacion")])
        selecciones_manual = Counter([c.get("seleccionManual", "") for c in cotizaciones_recientes if c.get("seleccionManual")])
        sistemas_electricos = Counter([c.get("sistemaElectrico", "") for c in cotizaciones_recientes if c.get("sistemaElectrico")])
        porcentajes_consumo = [c.get("porcentajeConsumodia", 50) for c in cotizaciones_recientes if c.get("porcentajeConsumodia") is not None]
        
        # Calcular promedio de porcentaje de consumo día
        porcentaje_promedio = round(sum(porcentajes_consumo) / len(porcentajes_consumo)) if porcentajes_consumo else 50
        
        # Obtener valores más comunes
        resultado = {
            "ciudad": ciudades.most_common(1)[0][0] if ciudades else "santa_marta",
            "tipoSistemaFV": tipos_sistema.most_common(1)[0][0] if tipos_sistema else "ongrid",
            "tipo_propiedad": tipos_propiedad.most_common(1)[0][0] if tipos_propiedad else "residencial",
            "legalizacion": legalizaciones.most_common(1)[0][0] if legalizaciones else "SI",
            "seleccionManual": selecciones_manual.most_common(1)[0][0] if selecciones_manual else "NO",
            "sistemaElectrico": sistemas_electricos.most_common(1)[0][0] if sistemas_electricos else "bifasico",
            "porcentajeConsumodia": porcentaje_promedio,
            "source": "analytics",
            "sample_size": len(cotizaciones_recientes)
        }
        
        return resultado
        
    except Exception as e:
        print(f"Error en valores-default: {e}")
        # En caso de error, retornar defaults fijos
        return {
            "ciudad": "santa_marta",
            "tipoSistemaFV": "ongrid",
            "tipo_propiedad": "residencial",
            "legalizacion": "SI",
            "seleccionManual": "NO",
            "sistemaElectrico": "bifasico",
            "porcentajeConsumodia": 50,
            "source": "defaults"
        }

@app.post("/api/cotizar", tags=["Cotización"])
async def cotizar(request: Request, req: CotizarRequest, _: Any = Depends(rate_limit)):
    """Generar cotización completa con 1 o 2 opciones según área disponible"""
    equipos = load_json(EQUIPOS_FILE)
    ciudades = load_json(CIUDADES_FILE)
    parametros = load_json(PARAMETROS_FILE)
    
    # Preparar datos de solicitud
    req_dict = req.dict()
    
    # Si seleccionManual es NO, usar equipos por defecto
    if req.seleccionManual == "NO":
        # FIX #4: Pasar sistema eléctrico para selección inteligente de inversor
        defaults = obtener_equipos_defaults(equipos, req.sistemaElectrico)
        req_dict["panel"] = defaults["panel"]
        req_dict["inversor"] = defaults["inversor"]
        
        # Log para debugging
        print(f"🔧 Selección automática de equipos:")
        print(f"   Sistema eléctrico: {req.sistemaElectrico}")
        print(f"   Panel default: {defaults['panel']}")
        print(f"   Inversor default: {defaults['inversor']}")
        
        # Solo asignar batería default si el sistema la requiere
        if req.tipoSistemaFV in ("offgrid", "hibrido_incluido") and defaults["bateria"]:
            req_dict["bateria"] = defaults["bateria"]
            print(f"   Batería default: {defaults['bateria']}")
    
    
    # Determinar COND_COM según legalización
    if req.legalizacion == "SI":
        cond_com = "Anticipo 70%, 25% en producción, 5% legalizado"
    else:
        cond_com = "Anticipo 70%, 30% contraentrega"
    
    try:
        # Calcular OPCIÓN 1 (ideal sin restricciones)
        resultado_opcion1 = calcular_cotizacion(req_dict, equipos, ciudades)
        # Agregar COND_COM al resultado
        resultado_opcion1["condicionesComerciales"] = cond_com
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Error cálculo: {e}")

    # Verificar si se necesita segunda opción (área disponible < umbral del área requerida)
    areaDisponible = float(req.areaDisponible or 0)
    areaRequerida = resultado_opcion1["areaRequerida"]
    
    # Obtener umbral desde parámetros (default 92%)
    parametros_sistema = parametros.get("parametros_sistema", {})
    umbral_porcentaje = parametros_sistema.get("umbral_segunda_opcion", 0.92)
    umbral = areaRequerida * umbral_porcentaje
    
    # Logs detallados para diagnóstico
    diagnostico = {
        "areaDisponible_raw": req.areaDisponible,
        "areaDisponible_float": areaDisponible,
        "areaRequerida": areaRequerida,
        "umbral_92": round(umbral, 2),
        "condicion1_mayor_cero": areaDisponible > 0,
        "condicion2_menor_umbral": areaDisponible < umbral,
        "generara_segunda_opcion": areaDisponible > 0 and areaDisponible < umbral,
        "error_opcion2": None  # Se llenará si hay error
    }
    
    print(f"\n{'='*80}")
    print(f"🔍 DIAGNÓSTICO COMPLETO - SEGUNDA OPCIÓN")
    print(f"{'='*80}")
    print(f"📥 DATOS RECIBIDOS:")
    print(f"   req.areaDisponible (raw): {req.areaDisponible}")
    print(f"   req.areaDisponible (type): {type(req.areaDisponible)}")
    print(f"   areaDisponible (float convertido): {areaDisponible}")
    print(f"\n📊 CÁLCULOS:")
    print(f"   Área requerida (opción 1): {areaRequerida} m²")
    print(f"   Umbral 92%: {umbral:.2f} m²")
    print(f"\n✅ EVALUACIÓN DE CONDICIONES:")
    print(f"   [1] ¿Área disponible > 0?: {areaDisponible > 0}")
    print(f"   [2] ¿Área disponible < umbral?: {areaDisponible < umbral}")
    print(f"\n📋 DIAGNÓSTICO JSON: {diagnostico}")
    
    necesita_segunda_opcion = areaDisponible > 0 and areaDisponible < umbral
    print(f"\n{'🎯 DECISIÓN FINAL: ' + ('✅ SÍ GENERA 2 OPCIONES' if necesita_segunda_opcion else '❌ NO, SOLO 1 OPCIÓN')}")
    print(f"{'='*80}\n")
    
    # CALCULAR SEGUNDA OPCIÓN si es necesario (sin generar PDFs aún)
    resultado_opcion2 = None
    num_opciones = 1
    
    if necesita_segunda_opcion:
        print(f"\n🚀 CALCULANDO SEGUNDA OPCIÓN")
        print(f"   Área disponible: {areaDisponible} m²")
        print(f"   Área requerida original: {areaRequerida} m²")
        
        try:
            print(f"   📊 Calculando segunda opción...")
            # Extraer ID base sin sufijo para mantener consistencia
            cotizacion_id_base = resultado_opcion1["cotizacionId"]
            resultado_opcion2 = calcular_segunda_opcion(req_dict, equipos, ciudades, areaDisponible, cotizacion_id_base)
            # Agregar COND_COM también a la opción 2
            resultado_opcion2["condicionesComerciales"] = cond_com
            num_opciones = 2
            print(f"   ✅ Cálculo completado:")
            print(f"      - Paneles: {resultado_opcion2['numeroPaneles']} (vs {resultado_opcion1['numeroPaneles']} original)")
            print(f"      - Capacidad: {resultado_opcion2['capacidadInstalada']} kW")
            print(f"      - Valor: ${resultado_opcion2['valorTotalSistema']:,.0f}")
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            diagnostico["error_opcion2"] = error_msg
            print(f"   ❌ ERROR CALCULANDO SEGUNDA OPCIÓN: {error_msg}")
            import traceback
            traceback.print_exc()
            # No lanzar excepción, continuar con una sola opción
    else:
        print(f"\n❌ NO SE CALCULA SEGUNDA OPCIÓN (condición no cumplida)")

    # Combinar datos de la solicitud con el resultado para el frontend
    resumen_completo = {
        **resultado_opcion1,
        "nombre": req.nombre,
        "email": req.email,
        "telefono": req.telefono,
        "ciudad": req.ciudad,
        "direccion": req.direccion,
        "tipoVivienda": req.tipoVivienda,
        "sistemaElectrico": req.sistemaElectrico,
        "tipoSistemaFV": req.tipoSistemaFV,
        "consumoMensual": req.consumoMensual,
        "valorFactura": req.valorFactura,
        "valorKwh": req.valorKwh,
        "porcentajeConsumodia": req.porcentajeConsumodia,
        "hspCalculado": req.hspCalculado,
        "panelSeleccionado": resultado_opcion1["panel"],
        "inversorSeleccionado": resultado_opcion1["inversor"],
        "bateriaSeleccionada": resultado_opcion1["bateria"],
        "hora": now_colombia().strftime("%H:%M:%S"),
        "numOpciones": num_opciones,
        "opcion2": {
            "numeroPaneles": resultado_opcion2["numeroPaneles"],
            "capacidadInstalada": resultado_opcion2["capacidadInstalada"],
            "valorTotalSistema": resultado_opcion2["valorTotalSistema"],
            "ahorroMensualEnergia": resultado_opcion2["ahorroMensualEnergia"],
            "tiempoRetorno": resultado_opcion2["tiempoRetorno"],
            "desgloseCostos": resultado_opcion2["desgloseCostos"]
        } if resultado_opcion2 else None
    }
    
    # TRACKING AUTOMÁTICO: Registrar selección para estadísticas (sin bloquear si falla)
    try:
        if os.path.exists(ESTADISTICAS_FILE):
            estadisticas = load_json(ESTADISTICAS_FILE)
        else:
            estadisticas = {"cotizaciones": []}
        
        registro = {
            "timestamp": now_colombia().isoformat(),
            "ciudad": req.ciudad,
            "tipoSistemaFV": req.tipoSistemaFV,
            "tipo_propiedad": req.tipoVivienda,
            "legalizacion": req.legalizacion,
            "seleccionManual": req.seleccionManual,
            "sistemaElectrico": req.sistemaElectrico,
            "porcentajeConsumodia": req.porcentajeConsumodia
        }
        
        estadisticas["cotizaciones"].append(registro)
        
        # Limitar a 500 registros
        if len(estadisticas["cotizaciones"]) > 500:
            estadisticas["cotizaciones"] = estadisticas["cotizaciones"][-500:]
        
        with open(ESTADISTICAS_FILE, "w", encoding="utf-8") as f:
            json.dump(estadisticas, f, ensure_ascii=False, indent=2)
        
        print(f"📊 Tracking: Selección registrada exitosamente")
    except Exception as e:
        print(f"⚠️ Error en tracking (no crítico): {e}")
    
    return JSONResponse({
        "status": "success",
        "mensaje": f"✅ Cotización calculada exitosamente. {num_opciones} opción(es) disponible(s).",
        "numOpciones": num_opciones,
        "resumen": resumen_completo,
        "diagnostico": diagnostico  # Agregar diagnóstico para debug
    })


@app.post("/api/enviar-cotizacion", tags=["Cotización"])
async def enviar_cotizacion(request: Request, data: dict, _: Any = Depends(rate_limit)):
    """
    Genera PDFs y envía cotización por email.
    Requiere los datos completos de la cotización previamente calculada.
    """
    try:
        # Validar campos requeridos
        campos_requeridos = ["email", "resumen", "datosCliente"]
        for campo in campos_requeridos:
            if campo not in data:
                raise HTTPException(400, f"Campo requerido faltante: {campo}")
        
        email_cliente = data["email"]
        resumen = data["resumen"]
        datos_cliente = data["datosCliente"]
        opcion2 = data.get("opcion2")  # Opcional
        num_opciones = 2 if opcion2 else 1
        
        # Recargar configuración
        equipos = load_json(EQUIPOS_FILE)
        ciudades = load_json(CIUDADES_FILE)
        parametros = load_json(PARAMETROS_FILE)
        
        pdf_paths = []
        pptx_paths = []
        
        print(f"\n📧 GENERANDO PDFs PARA ENVÍO")
        print(f"   Email destino: {email_cliente}")
        print(f"   Número de opciones: {num_opciones}")
        
        # GENERAR OPCIÓN 1
        print(f"\n🔄 Generando PDF Opción 1...")
        pptx_path1, pdf_path1 = fill_template_and_convert(
            datos_cliente,
            resumen,
            opcion="" if num_opciones == 1 else "OPCIÓN 1 DE 2"
        )
        pdf_paths.append(pdf_path1)
        pptx_paths.append(pptx_path1)
        print(f"✅ Opción 1: {os.path.basename(pdf_path1)}")
        
        # GENERAR OPCIÓN 2 si existe
        if opcion2:
            print(f"\n🔄 Generando PDF Opción 2...")
            # Verificar que existe Template-PreCotizacion2.pptx
            if os.path.isfile(TEMPLATE_PPTX_OP2):
                pptx_path2, pdf_path2 = fill_template_and_convert(
                    datos_cliente,
                    opcion2,
                    opcion="OPCIÓN 2 - Ajustada a área disponible",
                    template_path=TEMPLATE_PPTX_OP2
                )
                print(f"✅ Opción 2 (template 2): {os.path.basename(pdf_path2)}")
            else:
                pptx_path2, pdf_path2 = fill_template_and_convert(
                    datos_cliente,
                    opcion2,
                    opcion="OPCIÓN 2 - Ajustada a área disponible"
                )
                print(f"✅ Opción 2 (template principal): {os.path.basename(pdf_path2)}")
            
            pdf_paths.append(pdf_path2)
            pptx_paths.append(pptx_path2)
        
        # ENVIAR EMAIL
        email_enviado = False
        email_error = None
        
        print(f"\n📧 ENVIANDO EMAIL")
        print(f"   Total PDFs: {len(pdf_paths)}")
        
        try:
            enviar_email_sendgrid(email_cliente, pdf_paths, resumen, num_opciones)
            email_enviado = True
            print(f"✅ Email enviado exitosamente a {email_cliente}")
        except Exception as e:
            email_error = str(e)
            print(f"❌ Error enviando email: {e}")
            raise HTTPException(500, f"Error al enviar email: {e}")
        finally:
            # Limpiar archivos temporales
            print("\n🧹 Limpiando archivos temporales...")
            for pdf_path in pdf_paths:
                if pdf_path and os.path.exists(pdf_path):
                    try:
                        os.remove(pdf_path)
                        print(f"   🗑️  {os.path.basename(pdf_path)}")
                    except Exception as e:
                        print(f"   ⚠️ Error eliminando: {e}")
            
            for pptx_path in pptx_paths:
                if pptx_path and os.path.exists(pptx_path):
                    try:
                        os.remove(pptx_path)
                        print(f"   🗑️  {os.path.basename(pptx_path)}")
                    except Exception as e:
                        print(f"   ⚠️ Error eliminando: {e}")
        
        return JSONResponse({
            "status": "success",
            "mensaje": f"✅ Cotización enviada exitosamente a {email_cliente}",
            "emailEnviado": email_enviado,
            "numOpciones": num_opciones
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en enviar_cotizacion: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Error procesando envío: {e}")


# ========================================
# 🚀 EJECUCIÓN
# ========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        log_level="info"
    )# Trigger Railway redeploy - Thu Dec  4 10:42:41 -05 2025
