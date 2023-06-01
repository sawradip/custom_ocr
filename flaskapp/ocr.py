import os
import cv2
import pytesseract
import numpy as np
from PIL import Image
from pytesseract import Output


class FlaskOCR:
    def __init__(self, tesseract_exe = None):
        if not tesseract_exe:
            pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

        self.seperator = '<SEP>'
        self.mega_seperator = '<MEGASEP>'
    
    def load_img(self, img_path):
        if os.path.exists(img_path):
            img = Image.open(img_path)
            return img
        else:
            raise Exception(f'Image not found in path:{img_path}') 
        
    def get_info_str(self, img_path, min_conf = 90):
        
        img = self.load_img(img_path)
        ocr_dict = pytesseract.image_to_data(img, output_type=Output.DICT)
        conf_mask = np.array(ocr_dict["conf"])> min_conf

        text_list = np.array(ocr_dict["text"])[conf_mask].tolist()

        left_list = np.array(ocr_dict["left"])[conf_mask].tolist()
        top_list = np.array(ocr_dict["top"])[conf_mask].tolist()
        width_list = np.array(ocr_dict["width"])[conf_mask].tolist()
        height_list = np.array(ocr_dict["height"])[conf_mask].tolist()

        text_str = self.seperator.join(text_list).lower()
        left_str = self.seperator.join(list(map(str, left_list)))
        top_str = self.seperator.join(list(map(str, top_list)))
        width_str = self.seperator.join(list(map(str, width_list)))
        height_str = self.seperator.join(list(map(str, height_list)))

        positional_str = self.mega_seperator.join([left_str, top_str, width_str, height_str])
        return text_str, positional_str

    def write_ocr_img(self,
                      input_impath,
                      output_dir,
                      search_query,
                      text_str,
                      positional_str):
        
        text_list = text_str.split(self.seperator.lower())
        x_str, y_str, w_str, h_str = positional_str.split(self.mega_seperator)
        x_list = list(map(int, x_str.split(self.seperator)))
        y_list = list(map(int, y_str.split(self.seperator)))
        w_list = list(map(int, w_str.split(self.seperator)))
        h_list = list(map(int, h_str.split(self.seperator)))

        image = cv2.imread(input_impath)

        search_queries = search_query.split(' ')

        for search_query in search_queries:
            for i in range(0, len(text_list)):
                text = text_list[i]
                if search_query in text.lower():
                
                    x = x_list[i]
                    y = y_list[i]
                    w = w_list[i]
                    h = h_list[i]
                    
                    text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)
                    cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 0, 255), 1)
                
        output_impath = os.path.join(output_dir, os.path.split(input_impath)[-1])
        cv2.imwrite(output_impath, image)

        return output_impath

        



