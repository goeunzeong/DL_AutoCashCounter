from django.shortcuts import render
from django.http import StreamingHttpResponse

import yolov5, torch
from yolov5.utils.general import (check_img_size, non_max_suppression, scale_coords,
                                  check_imshow, xyxy2xywh, increment_path, strip_optimizer, colorstr)
from yolov5.utils.torch_utils import select_device, time_sync
from yolov5.utils.plots import Annotator, colors, save_one_box
from deep_sort.utils.parser import get_config
from deep_sort.deep_sort import DeepSort

import cv2
from PIL import Image as im
from PIL import ImageDraw

from webcam import encode_dict as en
import mydef.get_txt as txt
import mydef.get_receipt as receipt

import time
start = time.time()  # 시작 시간 저장

# Create your views here.
# def index(request):
#     myname = label
#     return render(request, 'index.html')

# load yolov5 model
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
model = yolov5.load('best.pt')
# model = yolov5.load('0516_best.pt')
device = select_device('0') # '0' : gpu, '' : cpu
# initialize deepsort
cfg = get_config()
cfg.merge_from_file('deep_sort/configs/deep_sort.yaml')
deepsort = DeepSort(
            'osnet_x0_25',
            device,
            max_dist=cfg.DEEPSORT.MAX_DIST,
            max_iou_distance=cfg.DEEPSORT.MAX_IOU_DISTANCE,
            max_age=cfg.DEEPSORT.MAX_AGE, n_init=cfg.DEEPSORT.N_INIT, nn_budget=cfg.DEEPSORT.NN_BUDGET,
        )

# Get names and colors
names = model.module.names if hasattr(model, 'module') else model.names

def stream():
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    # cap_time = time.time() 
    # print('1', cap_time - start)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    
    id_list = []

    while True:
        # a_time = time.time()
        # ret, frame = cap.read()

        # read_time = time.time() 
        # print('2', read_time - a_time)

        # frame = cv2.flip(frame, 1)
        if not ret:
            print('Error: failed to capture image')
            break

        # 화면 중앙에 검출 기준선 그릴 때
        # frame = cv2.line(frame, (int(width/2), int(height)), (int(width/2), int(0)), 0, thickness=2, lineType=None, shift=None) 
        
       
        
        results = model(frame, augment = True)


        # model_time = time.time() 
        # print('3', model_time - read_time)

        # process
        annotator = Annotator(frame, line_width = 2, pil = not ascii)


        det = results.pred[0]

        raccoon = False

        if det is not None and len(det):          

            xywhs = xyxy2xywh(det[:, 0:4])
            confs = det[:, 4]
            clss = det[:, 5]

            
            outputs = deepsort.update(xywhs.cpu(), confs.cpu(), clss.cpu(), frame)
            
            dsort_time = time.time() 
            # print('3', dsort_time - model_time)
            # t = 1
            if len(outputs) > 0:
                for j, (output, conf) in enumerate(zip(outputs, confs)):

                    bboxes = output[0:4]
                    id = output[4]
                    cls = output[5]
                    c = int(cls)
                    
                    label = f'{id} {names[c]} {conf:.2f}'
                    if(names[c] != 1018):

                        # annot_time = time.time() 
                        # print(t, annot_time - dsort_time)
                        # t += 1

                        annotator.box_label(tuple(bboxes), label, color=colors(c, True))
                        
                        cp = (bboxes[0] + bboxes[2]) / 2
                        # print(id, names[c], bboxes, 'cp:', cp)
                        if (cp > 270) & (cp < 370):
                            if id not in id_list:
                                if (names[c] != 0) and (conf >= 0.5):
                                    nframe = annotator.result()
                            
                                    frame = cv2.line(nframe, (320, 480), (320, 0), (255, 255, 255), thickness=2, lineType=None, shift=None)
                                    print(id, names[c], bboxes, 'cp:', cp, 'conf:', conf)
                                    txt.write_txt(names[c])
                                    id_list.append(id)

                            if names[c] == 0:
                                raccoon = True
                
                       

                # # 0번 (너구리)가 검출되면 촬영 중지
                # if names[c] == 0:
                #     raccoon = True
                        
                     
                    
        else:
            deepsort.increment_ages()

        # im0 = annotator.result()
        im0 = frame

        # 너구리가 감지되면 detect 종료
        if cv2.waitKey(1) & raccoon == True:
            im0 = cv2.imread('static/detect_fin.png')
            image_bytes = cv2.imencode('.jpg', im0)[1].tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + image_bytes + b'\r\n')
            break
            
        else:
            image_bytes = cv2.imencode('.jpg', im0)[1].tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + image_bytes + b'\r\n')
        
        


def index(request):
    return render(request, 'index.html')
 
def video_feed(request):
    return StreamingHttpResponse(stream(), content_type='multipart/x-mixed-replace; boundary=frame')

def calc(request):
    keys = txt.read_txt('./detected.txt')
    total = receipt.get_receipt(keys)
    print("total",total)
    print(request.method) 
    # {'total1':total}
    return render(request, 'calc.html', {'total1':total})