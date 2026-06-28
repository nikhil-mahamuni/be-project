from utils.constants import DEFAULT_GRID_FACTOR_GCO2E_PER_KWH

class CarbonCalculator:
    @staticmethod
    def calculate_carbon_footprint(energy_wh: float, grid_factor_gco2e_per_kwh: float = DEFAULT_GRID_FACTOR_GCO2E_PER_KWH) -> float:
        """
        Calculate carbon footprint in grams of CO2 equivalent based on energy consumed and the regional grid factor.
        """
        energy_kwh = energy_wh / 1000.0
        carbon_gco2e = energy_kwh * grid_factor_gco2e_per_kwh
        return carbon_gco2e
