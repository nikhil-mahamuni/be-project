from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex
from kivymd.uix.toolbar import MDTopAppBar
from utils.constants import COLOR_PRIMARY_GREEN
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

class SettingsScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings"
        self.app = app
        self.dialog = None

        main_layout = MDBoxLayout(orientation="vertical")

        # Toolbar
        self.toolbar = MDTopAppBar(
            title="Settings",
            anchor_title="left",
            md_bg_color=get_color_from_hex(COLOR_PRIMARY_GREEN),
            specific_text_color=get_color_from_hex("#ffffff"),
            left_action_items=[["arrow-left", lambda x: self.app.switch_screen("home")]]
        )
        main_layout.add_widget(self.toolbar)

        # Content
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(size_hint=(1, 1))
        content = MDBoxLayout(orientation="vertical", padding="20dp", spacing="20dp", size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        # Default Ratio
        ratio_box = MDBoxLayout(orientation="vertical", size_hint_y=None, height="70dp")
        ratio_box.add_widget(MDLabel(text="Default Summary Ratio (0.1 - 0.9)", font_style="Subtitle2"))
        self.field_ratio = MDTextField(text=str(self.app.settings.get('default_ratio', '0.3')))
        ratio_box.add_widget(self.field_ratio)
        content.add_widget(ratio_box)

        # Battery Capacity
        batt_box = MDBoxLayout(orientation="vertical", size_hint_y=None, height="70dp")
        batt_box.add_widget(MDLabel(text="Battery Capacity (mAh)", font_style="Subtitle2"))
        self.field_batt = MDTextField(text=str(self.app.settings.get('battery_capacity', '4000')))
        batt_box.add_widget(self.field_batt)
        content.add_widget(batt_box)

        # Grid Factor
        grid_box = MDBoxLayout(orientation="vertical", size_hint_y=None, height="70dp")
        grid_box.add_widget(MDLabel(text="Grid Carbon Factor (gCO₂e/kWh)", font_style="Subtitle2"))
        self.field_grid = MDTextField(text=str(self.app.settings.get('grid_factor', '708.2')))
        grid_box.add_widget(self.field_grid)
        content.add_widget(grid_box)

        # Save Button
        btn_save = MDRaisedButton(
            text="Save Settings",
            md_bg_color=get_color_from_hex(COLOR_PRIMARY_GREEN),
            pos_hint={"center_x": .5}
        )
        btn_save.bind(on_release=self.save_settings)
        content.add_widget(btn_save)

        # Clear History Button
        btn_clear = MDFlatButton(
            text="Clear All History",
            theme_text_color="Error",
            pos_hint={"center_x": .5}
        )
        btn_clear.bind(on_release=self.show_clear_dialog)
        content.add_widget(btn_clear)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def save_settings(self, instance):
        try:
            ratio = float(self.field_ratio.text)
            if ratio < 0.05: ratio = 0.05
            if ratio > 0.8: ratio = 0.8
            self.field_ratio.text = f"{ratio:.2f}"

            batt = float(self.field_batt.text)
            if batt <= 0: batt = 4000.0
            self.field_batt.text = str(batt)

            grid = float(self.field_grid.text)
            if grid < 0: grid = 708.2
            self.field_grid.text = str(grid)

            self.app.settings.set('default_ratio', str(ratio))
            self.app.settings.set('battery_capacity', str(batt))
            self.app.settings.set('grid_factor', str(grid))

            # Show toast or simple label
            self.toolbar.title = "Settings Saved!"
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: setattr(self.toolbar, 'title', 'Settings'), 2)

        except ValueError:
            self.toolbar.title = "Invalid input format"
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: setattr(self.toolbar, 'title', 'Settings'), 2)

    def show_clear_dialog(self, instance):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Clear History?",
                text="This will delete all saved summaries and analytics.",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="CLEAR",
                        theme_text_color="Error",
                        on_release=self.clear_history
                    ),
                ],
            )
        self.dialog.open()

    def clear_history(self, instance):
        self.app.db.clear_all_history()
        self.dialog.dismiss()
        self.toolbar.title = "History Cleared!"
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: setattr(self.toolbar, 'title', 'Settings'), 2)
