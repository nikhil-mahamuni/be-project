from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.spinner import MDSpinner
from utils.constants import COLOR_PRIMARY_GREEN
from summarizers.factory import SummarizerFactory
from documents.text_cleaner import TextCleaner
from widgets.chart_widgets import SimpleBarChart
import threading
import time

class CompareScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.name = "compare"
        self.app = app

        main_layout = MDBoxLayout(orientation="vertical")

        self.toolbar = MDTopAppBar(
            title="Compare Models",
            anchor_title="left",
            md_bg_color=get_color_from_hex(COLOR_PRIMARY_GREEN),
            specific_text_color=get_color_from_hex("#ffffff"),
            left_action_items=[["arrow-left", lambda x: self.app.switch_screen("home")]]
        )
        main_layout.add_widget(self.toolbar)

        # Split layout
        self.top_box = MDBoxLayout(orientation="vertical", padding="16dp", spacing="10dp", size_hint_y=0.4)

        self.text_input = MDTextField(
            hint_text="Paste text to compare...",
            mode="rectangle",
            multiline=True
        )
        self.top_box.add_widget(self.text_input)

        action_box = MDBoxLayout(orientation="horizontal", spacing="10dp", size_hint_y=None, height="50dp")
        self.spinner = MDSpinner(active=False, size_hint=(None, None), size=("30dp", "30dp"))
        self.btn_compare = MDRaisedButton(
            text="Run Comparison",
            md_bg_color=get_color_from_hex(COLOR_PRIMARY_GREEN),
            on_release=self.start_comparison
        )
        action_box.add_widget(self.spinner)
        action_box.add_widget(self.btn_compare)
        self.top_box.add_widget(action_box)

        main_layout.add_widget(self.top_box)

        # Results area
        from kivy.uix.scrollview import ScrollView
        self.scroll = ScrollView(size_hint=(1, 0.6))
        self.results_content = MDBoxLayout(orientation="vertical", padding="16dp", spacing="20dp", size_hint_y=None)
        self.results_content.bind(minimum_height=self.results_content.setter('height'))
        self.scroll.add_widget(self.results_content)
        main_layout.add_widget(self.scroll)

        self.add_widget(main_layout)

    def start_comparison(self, instance):
        raw_text = self.text_input.text
        if not raw_text.strip():
            self.toolbar.title = "Enter text to compare"
            return

        self.btn_compare.disabled = True
        self.spinner.active = True
        self.toolbar.title = "Running models..."
        self.results_content.clear_widgets()

        threading.Thread(target=self._process_comparison, args=(raw_text,)).start()

    def _process_comparison(self, raw_text):
        try:
            cleaned_text = TextCleaner.clean(raw_text)
            models = SummarizerFactory.get_available_models()

            try:
                ratio = float(self.app.settings.get('default_ratio', '0.3'))
                if ratio < 0.05: ratio = 0.05
                if ratio > 0.80: ratio = 0.80
            except ValueError:
                ratio = 0.3

            results = {}

            for model_name in models:
                self.app.profiler.start()
                summarizer = SummarizerFactory.get_summarizer(model_name)
                res = summarizer.summarize(cleaned_text, ratio)

                batt_cap = float(self.app.settings.get('battery_capacity', '4000'))
                grid_fac = float(self.app.settings.get('grid_factor', '708.2'))
                metrics = self.app.profiler.stop(
                    compression_ratio=res.compression_ratio,
                    output_words=res.output_word_count,
                    grid_factor=grid_fac,
                    capacity_mah=batt_cap
                )
                res.processing_time_seconds = metrics['duration_seconds']
                results[model_name] = {'res': res, 'metrics': metrics}

            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self._show_results(results))
        except Exception as e:
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self._on_error(str(e)))

    def _on_error(self, err_msg):
        self.spinner.active = False
        self.btn_compare.disabled = False
        self.toolbar.title = "Error occurred"
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: setattr(self.toolbar, 'title', 'Compare Models'), 3)

    def _show_results(self, results):
        self.spinner.active = False
        self.btn_compare.disabled = False
        self.toolbar.title = "Compare Models"

        # Recommendations
        latency_data = {m: d['metrics']['duration_seconds'] for m, d in results.items()}
        energy_data = {m: d['metrics']['energy_joules'] for m, d in results.items()}
        eff_data = {m: d['metrics']['efficiency_score'] for m, d in results.items()}

        best_time = min(latency_data, key=latency_data.get)
        best_energy = min(energy_data, key=energy_data.get)
        best_eff = max(eff_data, key=eff_data.get)

        from widgets.model_card import ModelCard
        self.results_content.add_widget(ModelCard("🏆 Recommended Model", f"{best_eff} (Efficiency Score: {eff_data[best_eff]:.1f}/100)"))
        self.results_content.add_widget(ModelCard("⚡ Fastest Speed", f"{best_time} ({latency_data[best_time]:.3f} s)"))
        self.results_content.add_widget(ModelCard("🔋 Lowest Energy", f"{best_energy} ({energy_data[best_energy]:.4f} Joules)"))

        # Detailed Stats for each
        self.results_content.add_widget(MDLabel(text="Detailed Results", font_style="H6", bold=True, size_hint_y=None, height="40dp"))

        for m, d in results.items():
            metrics = d['metrics']
            res = d['res']
            desc = (
                f"Words: {res.input_word_count} -> {res.output_word_count} ({res.compression_ratio*100:.1f}%)\n"
                f"Time: {metrics['duration_seconds']:.3f} s | Energy: {metrics['energy_joules']:.4f} J\n"
                f"Carbon: {metrics['carbon_gco2e']:.5f} gCO2e | Data: {metrics['data_used_bytes']} bytes\n"
                f"Efficiency Score: {metrics['efficiency_score']:.1f}"
            )
            self.results_content.add_widget(ModelCard(m, desc))

        # Charts
        self.results_content.add_widget(MDLabel(text="Processing Time (Seconds)", font_style="Subtitle1", bold=True, size_hint_y=None, height="30dp"))
        self.results_content.add_widget(SimpleBarChart(data=latency_data))

        self.results_content.add_widget(MDLabel(text="Efficiency Score (0-100)", font_style="Subtitle1", bold=True, size_hint_y=None, height="30dp"))
        self.results_content.add_widget(SimpleBarChart(data=eff_data))
