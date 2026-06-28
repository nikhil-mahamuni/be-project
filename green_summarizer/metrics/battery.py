from typing import Dict, Any

try:
    from jnius import autoclass, cast
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False

class BatteryManager:
    def __init__(self):
        self.is_android = ANDROID_AVAILABLE

    def get_battery_stats(self) -> Dict[str, Any]:
        """
        Retrieves battery statistics. Uses Android APIs if available, otherwise returns mock/estimated data.
        """
        stats = {
            'level': 100.0,
            'voltage_mv': 3850.0,  # 3.85V nominal
            'current_ua': 0.0,
            'temperature': 25.0,
            'is_mock': True
        }

        if self.is_android:
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Context = autoclass('android.content.Context')
                Intent = autoclass('android.content.Intent')
                IntentFilter = autoclass('android.content.IntentFilter')
                BatteryManagerAPI = autoclass('android.os.BatteryManager')

                activity = PythonActivity.mActivity

                # Intent based approach for battery level and voltage
                ifilter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
                batteryStatus = activity.registerReceiver(None, ifilter)

                if batteryStatus:
                    level = batteryStatus.getIntExtra(BatteryManagerAPI.EXTRA_LEVEL, -1)
                    scale = batteryStatus.getIntExtra(BatteryManagerAPI.EXTRA_SCALE, -1)
                    if level != -1 and scale != -1:
                        stats['level'] = (level / float(scale)) * 100.0

                    voltage = batteryStatus.getIntExtra(BatteryManagerAPI.EXTRA_VOLTAGE, -1)
                    if voltage > 0:
                        stats['voltage_mv'] = float(voltage)

                    temp = batteryStatus.getIntExtra(BatteryManagerAPI.EXTRA_TEMPERATURE, -1)
                    if temp > 0:
                        stats['temperature'] = float(temp) / 10.0 # typically tenths of a degree

                # BatteryManager API for current
                batteryManager = activity.getSystemService(Context.BATTERY_SERVICE)
                if batteryManager:
                    current_now = batteryManager.getIntProperty(BatteryManagerAPI.BATTERY_PROPERTY_CURRENT_NOW)
                    # if returning valid value (not 0 or maxint)
                    if current_now != 0 and abs(current_now) < 100000000:
                        stats['current_ua'] = float(current_now)

                stats['is_mock'] = False
            except Exception as e:
                print(f"Error accessing Android Battery APIs: {e}")
                # Fallback to mock values already set

        return stats
