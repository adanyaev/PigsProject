import argparse
import threading
import cv2
import time
# from moviepy.video.io.VideoFileClip import VideoFileClip
# from transformers import (YolosFeatureExtractor, 
#                           YolosForObjectDetection, 
#                           DetrImageProcessor, 
#                           DetrForObjectDetection)
from PIL import Image, ImageDraw, ImageFont
import numpy as np
# import requests
import torch
import pandas as pd
import numpy as np
import psycopg2
import queue
import os
import tritonclient.http as httpclient

from ByteTracker.byte_tracker import BYTETracker

parser = argparse.ArgumentParser(description='Arguments for camera')
parser.add_argument('-c','--camera_url', type=str, help='Camera web url (path)', required=True)
parser.add_argument('-d', '--pig_direction', type=str, help='Where do the pigs go', choices=['Up', 'Down', 'Left', 'Right'], required=True)
parser.add_argument('--pig_detection_line_place', type=float, help='Where is the counting line, between 0 and 1', default=0.5)
parser.add_argument('--pig_detection_line_width', type=int, help='Detection line width', default=20)
parser.add_argument('-m', '--detection_model', type=str, help='Detection model path', required=True)


my_namespace = parser.parse_args()

print(my_namespace)

pig_weights_table = pd.read_csv('./subprocess/pig_weights_table.csv')
pig_width_2_height = (pig_weights_table['1']/pig_weights_table['0']).mean()

cap = cv2.VideoCapture(my_namespace.camera_url)
width = cap.get(3)
height = cap.get(4)
print(width, height)


dim = (640, 640)

conn = psycopg2.connect(
    host="localhost",
    database="PigsProjectDb",
    user="PigsProjectUser",
    password="Qwerty2312")
cur = conn.cursor()

sql_update_counter = """UPDATE main_camera SET current_counter = current_counter + %s WHERE pid = %s"""

def get_mass_from_box(box, horizontal_pixel_to_mm=0, pig_width_2_height=pig_width_2_height, pig_weights_table_tmp = pig_weights_table):
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

def get_detection_line(direction="Up",
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

def get_image_with_boxes_ind(img, 
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
        draw.text((annot_pred[i][0], annot_pred[i][1]), text=str(int(annot_pred[i][4])), fill=(0,255,0), font=font)
        if annot_pred[i][4] in pig_id_2_weight:
            draw.text((annot_pred[i][0], annot_pred[i][3]-100), text=str(int(sum(pig_id_2_weight[annot_pred[i][4]])/len(pig_id_2_weight[annot_pred[i][4]])))+" кг", fill=(139,0,255), font=font_mass)
    if counter is not None:       
        #draw.rectangle([(width-150, 0), (width, 150)], fill=(0, 0, 0))
        draw.text((width - 74, 10), text=str(len(counter)), fill="red", font=font_counter)
    if detection_line is not None:
        draw.rectangle([(detection_line[0],
                         detection_line[1]),
                        (detection_line[2],
                         detection_line[3])], outline=(0,255,255), width=2)
    if pig_id_2_weight:
        pigs_weights = [sum(i)/len(i) for i in pig_id_2_weight.values()]
        draw.text((0, height-50), text="Total mass: " + str(int(sum(pigs_weights))) + ' кг', fill="red", font=font_total_mass)
    return np.array(image_for_draw)

font = ImageFont.truetype("arial.ttf", 20)
font_counter = ImageFont.truetype("arial.ttf", 64)
font_mass = ImageFont.truetype("arial.ttf", 35)
font_total_mass = ImageFont.truetype("arial.ttf", 32)

q = queue.Queue()

tracker = BYTETracker(frame_rate=60, track_thresh=0.5, track_buffer=30)


checker_treshold = 13
line_diff = my_namespace.pig_detection_line_width
pigs_set = set()
checker = {}
pig_id_2_weight = {}


(x1, y1, x2, y2), sign, detection_line_orient = get_detection_line(my_namespace.pig_direction,
                                              divider=my_namespace.pig_detection_line_place,
                                              width=width,
                                              height=height,
                                              line_diff=line_diff)


def grab(cap):
        counter = 0
        while True:
            try:
                (grabbed, img) = cap.read()
                counter += 1
                if counter == 3:
                    q.put(img)
                    counter = 0
            except:
                continue
            if not grabbed:
                continue

threading.Thread(target=grab, args=([cap])).start()


client = httpclient.InferenceServerClient(url="127.0.0.1:8000")
global frame_pig_inc
while True:
    frame_pig_inc = 0
    cur.execute(sql_update_counter,(frame_pig_inc, os.getpid()))
    conn.commit()
    if q.empty() !=True:
        img=q.get()
    else:
        continue
    img_preprocessed = cv2.resize(img, dim, interpolation = cv2.INTER_LANCZOS4)
    img_preprocessed = img_preprocessed.transpose(2,0,1)
    img_preprocessed = (img_preprocessed.astype('float32')-110)/58
    img_preprocessed = np.expand_dims(img_preprocessed, axis=0)
    # try:
    #     rgb_frame_for_detection = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # except:
    #     continue
    detection_input = httpclient.InferInput("images", img_preprocessed.shape, datatype="FP32")
    detection_input.set_data_from_numpy(img_preprocessed, binary_data=True)
    
    outputs = client.infer(model_name="detector", inputs=[detection_input])
    print(my_namespace.camera_url)
    boxes = outputs.as_numpy('boxes')
    scores = outputs.as_numpy('scores')
    labels = outputs.as_numpy('labels')
    
    # outputs = model(rgb_frame_for_detection)
    inputs = []
    for i in range(len(boxes[0])):
        bb = boxes[0][i]
        t = (min(bb[0], bb[2]), min(bb[1], bb[3]), abs(bb[0] - bb[2]), abs(bb[1] - bb[3]), scores[0][i], labels[0][i])
        inputs.append(t)
    if inputs:
        inputs = np.stack(inputs, axis=0)
        print(inputs.shape)
        online_targets = tracker.update(inputs, (640, 640), (640, 640))
        inp = []
        for t in online_targets:
            inp.append([t.tlwh[0], t.tlwh[1], t.tlwh[0]+t.tlwh[2], t.tlwh[1]+t.tlwh[3], t.track_id])
            
        for i in inp:
            x_c = (i[0]+i[2])/2
            y_c = (i[3]+i[1])/2
            if i[4] in checker:
                pig_direction = checker[i[4]]
                if len(pig_direction) >= checker_treshold:
                    if detection_line_orient=="horizontal" and y1 < y_c < y2 or detection_line_orient=="vertical" and x1 < x_c < x2:
                        if sum([pig_direction[i+1]-pig_direction[i] for i in range(len(pig_direction)-1)]) < 0 and sign=="minus":
                            pigs_set.add(i[4])
                            frame_pig_inc+=1
                        elif sum([pig_direction[i+1]-pig_direction[i] for i in range(len(pig_direction)-1)]) > 0 and sign=="plus":
                            pigs_set.add(i[4])
                            frame_pig_inc+=1
            if detection_line_orient=="horizontal":
                if i[4] in checker:
                    checker[i[4]].append(y_c)
                else:
                    checker[i[4]] = [y_c]
            elif detection_line_orient=="vertical":
                if i[4] in checker:
                    checker[i[4]].append(x_c)
                else:
                    checker[i[4]] = [x_c]
    for i in checker:
        if len(checker[i])>checker_treshold:
                    checker[i] = checker[i][-checker_treshold:]
    print('working!')
    cur.execute(sql_update_counter,(frame_pig_inc, os.getpid()))
    conn.commit()


# threading.Thread(target=grab, args=([cap])).start()
#threading.Thread(target=update, args=()).start()