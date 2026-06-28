from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex
from kivymd.uix.toolbar import MDTopAppBar
from utils.constants import COLOR_PRIMARY_GREEN, COLOR_LIGHT_GREEN
from widgets.metric_card import MetricCard
from collections import Counter

class AnalyticsScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.name = "analytics"
        self.app = app

        main_layout = MDBoxLayout(orientation="vertical")

        self.toolbar = MDTopAppBar(
            title="Green Analytics",
            anchor_title="left",
            md_bg_color=get_color_from_hex(COLOR_PRIMARY_GREEN),
            specific_text_color=get_color_from_hex("#ffffff"),
            left_action_items=[["arrow-left", lambda x: self.app.switch_screen("home")]]
        )
        main_layout.add_widget(self.toolbar)

        from kivy.uix.scrollview import ScrollView
        self.scroll = ScrollView(size_hint=(1, 1))
        self.content = MDBoxLayout(orientation="vertical", padding="16dp", spacing="16dp", size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter('height'))

        self.scroll.add_widget(self.content)
        main_layout.add_widget(self.scroll)
        self.add_widget(main_layout)

    def on_enter(self):
        self.content.clear_widgets()

        history = self.app.db.get_all_history()

        if not history:
            self.content.add_widget(MDLabel(text="No data yet. Summarize some text to see analytics.", halign="center"))
            return

        total_summaries = len(history)
        total_words = sum(h.input_word_count for h in history)
        total_energy = sum(h.energy_joules for h in history)
        total_carbon = sum(h.carbon_gco2e for h in history)

        avg_latency = sum(h.duration_seconds for h in history) / total_summaries

        models = [h.model_name for h in history]
        most_used_model = Counter(models).most_common(1)[0][0]

        # Grid
        from kivymd.uix.gridlayout import MDGridLayout
        grid = MDGridLayout(cols=2, spacing="10dp", size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        grid.add_widget(MetricCard("Total Summaries", str(total_summaries), ""))
        grid.add_widget(MetricCard("Words Processed", f"{total_words:,}", ""))
        grid.add_widget(MetricCard("Total Energy", f"{total_energy:.2f} J", ""))
        grid.add_widget(MetricCard("Total Carbon", f"{total_carbon:.4f} g", ""))
        grid.add_widget(MetricCard("Avg Latency", f"{avg_latency:.2f} s", ""))
        grid.add_widget(MetricCard("Top Model", most_used_model, ""))

        self.content.add_widget(grid)

        # Info Cards
        from widgets.model_card import ModelCard

        # We assume offline processing saves ~0.05g CO2e per query compared to cloud
        savings = total_summaries * 0.05

        self.content.add_widget(ModelCard("Internet Data Saved", f"Processed entirely offline.\nEstimated cloud savings: {savings:.2f}g CO₂e"))
        self.content.add_widget(ModelCard("Privacy Secured", f"All {total_words:,} words remained on this device."))
