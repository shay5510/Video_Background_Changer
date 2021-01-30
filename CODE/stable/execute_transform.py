import numpy as np
import cv2
from fix_box import *

def execute_transform(cap, n_frames, transforms_smooth, dim, out):
    for i in range(n_frames - 2):
        # Read next frame
        success, frame = cap.read()
        if not success:
            break
        frame = cv2.resize(frame, dim)
        # Extract transformations from the new transformation array
        dx = transforms_smooth[i, 0]
        dy = transforms_smooth[i, 1]
        da = transforms_smooth[i, 2]

        # Reconstruct transformation matrix accordingly to new values
        m = np.zeros((2, 3), np.float32)
        m[0, 0] = np.cos(da)
        m[0, 1] = -np.sin(da)
        m[1, 0] = np.sin(da)
        m[1, 1] = np.cos(da)
        m[0, 2] = dx
        m[1, 2] = dy

        # Apply affine wrapping to the given frame
        frame_stabilized = cv2.warpAffine(frame, m, dim)
        h1 = transforms_smooth[i].reshape(3, 3)
        frame_stabilized = cv2.warpPerspective(frame,h1, dim)
        # Fix border artifacts
        frame_stabilized = fixBorder(frame_stabilized)

        # Write the frame to the file
        frame_out = cv2.hconcat([frame, frame_stabilized])

        # If the image is too big, resize it.
        # if (frame_out.shape[1] > 1920):
        # frame_out = cv2.resize(frame_out, (frame_out.shape[1] / 2, frame_out.shape[0] / 2));


        out.write(frame_stabilized)