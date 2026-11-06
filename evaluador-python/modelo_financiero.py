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
        inv_pt_a0 = (ventas_unidades[0] * self.pct_inv_pt) * costo_unit_base
        inv_md_a0 = modulo_compras_md[0]["inv_final_md"] * costo_unit_base
        ct_inicial = (cxc_a0 + inv_pt_a0 + inv_md_a0) - cxp_a0

        capital_propio = (inversion_fija + ct_inicial) - self.prestamo
        
        estado_situacion = [{
            "anio": 0, "caja": ct_inicial, "cxc": cxc_a0, "inv": inv_pt_a0 + inv_md_a0,
            "activo_corriente": ct_inicial + cxc_a0 + inv_pt_a0 + inv_md_a0,
            "activo_fijo_neto": inversion_fija, "activo_total": ct_inicial + cxc_a0 + inv_pt_a0 + inv_md_a0 + inversion_fija,
            "cxp": cxp_a0, "deuda_bancaria": self.prestamo, "pasivo_total": cxp_a0 + self.prestamo,
            "capital": capital_propio, "utilidad_retenida": 0.0, "patrimonio_total": capital_propio,
            "total_pasivo_patrimonio": cxp_a0 + self.prestamo + capital_propio
        }]

        credito_fiscal = inversion_tangible * self.igv
        modulo_igv = []
        modulo_ct = []
        estado_resultados = []
        flujo_efectivo = []
        
        ct_historico = ct_inicial
        caja_acumulada = ct_inicial
        activo_fijo_neto = inversion_fija
        utilidad_retenida_acumulada = 0.0
        
        fcl = [-inversion_fija - ct_inicial]
        fca = [-inversion_fija - ct_inicial + self.prestamo]

        filas_flujo = {
            "ventas": [0.0], "costo_ventas": [0.0], "utilidad_bruta": [0.0],
            "gastos_operativos": [0.0], "depreciacion": [0.0], "ebit": [0.0],
            "impuesto_renta": [0.0], "nopat": [0.0], "depreciacion_reversion": [0.0],
            "flujo_operativo": [0.0], "inversion_fija": [-inversion_fija],
            "capital_trabajo": [-ct_inicial], "valor_residual": [0.0],
            "flujo_inversiones": [-inversion_fija - ct_inicial], "flujo_economico": [-inversion_fija - ct_inicial],
            "prestamo": [self.prestamo], "interes": [0.0], "amortizacion": [0.0],
            "flujo_deuda": [self.prestamo], "ahorro_impuestos": [0.0],
            "flujo_financiero": [-inversion_fija - ct_inicial + self.prestamo],
            "igv_pagar": [0.0], "cambio_ct": [-ct_inicial]
        }

        for i in range(self.plazo):
            anio = i + 1
            precio = precio_base * ((1 + crec_precio) ** i)
            v_unidades = ventas_unidades[i]
            ventas = v_unidades * precio

            md_datos = modulo_compras_md[i]
            costo_unitario_md = md_datos["costo_unitario"]
            costo_ventas = (v_unidades * costo_unitario_md) + mod + costos_indirectos
            gastos_operativos = gastos_ventas + gastos_admin

            egresos_afectos_igv = md_datos["compras_sin_igv"] + costos_indirectos + gastos_operativos
            igv_ventas = ventas * self.igv
            igv_egresos = egresos_afectos_igv * self.igv
            saldo_igv = igv_ventas - igv_egresos

            if credito_fiscal > 0:
                if credito_fiscal >= saldo_igv:
                    igv_pagar = 0.0
                    credito_fiscal -= max(0.0, saldo_igv)
                else:
                    igv_pagar = saldo_igv - credito_fiscal
                    credito_fiscal = 0.0
            else:
                igv_pagar = max(0.0, saldo_igv)

            modulo_igv.append({
                "anio": anio, "igv_ventas": igv_ventas, "igv_egresos": igv_egresos,
                "credito_fiscal": credito_fiscal, "igv_pagar": igv_pagar
            })

            cxc = (ventas + igv_ventas) * (self.dias_cobro / 360)
            cxp = (egresos_afectos_igv + igv_egresos) * (self.dias_pago / 360)
            inv_pt_val = (v_unidades * self.pct_inv_pt) * costo_unitario_md
            inv_md_val = md_datos["inv_final_md"] * costo_unitario_md

            ct_actual = (cxc + inv_pt_val + inv_md_val) - cxp
            cambio_ct = ct_actual - ct_historico
            ct_historico = ct_actual

            modulo_ct.append({
                "anio": anio, "cxc": cxc, "inv_pt": inv_pt_val, "inv_md": inv_md_val,
                "cxp": cxp, "ct": ct_actual, "cambio_ct": cambio_ct
            })

            utilidad_bruta = ventas - costo_ventas
            ebit = utilidad_bruta - gastos_operativos - depreciacion_anual

            deuda_anual = deuda[i] if i < len(deuda) else {"interes": 0.0, "amortizacion": 0.0, "saldo_final": 0.0}
            interes = float(deuda_anual["interes"])
            amortizacion = float(deuda_anual["amortizacion"])

            impuesto_con_deuda = max(0.0, (ebit - interes) * self.impuesto_renta)
            impuesto_operativo = max(0.0, ebit * self.impuesto_renta)
            ahorro_impuestos = max(0.0, impuesto_operativo - impuesto_con_deuda)
            nopat = ebit - impuesto_operativo

            utilidad_neta = ebit - interes - impuesto_con_deuda
            dividendos = max(0.0, utilidad_neta * self.pct_dividendos)
            utilidad_retenida = utilidad_neta - dividendos
            utilidad_retenida_acumulada += utilidad_retenida

            estado_resultados.append({
                "anio": anio, "ventas": ventas, "costo_ventas": costo_ventas,
                "utilidad_bruta": utilidad_bruta, "gastos_operativos": gastos_operativos,
                "depreciacion": depreciacion_anual, "ebit": ebit, "interes": interes,
                "impuesto": impuesto_con_deuda, "utilidad_neta": utilidad_neta,
                "dividendos": dividendos, "utilidad_retenida": utilidad_retenida
            })

            ingresos_efectivo = (ventas + igv_ventas) - (cxc - estado_situacion[i]["cxc"])
            egresos_efectivo = (egresos_afectos_igv + igv_egresos) - (cxp - estado_situacion[i]["cxp"]) + mod
            
            fe_operativo = ingresos_efectivo - egresos_efectivo - igv_pagar - impuesto_con_deuda
            fe_inversion = self.valor_residual if anio == self.plazo else 0.0
            fe_financiero = -interes - amortizacion - dividendos
            fe_neto = fe_operativo + fe_inversion + fe_financiero

            caja_acumulada += fe_neto

            flujo_efectivo.append({
                "anio": anio, "ingresos": ingresos_efectivo, "egresos": egresos_efectivo,
                "igv_pagar": igv_pagar, "impuesto_renta": impuesto_con_deuda,
                "fe_operativo": fe_operativo, "fe_inversion": fe_inversion,
                "fe_financiero": fe_financiero, "fe_neto": fe_neto, "caja_final": caja_acumulada
            })

            activo_fijo_neto = max(0.0, activo_fijo_neto - depreciacion_anual)
            act_corriente = caja_acumulada + cxc + inv_pt_val + inv_md_val
            act_total = act_corriente + activo_fijo_neto
            pasivo_tot = cxp + float(deuda_anual["saldo_final"])
            patrimonio_tot = capital_propio + utilidad_retenida_acumulada

            estado_situacion.append({
                "anio": anio, "caja": caja_acumulada, "cxc": cxc, "inv": inv_pt_val + inv_md_val,
                "activo_corriente": act_corriente, "activo_fijo_neto": activo_fijo_neto,
                "activo_total": act_total, "cxp": cxp, "deuda_bancaria": float(deuda_anual["saldo_final"]),
                "pasivo_total": pasivo_tot, "capital": capital_propio,
                "utilidad_retenida": utilidad_retenida_acumulada, "patrimonio_total": patrimonio_tot,
                "total_pasivo_patrimonio": pasivo_tot + patrimonio_tot
            })

            flujo_operativo = nopat + depreciacion_anual - cambio_ct - igv_pagar
            recuperacion_ct = ct_actual if anio == self.plazo else 0.0
            flujo_inversiones = recuperacion_ct + (self.valor_residual if anio == self.plazo else 0)
            flujo_economico = flujo_operativo + flujo_inversiones
            flujo_deuda = -interes - amortizacion
            flujo_financiero = flujo_economico + flujo_deuda + ahorro_impuestos

            fcl.append(flujo_economico)
            fca.append(flujo_financiero)

            valores = {
                "ventas": ventas, "costo_ventas": -costo_ventas, "utilidad_bruta": utilidad_bruta,
                "gastos_operativos": -gastos_operativos, "depreciacion": -depreciacion_anual, "ebit": ebit,
                "impuesto_renta": -impuesto_operativo, "nopat": nopat, "depreciacion_reversion": depreciacion_anual,
                "flujo_operativo": flujo_operativo, "inversion_fija": 0.0, "capital_trabajo": recuperacion_ct,
                "valor_residual": self.valor_residual if anio == self.plazo else 0.0,
                "flujo_inversiones": flujo_inversiones, "flujo_economico": flujo_economico,
                "prestamo": 0.0, "interes": -interes, "amortizacion": -amortizacion,
                "flujo_deuda": flujo_deuda, "ahorro_impuestos": ahorro_impuestos,
                "flujo_financiero": flujo_financiero, "igv_pagar": -igv_pagar, "cambio_ct": -cambio_ct
            }
            for k, v in valores.items():
                filas_flujo[k].append(v)

        van_fcl = float(npv_nativo(self.cok, fcl))
        tir_fcl = calcular_tir_segura(fcl)
        van_fca = float(npv_nativo(self.ke, fca))
        tir_fca = calcular_tir_segura(fca)

        return {
            "deuda": deuda,
            "depreciaciones": desglose_activos,
            "modulo_compras_md": modulo_compras_md,
            "modulo_igv": modulo_igv,
            "modulo_ct": modulo_ct,
            "estado_situacion": estado_situacion,
            "flujo_efectivo": flujo_efectivo,
            "estado_resultados": [
                {k: numero_json(v) if isinstance(v, (int, float)) else v for k, v in f.items()}
                for f in estado_resultados
            ],
            "flujo_detallado": {k: [numero_json(v) for v in l] for k, l in filas_flujo.items()},
            "evaluacion": {
                "van_fcl": numero_json(van_fcl),
                "tir_fcl": numero_json(tir_fcl * 100) if tir_fcl is not None else None,
                "van_fca": numero_json(van_fca),
                "tir_fca": numero_json(tir_fca * 100) if tir_fca is not None else None,
            },
        }
