from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.properties import StringProperty

class MapArea(Widget):
    pass  # Placeholder for map rendering

class ControlButton(Button):
    pass

class StatusLabel(Label):
    text = StringProperty("")

class GPSInterface(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # Main content area with map and side controls
        main_area = BoxLayout(orientation='horizontal', size_hint_y=0.85)

        # Left controls vertical box
        left_controls = BoxLayout(orientation='vertical', size_hint_x=0.1, spacing=10, padding=10)
        btn_zoom_in = Button(text='+', size_hint_y=None, height=50)
        btn_zoom_out = Button(text='-', size_hint_y=None, height=50)
        btn_3d = ToggleButton(text='3D', size_hint_y=None, height=50)
        btn_location = Button(text='Loc', size_hint_y=None, height=50)
        left_controls.add_widget(btn_zoom_in)
        left_controls.add_widget(btn_zoom_out)
        left_controls.add_widget(btn_3d)
        left_controls.add_widget(btn_location)

        # Map area
        map_area = MapArea(size_hint_x=0.8)

        # Right controls vertical box
        right_controls = BoxLayout(orientation='vertical', size_hint_x=0.1, padding=10)
        btn_pause = ToggleButton(text='Pause', size_hint_y=None, height=50)
        right_controls.add_widget(Widget())  # Spacer
        right_controls.add_widget(btn_pause)

        main_area.add_widget(left_controls)
        main_area.add_widget(map_area)
        main_area.add_widget(right_controls)

        # Bottom status bar
        status_bar = GridLayout(cols=5, size_hint_y=0.15, padding=10, spacing=10)
        self.status_area = StatusLabel(text="Area: -- ha")
        self.status_speed = StatusLabel(text="Speed: -- km/h")
        self.status_time = StatusLabel(text="Time: 00:00:00")
        self.status_gps = StatusLabel(text="GPS: --")
        self.status_pattern = StatusLabel(text="Pattern: --")

        status_bar.add_widget(self.status_area)
        status_bar.add_widget(self.status_speed)
        status_bar.add_widget(self.status_time)
        status_bar.add_widget(self.status_gps)
        status_bar.add_widget(self.status_pattern)

        self.add_widget(main_area)
        self.add_widget(status_bar)

class GPSApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        return GPSInterface()

if __name__ == '__main__':
    GPSApp().run()
