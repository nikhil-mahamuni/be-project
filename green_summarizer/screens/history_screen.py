from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton
from utils.constants import COLOR_PRIMARY_GREEN, COLOR_LIGHT_GREEN
import datetime

class HistoryCard(MDCard):
    def __init__(self, entry, app, parent_screen, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.entry = entry
        self.parent_screen = parent_screen
        self.orientation = "vertical"
        self.padding = "10dp"
        self.size_hint_y = None
        self.height = "120dp"
        self.elevation = 1
        self.radius = [8, 8, 8, 8]

        top_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="30dp")

        dt_str = datetime.datetime.fromtimestamp(entry.created_at).strftime("%Y-%m-%d %H:%M")
        lbl_date = MDLabel(text=dt_str, font_style="Caption", theme_text_color="Secondary", size_hint_x=0.8)

        btn_del = MDIconButton(icon="delete", theme_text_color="Error", size_hint_x=0.2, pos_hint={'center_y': 0.5})
        btn_del.bind(on_release=self.delete_entry)

        top_row.add_widget(lbl_date)
        top_row.add_widget(btn_del)

        lbl_source = MDLabel(text=f"Source: {entry.source_name} ({entry.model_name})", font_style="Subtitle2", bold=True)
        lbl_preview = MDLabel(text=entry.summary_text.replace('\n', ' ')[:100] + "...", font_style="Body2", theme_text_color="Secondary")

        self.add_widget(top_row)
        self.add_widget(lbl_source)
        self.add_widget(lbl_preview)

    def delete_entry(self, instance):
        self.app.db.delete_history(self.entry.id)
        self.parent_screen.refresh()

    def on_release(self):
        from storage.models import SummaryResult
        # Reconstruct a SummaryResult object to pass to the ResultScreen
        result = SummaryResult(
            summary_text=self.entry.summary_text,
            model_name=self.entry.model_name,
            input_word_count=self.entry.input_word_count,
            output_word_count=self.entry.output_word_count,
            compression_ratio=self.entry.compression_ratio,
            sentence_count=0, # not saved in history explicitly, but 0 is fine
            keywords=[],
            processing_time_seconds=self.entry.duration_seconds
        )

        metrics = {
            'duration_seconds': self.entry.duration_seconds,
            'data_used_bytes': self.entry.data_used_bytes,
            'battery_delta_percent': self.entry.battery_delta_percent,
            'energy_joules': self.entry.energy_joules,
            'energy_wh': self.entry.energy_wh,
            'carbon_gco2e': self.entry.carbon_gco2e,
            'efficiency_score': self.entry.efficiency_score,
            'is_estimated': True
        }

        self.app.screens['result'].show_result(result, metrics)
        self.app.switch_screen("result")

class HistoryScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.name = "history"
        self.app = app

        main_layout = MDBoxLayout(orientation="vertical")

        self.toolbar = MDTopAppBar(
            title="History",
            anchor_title="left",
            md_bg_color=get_color_from_hex(COLOR_PRIMARY_GREEN),
            specific_text_color=get_color_from_hex("#ffffff"),
            left_action_items=[["arrow-left", lambda x: self.app.switch_screen("home")]]
        )
        main_layout.add_widget(self.toolbar)

        from kivy.uix.scrollview import ScrollView
        self.scroll = ScrollView(size_hint=(1, 1))
        self.content = MDBoxLayout(orientation="vertical", padding="16dp", spacing="10dp", size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter('height'))

        self.scroll.add_widget(self.content)
        main_layout.add_widget(self.scroll)
        self.add_widget(main_layout)

    def on_enter(self):
        self.refresh()

    def refresh(self):
        self.content.clear_widgets()
        history = self.app.db.get_all_history()

        if not history:
            self.content.add_widget(MDLabel(text="No history found.", halign="center"))
            return

        for entry in history:
            self.content.add_widget(HistoryCard(entry, self.app, self))
