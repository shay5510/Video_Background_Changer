import cv2
import numpy as np
from tqdm import tqdm

# Finding background using median
def find_background(cap, dim):

    # Randomly select 25 frames
    frameIds = cap.get(cv2.CAP_PROP_FRAME_COUNT) * np.random.uniform(size=75)

    # Store selected frames in an array
    frames = []
    for fid in frameIds:
        cap.set(cv2.CAP_PROP_POS_FRAMES, fid)
        ret, frame = cap.read()

        width = int(frame.shape[1])
        height = int(frame.shape[0])
        dim = (width, height)
        resized_frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
        frames.append(resized_frame)

    # Calculate the median along the time axis
    background = np.median(frames, axis=0).astype(dtype=np.uint8)
    return background
