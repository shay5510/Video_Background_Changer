import cv2
import sys
import numpy as np
sys.path.append("./stable")
from calc_transform import *
from moving_average import *
from execute_transform import *
from smooth import *
import time
import os

def stabilize(input_address, output_address,projective_transform):

    # input_address = os.path.join("../", input_address)
    # output_address = os.path.join("../", output_address)
    # projective_transform = os.path.join("../", projective_transform)

    start_time=time.time()
    print("Starting Stage 1: Stabilization")

    cap = cv2.VideoCapture(input_address)

    # Get frame count
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # Get width, height and fps of video stream
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    image_scale = 1
    frame_width = int(cap.get(3) / image_scale)
    frame_height = int(cap.get(4) / image_scale)
    dim = (frame_width, frame_height)

    # Define the codec for output video
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    # Set up output video
    out = cv2.VideoWriter(output_address, fourcc, fps, (w, h))
    transforms = calc_transform(cap,n_frames, dim,projective_transform)
    # Compute trajectory using cumulative sum of transformations
    trajectory = np.cumsum(transforms, axis=0)

    smoothed_trajectory = smooth(trajectory)
    # Calculate difference in smoothed_trajectory and trajectory
    difference = smoothed_trajectory - trajectory

    transforms_smooth = transforms + difference

    # Reset stream to first frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # Write n_frames-1 transformed frames
    execute_transform(cap, n_frames, transforms_smooth, dim, out)
    out.release()
    cv2.destroyAllWindows()

    print("Finish Stage 2: Stabilization")
    finish_time=time.time()
    total_time_seconds=finish_time-start_time
    minutes=int(total_time_seconds/60)
    seconds=int(total_time_seconds - minutes*60)
    total_time="Stabilization Elapsed time: {}:{:02d} minutes".format(minutes,seconds)
    print (total_time)

    return total_time