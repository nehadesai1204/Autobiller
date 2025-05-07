#!/usr/bin/env python


import cv2
import os
import sys, getopt
import signal
import time
from edge_impulse_linux.image import ImageImpulseRunner
import itertools 
from collections import deque
import numpy as np

runner = None
# if you don't want to see a camera preview, set this to False
show_camera = True
if (sys.platform == 'linux' and not os.environ.get('DISPLAY')):
    show_camera = False

detected_objects = [{'label': 'Maggi', 'precision': 0.7524408102035522}, 
{'label': 'Maggi', 'precision': 0.6873443722724915}, 
{'label': 'Maggi', 'precision': 0.7748854756355286}, 
{'label': 'Maggi', 'precision': 0.7709378600120544}, 
{'label': 'Maggi', 'precision': 0.7863907814025879}, 
{'label': 'Maggi', 'precision': 0.7090469598770142}, 
{'label': 'Maggi', 'precision': 0.8815599679946899}, 
{'label': 'Maggi', 'precision': 0.5402244329452515}, 
{'label': 'Maggi', 'precision': 0.5678010582923889}, 
{'label': 'Maggi', 'precision': 0.5692270994186401}, 
{'label': 'Maggi', 'precision': 0.7034330368041992}, 
{'label': 'Maggi', 'precision': 0.5539481043815613}, 
{'label': 'Maggi', 'precision': 0.6524307131767273}, 
{'label': 'Maggi', 'precision': 0.6734236478805542}, 
{'label': 'Maggi', 'precision': 0.7261595129966736}, 
{'label': 'Vim', 'precision': 0.540699303150177},
{'label': 'Vim', 'precision': 0.7724677920341492}]


def now():
    return round(time.time() * 1000)

def get_webcams():
    port_ids = []
    for port in range(5):
        print("Looking for a camera in port %s:" %port)
        camera = cv2.VideoCapture(port)
        if camera.isOpened():
            ret = camera.read()[0]
            if ret:
                backendName =camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print("Camera %s (%s x %s) found in port %s " %(backendName,h,w, port))
                port_ids.append(port)
            camera.release()
    return port_ids

def sigint_handler(sig, frame):
    print('Interrupted')
    if (runner):
        runner.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def help():
    print('python classify.py <path_to_model.eim> <Camera port ID, only required when more than 1 camera is present>')

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "h", ["--help"])
    except getopt.GetoptError:
        help()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help()
            sys.exit()

    if len(args) == 0:
        help()
        sys.exit(2)

    model = args[0]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, model)

    print('MODEL: ' + modelfile)

    with ImageImpulseRunner(modelfile) as runner:
        try:
            model_info = runner.init()
            print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
            labels = model_info['model_parameters']['labels']
            if len(args)>= 2:
                videoCaptureDeviceId = int(args[1])
            else:
                port_ids = get_webcams()
                if len(port_ids) == 0:
                    raise Exception('Cannot find any webcams')
                if len(args)<= 1 and len(port_ids)> 1:
                    raise Exception("Multiple cameras found. Add the camera port ID as a second argument to use to this script")
                videoCaptureDeviceId = int(port_ids[0])

            camera = cv2.VideoCapture(videoCaptureDeviceId)
            ret = camera.read()[0]
            if ret:
                backendName = camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print("Camera %s (%s x %s) in port %s selected." %(backendName,h,w, videoCaptureDeviceId))
                camera.release()
            else:
                raise Exception("Couldn't initialize selected camera.")

            next_frame = 0 # limit to ~10 fps here
            
            # Change x and y windows to detect smaller items (limited by FOMO windowing)
            x_windows = 20
            y_windows = 10
            # forward_buffer-1 == how many frames have no object after one is detected to count
            forward_buffer = 2
            detections = np.zeros((x_windows,y_windows))
            frame_queue = deque(maxlen=forward_buffer)
            frame_queue.append(detections[0,:])
            count = 0
            

            while count < 15:
                for res, img in runner.classifier(videoCaptureDeviceId):
                    if next_frame > now():
                        time.sleep((next_frame - now()) / 1000)
                    detections = np.zeros((x_windows, y_windows))

                    if "bounding_boxes" in res["result"].keys():
                        print('Found %d bounding boxes (%d ms.)' % (len(res["result"]["bounding_boxes"]), res['timing']['dsp'] + res['timing']['classification']))
                        for bb in res["result"]["bounding_boxes"]:
                            print('\t%s (%.2f)' % (bb['label'], bb['value']))
                            img = cv2.rectangle(img, (bb['x'], bb['y']), (bb['x'] + bb['width'], bb['y'] + bb['height']),
                                                (255, 0, 0), 1)
                            x = bb['x'] + (bb['width'] / 2)
                            x_n = round(np.interp(x, [0, img.shape[0]], [0, y_windows - 1]))
                            y = bb['y'] + (bb['height'] / 2)
                            y_n = round(np.interp(y, [0, img.shape[1]], [0, x_windows - 1]))
                            detections[y_n, x_n] = 1

                            # Append detection information to the list
                            detected_objects.append({'label': bb['label'], 'precision': bb['value']})

                            count += 1

                    top_row = detections[0, :]
                    frame_queue.append(top_row)
                    for column, value in enumerate(frame_queue[0]):
                        debounced = all(ele[column] == 0 for ele in itertools.islice(frame_queue, 1, forward_buffer))
                        if value == 1 and debounced:
                            count += 1
                            print(f'{count} items passed')

                    if show_camera:
                        im2 = cv2.resize(img, dsize=(800, 800))
                        cv2.putText(im2, f'{count} items passed', (15, 750), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                        cv2.imshow('edgeimpulse', cv2.cvtColor(im2, cv2.COLOR_RGB2BGR))
                        if cv2.waitKey(1) == ord('q'):
                            break

                    next_frame = now() + 100

                    if count >= 15:
                        break

            # Print the detected objects array at the end
            print(detected_objects)
        finally:
            if (runner):
                runner.stop()

if __name__ == "__main__":
   main(sys.argv[1:])