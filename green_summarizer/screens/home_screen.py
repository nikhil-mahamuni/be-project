from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex
from kivymd.uix.card import MDCard
from utils.constants import COLOR_PRIMARY_GREEN

class NavigationCard(MDCard):
    def __init__(self, title, subtitle, target_screen, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.target_screen = target_screen
        self.orientation = "vertical"
        self.padding = "16dp"
        self.size_hint_y = None
        self.height = "100dp"
        self.elevation = 2
        self.radius = [12, 12, 12, 12]
        self.md_bg_color = get_color_from_hex("#ffffff")

        lbl_title = MDLabel(
            text=title,
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLOR_PRIMARY_GREEN),
            font_style="H6",
            bold=True
        )
        lbl_subtitle = MDLabel(
            text=subtitle,
            theme_text_color="Secondary",
            font_style="Caption"
        )
        self.add_widget(lbl_title)
        self.add_widget(lbl_subtitle)

    def on_release(self):
        self.app.switch_screen(self.target_screen)

class HomeScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.name = "home"
        self.app = app

        layout = MDBoxLayout(orientation="vertical", padding="16dp", spacing="16dp")

        # Header
        header_box = MDBoxLayout(orientation="vertical", size_hint_y=None, height="120dp", spacing="8dp")
        header_title = MDLabel(
            text="GreenSummarizer",
            font_style="H4",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLOR_PRIMARY_GREEN),
            bold=True,
            halign="center"
        )
        header_subtitle = MDLabel(
            text="Offline AI Text & PDF Summarizer",
            font_style="Subtitle1",
            theme_text_color="Secondary",
            halign="center"
        )
        header_box.add_widget(header_title)
        header_box.add_widget(header_subtitle)

        # Cards
        cards_layout = MDBoxLayout(orientation="vertical", spacing="12dp", size_hint_y=None)
        cards_layout.bind(minimum_height=cards_layout.setter('height'))

        cards_layout.add_widget(NavigationCard("Summarize Text", "Paste or type text", "text_summary", app))
        cards_layout.add_widget(NavigationCard("Summarize PDF", "Extract from documents", "pdf_summary", app))
        cards_layout.add_widget(NavigationCard("Compare Models", "Test efficiency and speed", "compare", app))
        cards_layout.add_widget(NavigationCard("Green Analytics", "View your energy savings", "analytics", app))
        cards_layout.add_widget(NavigationCard("History", "Previous summaries", "history", app))

        # Settings button at bottom
        btn_settings = MDFlatButton(
            text="Settings",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLOR_PRIMARY_GREEN),
            pos_hint={"center_x": .5}
        )
        btn_settings.bind(on_release=lambda x: self.app.switch_screen("settings"))

        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(size_hint=(1, 1))
        scroll_content = MDBoxLayout(orientation="vertical", spacing="16dp", size_hint_y=None)
        scroll_content.bind(minimum_height=scroll_content.setter('height'))

        scroll_content.add_widget(header_box)
        scroll_content.add_widget(cards_layout)
        scroll_content.add_widget(btn_settings)

        scroll.add_widget(scroll_content)
        layout.add_widget(scroll)

        self.add_widget(layout)
