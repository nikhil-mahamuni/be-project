from utils.time_utils import get_current_timestamp
from metrics.battery import BatteryManager
from metrics.network import NetworkStats
from metrics.energy import EnergyEstimator
from metrics.carbon import CarbonCalculator
from metrics.efficiency import EfficiencyCalculator
import time

class Profiler:
    def __init__(self, battery_manager: BatteryManager, network_stats: NetworkStats):
        self.battery_manager = battery_manager
        self.network_stats = network_stats
        self.start_time = 0.0
        self.start_battery = {}
        self.start_network = 0

    def start(self):
        self.start_time = get_current_timestamp()
        self.start_battery = self.battery_manager.get_battery_stats()
        self.start_network = self.network_stats.get_app_tx_rx_bytes()

    def stop(self, compression_ratio: float, output_words: int, grid_factor: float = None, capacity_mah: float = None, voltage: float = None, model_wh_per_sec: float = 0.00001) -> dict:
        end_time = get_current_timestamp()
        end_battery = self.battery_manager.get_battery_stats()
        end_network = self.network_stats.get_app_tx_rx_bytes()

        duration = end_time - self.start_time

        data_used = max(0, end_network - self.start_network)

        battery_delta = max(0.0, self.start_battery.get('level', 100) - end_battery.get('level', 100))

        # Energy
        kwargs_energy = {
            'duration_seconds': duration,
            'voltage_mv': end_battery.get('voltage_mv', 3850),
            'current_ua': end_battery.get('current_ua', 0),
            'battery_delta_percent': battery_delta,
            'is_mock_battery': end_battery.get('is_mock', True),
            'model_wh_per_second': model_wh_per_sec
        }
        if capacity_mah: kwargs_energy['battery_capacity_mah'] = capacity_mah
        if voltage: kwargs_energy['nominal_voltage_v'] = voltage

        energy_data = EnergyEstimator.calculate_energy(**kwargs_energy)

        # Carbon
        kwargs_carbon = {'energy_wh': energy_data['wh']}
        if grid_factor is not None: kwargs_carbon['grid_factor_gco2e_per_kwh'] = grid_factor
        carbon_footprint = CarbonCalculator.calculate_carbon_footprint(**kwargs_carbon)

        # Efficiency
        efficiency = EfficiencyCalculator.calculate_score(
            duration_seconds=duration,
            energy_joules=energy_data['joules'],
            data_used_bytes=data_used,
            compression_ratio=compression_ratio,
            output_words=output_words
        )

        return {
            'duration_seconds': duration,
            'data_used_bytes': data_used,
            'battery_delta_percent': battery_delta,
            'energy_joules': energy_data['joules'],
            'energy_wh': energy_data['wh'],
            'carbon_gco2e': carbon_footprint,
            'efficiency_score': efficiency,
            'is_estimated': energy_data['estimated']
        }
