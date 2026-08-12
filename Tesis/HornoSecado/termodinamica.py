import numpy as np
import warnings

class Solvente:
    """
    Clase para representar las propiedades termodinámicas de un solvente,
    basado en la Ecuación de Antoine: log10(P) = A - (B / (T + C))
    """
    def __init__(self, nombre, A, B, C, rango_T=None):
        self.nombre = nombre
        self.A = A
        self.B = B
        self.C = C
        self.rango_T = rango_T  # Tupla opcional (T_min, T_max) en Celsius

    def _verificar_rango(self, T_C):
        """
        Método interno de seguridad. Revisa si la temperatura solicitada 
        está dentro del rango experimental válido, compatible con floats y arrays de NumPy.
        """
        if self.rango_T is not None:
            t_min, t_max = self.rango_T
            # Conversión temporal a array para asegurar compatibilidad de vectorización
            T_arr = np.atleast_1d(T_C)
            
            # np.any permite verificar si al menos un elemento del vector viola los límites
            if np.any(T_arr < t_min) or np.any(T_arr > t_max):
                warnings.warn(
                    f"\n[ALERTA TERMODINÁMICA] Para '{self.nombre}': "
                    f"Se detectó una temperatura fuera del rango válido ({t_min} a {t_max} °C). "
                    f"¡El cálculo es una extrapolación y puede ser erróneo!",
                    category=RuntimeWarning
                )    

    def presion_saturacion(self, T_C):
        """
        Calcula la presión de vapor (saturación) a una temperatura dada.
        Soporta valores individuales (floats) y arreglos de NumPy.
        """
        self._verificar_rango(T_C)
        return 10**(self.A - (self.B / (T_C + self.C)))

    def temperatura_ebullicion(self, P_total_mbar):
        """
        Calcula la temperatura a la cual el solvente hierve a la presión del horno.
        Incluye salvaguardas físicas para simulación numérica y verificación de rangos.
        """
        # Salvaguarda física: si la presión es cero o negativa, se asume vacío absoluto teórico
        # o se limita a un valor mínimo positivo muy pequeño (1e-5 mbar) para evitar fallos matemáticos
        P_safe = np.maximum(P_total_mbar, 1e-5)

        # Conversión de mbar a mmHg (unidad de las constantes de Antoine)
        P_total_mmHg = P_safe * 0.750062

        # Despejando T de la ecuación de Antoine
        T_sat = (self.B / (self.A - np.log10(P_total_mmHg))) - self.C
        
        # Corrección: Verificar rango del resultado calculado
        self._verificar_rango(T_sat)
        
        return T_sat

# ==========================================
# BASE DE DATOS DE SOLVENTES
# ==========================================
# Constantes validadas de 1 a 100 °C
Agua = Solvente("Agua", 8.07131, 1730.63, 233.426, (1, 100))
# Constantes validadas de -57 a 80 °C
Etanol = Solvente("Etanol", 8.20417, 1642.89, 230.300, (-57, 80))