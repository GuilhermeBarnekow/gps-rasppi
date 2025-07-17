from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.graphics import Color, Rectangle, Triangle
from kivy.clock import Clock

from gnss_controller import GNSSController

class MapArea(Widget):
    path_points = ListProperty([])  # List of (x, y) points where the triangle has passed
    triangle_pos = ListProperty([0, 0])  # Current triangle position
    triangle_size = ListProperty([0, 0])  # Size of the triangle
    implement_width = NumericProperty(10)  # largura do implemento em metros (default 10)
    zoom_level = NumericProperty(1.0)  # zoom do mapa, 1.0 = 100%

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas, path_points=self.update_canvas, triangle_pos=self.update_canvas, implement_width=self.update_canvas, zoom_level=self.update_canvas)
        self.triangle_size = [self.width * 0.1, self.height * 0.1]

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Draw terrain areas (initially empty, will fill blue where passed)
            # Draw green area as default
            Color(0.3, 0.6, 0.3, 1)  # green
            Rectangle(pos=self.pos, size=self.size)

            # Draw blue path where triangle has passed, projetado linearmente com base na largura do implemento e zoom
            Color(0.2, 0.4, 0.8, 1)  # blue
            half_width = (self.implement_width / 2) * self.zoom_level
            for point in self.path_points:
                # Desenhar retângulo azul com largura proporcional ao implemento
                size = (half_width, half_width * 2)
                Rectangle(pos=(point[0] - size[0]/2, point[1] - size[1]/2), size=size)

            # Draw yellow navigation triangle at current position
            Color(1, 1, 0, 1)  # yellow
            cx, cy = self.triangle_pos
            size = min(self.width, self.height) * 0.1 * self.zoom_level
            points = [
                (cx, cy + size),
                (cx - size * 0.6, cy - size * 0.6),
                (cx + size * 0.6, cy - size * 0.6)
            ]
            Triangle(points=[p for point in points for p in point])

class ControlButton(Button):
    pass

class StatusLabel(Label):
    text = StringProperty("")

class GPSInterface(BoxLayout):
    gnss_controller = None
    connected = BooleanProperty(False)
    implement_width = NumericProperty(10)
    zoom_level = NumericProperty(1.0)
    running = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # Set window to fullscreen - use 'auto' but fallback to False if issues
        try:
            Window.fullscreen = 'auto'
        except Exception:
            Window.fullscreen = False

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
        self.map_area = MapArea(size_hint_x=0.8)

        # Right controls vertical box
        right_controls = BoxLayout(orientation='vertical', size_hint_x=0.1, padding=10)
        btn_start = Button(text='Iniciar', size_hint_y=None, height=50)
        btn_pause = ToggleButton(text='Pause', size_hint_y=None, height=50)
        right_controls.add_widget(btn_start)
        right_controls.add_widget(Widget())  # Spacer
        right_controls.add_widget(btn_pause)

        main_area.add_widget(left_controls)
        main_area.add_widget(self.map_area)
        main_area.add_widget(right_controls)

        # Bottom controls for implement width input
        bottom_controls = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=10, spacing=10)
        lbl_width = Label(text="Largura do Implemento (m):", size_hint_x=None, width=180)
        self.input_width = TextInput(text=str(self.implement_width), multiline=False, input_filter='float', size_hint_x=None, width=100)
        bottom_controls.add_widget(lbl_width)
        bottom_controls.add_widget(self.input_width)

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
        self.add_widget(bottom_controls)
        self.add_widget(status_bar)

        # Initialize GNSS controller
        self.gnss_controller = GNSSController()

        # Bind button events
        btn_start.bind(on_press=self.start_tracking)
        btn_pause.bind(on_press=self.toggle_pause)
        btn_zoom_in.bind(on_press=self.zoom_in)
        btn_zoom_out.bind(on_press=self.zoom_out)
        self.input_width.bind(text=self.on_width_change)

        # Schedule periodic UI updates
        Clock.schedule_interval(self.update_ui, 1.0)

    def start_tracking(self, instance):
        if not self.running:
            self.gnss_controller.start()
            self.running = True

    def toggle_pause(self, instance):
        if self.running:
            if instance.state == 'down':
                self.gnss_controller.stop()
                self.running = False
            else:
                self.gnss_controller.start()
                self.running = True

    def zoom_in(self, instance):
        self.zoom_level = min(self.zoom_level + 0.1, 3.0)
        self.map_area.zoom_level = self.zoom_level

    def zoom_out(self, instance):
        self.zoom_level = max(self.zoom_level - 0.1, 0.5)
        self.map_area.zoom_level = self.zoom_level

    def on_width_change(self, instance, value):
        try:
            width = float(value)
            if width > 0:
                self.implement_width = width
                self.map_area.implement_width = width
        except ValueError:
            pass

    def update_ui(self, dt):
        # Update connection status
        connected = self.gnss_controller.is_connected()
        self.connected = connected
        self.status_gps.text = "GPS: " + ("Conectado" if connected else "Desconectado")

        # Update triangle position and path if connected and position available
        pos = self.gnss_controller.get_position()
        if pos and self.running:
            lat, lon = pos[0], pos[1]
            # Convert lat/lon to widget coordinates constrained to green terrain area (right half)
            terrain_x_start = self.map_area.x + self.map_area.width * 0.5
            terrain_width = self.map_area.width * 0.5
            x = terrain_x_start + (lon + 180) / 360 * terrain_width
            y = self.map_area.y + (lat + 90) / 180 * self.map_area.height

            # Clamp x and y to stay within terrain rectangle
            x = max(terrain_x_start, min(x, terrain_x_start + terrain_width))
            y = max(self.map_area.y, min(y, self.map_area.y + self.map_area.height))

            # Update triangle position
            self.map_area.triangle_pos = [x, y]

            # Add to path points if not already close
            if not self.map_area.path_points or self.distance(self.map_area.path_points[-1], (x, y)) > 10:
                self.map_area.path_points.append((x, y))
        else:
            # No position or not running, keep triangle in center
            self.map_area.triangle_pos = [self.map_area.center_x, self.map_area.center_y]

    def distance(self, p1, p2):
        return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

class GPSApp(App):
    def build(self):
        # Set a lighter background color for better visibility
        Window.clearcolor = (0.15, 0.15, 0.15, 1)
        return GPSInterface()

if __name__ == '__main__':
    GPSApp().run()

class ControlButton(Button):
    pass

class StatusLabel(Label):
    text = StringProperty("")

class GPSInterface(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # Set window to fullscreen - use 'auto' but fallback to False if issues
        try:
            Window.fullscreen = 'auto'
        except Exception:
            Window.fullscreen = False

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
        # Set a lighter background color for better visibility
        Window.clearcolor = (0.15, 0.15, 0.15, 1)
        return GPSInterface()

if __name__ == '__main__':
    GPSApp().run()
