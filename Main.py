import cv2
import numpy as np
import winsound
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
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
            text: 'Choose Video'
            on_release:
                root.choose_video()
        Button:
            text: 'Quit'
            on_release: app.stop()
    Image:
        id: camera_preview
        allow_stretch: True
        keep_ratio: False
""")


def region_of_interest(img):
    height = img.shape[0]
    polygons = np.array([
        [(200, height), (1100, height), (550, 250)]
    ])
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, polygons, 255)
    masked_img = cv2.bitwise_and(img, mask)
    return masked_img

class LaneDetectionUI(BoxLayout):
    camera_preview = ObjectProperty(None)

    def choose_video(self):
        filechooser = FileChooserListView()
        filechooser.bind(selection=self.play_video)
        self.add_widget(filechooser)

    def play_video(self, instance, selection):
        if selection:
            video_path = selection[0]
            self.cap = cv2.VideoCapture(video_path)
            Clock.schedule_interval(self.update_frame, 1.0/30.0)
            self.remove_widget(instance)

    def __init__(self, **kwargs):
        super(LaneDetectionUI, self).__init__(**kwargs)
        self.cap = None
        self.lines = []
        self.beep = False


    def detect_lanes(self, start_detection):
        if start_detection:
            if self.cap is None:
                self.cap = cv2.VideoCapture(0)
            Clock.schedule_interval(self.update_frame, 1.0/30.0)
        else:
            Clock.unschedule(self.update_frame)
            if self.cap is not None:
                self.cap.release()
            self.cap = None


    def update_frame(self, dt):
        ret, frame = self.cap.read()
        if not ret:
            return

        width = frame.shape[1]

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to the grayscale image
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # Detect edges using Canny edge detection algorithm
        edges = cv2.Canny(blur, 50, 150)

        # Create a mask for the edges image
        masked_edges = region_of_interest(edges)

        # Find lines using Hough transform
        lines = cv2.HoughLinesP(masked_edges, 2, np.pi/180, 100, np.array([]), minLineLength=40, maxLineGap=2)

        # If lines are found, draw them on the original frame
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if (x1 + x2) / 2 > width / 2 + 50 or (x1 + x2) / 2 < width / 2 - 50:
                    self.beep = True
                    cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 10)

        # Play beep sound if lane departure is detected
        if self.beep:
            winsound.Beep(1000, 500)

        # Update the camera preview
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        image_texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.camera_preview.texture = image_texture


class LaneDetectionApp(App):
    def build(self):
        return LaneDetectionUI()


if __name__ == '__main__':
   LaneDetectionApp().run()
