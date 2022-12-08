import os
import cv2
import easyocr
import numpy as np
import pyautogui  # take a screenshot
import torch
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
        cv2.setWindowProperty("Snip Window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        cv2.setMouseCallback('Snip Window', self.draw_rectangle_callback)
        while True:
            cv2.imshow('Snip Window', self.canvas_img)
            if cv2.waitKey(20) and 0xFF == ord('q') or self.cropped:
                cv2.destroyAllWindows()
                cv2.waitKey(1)
                break
        return


def image_to_gray(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    GrayImg = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    return img, GrayImg


def dilate_image(mask):
    kernel_length = 30
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
    dilate = cv2.dilate(mask, horizontal_kernel, iterations=1)
    return dilate


def process_image(img):
    img, GrayImg = image_to_gray(img)
    dilate = dilate_image(GrayImg)
    return img, dilate


def create_bounding_box_by_line(img):
    if find_black_background(img):
        _, temp = image_to_gray(img)
        cv2.imwrite(f"{os.path.realpath(os.path.dirname(__file__))}/../data/app image/temp_process.png", temp)
        new_image_path = f"{os.path.realpath(os.path.dirname(__file__))}/../data/app image/temp_process.png"
        img = cv2.imread(new_image_path)
    img, dilate = process_image(img)
    img2 = img.copy()
    contours = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    rect = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        rect.append(cv2.boundingRect(c))
        img2 = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        crop_img = img[y:y + w, x:x + h]

    return img2, rect


def find_black_background(img, threshold=0.3):
    """remove images with transparent or white background"""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 85])
    percent = (cv2.inRange(hsv, lower_black, upper_black)).sum() / img.size
    percent = percent / 100
    if percent >= threshold:
        return True
    else:
        return False


def image_to_text(img):
    origin_image = img.copy()

    _, rect = create_bounding_box_by_line(img)

    rect = sorted(rect, key=lambda x: (x[1], x))
    results = []

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
            end_y = image_width

        crop_img = origin_image[start_y:end_y, start_x:end_x]

        temp = reader.readtext(crop_img, detail=0, paragraph=True, y_ths=1, x_ths=100)
        results = results + temp
    return results


def crop():
    # print("Start snip ...")

    image_path = f"{os.path.realpath(os.path.dirname(__file__))}/../data/app image/test1.png"
    # crop image from screen
    raw_img = pyautogui.screenshot().convert('RGB')

    raw_img = cv2.cvtColor(np.array(raw_img), cv2.COLOR_RGB2BGR)
    cropper = Cropper(raw_img)
    start, end = cropper.get_start_end()

    # print(f"startx, start_y = {start}")
    # print(f"endx, endy = {end}")
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
