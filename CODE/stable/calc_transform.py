# Import numpy and OpenCV
import numpy as np
import cv2
import matplotlib.pyplot as plt
import json


def calc_transform(cap, n_frames, dim, projective_transform):

    # Read input video
    data = {}
    # Read first frame
    _, prev = cap.read()
    prev = cv2.resize(prev, dim)
    # Convert frame to grayscale
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

    # Pre-define transformation-store array
    transforms_homography = np.zeros((n_frames - 1, 9), np.float32)

    for i in range(n_frames - 1):
        # Detect feature points in previous frame
        prev_pts = cv2.goodFeaturesToTrack(prev_gray,
                                           maxCorners=200,
                                           qualityLevel=0.1,
                                           minDistance=40,
                                           blockSize=5)

        # Read next frame
        success, curr = cap.read()
        if not success:
            break
        curr = cv2.resize(curr, dim)

        # Convert to grayscale
        curr_gray = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY)

        # Calculate optical flow (i.e. track feature points)
        curr_pts, status, err = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, prev_pts, None)

        # Sanity check
        assert prev_pts.shape == curr_pts.shape

        # Filter only valid points
        idx = np.where(status == 1)[0]
        prev_pts = prev_pts[idx]
        curr_pts = curr_pts[idx]

        # Find transformation matrix
        m, m_status = cv2.findHomography(prev_pts, curr_pts)
        data[str(i)] = []
        data[str(i)].append({
            '00': str(m[0][0]),
            '01': str(m[0][1]),
            '02': str(m[0][2]),
            '10': str(m[1][0]),
            '11': str(m[1][1]),
            '12': str(m[1][2]),
            '20': str(m[2][0]),
            '21': str(m[2][1]),
            '22': str(m[2][2])
        })
        # Adding curr transform to tramsforms vector
        transforms_homography[i] = m.reshape(-1)

        # Move to next frame
        prev_gray = curr_gray

        print("Frame: " + str(i) + "/" + str(n_frames) + " -  Tracked points : " + str(len(prev_pts)))

    with open(projective_transform, 'w') as outfile:
        json.dump(data, outfile)
    return transforms_homography