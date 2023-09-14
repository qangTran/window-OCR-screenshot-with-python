import os
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


def image_to_text(img):
    # ocr_results = reader.readtext(img, paragraph=True, y_ths=-0.2, x_ths=500) # best for Phu's Ver

    ocr_results = reader.readtext(img, paragraph=False)
    # print bounding box
    # for i in ocr_results:
    #     print(i)
    # for (bbox, text, _) in ocr_results:
    #     # Define bounding boxes
    #     (tl, tr, br, bl) = bbox
    #     tl = (int(tl[0]), int(tl[1]))
    #     tr = (int(tr[0]), int(tr[1]))
    #     br = (int(br[0]), int(br[1]))
    #     bl = (int(bl[0]), int(bl[1]))
    #
    #     # Remove non-ASCII characters to display clean text on the image (using opencv)
    #     text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
    #
    #     # Put rectangles and text on the image
    #     cv2.rectangle(img, tl, br, (0, 255, 0), 2)
    #     # cv2.putText(img, text, (tl[0], tl[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    # # show the output image
    # cv2.imshow("Image", img)
    # cv2.waitKey(0)

    # sort by y position
    ocr_results = sorted(ocr_results, key=lambda z: z[0][0][1])

    # detect by line
    len_result = len(ocr_results)
    line_mark = list()
    i = 0

    while i < len_result:
        upper_y = ocr_results[i][0][0][1]
        lower_y = ocr_results[i][0][2][1]
        next_i = i + 1
        if next_i < len_result:
            lower_threshold = lower_y + round(
                ((lower_y - upper_y) + (ocr_results[next_i][0][2][1] - ocr_results[next_i][0][0][1])) / 8)
            while next_i < len_result:
                next_lower_y = ocr_results[next_i][0][2][1]
                if next_lower_y <= lower_threshold:
                    next_i = next_i + 1
                else:
                    break
        # sort by line
        ocr_results[i:next_i] = sorted(ocr_results[i:next_i], key=lambda z: z[0][0][0])
        line_mark.append((i, next_i))
        i = next_i

    text_result = [i[1] for i in ocr_results]
    last_result = [" ".join(text_result[i:j]) for i, j in line_mark]
    return last_result


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
        cv2.imwrite(r"D:\OneDrive - VNU-HCMUS\H - Tech\Code\test ocr and normal default text\cropped_image.png",
                    raw_img)
    else:
        return None

    # OCR
    results = image_to_text(raw_img)

    # for i in results:
    #     print(i)
    if results:
        return "\n".join(results)
    else:
        return None


def test_single_image():
    ###############
    raw_img = cv2.imread('../data/app image/cropped_image.png')
    ###############
    # cv2.imshow('image',raw_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    print(type(raw_img))
    # OCR
    results = image_to_text(raw_img)
    for i in results:
        print(i)


if __name__ == "__main__":
    test_single_image()
