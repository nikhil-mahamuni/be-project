from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex
from utils.constants import COLOR_PRIMARY_GREEN, COLOR_LIGHT_GREEN

class ModelCard(MDCard):
    def __init__(self, model_name: str, desc: str, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = "16dp"
        self.size_hint_y = None
        self.height = "120dp"
        self.elevation = 2
        self.radius = [15, 15, 15, 15]
        self.md_bg_color = get_color_from_hex(COLOR_LIGHT_GREEN)

        lbl_name = MDLabel(
            text=model_name,
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLOR_PRIMARY_GREEN),
            font_style="Subtitle1",
            bold=True,
            size_hint_y=None,
            height="30dp"
        )

        lbl_desc = MDLabel(
            text=desc,
            theme_text_color="Secondary",
            font_style="Caption"
        )

        self.add_widget(lbl_name)
        self.add_widget(lbl_desc)
