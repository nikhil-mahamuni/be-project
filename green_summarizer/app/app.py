from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivy.core.window import Window

from storage.database import Database
from storage.settings_store import SettingsStore
from metrics.battery import BatteryManager
from metrics.network import NetworkStats
from metrics.profiler import Profiler
from utils.constants import DB_PATH

from screens.home_screen import HomeScreen
from screens.text_screen import TextScreen
from screens.pdf_screen import PDFScreen
from screens.result_screen import ResultScreen
from screens.compare_screen import CompareScreen
from screens.analytics_screen import AnalyticsScreen
from screens.history_screen import HistoryScreen
from screens.settings_screen import SettingsScreen

class GreenSummarizerApp(MDApp):
    def build(self):
        self.title = "GreenSummarizer"

        # Theme setup
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_hue = "700"

        import os

        # In Android, DB_PATH might be read-only if it's in the app source root.
        # We use the app's user_data_dir for the persistent database location.
        actual_db_path = os.path.join(self.user_data_dir, 'history.db')

        # Initialize Core Systems
        self.db = Database(actual_db_path)
        self.settings = SettingsStore(actual_db_path)

        # Set default settings if not exists
        if not self.settings.get('default_ratio'):
            self.settings.set('default_ratio', '0.3')
        if not self.settings.get('battery_capacity'):
            self.settings.set('battery_capacity', '4000')
        if not self.settings.get('grid_factor'):
            self.settings.set('grid_factor', '708.2')

        # Initialize Metrics
        self.battery_manager = BatteryManager()
        self.network_stats = NetworkStats()
        self.profiler = Profiler(self.battery_manager, self.network_stats)

        # Screen Manager
        self.sm = MDScreenManager()

        # Initialize Screens
        self.screens = {
            'home': HomeScreen(app=self),
            'text_summary': TextScreen(app=self),
            'pdf_summary': PDFScreen(app=self),
            'result': ResultScreen(app=self),
            'compare': CompareScreen(app=self),
            'analytics': AnalyticsScreen(app=self),
            'history': HistoryScreen(app=self),
            'settings': SettingsScreen(app=self)
        }

        for name, screen in self.screens.items():
            self.sm.add_widget(screen)

        return self.sm

    def switch_screen(self, screen_name):
        self.sm.current = screen_name
