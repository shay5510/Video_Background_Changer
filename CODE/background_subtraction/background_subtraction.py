import cv2
import time
import sys
sys.path.append('./background_subtraction')
from find_background import *
from create_initial_mask import *
from second_mask import *
from hist_max_vals import *
import os
import time


def background_subtraction(stabilized_video_address, extracted_video_address, binary_video_address):

    start_time = time.time()
    print("Starting Stage 2: Background Subtraction")

    # Read stabilized video
    cap = cv2.VideoCapture(stabilized_video_address)
    fps = cap.get(cv2.CAP_PROP_FPS)
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # read first frame:
    ret, frame1 = cap.read()
    scale = 2
    dim = (int(frame1.shape[1] / scale), int(frame1.shape[0] / scale))
    dim_orig = (frame1.shape[1], frame1.shape[0])

    # Find Background:
    back_ground = find_background(cap, dim)

    # initial extracted and binary
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out_mask = cv2.VideoWriter(binary_video_address, fourcc, fps, dim_orig)
    out_extractes = cv2.VideoWriter(extracted_video_address, fourcc, fps, dim_orig)

    # Reset stream to first frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # Calc simple mask with optical flow and calc hue histogram
    initial_mask(cap, back_ground, out_extractes, out_mask)
    cap.release()
    out_mask.release()
    out_extractes.release()

    # Load stabilized video and get video params
    out_mask.release()
    cap.release()
    cv2.destroyAllWindows()

    print("Finish Stage 2: Background Subtraction")
    finish_time = time.time()
    total_time_seconds = finish_time - start_time
    minutes = int(total_time_seconds / 60)
    seconds = int(total_time_seconds - minutes * 60)
    total_time = "Background Subtraction Elapsed time: {}:{:02d} minutes".format(minutes, seconds)
    print(total_time)

    return total_time