import math


def numero_json(valor):
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    return numero if math.isfinite(numero) else None


def npv_nativo(rate, values):
    """Calcula el Valor Actual Neto (VAN)."""
    return sum(v / ((1 + rate) ** i) for i, v in enumerate(values))


def irr_nativo(values, iterations=1000):
    """Calcula la Tasa Interna de Retorno (TIR) mediante bisección."""
    if not any(x < 0 for x in values) or not any(x > 0 for x in values):
        return None
    
    low, high = -0.9999, 10.0
    for _ in range(iterations):
        mid = (low + high) / 2
        val = sum(v / ((1 + mid) ** i) for i, v in enumerate(values))
        if abs(val) < 1e-6:
            return mid
        if val > 0:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def calcular_tir_segura(flujos):
    try:
        res = irr_nativo(flujos)
        return numero_json(res)
    except Exception:
        return None


class ModeloFinanciero:
    def __init__(self, datos):
        self.datos = datos
        self.plazo = max(1, int(datos.get("plazo", 5)))
        self.cok = float(datos.get("cok", 0.14))
        self.ke = float(datos.get("ke", self.cok))
        self.impuesto_renta = float(datos.get("impuestos", 0.30))
        self.prestamo = max(0.0, float(datos.get("prestamo", 1173354)))
        self.tasa_interes = float(datos.get("tasa_interes", 0.12))
        self.valor_residual = max(0.0, float(datos.get("valor_residual", 0)))
        
        # Políticas
        self.igv = float(datos.get("igv", 0.18))
        self.dias_cobro = float(datos.get("dias_cobro", 30))
        self.dias_pago = float(datos.get("dias_pago", 45))
        self.pct_inv_pt = float(datos.get("pct_inv_pt", 0.10))
        self.pct_inv_md = float(datos.get("pct_inv_md", 0.10))
        self.pct_dividendos = float(datos.get("pct_dividendos", 0.40))

    def calcular_depreciacion_activos(self):
        activos = self.datos.get("activos", [])
        total_depreciacion = 0.0
        inversion_tangible = 0.0
        desglose = []
        for act in activos:
            valor = float(act.get("valor", 0) or 0)
            vida_util = float(act.get("vida_util", 0) or 0)
            tipo = "intangible" if str(act.get("tipo", "tangible")).lower() == "intangible" else "tangible"
            depreciacion = valor / vida_util if vida_util > 0 else 0.0
            total_depreciacion += depreciacion
            if tipo == "tangible":
                inversion_tangible += valor
            desglose.append({
                "nombre": str(act.get("nombre") or "Activo"),
                "tipo": tipo,
                "valor": valor,
                "vida_util": vida_util,
                "depr_anual": depreciacion
            })
        return total_depreciacion, desglose, inversion_tangible

    def calcular_servicio_deuda(self):
        cronograma = []
        saldo = self.prestamo
        
        if self.prestamo <= 0:
            cuota = 0.0
        elif self.tasa_interes == 0:
            cuota = self.prestamo / self.plazo
        else:
            i = self.tasa_interes
            cuota = float(self.prestamo * (i * ((1 + i) ** self.plazo)) / (((1 + i) ** self.plazo) - 1))

        for anio in range(1, self.plazo + 1):
            saldo_inicial = saldo
            interes = saldo_inicial * self.tasa_interes
            amortizacion = min(saldo_inicial, max(0.0, cuota - interes))
            saldo = max(0.0, saldo_inicial - amortizacion)
            if anio == self.plazo and saldo > 0:
                amortizacion += saldo
                saldo = 0.0
            cuota_anual = interes + amortizacion
            cronograma.append({
                "anio": anio,
                "saldo_inicial": saldo_inicial,
                "interes": interes,
                "amortizacion": amortizacion,
                "cuota": cuota_anual,
                "saldo_final": saldo,
            })
        return cronograma

    def ejecutar_modelo_completo(self):
        deuda = self.calcular_servicio_deuda()
        depreciacion_anual, desglose_activos, inversion_tangible = self.calcular_depreciacion_activos()
        inversion_fija = sum(float(a["valor"]) for a in desglose_activos)

        # 1. Proyección de Ventas
        tipo_proyeccion = self.datos.get("tipo_proyeccion", "Manual por Año")
        ventas_unidades = []
        
        if tipo_proyeccion == "Manual por Año":
            ventas_unidades = [float(v) for v in self.datos.get("ventas_manuales", [4000, 4200, 4400, 4700, 5000])]
            if len(ventas_unidades) <= self.plazo:
                ventas_unidades.append(ventas_unidades[-1])
        else:
            unidades_base = float(self.datos.get("unidades_base", 4000))
            crec_unidades = float(self.datos.get("crec_unidades", 0.05))
            capacidad_max = float(self.datos.get("capacidad_max", 100000))
            for i in range(self.plazo + 1):
                v = min(unidades_base * ((1 + crec_unidades) ** i), capacidad_max)
                ventas_unidades.append(v)

        precio_base = float(self.datos.get("precio_base", 1140))
        crec_precio = float(self.datos.get("crec_precio", 0.03))
        costo_unit_base = float(self.datos.get("costo_unit_base", 440))
        mod = float(self.datos.get("mod", 224400))
        costos_indirectos = float(self.datos.get("costos_indirectos", 635400))
        gastos_ventas = float(self.datos.get("gastos_ventas", 271400))
        gastos_admin = float(self.datos.get("gastos_admin", 223000))

        # Producción e Inventario PT
        produccion_unidades = []
        inv_inicial_pt = 0.0
        for i in range(self.plazo):
            v_act = ventas_unidades[i]
            inv_fin_pt = v_act * self.pct_inv_pt
            prod = v_act + inv_fin_pt - inv_inicial_pt
            produccion_unidades.append(prod)
            inv_inicial_pt = inv_fin_pt

        prod_ext = ventas_unidades[self.plazo] + (ventas_unidades[self.plazo] * self.pct_inv_pt) - inv_inicial_pt
        produccion_unidades.append(prod_ext)

        # Compras MD
        modulo_compras_md = []
        inv_inicial_md = 0.0
        for i in range(self.plazo):
            costo_unit_md = costo_unit_base * ((1 + 0.02) ** i)
            req_prod_actual = produccion_unidades[i]
            req_prod_sig = produccion_unidades[i + 1]
            inv_final_md = req_prod_sig * self.pct_inv_md
            compras_u = req_prod_actual + inv_final_md - inv_inicial_md
            compras_sin_igv = compras_u * costo_unit_md
            
            modulo_compras_md.append({
                "anio": i + 1, "req_prod": req_prod_actual, "inv_final_md": inv_final_md,
                "inv_inicial_md": inv_inicial_md, "compras_unidades": compras_u,
                "costo_unitario": costo_unit_md, "compras_sin_igv": compras_sin_igv,
                "compras_con_igv": compras_sin_igv * (1 + self.igv)
            })
            inv_inicial_md = inv_final_md

        # Capital de Trabajo Año 0
        compras_a1_con_igv = modulo_compras_md[0]["compras_con_igv"]
        egresos_a1_con_igv = compras_a1_con_igv + ((costos_indirectos + gastos_ventas + gastos_admin) * (1 + self.igv))
        ventas_a1_con_igv = (ventas_unidades[0] * precio_base) * (1 + self.igv)

        cxc_a0 = ventas_a1_con_igv * (self.dias_cobro / 360)
        cxp_a0 = egresos_a1_con_igv * (self.dias_pago / 360)
