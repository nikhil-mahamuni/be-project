from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.spinner import MDSpinner
from kivy.utils import get_color_from_hex
from kivymd.uix.menu import MDDropdownMenu
from utils.constants import COLOR_PRIMARY_GREEN
from summarizers.factory import SummarizerFactory
from documents.text_cleaner import TextCleaner
import threading

class TextScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.name = "text_summary"
        self.app = app
        self.models = SummarizerFactory.get_available_models()
        self.selected_model = self.models[-1] if self.models else "Hybrid Green Mode"
        self.menu = None

        main_layout = MDBoxLayout(orientation="vertical")

        # Toolbar
        self.toolbar = MDTopAppBar(
            title="Summarize Text",
            anchor_title="left",
            md_bg_color=get_color_from_hex(COLOR_PRIMARY_GREEN),
            specific_text_color=get_color_from_hex("#ffffff"),
            left_action_items=[["arrow-left", lambda x: self.app.switch_screen("home")]]
        )
        main_layout.add_widget(self.toolbar)

        # Content
        content = MDBoxLayout(orientation="vertical", padding="16dp", spacing="16dp")

        self.text_input = MDTextField(
            hint_text="Paste your long text here...",
            mode="rectangle",
            multiline=True,
            size_hint_y=0.7
        )
        content.add_widget(self.text_input)

        # Controls Row
        controls_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="50dp", spacing="10dp")

        self.btn_model = MDFlatButton(
            text=f"Model: {self.selected_model}",
            size_hint_x=0.6,
            on_release=self.open_menu
        )
        controls_box.add_widget(self.btn_model)

        self.field_ratio = MDTextField(
            text=str(self.app.settings.get('default_ratio', '0.3')),
            hint_text="Ratio (0-1)",
            size_hint_x=0.4
        )
        controls_box.add_widget(self.field_ratio)

        content.add_widget(controls_box)

        # Summarize Button & Spinner
        action_box = MDBoxLayout(orientation="vertical", size_hint_y=None, height="80dp", spacing="10dp")

        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=("30dp", "30dp"),
            pos_hint={'center_x': .5},
            active=False
        )
        action_box.add_widget(self.spinner)

        self.btn_summarize = MDRaisedButton(
            text="Summarize Now",
            md_bg_color=get_color_from_hex(COLOR_PRIMARY_GREEN),
            pos_hint={"center_x": .5},
            size_hint_x=0.8,
            on_release=self.start_summarization
        )
        action_box.add_widget(self.btn_summarize)

        content.add_widget(action_box)
        main_layout.add_widget(content)
        self.add_widget(main_layout)

    def open_menu(self, instance):
        if not self.menu:
            menu_items = [
                {
                    "text": m,
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=m: self.menu_callback(x),
                } for m in self.models
            ]
            self.menu = MDDropdownMenu(
                caller=self.btn_model,
                items=menu_items,
                width_mult=4,
            )
        self.menu.open()

    def menu_callback(self, text_item):
        self.selected_model = text_item
        self.btn_model.text = f"Model: {self.selected_model}"
        self.menu.dismiss()

    def start_summarization(self, instance):
        raw_text = self.text_input.text
        if not raw_text.strip():
            self.toolbar.title = "Please enter some text."
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: setattr(self.toolbar, 'title', 'Summarize Text'), 2)
            return

        try:
            ratio = float(self.field_ratio.text)
            if ratio < 0.05: ratio = 0.05
            if ratio > 0.80: ratio = 0.80
        except ValueError:
            ratio = float(self.app.settings.get('default_ratio', '0.3'))

        self.field_ratio.text = f"{ratio:.2f}"

        self.btn_summarize.disabled = True
        self.spinner.active = True
        self.toolbar.title = "Processing..."

        # Run in thread to keep UI responsive
        threading.Thread(target=self._process_summarization, args=(raw_text, ratio)).start()

    def _process_summarization(self, raw_text, ratio):
        try:
            cleaned_text = TextCleaner.clean(raw_text)

            # Start profiler
            self.app.profiler.start()

            summarizer = SummarizerFactory.get_summarizer(self.selected_model)
            result = summarizer.summarize(cleaned_text, ratio)

            # Stop profiler
            batt_cap = float(self.app.settings.get('battery_capacity', '4000'))
            grid_fac = float(self.app.settings.get('grid_factor', '708.2'))
            metrics = self.app.profiler.stop(
                compression_ratio=result.compression_ratio,
                output_words=result.output_word_count,
                grid_factor=grid_fac,
                capacity_mah=batt_cap
            )
        except Exception as e:
            print(f"Error in summarization: {e}")
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self._on_error(str(e)))
            return

        # Save History
        from storage.models import HistoryEntry
        import time
        entry = HistoryEntry(
            id=None,
            created_at=time.time(),
            input_type='text',
            source_name='Pasted Text',
            model_name=result.model_name,
            input_word_count=result.input_word_count,
            output_word_count=result.output_word_count,
            compression_ratio=result.compression_ratio,
            summary_text=result.summary_text,
            duration_seconds=metrics['duration_seconds'],
            data_used_bytes=metrics['data_used_bytes'],
            battery_delta_percent=metrics['battery_delta_percent'],
            energy_joules=metrics['energy_joules'],
            energy_wh=metrics['energy_wh'],
            carbon_gco2e=metrics['carbon_gco2e'],
            efficiency_score=metrics['efficiency_score']
        )
        self.app.db.add_history(entry)

        # Schedule UI update
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._on_summarization_complete(result, metrics))

    def _on_error(self, err_msg):
        self.spinner.active = False
        self.btn_summarize.disabled = False
        self.toolbar.title = "Error occurred."
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: setattr(self.toolbar, 'title', 'Summarize Text'), 3)

    def _on_summarization_complete(self, result, metrics):
        self.spinner.active = False
        self.btn_summarize.disabled = False
        self.toolbar.title = "Summarize Text"

        # Pass data to result screen
        self.app.screens['result'].show_result(result, metrics)
        self.app.switch_screen("result")
