import cv2
import numpy as np
import winsound
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.uix.filechooser import FileChooser
from kivy.uix.image import Image
from kivy.graphics.texture import Texture

class LaneDetectionApp(App):
    def build(self):
        # Create the widgets
        self.camera = Camera(resolution=(640, 480), play=True)
        self.file_chooser = FileChooser()
        self.detect_button = Button(text='Detect', size_hint=(1, 0.1))
        self.detect_button.bind(on_press=self.detect_lane)
        self.choose_file_button = Button(text='Choose File', size_hint=(1, 0.1))
        self.choose_file_button.bind(on_press=self.choose_file)
        self.image_widget = Image()

        # Create the layout and add the widgets
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.camera)
        button_layout = BoxLayout(size_hint=(1, 0.1))
        button_layout.add_widget(self.detect_button)
        button_layout.add_widget(self.choose_file_button)
        layout.add_widget(button_layout)
        layout.add_widget(self.file_chooser)
        layout.add_widget(self.image_widget)

        return layout

    def choose_file(self, instance):
        self.file_chooser.path = './OPENCV/test.mp4'
        self.file_chooser.filters = ['*.mp4']
        self.file_chooser.selection_mode = 'single'
        self.file_chooser.show_hidden = False
        self.file_chooser.bind(on_selection=self.file_selected)

    def file_selected(self, chooser, selection):
        self.video_file_path = selection[0]

    def detect_lane(self, instance):
        # Open the video file
        cap = cv2.VideoCapture(self.video_file_path)

        while(cap.isOpened()):
            ret, frame = cap.read()
            canny_image = self.canny(frame)
            cropped_img = self.region_of_interest(canny_image)
            # detect lines using HoughLine method
            lines = cv2.HoughLinesP(cropped_img, 2, np.pi/180, 100, np.array([]), minLineLength=40, maxLineGap=5)
            averaged_lines = self.average_slope_intercept(frame,lines)
            line_img = self.display_lines(frame, averaged_lines)
            combo_img = cv2.addWeighted(frame, 0.8, line_img, 1, 1)
            self.display_image(combo_img)

            height, width, _ = frame.shape
            self.beep_sound(averaged_lines, height, width)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()

    def canny(self, img):
        # convert the frame into grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        # Apply GaussianBlur to the grayscale frame
        blur = cv2.GaussianBlur(gray, (5 ,5), 0)
        canny = cv2.Canny(blur, 50, 150)
        return canny

    def region_of_interest(self, img):
        height = img.shape[0]
        polygons = np.array([
            [(200, height), (1100, height), (550, 250)]
        ])
        mask = np.zeros_like(img)
        cv2.fillPoly(mask, polygons, 255)
        masked_img = cv2.bitwise_and(img, mask)
        return masked_img

    def display_lines(self, img, lines):
        line_img = np.zeros_like(img)
        if lines is not None:
            for x1, y1, x2, y2 in lines:
                cv2.line(line_img, (x1, y1), (x2, y2), (255, 0, 0), 10)
            return line_img

    def average_slope_intercept(self, img, lines):
        left_fit = []
        right_fit = []
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            parameters = np.polyfit((x1, x2), (y1, y2), 1)
            slope = parameters[0]
            y_intercept = parameters[1]
            if slope < 0:
                left_fit.append((slope, y_intercept))
            else:
                right_fit.append((slope, y_intercept))

        left_fit_average = np.average(left_fit, axis=0)
        right_fit_average = np.average(right_fit, axis=0)

        left_line = self.make_coordinates(img, left_fit_average)
        right_line = self.make_coordinates(img, right_fit_average)

        return np.array([left_line, right_line])

def make_coordinates(self, img, line_parameters):
    slope, intercept = line_parameters
    y1 = img.shape[0]
    y2 = int(y1*(3/5))
    x1 = int((y1 - intercept)/slope)
    x2 = int((y2 - intercept)/slope)
    return np.array([x1, y1, x2, y2])

def display_image(self, img):
    # Convert the image to texture
    texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='bgr')
    texture.blit_buffer(img.tobytes(), colorfmt='bgr', bufferfmt='ubyte')
    self.image_widget.texture = texture

def beep_sound(self, lines, height, width):
    if lines is not None:
        left_line, right_line = lines
        left_slope, left_intercept = left_line
        right_slope, right_intercept = right_line
        mid = int(width / 2)
        left_x = int((height - left_intercept) / left_slope)
        right_x = int((height - right_intercept) / right_slope)
        avg_x = int((left_x + right_x) / 2)
        # Calculate the distance between the center of the frame and the midpoint of the two lanes
        distance = mid - avg_x
        # If the distance is negative, the car is on the left side of the lane, and if it is positive, the car is on the right side of the lane
        if distance < 0:
            frequency = 600
        else:
            frequency = 800
        duration = abs(distance) // 2  # Set the duration based on the distance
        winsound.Beep(frequency, duration)

# class LaneDetectionApp(App):
#     def build(self):
#         return LaneDetectionUI()


if __name__ == '__main__':
   LaneDetectionApp().run()


