import os

try:
    from jnius import autoclass
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False

class NetworkStats:
    def __init__(self):
        self.is_android = ANDROID_AVAILABLE

    def get_app_tx_rx_bytes(self) -> int:
        """
        Gets total network bytes used by the application (tx + rx).
        Returns 0 if offline or unable to determine.
        """
        if not self.is_android:
            return 0

        try:
            TrafficStats = autoclass('android.net.TrafficStats')
            Process = autoclass('android.os.Process')

            uid = Process.myUid()
            rx_bytes = TrafficStats.getUidRxBytes(uid)
            tx_bytes = TrafficStats.getUidTxBytes(uid)

            # API returns TrafficStats.UNSUPPORTED (-1) if not available
            if rx_bytes == -1 or tx_bytes == -1:
                return 0

            return rx_bytes + tx_bytes
        except Exception as e:
            print(f"Error accessing Android TrafficStats: {e}")
            return 0
