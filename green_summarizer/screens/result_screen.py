from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex
from kivymd.uix.toolbar import MDTopAppBar
from utils.constants import COLOR_PRIMARY_GREEN
from widgets.metric_card import MetricCard
from widgets.summary_card import SummaryCard
from utils.time_utils import format_duration
from kivy.core.clipboard import Clipboard

class ResultScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.name = "result"
        self.app = app
        self.summary_text = ""

        main_layout = MDBoxLayout(orientation="vertical")

        # Toolbar
        self.toolbar = MDTopAppBar(
            title="Summary Result",
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

    def show_result(self, result, metrics):
        self.content.clear_widgets()
        self.summary_text = result.summary_text

        # Stats Header
        stats_txt = f"Original: {result.input_word_count} words  |  Summary: {result.output_word_count} words  |  Compression: {result.compression_ratio*100:.1f}%"
        self.content.add_widget(MDLabel(text=stats_txt, font_style="Caption", theme_text_color="Secondary", size_hint_y=None, height="20dp"))

        # Summary Card
        self.content.add_widget(SummaryCard(summary_text=result.summary_text))

        # Actions
        action_box = MDBoxLayout(orientation="horizontal", spacing="10dp", size_hint_y=None, height="50dp")
        btn_copy = MDRaisedButton(text="Copy", md_bg_color=get_color_from_hex(COLOR_PRIMARY_GREEN), on_release=self.copy_to_clipboard)
        action_box.add_widget(btn_copy)
        self.content.add_widget(action_box)

        # Metrics Grid
        from kivymd.uix.gridlayout import MDGridLayout
        grid = MDGridLayout(cols=2, spacing="10dp", size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        grid.add_widget(MetricCard("Time Taken", format_duration(metrics['duration_seconds']), ""))
        grid.add_widget(MetricCard("Data Used", f"{metrics['data_used_bytes']/1024:.1f} KB", ""))
        grid.add_widget(MetricCard("Energy (Est)", f"{metrics['energy_joules']:.3f} J", ""))
        grid.add_widget(MetricCard("Carbon (Est)", f"{metrics['carbon_gco2e']:.4f} g", ""))
        grid.add_widget(MetricCard("Efficiency", f"{metrics['efficiency_score']:.1f}/100", ""))
        grid.add_widget(MetricCard("Model", result.model_name, ""))

        self.content.add_widget(grid)

    def copy_to_clipboard(self, instance):
        Clipboard.copy(self.summary_text)
        self.toolbar.title = "Copied!"
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: setattr(self.toolbar, 'title', 'Summary Result'), 2)
