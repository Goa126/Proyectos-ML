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
        self.rango_T = rango_T #Tupla opcional (T_min, T_max) en Celsius

    def _verificar_rango(self, T_C):
        """
        Método interno de seguridad. Revisa si la temperatura solicitada 
        está dentro del rango experimental válido para estas constantes.
        """
        if self.rango_T is not None:
            t_min, t_max = self.rango_T
            if T_C < t_min or T_C > t_max:
                warnings.warn(
                    f"\n[ALERTA TERMODINÁMICA] Para '{self.nombre}': "
                    f"La temperatura {T_C:.2f} °C está fuera del rango válido "
                    f"({t_min} a {t_max} °C). ¡El cálculo es una extrapolación y puede ser erróneo!"
                )    

    def presion_saturacion(self, T_C):
        """
        Calcula la presión de vapor (saturación) a una temperatura dada.

        Parámetros:
        T_C (float): Temperatura en grados Celsius.

        Retorna:
        float: Presión de vapor en mmHg.
        """
        self._verificar_rango(T_C)
        return 10**(self.A - (self.B / (T_C + self.C)))

    def temperatura_ebullicion(self, P_total_mbar):
        """
        Calcula la temperatura a la cual el solvente hierve a la presión del horno.

        Parámetros:
        P_total_mbar (float): Presión total del sistema de vacío en mbar.

        Retorna:
        float: Temperatura de ebullición teórica en grados Celsius.
        """
        # Conversión de mbar a mmHg (unidad de las constantes de Antoine)
        P_total_mmHg = P_total_mbar * 0.750062

        # Despejando T de la ecuación de Antoine
        # CORRECCIÓN 2: Cambiar P_mmHg por P_total_mmHg
        T_sat = (self.B / (self.A - np.log10(P_total_mmHg))) - self.C
        return T_sat

# ==========================================
# BASE DE DATOS DE SOLVENTES
# ==========================================
Agua = Solvente("Agua", 8.07131, 1730.63, 233.426, (1, 100))
Etanol = Solvente("Etanol", 8.20417, 1642.89, 230.300, (-57, 80))