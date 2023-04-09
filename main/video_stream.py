from main.models import *
import cv2
import threading
import torch
from PIL import Image, ImageDraw, ImageFont
from deep_sort_realtime.deepsort_tracker import DeepSort
import pandas as pd
import numpy as np
from pathlib import Path
import queue

BASE_DIR = Path(__file__).resolve().parent.parent

class VideoCamera(object):
    def __init__(self, id, line_width, line_place, direction):
        self.camera = Camera.objects.get(pk=id)
        self.video = cv2.VideoCapture(self.camera.url)
        print( BASE_DIR / 'subprocess/best.pt')
        self.font = ImageFont.truetype("arial.ttf", 20)
        self.font_counter = ImageFont.truetype("arial.ttf", 64)
        self.font_mass = ImageFont.truetype("arial.ttf", 35)
        self.font_total_mass = ImageFont.truetype("arial.ttf", 32)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', BASE_DIR / 'subprocess/best.pt')
        self.model.to(self.device)
        self.tracker = DeepSort(max_age=15)
        self.q=queue.Queue()


        self.checker_treshold = 13
        self.line_diff = line_width
        self.pigs_set = set()
        self.checker = {}
        self.pig_id_2_weight = {}
        (self.grabbed, self.frame) = self.video.read()
        print(self.frame.shape)
        self.width = self.frame.shape[1]
        self.height = self.frame.shape[0]


        (self.x1, self.y1, self.x2, self.y2), self.sign, self.detection_line_orient = self.get_detection_line(direction,
                                                    divider=line_place,
                                                    width=self.width,
                                                    height=self.height,
                                                    line_diff=self.line_diff)
        print(0)
        self.pig_weights_table = pd.read_csv(BASE_DIR / 'subprocess/pig_weights_table.csv')
        print(1)
        self.pig_width_2_height = (self.pig_weights_table['1']/self.pig_weights_table['0']).mean()
        print(2)
        threading.Thread(target=self.grab, args=()).start()
        threading.Thread(target=self.update, args=()).start()


    def get_mass_from_box(self, box, horizontal_pixel_to_mm=0):
        pig_width_2_height=self.pig_width_2_height
        pig_weights_table_tmp = self.pig_weights_table
        w_is_bigger = None
        w = abs(box[0] - box[2])
        h = abs(box[1] - box[3])
        if w >= h and w/h <= pig_width_2_height:
            big_dim = np.sqrt(w**2 + h**2)
            big_dim *= horizontal_pixel_to_mm
            small_dim = big_dim / pig_width_2_height
        elif w <= h and w/h <= pig_width_2_height:
            big_dim = np.sqrt(w**2 + h**2)
            big_dim *= horizontal_pixel_to_mm
            small_dim = big_dim / pig_width_2_height
        elif w >= h and w/h > pig_width_2_height:
            big_dim = w * horizontal_pixel_to_mm
            small_dim = big_dim/pig_width_2_height
        elif w <= h and w/h > pig_width_2_height:
            small_dim = w * pig_width_2_height
            big_dim = small_dim * pig_width_2_height
        big_dim //= 10
        small_dim //= 10
        pig_weights_table_tmp["len_diff"] = abs(big_dim - pig_weights_table_tmp[1])
        pig_weights_table_tmp["br_diff"] = abs(small_dim - pig_weights_table_tmp[0])
        pig_weights_table_tmp["len_diff"]/=max(pig_weights_table_tmp["len_diff"])
        pig_weights_table_tmp["br_diff"]/=max(pig_weights_table_tmp["br_diff"])
        pig_weights_table_tmp["all_diff"] = pig_weights_table_tmp["br_diff"]+pig_weights_table_tmp["len_diff"]
        return pig_weights_table_tmp.sort_values(by="all_diff").iloc[0][2]




    def get_image_with_boxes_ind(self,
                                 img, 
                                annot_pred, 
                                counter=None, 
                                detection_line=None, 
                                horizontal_pixel_2_mm=None, 
                                pig_id_2_weight={}):
        image_for_draw = img
        
        image_for_draw = Image.fromarray(np.uint8(img)).convert('RGB')
        
        draw = ImageDraw.Draw(image_for_draw)
        
        for i in range(len(annot_pred)):
            if counter is not None and annot_pred[i][4] in counter:
                color_bbox = (0, 255, 0)
            else:
                color_bbox = (255,0,0) 
            draw.rectangle([(annot_pred[i][0],
                            annot_pred[i][1]),
                            (annot_pred[i][2],
                            annot_pred[i][3])],
                        outline=color_bbox, width=2)
            draw.text((annot_pred[i][0], annot_pred[i][1]), text=str(int(annot_pred[i][4])), fill=(0,255,0), font=self.font)
            if annot_pred[i][4] in pig_id_2_weight:
                draw.text((annot_pred[i][0], annot_pred[i][3]-100), text=str(int(sum(pig_id_2_weight[annot_pred[i][4]])/len(pig_id_2_weight[annot_pred[i][4]])))+" кг", fill=(139,0,255), font=self.font_mass)
        if counter is not None:       
            #draw.rectangle([(width-150, 0), (width, 150)], fill=(0, 0, 0))
            draw.text((self.width - 74, 10), text=str(len(counter)), fill="red", font=self.font_counter)
        if detection_line is not None:
            draw.rectangle([(detection_line[0],
                            detection_line[1]),
                            (detection_line[2],
                            detection_line[3])], outline=(0,255,255), width=2)
        if pig_id_2_weight:
            pigs_weights = [sum(i)/len(i) for i in pig_id_2_weight.values()]
            draw.text((0, self.height-50), text="Total mass: " + str(int(sum(pigs_weights))) + ' кг', fill="red", font=self.font_total_mass)
        return np.array(image_for_draw)


    def get_detection_line(self, direction="Up",
                        divider=0.5,
                        width=None,
                        height=None,
                        line_diff=20):
        x1 = None
        x2 = None
        y1 = None
        y2 = None
        sign = None
        detection_line_orient=None
        if direction=="Up":
            x1 = 0
            x2 = width
            y1 = height*divider-line_diff
            y2 = height*divider+line_diff
            sign="minus"
            detection_line_orient="horizontal"
        elif direction=="Left":
            x1 = width*divider-line_diff
            x2 = width*divider+line_diff
            y1 = 0
            y2 = height
            sign="minus"
            detection_line_orient="vertical"
        elif direction=="Down":
            x1 = 0
            x2 = width
            y1 = height*divider-line_diff
            y2 = height*divider+line_diff
            sign="plus"
            detection_line_orient="horizontal"
        elif direction=="Right":
            x1 = width*divider-line_diff
            x2 = width*divider+line_diff
            y1 = 0
            y2 = height
            sign="plus"
            detection_line_orient="vertical"
        return (x1,y1, x2, y2), sign, detection_line_orient




    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()


    def grab(self):
        while True:
            try:
                (grabbed, img) = self.video.read()
                self.q.put(img)
            except:
                continue
            if not grabbed:
                continue


    def update(self):

        while True:
            if self.q.empty() !=True:
                img=self.q.get()
            else:
                continue
            try:
                rgb_frame_for_detection = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            except:
                continue
            outputs = self.model(rgb_frame_for_detection)
            
            inp = []
            for i in range(len(outputs.xyxy[0])):
                bb = outputs.xyxy[0][i][:4].detach().cpu().numpy()
                t = ([min(bb[0], bb[2]), min(bb[1], bb[3]), abs(bb[0] - bb[2]), abs(bb[1] - bb[3])], outputs.xyxy[0][i][4].item(), 0)
                inp.append(t)
            if inp:
                tracks = self.tracker.update_tracks(inp, frame=rgb_frame_for_detection)
            
                inp = []
                for track in tracks:
                    if not track.is_confirmed():
                        continue
                    track_id = track.track_id
                    ltrb = track.to_ltrb()
                    inp.append(ltrb.tolist() + [track_id])
                    
                for i in inp:
                    x_c = (i[0]+i[2])/2
                    y_c = (i[3]+i[1])/2
                    if i[4] in self.checker:
                        pig_direction = self.checker[i[4]]
                        if len(pig_direction) >= self.checker_treshold:
                            if self.detection_line_orient=="horizontal" and self.y1 < y_c < self.y2 or self.detection_line_orient=="vertical" and self.x1 < x_c < self.x2:
                                if sum([pig_direction[i+1]-pig_direction[i] for i in range(len(pig_direction)-1)]) < 0 and self.sign=="minus":
                                    self.pigs_set.add(i[4])
                                elif sum([pig_direction[i+1]-pig_direction[i] for i in range(len(pig_direction)-1)]) > 0 and self.sign=="plus":
                                    self.pigs_set.add(i[4])
                    if self.detection_line_orient=="horizontal":
                        if i[4] in self.checker:
                            self.checker[i[4]].append(y_c)
                        else:
                            self.checker[i[4]] = [y_c]
                    elif self.detection_line_orient=="vertical":
                        if i[4] in self.checker:
                            self.checker[i[4]].append(x_c)
                        else:
                            self.checker[i[4]] = [x_c]
            for i in self.checker:
                if len(self.checker[i])>self.checker_treshold:
                            self.checker[i] = self.checker[i][-self.checker_treshold:]
        
        
            
            img = self.get_image_with_boxes_ind(rgb_frame_for_detection, inp, self.pigs_set, detection_line=[self.x1,self.y1,self.x2,self.y2])

            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            self.frame = img


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

