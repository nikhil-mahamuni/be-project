from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.utils import get_color_from_hex
from utils.constants import COLOR_PRIMARY_GREEN

class MetricCard(MDCard):
    def __init__(self, title: str, value: str, icon: str, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = "16dp"
        self.size_hint = (1, None)
        self.height = "100dp"
        self.elevation = 1
        self.radius = [12, 12, 12, 12]
        self.md_bg_color = get_color_from_hex("#ffffff")

        # Top row with icon and title
        top_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="30dp")

        lbl_title = MDLabel(
            text=title,
            theme_text_color="Hint",
            font_style="Caption",
            halign="left"
        )

        # Could use MDIcon here if we had full MD icons loaded, for now we use text

        top_box.add_widget(lbl_title)

        # Value
        lbl_val = MDLabel(
            text=value,
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLOR_PRIMARY_GREEN),
            font_style="H6",
            bold=True,
            halign="left"
        )

        self.add_widget(top_box)
        self.add_widget(lbl_val)
