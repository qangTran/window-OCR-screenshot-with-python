import easyocr
import torch
from .cropper import Cropper

class ImageProcessor:
    def __init__(self):
        self.reader = easyocr.Reader(['vi', 'en'], gpu=torch.cuda.is_available(), verbose=False)

    def capture_and_process_image(self):
        """ Capture, crop and process the image to extract text. """
        cropper = Cropper()
        cropped_img = cropper.get_image_from_screen()
        if cropped_img is not None and len(cropped_img):
            return self.image_to_text(cropped_img)
        return None

    def image_to_text(self, img):
        """ Use EasyOCR to convert image to text. """
        ocr_results = self.reader.readtext(img, paragraph=False)
        # ocr_results = reader.readtext(img, paragraph=True, y_ths=-0.2, x_ths=500) # other old setup 
        
        # # print bounding box for test
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

        ocr_results = sorted(ocr_results, key=lambda z: z[0][0][1])  # Sort by y position
        line_mark = self._get_line_marks(ocr_results)
        text_result = [i[1] for i in ocr_results] # get only text from ocr result
        last_result = [" ".join(text_result[i:j]) for i, j in line_mark]
        return "\n".join(last_result)

    def _get_line_marks(self, ocr_results):
        """ Helper method to determine line breaks in OCR results. """
        len_result = len(ocr_results)
        line_mark = []
        i = 0
        while i < len_result:
            # get items in one line, determine by threshold
            upper_y = ocr_results[i][0][0][1]
            lower_y = ocr_results[i][0][2][1]
            next_i = i + 1
            if next_i < len_result:
                lower_threshold = lower_y + round(
                    ((lower_y - upper_y) + (ocr_results[next_i][0][2][1] - ocr_results[next_i][0][0][1])) / 8)
                while next_i < len_result and ocr_results[next_i][0][2][1] <= lower_threshold:
                    next_i += 1
            
            # sort item in one line
            ocr_results[i:next_i] = sorted(ocr_results[i:next_i], key=lambda z: z[0][0][0])  # Sort by line
            line_mark.append((i, next_i)) # one line is determined by i to right before next i

            i = next_i
        return line_mark

if __name__ == "__main__":
    # For testing purposes
    image_processor = ImageProcessor()
    text = image_processor.capture_and_process_image()
    if text:
        print(text)
