import cv2
import numpy as np
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty


# Load the Kivy UI definition file
Builder.load_string("""
<LaneDetectionUI>:
    orientation: 'vertical'
    camera_preview: camera_preview
    BoxLayout:
        size_hint_y: None
        height: '48dp'
        ToggleButton:
            text: 'Start Detection'
            on_state:
                root.detect_lanes(self.state == 'down')
        Button:
            text: 'Quit'
            on_release: app.stop()
    Image:
        id: camera_preview
        allow_stretch: True
        keep_ratio: False
""")

class LaneDetectionUI(BoxLayout):
    camera_preview = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cap = cv2.VideoCapture(0)  # Open the default camera
        self.lines = []

    def detect_lanes(self, start_detection):
        if start_detection:
            Clock.schedule_interval(self.update_frame, 1/60.)  # Call update_frame() 60 times per second
        else:
            Clock.unschedule(self.update_frame)

    def update_frame(self, dt):
        ret, frame = self.cap.read()  # Capture a frame from the camera
        if not ret:
            return

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to the grayscale image
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # Detect edges using Canny edge detection algorithm
        edges = cv2.Canny(blur, 50, 150)

        # Create a mask for the edges image
        mask = np.zeros_like(edges)
        mask.fill(255)
        height, width = frame.shape[:2]
        vertices = np.array([[(0, height), (width/2, height/2), (width, height)]], dtype=np.int32)
        cv2.fillPoly(mask, vertices, 0)
        masked_edges = cv2.bitwise_and(edges, mask)

        # Detect lines using Hough transform
        self.lines = cv2.HoughLinesP(masked_edges, rho=1, theta=np.pi/180, threshold=20, minLineLength=40, maxLineGap=5)
        if self.lines is not None:
            for line in self.lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 10)



        # Convert the frame to a texture and display it in the Kivy UI
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.camera_preview.texture = texture

class LaneDetectionApp(App):
    def build(self):
        return LaneDetectionUI()


if __name__ == '__main__':
   LaneDetectionApp().run()
