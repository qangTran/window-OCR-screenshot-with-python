import os

import cv2
import easyocr
import numpy as np
import pyautogui  # take a screenshot
import torch
import win32con
import win32gui
from screeninfo import get_monitors

reader = easyocr.Reader(['vi', 'en'], gpu=torch.cuda.is_available(), verbose=False)


def get_screen_info() -> tuple:
    si = get_monitors()[0]
    screen_width = si.width
    screen_height = si.height
    return screen_width, screen_height


class Cropper:

    def __init__(self, img):
        self.ratio = 1.0  # saved ratio after cut
        self.screen_width, self.screen_height = get_screen_info()
        self.img = img
        height, width, _ = self.img.shape
        self.cropped = False

        # resize the img to fit the current user screen
        if width / self.screen_width > self.ratio or height / self.screen_height > self.ratio:
            self.img = cv2.resize(self.img, None, fx=self.ratio, fy=self.ratio)
        else:
            self.ratio = 1.0

        self.canvas_img = np.copy(self.img)

        self.start = (-1, -1)  # for hold start pointer position
        self.end = (-1, -1)  # for hold end pointer position
        self.roi = (-1, -1)  # for handle moving the crop window

        self.get_range_for_cropping()

    def get_start_end(self):
        start_x, start_y = self.start
        end_x, end_y = self.end
        return (int(start_x // self.ratio), int(start_y // self.ratio)), (
            int(end_x // self.ratio), int(end_y // self.ratio))

    # mouse callback function
    def draw_rectangle_callback(self, event, x, y, flags, _):

        # # TODO: unresolved error
        # if event != 0:
        #     print(time.time(), event, f"(x,y) = {(x, y)}")
        # if event == cv2.EVENT_LBUTTONDOWN:
        #     self.start = (x, y)

        if event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
            roi_x, roi_y = self.roi
            start_x, start_y = self.start

            # print(start_x, roi_x)

            if start_x > roi_x:
                temp = start_x
                start_x = roi_x
                roi_x = temp
            if start_y > roi_y:
                temp = start_y
                start_y = roi_y
                roi_y = temp

            if roi_x == -1:
                self.canvas_img = np.copy(self.img)
            else:
                # just change B G channel 0:1
                self.canvas_img[start_y:roi_y, start_x:roi_x, 0:1] = self.img[start_y:roi_y, start_x:roi_x, 0:1]

            self.roi = (x, y)

            # ---------------test true
            q_start_x, q_start_y = self.start
            qx = x
            qy = y

            if q_start_x > qx:
                temp = q_start_x
                q_start_x = qx
                qx = temp
            if q_start_y > qy:
                temp = q_start_y
                q_start_y = qy
                qy = temp

            self.canvas_img[q_start_y:qy, q_start_x:qx, 0:1] = 0

        elif event == cv2.EVENT_LBUTTONUP:
            self.end = (x, y)
            self.cropped = True
        elif not self.cropped:  # TODO: not proper way
            # Unresolved problem test
            # print(time.time(), event, f"(x,y) = {(x, y)}, assign new start") # for DEBUG
            self.start = (x, y)

    def get_range_for_cropping(self):
        # set as window
        # cv2.namedWindow('Crop Window')
        # set as fullscreen
        cv2.namedWindow("Snip Window", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Snip Window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        cv2.waitKey(1)
        cv2.setWindowProperty("Snip Window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback('Snip Window', self.draw_rectangle_callback)
        hWnd = win32gui.FindWindow(None, 'Snip Window')
        win32gui.SetWindowPos(hWnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_SHOWWINDOW | win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
        while True:
            cv2.imshow('Snip Window', self.canvas_img)
            if cv2.waitKey(20) and 0xFF == ord('q') or self.cropped:
                cv2.destroyAllWindows()
                cv2.waitKey(1)
                break
        return


def convert_image_to_gray(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    return gray_img


def get_dilate(img):
    gray_img = convert_image_to_gray(img)
    kernel_length = 30
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
    dilate = cv2.dilate(gray_img, horizontal_kernel, iterations=1)
    return dilate


def is_black_background_image(img, threshold=0.3):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 85])
    percent = (cv2.inRange(hsv, lower_black, upper_black)).sum() / img.size
    percent = percent / 100
    if percent >= threshold:
        return True
    else:
        return False


def get_rect(img):
    copy_image = img.copy()

    # if image has black background, convert it to white background
    if is_black_background_image(img):
        gray_image = convert_image_to_gray(img)
        # reset after mess up
        cv2.imwrite(f"{os.path.realpath(os.path.dirname(__file__))}/../data/app image/temp_process.png", gray_image)
        new_image_path = f"{os.path.realpath(os.path.dirname(__file__))}/../data/app image/temp_process.png"
        copy_image = cv2.imread(new_image_path)

    dilate = get_dilate(copy_image)

    contours = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    rect = [tuple(cv2.boundingRect(c)) for c in contours]

    return rect


def image_to_text(img):
    origin_image = img.copy()

    rect = get_rect(img)

    rect = sorted(rect, key=lambda z: (z[1], z))

    len_rect = len(rect)
    for i, r in enumerate(rect):
        x, y, w, h = r
        padding = round(h / 4)
        vertical_range = (y - padding, y + h + padding)
        next_i = i + 1
        while True and next_i < len_rect:
            if rect[next_i][1] >= vertical_range[0] and rect[next_i][1] + rect[next_i][3] <= vertical_range[1]:
                next_i = next_i + 1
            else:
                break
        rect[i:next_i-1] = sorted(rect[i:next_i-1],  key=lambda z: (z[0], z))

    results = list()

    image_height, image_width, _ = origin_image.shape

    for r in range(len(rect)):
        x, y, w, h = rect[r]

        # add padding
        padding = round(h / 5)

        start_y = y - padding
        end_y = y + h + padding
        start_x = x - padding
        end_x = x + w + padding

        if start_y < 0:
            start_y = 0
        if start_x < 0:
            start_x = 0
        if end_y > image_height:
            end_y = image_height
        if end_x > image_width:
            end_x = image_width

        crop_img = origin_image[start_y:end_y, start_x:end_x]
        #
        # cv2.imshow("test", crop_img)
        # cv2.waitKey(0)

        temp = reader.readtext(crop_img, detail=0, paragraph=True, y_ths=-0.2, x_ths=500)
        if len(temp) > 0:
            temp = " ".join(temp)
            results.append(temp)

    return results


def crop():
    # print("Start snip ...")

    image_path = f"{os.path.realpath(os.path.dirname(__file__))}/../data/app image/cropped_image.png"
    # crop image from screen
    raw_img = pyautogui.screenshot().convert('RGB')

    raw_img = cv2.cvtColor(np.array(raw_img), cv2.COLOR_RGB2BGR)
    cropper = Cropper(raw_img)
    start, end = cropper.get_start_end()

    start_x, start_y = start
    end_x, end_y = end

    # swap position for suitable slicing image
    if start_x > end_x:
        temp = start_x
        start_x = end_x
        end_x = temp
    if start_y > end_y:
        temp = start_y
        start_y = end_y
        end_y = temp
    if start_x != end_x and start_y != end_y:
        raw_img = raw_img[start_y:end_y, start_x:end_x, :]
        cv2.imwrite(image_path, raw_img)
    else:
        return None

    # OCR
    results = image_to_text(raw_img)

    if results:
        return "\n".join(results)
    else:
        return None
