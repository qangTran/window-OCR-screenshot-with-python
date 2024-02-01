import cv2
import numpy as np
import pyautogui
import win32con
import win32gui


class Cropper:
    def __init__(self):
        self.img = None
        self.cropped = False
        self.canvas_img = None
        self.start = (-1, -1)
        self.end = (-1, -1)

    def get_image_from_screen(self):
        """ Capture a screenshot, cropping, and return the cropped image. """
        self.capture_screen()
        self.get_range_for_cropping()
        return self.crop_image()

    def capture_screen(self):
        """ Capture a screenshot and store it for cropping. """
        self.img = pyautogui.screenshot().convert('RGB')
        self.img = cv2.cvtColor(np.array(self.img), cv2.COLOR_RGB2BGR)
        self.canvas_img = np.copy(self.img)

    def get_range_for_cropping(self):
        """ Set up the window for cropping. """
        cv2.namedWindow("Snip Window", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(
            "Snip Window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        hWnd = win32gui.FindWindow(None, 'Snip Window')
        cv2.setMouseCallback('Snip Window', self.draw_rectangle_callback)
        win32gui.SetWindowPos(hWnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_SHOWWINDOW | win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)

        while not self.cropped:
            cv2.imshow('Snip Window', self.canvas_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
        self.cropped = False  # reset the flag

    def draw_rectangle_callback(self, event, x, y, flags, _):
        """ Handle the drawing of the rectangle on mouse events. """

        # ! Note: Due to potential conflicts with pynput or pystray libraries, cv2 is unable to detect the mouse button down event.
        # As a workaround, I've implemented a mechanism that captures the event when the mouse button is pressed and moved.
        # if event != 0:
        #     print(f"Event: {event}, Coordinates: ({x}, {y}), Flags: {flags}")

        # if event == cv2.EVENT_LBUTTONDOWN:
        #     self.start = (x, y)
        #     print(f"Left button down at {self.start}")

        if event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
            if self.start == (-1, -1):
                self.start = (x, y)
            self.canvas_img = np.copy(self.img)
            cv2.rectangle(self.canvas_img, self.start, (x, y), (0, 255, 0), 1)
        elif event == cv2.EVENT_LBUTTONUP:
            self.end = (x, y)
            self.cropped = True

    def crop_image(self):
        """ Return the cropped portion of the image. """

        # Ensure coordinates are in the correct order
        start_x, end_x = sorted([self.start[0], self.end[0]])
        start_y, end_y = sorted([self.start[1], self.end[1]])

        # Check if the coordinates define a valid area
        if start_x != end_x and start_y != end_y:
            return self.img[start_y:end_y, start_x:end_x]
        else:
            return None


if __name__ == "__main__":
    # for test
    cropper = Cropper()
    cropped_img = cropper.get_image_from_screen()
    if cropped_img is not None:
        cv2.imwrite("cropped_image.png", cropped_img)
