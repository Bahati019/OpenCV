import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.uix.image import Image

class CameraApp(App):
    def build(self):
        # Create a BoxLayout to hold the camera and button widgets
        box = BoxLayout(orientation='horizontal')
        
        # Create a Camera widget
        self.camera = Camera(resolution=(640, 480), play=True)
        
        # Create a Button widget with a plus icon
        self.button = Button(text='+', font_size=20, size_hint=(0.1, 0.1), pos_hint={'x': 0.45, 'y': 0.45})
        self.button.bind(on_press=self.capture_image)
        
        # Add the Camera and Button widgets to the BoxLayout
        box.add_widget(self.camera)
        box.add_widget(self.button)
        
        return box
    
    def capture_image(self, *args):
        # Take a picture with the Camera and display it as an Image widget
        self.camera.export_to_png('capture.png')
        self.img = Image(source='capture.png')
        self.camera.play = False
        
        # Clear the BoxLayout and add the Image widget
        self.root.clear_widgets()
        self.root.add_widget(self.img)

if __name__ == '__main__':
    CameraApp().run()
