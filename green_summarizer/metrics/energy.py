from utils.constants import DEFAULT_BATTERY_CAPACITY_MAH, DEFAULT_NOMINAL_VOLTAGE

class EnergyEstimator:
    @staticmethod
    def calculate_energy(duration_seconds: float,
                         voltage_mv: float,
                         current_ua: float,
                         battery_delta_percent: float,
                         battery_capacity_mah: float = DEFAULT_BATTERY_CAPACITY_MAH,
                         nominal_voltage_v: float = DEFAULT_NOMINAL_VOLTAGE,
                         is_mock_battery: bool = True,
                         model_wh_per_second: float = 0.00001) -> dict:
        """
        Calculate power and energy estimates based on available data.
        Returns joules and wh.
        """
        energy_joules = 0.0
        energy_wh = 0.0

        # Method 1: If we have real hardware voltage/current
        if not is_mock_battery and current_ua != 0:
            voltage_v = voltage_mv / 1000.0
            current_a = abs(current_ua) / 1000000.0
            power_watts = voltage_v * current_a
            energy_joules = power_watts * duration_seconds
            energy_wh = energy_joules / 3600.0

        # Method 2: Delta percent fallback (good for long tasks)
        elif battery_delta_percent > 0:
            # delta_percent is e.g. 0.5 for 0.5%
            energy_wh = battery_capacity_mah * nominal_voltage_v * (battery_delta_percent / 100.0) / 1000.0
            energy_joules = energy_wh * 3600.0

        # Method 3: Model-based empirical estimation (for fast offline tasks where delta=0)
        else:
            energy_wh = model_wh_per_second * duration_seconds
            energy_joules = energy_wh * 3600.0

        return {
            'joules': energy_joules,
            'wh': energy_wh,
            'estimated': True # Always label as estimated for safety in UI
        }
