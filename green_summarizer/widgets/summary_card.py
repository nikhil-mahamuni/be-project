from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex
from utils.constants import COLOR_PRIMARY_GREEN

class SummaryCard(MDCard):
    def __init__(self, summary_text: str, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = "16dp"
        self.size_hint_y = None
        self.elevation = 1
        self.radius = [10, 10, 10, 10]
        self.md_bg_color = get_color_from_hex("#ffffff")

        lbl = MDLabel(
            text=summary_text,
            theme_text_color="Primary",
            font_style="Body1",
            size_hint_y=None
        )
        lbl.bind(texture_size=lbl.setter('size'))

        # Calculate height dynamically based on label texture size approximation
        # For a more robust app we would use ScrollView + dynamic height
        approx_lines = len(summary_text) / 40 + summary_text.count('\n')
        self.height = f"{max(100, int(approx_lines * 24 + 32))}dp"

        self.add_widget(lbl)
