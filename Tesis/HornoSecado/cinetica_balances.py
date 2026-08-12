"""
Módulo de balances de masa, energía y cinética de secado de capa delgada (Jena & Das) 
para el horno continuo al vacío de 7 niveles SUNGDZ-07-130.

Este módulo reutiliza la clase Solvente e instancia Agua de termodinamica.py 
e implementa la lógica del Tiempo Equivalente de Estado (t_eff) para evitar el estancamiento.
"""

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
import warnings
import termodinamica

# Constantes Físicas Universales y de la Biomasa (Cannabis sativa L.)
R_GAS = 8.314          # J/(mol K)
CP_BIOMASA = 1600.0     # J/(kg K) - Biomasa seca libre de agua
CP_AGUA = 4186.0        # J/(kg K) - Agua líquida

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
    
    # Temperatura de ebullición del agua al vacío de la cámara
    T_eb = termodinamica.Agua.temperatura_ebullicion(P_vac)
    delta_H_vap = (2501.0 - 2.36 * T_eb) * 1000.0  # Convertir kJ/kg a J/kg
    
    # Calor específico promedio de entrada de la mezcla húmeda
    Cp_in = (1.0 - w_in) * CP_BIOMASA + w_in * CP_AGUA
    
    Q_sensible_W = (m_in / 3600.0) * Cp_in * (T_eb - T_in)
    Q_latente_W = m_v_kgs * delta_H_vap
    Q_total_kW = (Q_sensible_W + Q_latente_W) / 1000.0
    Q_nominal_kW = Q_total_kW * 1.20  # 20% factor de seguridad
    
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

def coeficientes_jena_das(T_b_C, k_ref=0.085, g_ref=0.25, Ea=28500.0, T_ref_C=55.0):
    """
    Calcula los coeficientes k y g del modelo de Jena & Das mediante Arrhenius en base a la temperatura local.
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
    Sistema EDO acoplado de masa y energía para un nivel del horno.
    y = [X, T_b]
    Utiliza el Tiempo Equivalente de Estado (t_eff) en lugar de t_min físico para Jena & Das.
    """
    X, T_b = y
    
    # 1. Propiedades Termodinámicas en Vacío (Antoine)
    T_eb = termodinamica.Agua.temperatura_ebullicion(P_vac_mbar)
    h_fg = (2501.0 - 2.36 * T_b) * 1000.0  # J/kg
    
    # Coeficiente global efectivo que disminuye con la pérdida de humedad (pérdida de contacto térmico)
    U_efectivo = U * (0.35 + 0.65 * max(0.02, X / X_0))
    
    # 2. Lógica de Acoplamiento Fenomenológico por Período de Secado
    if X > 0.4 and T_b >= T_eb:
        # Período Antecrítico (Velocidad Constante controlada por transferencia de calor)
        dT_b_dt = 0.0
        T_b = T_eb  # Clavar la biomasa húmeda a la temperatura de ebullición del vacío
        
        Q_conduccion = U_efectivo * A_placa * (T_placa_C - T_eb)  # Watts
        m_evap_kgs = Q_conduccion / h_fg  # kg/s
        
        # Variación de humedad (dX/dt) resultante de la tasa de evaporación en base seca por minuto
        dX_dt = - (m_evap_kgs * 60.0) / m_seco
    else:
        # Período Poscrítico (Velocidad Decreciente controlada por difusión interna)
        k_T, g_T, a, b = coeficientes_jena_das(T_b)
        
        # Calcular el Moisture Ratio (MR) actual
        MR = np.clip((X - X_eq) / (X_0 - X_eq), 1e-6, 1.0)
        
        # IMPLEMENTACIÓN DE TU SOLUCIÓN: Tiempo Equivalente de Estado (t_eff)
        # Aproxima el tiempo transcurrido en la cinética de Jena & Das para el MR actual
        t_eff = np.maximum(1e-4, -np.log(MR) / k_T)
        
        # Derivada cinética de Jena & Das usando t_eff
        dMR_dt = - a * k_T * np.exp(-k_T * t_eff) - b * g_T * np.exp(-g_T * t_eff)
        
        dX_dt = (X_0 - X_eq) * dMR_dt
        dX_dt = min(0.0, dX_dt)  # Evitar rehidratación física
        
        m_evap_kgs = - (dX_dt / 60.0) * m_seco  # kg/s
        
        Q_conduccion = U_efectivo * A_placa * (T_placa_C - T_b)  # Watts
        Q_evaporacion = m_evap_kgs * h_fg                       # Watts
        
        # Calor específico del lecho húmedo actual (biomasa + agua remanente)
        Cp_lecho = m_seco * (CP_BIOMASA + X * CP_AGUA)
        
        # dT_b/dt resultante de la Primera Ley en Watts convertida a minutos
        dT_b_dt = 60.0 * (Q_conduccion - Q_evaporacion) / max(10.0, Cp_lecho)
        
    return [dX_dt, dT_b_dt]

class BeltCascadeDryer:
    """
    Simulador Orientado a Objetos del Horno Continuo al Vacío SUNGDZ-07-130 (7 Niveles en Cascada).
    """
    def __init__(self, v_belt_mm_min=500.0, L_belt_m=16.5, P_vac_mbar=30.0, m_in_kgh=139.0, w_in=0.75, T_in_C=15.0, T_setpoints=None, U_global=50.0, A_placa=18.57):
        self.v_belt_mm_min = v_belt_mm_min
        self.v_belt_m_min = v_belt_mm_min / 1000.0  # m/min (ej. 500 mm/min = 0.5 m/min)
        self.L_belt_m = L_belt_m
        self.P_vac_mbar = P_vac_mbar
        self.m_in_kgh = m_in_kgh
        self.w_in = w_in
        self.X_0 = w_in / (1.0 - w_in)
        self.T_in_C = T_in_C
        self.U_global = U_global
        self.A_placa = A_placa
        self.m_seco_kgh = m_in_kgh * (1.0 - w_in)  # 34.75 kg/h de masa seca fija
        self.n_niveles = 7
        
        if T_setpoints is None:
            # Perfil térmico óptimo zonificado: Layer 1-6 calentamiento, 7 enfriamiento
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
        Resuelve la cascada completa del horno continuo del Nivel 1 al 7.
        """
        t_res_nivel_min = self.calcular_tiempo_residencia()
        
        # CORRECCIÓN: Inventario físico de masa seca en cada cinta (kg)
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
            
            # Integración de la cinta actual
            t_span = (0.0, t_res_nivel_min)
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
            
            # Muestrear 30 puntos a lo largo de la cinta para graficación continua
            t_eval = np.linspace(0.0, t_res_nivel_min, 30)
            y_eval = sol.sol(t_eval)
            
            for k in range(1, len(t_eval)):
                t_rel = t_eval[k]
                dist_rel = t_rel * self.v_belt_m_min
                tiempo_acum_min.append(tiempo_global + t_rel)
                distancia_acum_m.append(distancia_global + dist_rel)
                nivel_registro.append(i)
                X_hist.append(max(X_eq, y_eval[0, k]))
                T_hist.append(y_eval[1, k])
            
            # Actualizar condiciones de salida para el nivel de cascada posterior (Nivel i -> Nivel i+1)
            distancia_global += self.L_belt_m
            tiempo_global += t_res_nivel_min
            X_actual = max(X_eq, y_eval[0, -1])
            T_actual = y_eval[1, -1]
            
            # Cálculos operacionales de balance de masa y calor por nivel (kg/h)
            m_agua_in_kgh = self.m_seco_kgh * X_in_nivel
            m_agua_out_kgh = self.m_seco_kgh * X_actual
            m_evap_nivel_kgh = max(0.0, m_agua_in_kgh - m_agua_out_kgh)
            w_out_pct = (X_actual / (1.0 + X_actual)) * 100.0
            
            # Carga térmica promedio por conducción de la placa (kW)
            T_eb = termodinamica.Agua.temperatura_ebullicion(self.P_vac_mbar)
            h_fg = (2501.0 - 2.36 * T_actual) * 1000.0  # J/kg
            
            Q_evap_kW = (m_evap_nivel_kgh / 3600.0) * h_fg / 1000.0
            Q_sensible_kW = (self.m_seco_kgh / 3600.0) * (CP_BIOMASA + X_actual * CP_AGUA) * (T_actual - T_in_nivel) / 1000.0
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