"""
Módulo de balances de masa, energía y cinética de secado de capa delgada (Jena & Das)
para el horno continuo al vacío de 7 niveles SUNGDZ-07-130.

Este módulo reutiliza la clase Solvente e instancia Agua de `termodinamica.py`.
"""

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
import warnings
import termodinamica

# Constantes Físicas Universales y de la Biomasa (Cannabis sativa L.)
R_GAS = 8.314        # J/(mol K)
CP_BIOMASA = 1600.0   # J/(kg K) - Biomasa seca
CP_AGUA = 4186.0      # J/(kg K) - Agua líquida

def calcular_balance_global(m_in=139.0, w_in=0.75, w_out=0.05, T_in=20.0, P_vac=30.0):
    """
    Calcula los balances globales de masa y energía en estado estacionario para el horno SUNGDZ-07-130.
    """
    assert 0.0 < w_in < 1.0, "La humedad inicial debe estar entre 0 y 1."
    assert 0.0 < w_out < w_in, "La humedad final debe ser menor que la inicial."
    assert m_in > 0, "El flujo de entrada debe ser positivo."

    m_seco = m_in * (1.0 - w_in)
    m_out = m_seco / (1.0 - w_out)
    m_v = m_in - m_out
    m_v_kgs = m_v / 3600.0

    T_eb = termodinamica.Agua.temperatura_ebullicion(P_vac)
    delta_H_vap = 2501000.0 - 2370.0 * T_eb
    
    Cp_in = (1.0 - w_in) * CP_BIOMASA + w_in * CP_AGUA
    
    Q_sensible_W = (m_in / 3600.0) * Cp_in * (T_eb - T_in)
    Q_latente_W = m_v_kgs * delta_H_vap
    
    Q_total_kW = (Q_sensible_W + Q_latente_W) / 1000.0
    Q_nominal_kW = Q_total_kW * 1.20

    return {
        "m_in_kgh": m_in,
        "m_seco_kgh": m_seco,
        "m_out_kgh": m_out,
        "m_v_kgh": m_v,
        "m_v_kgs": m_v_kgs,
        "T_eb_C": T_eb,
        "Q_total_kW": Q_total_kW,
        "Q_nominal_kW": Q_nominal_kW
    }

# ==============================================================================
# ETAPA 2: CINÉTICA DE CAPA DELGADA (JENA & DAS) Y SOLUCIONADOR ACOPLADO NIVEL
# ==============================================================================

def coeficientes_jena_das(T_b_C, k_ref=0.085, g_ref=0.25, Ea=28500.0, T_ref_C=55.0):
    """
    Calcula los coeficientes k y g del modelo de Jena & Das mediante Arrhenius.
    Parámetros t en minutos.
    """
    T_K = T_b_C + 273.15
    T_ref_K = T_ref_C + 273.15
    
    factor_arrhenius = np.exp(-(Ea / R_GAS) * ((1.0 / T_K) - (1.0 / T_ref_K)))
    
    k_T = k_ref * factor_arrhenius  # min^-1
    g_T = g_ref * factor_arrhenius  # min^-1
    a = 0.92
    b = 0.08
    
    return k_T, g_T, a, b


def edos_acopladas_nivel(t_min, y, T_placa_C, P_vac_mbar, U, A_placa, m_seco, X_0, X_eq):
    """
    Sistema EDO acoplado de masa y energía para un nivel del horno en función del tiempo t (minutos).
    y = [X, T_b]
    """
    X, T_b = y
    
    T_eb = termodinamica.Agua.temperatura_ebullicion(P_vac_mbar)
    h_fg = 2501000.0 - 2370.0 * T_b
    U_efectivo = U * (0.35 + 0.65 * max(0.02, X / X_0))
    
    # Lógica de acoplamiento termofísico real
    if X > 0.4 and T_b >= T_eb:  # Período de velocidad constante controlado por transferencia de calor
        T_b = T_eb
        dT_b_dt = 0.0
        # La evaporación es igual al calor neto que ingresa por conducción dividido por h_fg
        Q_conduccion = U_efectivo * A_placa * (T_placa_C - T_eb)
        m_evap_kgs = Q_conduccion / h_fg
        dX_dt = - (m_evap_kgs * 60.0) / m_seco
    else:  # Período de velocidad decreciente controlado por difusión interna (Jena & Das)
        k_T, g_T, a, b = coeficientes_jena_das(T_b)
        
        # Tiempo efectivo equivalente basado en el estado de humedad para evitar estancamiento
        MR = (X - X_eq) / (X_0 - X_eq)
        t_eff = - np.log(max(1e-6, MR)) / k_T
        
        dMR_dt = - a * k_T * np.exp(-k_T * t_eff) - b * g_T * np.exp(-g_T * t_eff)
        
        if X > X_eq:
            dX_dt = (X_0 - X_eq) * dMR_dt
            dX_dt = min(0.0, dX_dt)
        else:
            dX_dt = 0.0
            
        m_evap_kgs = - (dX_dt / 60.0) * m_seco
        Q_conduccion = U_efectivo * A_placa * (T_placa_C - T_b)
        Q_evaporacion = m_evap_kgs * h_fg
        
        Cp_lecho = m_seco * (CP_BIOMASA + X * CP_AGUA)
        dT_b_dt = 60.0 * (Q_conduccion - Q_evaporacion) / max(10.0, Cp_lecho)
        
    return [dX_dt, dT_b_dt]


def simular_secado_nivel(t_total_min=30.0, T_placa_C=55.0, P_vac_mbar=30.0, X_0=3.0, X_eq=0.0526, U=50.0, A_placa=18.57, m_seco=17.375):
    """
    Resuelve el sistema diferencial acoplado para un tiempo de residencia de 30 min en un nivel.
    """
    T_0 = 20.0
    y0 = [X_0, T_0]
    t_span = (0.0, t_total_min)
    t_eval = np.linspace(0.0, t_total_min, 150)
    
    sol = solve_ivp(
        fun=edos_acopladas_nivel,
        t_span=t_span,
        y0=y0,
        t_eval=t_eval,
        args=(T_placa_C, P_vac_mbar, U, A_placa, m_seco, X_0, X_eq),
        method='Radau',
        dense_output=True
    )
    
    t_min = sol.t
    X_t = np.maximum(X_eq, sol.y[0])
    T_b = sol.y[1]
    
    MR = (X_t - X_eq) / (X_0 - X_eq)
    MR = np.maximum(0.0, MR)
    w_bh_pct = (X_t / (1.0 + X_t)) * 100.0
    
    assert np.all(MR >= 0.0), "Error Físico: El Moisture Ratio (MR) no puede ser negativo."
    assert np.all(X_t >= 0.0), "Error Físico: La humedad no puede ser negativa."
    
    return {
        "t_min": t_min,
        "X_t": X_t,
        "T_b": T_b,
        "MR": MR,
        "w_bh_pct": w_bh_pct
    }

# ==============================================================================
# ETAPA 3: CLASE DE SIMULACIÓN 'BeltCascadeDryer' (7 NIVELES EN CASCADA)
# ==============================================================================

class BeltCascadeDryer:
    """
    Simulador Orientado a Objetos del Horno Continuo al Vacío SUNGDZ-07-130 (7 Niveles en Cascada).
    """
    def __init__(
        self,
        v_belt_mm_min=500.0,
        L_belt_m=16.5,
        P_vac_mbar=30.0,
        m_in_kgh=139.0,
        w_in=0.75,
        T_in_C=15.0,
        T_setpoints=None,
        U_global=50.0,
        A_placa=18.57
    ):
        self.v_belt_mm_min = v_belt_mm_min
        self.v_belt_m_min = v_belt_mm_min / 1000.0  # m/min (500 mm/min = 0.5 m/min)
        self.L_belt_m = L_belt_m
        self.P_vac_mbar = P_vac_mbar
        self.m_in_kgh = m_in_kgh
        self.w_in = w_in
        self.X_0 = w_in / (1.0 - w_in)
        self.T_in_C = T_in_C
        self.U_global = U_global
        self.A_placa = A_placa
        self.m_seco_kgh = m_in_kgh * (1.0 - w_in) # 34.75 kg/h masa seca
        self.n_niveles = 7
        
        # Temperatura por defecto por nivel si no se especifica
        if T_setpoints is None:
            self.T_setpoints = {1: 45.0, 2: 55.0, 3: 55.0, 4: 50.0, 5: 45.0, 6: 40.0, 7: 25.0}
        else:
            self.T_setpoints = T_setpoints
            
        self.resultado_simulacion = None
        self.df_resumen = None

    def calcular_tiempo_residencia(self):
        """Retorna el tiempo de residencia (minutos) en cada nivel de cinta."""
        return self.L_belt_m / self.v_belt_m_min

    def simular_proceso(self):
        """
        Ejecuta el bucle en cascada desde el Nivel 1 hasta el Nivel 7.
        """
        t_res_nivel_min = self.calcular_tiempo_residencia()
        m_seco_nivel = self.m_seco_kgh * (t_res_nivel_min / 60.0)
        X_eq = 0.0526
        
        X_actual = self.X_0
        T_actual = self.T_in_C
        
        distancia_acum_m = [0.0]
        tiempo_acum_min = [0.0]
        nivel_registro = [1]
        X_hist = [X_actual]
        T_hist = [T_actual]
        
        resumen_niveles = []
        distancia_global = 0.0
        tiempo_global = 0.0
        
        for i in range(1, self.n_niveles + 1):
            T_placa = self.T_setpoints.get(i, 25.0 if i == 7 else 50.0)
            X_in_nivel = X_actual
            T_in_nivel = T_actual
            
            t_span = ((i - 1) * t_res_nivel_min, i * t_res_nivel_min)
            y0 = [X_in_nivel, T_in_nivel]
            
            sol = solve_ivp(
                fun=edos_acopladas_nivel,
                t_span=t_span,
                y0=y0,
                args=(T_placa, self.P_vac_mbar, self.U_global, self.A_placa, m_seco_nivel, self.X_0, X_eq),
                method='Radau',
                dense_output=True,
                max_step=t_res_nivel_min / 15.0
            )
            
            t_eval = np.linspace((i - 1) * t_res_nivel_min, i * t_res_nivel_min, 30)
            y_eval = sol.sol(t_eval)
            
            for k in range(1, len(t_eval)):
                t_rel = t_eval[k] - (i - 1) * t_res_nivel_min
                dist_rel = t_rel * self.v_belt_m_min
                tiempo_acum_min.append(t_eval[k])
                distancia_acum_m.append(distancia_global + dist_rel)
                nivel_registro.append(i)
                X_hist.append(max(X_eq, y_eval[0, k]))
                T_hist.append(y_eval[1, k])
                
            distancia_global += self.L_belt_m
            tiempo_global += t_res_nivel_min
            
            X_actual = max(X_eq, y_eval[0, -1])
            T_actual = y_eval[1, -1]
            
            # Balances de agua evaporada y potencia por nivel
            m_agua_in_kgh = self.m_seco_kgh * X_in_nivel
            m_agua_out_kgh = self.m_seco_kgh * X_actual
            m_evap_nivel_kgh = max(0.0, m_agua_in_kgh - m_agua_out_kgh)
            
            w_out_pct = (X_actual / (1.0 + X_actual)) * 100.0
            
            # Carga térmica en el nivel (kW)
            T_eb = termodinamica.Agua.temperatura_ebullicion(self.P_vac_mbar)
            h_fg = 2501000.0 - 2370.0 * T_actual
            Q_evap_kW = (m_evap_nivel_kgh / 3600.0) * h_fg / 1000.0
            Q_sensible_kW = (self.m_seco_kgh / 3600.0) * (CP_BIOMASA + X_actual * CP_AGUA) * max(0.0, T_actual - T_in_nivel) / 1000.0
            Q_total_nivel_kW = Q_evap_kW + Q_sensible_kW
            
            resumen_niveles.append({
                "Nivel": i,
                "Zona": "Calentamiento" if i < 7 else "Enfriamiento",
                "T_Placa (°C)": T_placa,
                "Humedad Salida (% b.h.)": w_out_pct,
                "Humedad Salida (kg/kg d.b.)": X_actual,
                "T Producto Salida (°C)": T_actual,
                "Agua Evaporada (kg/h)": m_evap_nivel_kgh,
                "Potencia Térmica (kW)": Q_total_nivel_kW
            })

        self.resultado_simulacion = {
            "distancia_m": np.array(distancia_acum_m),
            "tiempo_min": np.array(tiempo_acum_min),
            "nivel": np.array(nivel_registro),
            "X_db": np.array(X_hist),
            "w_pct": (np.array(X_hist) / (1.0 + np.array(X_hist))) * 100.0,
            "T_C": np.array(T_hist),
            "resumen_niveles": resumen_niveles
        }
        
        self.df_resumen = pd.DataFrame(resumen_niveles)
        return self.resultado_simulacion

    def generar_tabla_resumen(self):
        """Retorna el DataFrame de Pandas con el resumen operacional por nivel."""
        if self.df_resumen is None:
            self.simular_proceso()
        return self.df_resumen
