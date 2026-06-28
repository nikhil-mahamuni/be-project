from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex
from utils.constants import COLOR_PRIMARY_GREEN

class SimpleBarChart(MDBoxLayout):
    def __init__(self, data: dict, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "10dp"
        self.padding = "10dp"
        self.size_hint_y = None
        self.height = f"{len(data) * 50 + 40}dp"

        if not data:
            self.add_widget(MDLabel(text="No data available", halign="center"))
            return

        max_val = max(data.values()) if max(data.values()) > 0 else 1

        for key, val in data.items():
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="40dp", spacing="10dp")

            lbl_key = MDLabel(text=str(key), size_hint_x=0.4, halign="right", font_style="Caption")

            bar_container = MDBoxLayout(size_hint_x=0.6)

            # Custom drawing for bar
            class Bar(Widget):
                def __init__(self, width_pct, **kwargs):
                    super().__init__(**kwargs)
                    self.width_pct = width_pct
                    self.bind(pos=self.update_canvas, size=self.update_canvas)

                def update_canvas(self, *args):
                    self.canvas.clear()
                    with self.canvas:
                        Color(*get_color_from_hex(COLOR_PRIMARY_GREEN))
                        Rectangle(pos=(self.x, self.y + self.height*0.25), size=(self.width * self.width_pct, self.height*0.5))

            width_pct = val / max_val
            bar = Bar(width_pct=width_pct)

            bar_container.add_widget(bar)

            lbl_val = MDLabel(text=f"{val:.2f}", size_hint_x=0.3, font_style="Caption")

            row.add_widget(lbl_key)
            row.add_widget(bar_container)
            row.add_widget(lbl_val)

            self.add_widget(row)
