import numpy as np
import cv2
from person_location import *
from tqdm import tqdm

def best_shifted_bg(background_orig, frame, threshold, dim, para, hori):

    first_time = True
    min_err = 0

    for i in range(-para, para):
        for j in range(-hori, hori):

            M = np.float32([[1, 0, -i], [0, 1, -j]])
            dst1 = cv2.warpAffine(background_orig, M, dim)
            mask = cv2.absdiff(dst1, frame)
            _, mask = cv2.threshold(mask, threshold, 255, cv2.THRESH_BINARY)
            if first_time:
                first_time = False
                best_mask = mask
                min_err = np.sum(mask == 255)
            else:
                temp_err = np.sum(mask == 255)
                if temp_err < min_err:
                    min_err = temp_err
                    best_mask = mask

    return best_mask

def initial_mask(cap,n_frames, dim, bgs, out_extractes, out_mask):

    first = True
    list_up = []
    list_mid = []
    list_down = []

    for i in range(180):
        list_up.append(0)
        list_mid.append(0)
        list_down.append(0)

    # Start reading frames:
    frame_id =- 1
    bgs_index = 0
    first_frame = True
    print("Stage : Background Subtraction - calculate initial mask by optical flow")
    progbar = tqdm(total=n_frames)

    while True:

        frame_id += 1

        if frame_id % int(n_frames/len(bgs)) == 0:
            if bgs_index >= (len(bgs)-1):
                bgs_index = (len(bgs)-1)
            bg = bgs[bgs_index]
            bgs_index += 1
            hsv_bg = cv2.cvtColor(bg, cv2.COLOR_BGR2HSV)
            _, s_bg, v_bg = cv2.split(hsv_bg)
        ret, frame2 = cap.read()

        if not ret:
            break

        # Resized Frame:
        resized_frame = cv2.resize(frame2, dim)

        if first:
            first = False
            prvs = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
            prvs_bgr = resized_frame
            prvs_bgr_orig = frame2
            hsv_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2HSV)
            _, prev_s, prev_v = cv2.split(hsv_frame)

            continue

        # BGR
        b_frame, g_frame, r_frame = cv2.split(resized_frame)

        # HSV Space:
        hsv_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2HSV)
        h_frame, s_frame, v_frame = cv2.split(hsv_frame)
        _, s_binary = cv2.threshold(prev_s, 50, 255, cv2.THRESH_BINARY)

        # Calc Opitical Flow By Gray Frames:
        next = s_frame
        next = cv2.medianBlur(next, 5)

        optic_flow_params = {'prev': prvs,
                             'next': next,
                             'flow': None,
                             'pyr_scale': 0.5,
                             'levels': 3,
                             'winsize': 3,
                             'iterations': 1,
                             'poly_n': 7,
                             'poly_sigma': 1.2,
                             'flags': 0}

        flow = cv2.calcOpticalFlowFarneback(**optic_flow_params)
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])

        # Finding the 3 sectors:
        if first_frame:
            first_frame = False
            diff_first = cv2.absdiff(prev_s, s_bg)
            _, diff_first = cv2.threshold(diff_first, 17, 255, cv2.THRESH_BINARY)
            _, first_opticalflow_mask = cv2.threshold(mag, 50, 255, cv2.THRESH_BINARY)
            upper_crop, lower_crop = person_location(diff_first)
            upper_crop, lower_crop = upper_crop/dim[1], lower_crop/dim[1]

        s_binary[int(dim[1] * lower_crop):, :] = 1

        # Upper Masking:
        upper_optical_mask_param = 0.8
        _, upper_opticalflow_mask = cv2.threshold(mag, upper_optical_mask_param, 255, cv2.THRESH_BINARY)
        upper_mask = np.ones_like(mag)
        upper_mask[int(upper_crop * dim[1]):, :] = 0
        upper_opticalflow_mask[upper_mask <= 0] = 0

        # Middle Masking:
        middle_optical_flow_param = 0.2
        _, middle_opticalflow_mask = cv2.threshold(mag, middle_optical_flow_param, 255, cv2.THRESH_BINARY)
        middle_mask = np.ones_like(mag)
        middle_mask[:int(upper_crop * dim[1]), :] = 0  # put zeros where upper mask
        middle_mask[int(lower_crop * dim[1]):, :] = 0  # put zeros where lower mask
        middle_opticalflow_mask[middle_mask <= 0] = 0

        # Lower Masking:
        diff_gray = cv2.absdiff(prvs_bgr, bg)
        diff_mask_gray = cv2.cvtColor(diff_gray, cv2.COLOR_BGR2GRAY)
        _, diff_mask_gray = cv2.threshold(diff_mask_gray, 10, 255, cv2.THRESH_BINARY)
        diff_mask = best_shifted_bg(s_bg, prev_s, 17, dim, 3, 4)
        diff2 = cv2.absdiff(prev_v, v_bg)
        _, diff_mask2 = cv2.threshold(diff2, 40, 255, cv2.THRESH_BINARY)

        # Main Mask:
        mask = cv2.bitwise_or(upper_opticalflow_mask, middle_opticalflow_mask)
        mask = mask.astype(np.uint8)
        mask = mask.astype(np.uint8)
        diff_mask = cv2.bitwise_or(diff_mask, diff_mask2)
        mask[int(dim[1] * lower_crop):, :] = cv2.bitwise_or(mask[int(dim[1] * lower_crop):, :], diff_mask[int(dim[1] * lower_crop):, :])

        # Morphology:
        mask = cv2.medianBlur(mask, 7)
        kernel_dilate = np.ones((2, 2), np.uint8)
        mask[:int(dim[1] * lower_crop), :] = cv2.dilate(mask[:int(dim[1] * lower_crop), :], kernel_dilate, iterations=1)
        mask[s_binary <= 0] = 0
        mask = cv2.medianBlur(mask, 5)

        # Finding the largest object in Mask
        im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if len(contours) != 0:
            # the contours are drawn here
            mask_contour = np.zeros_like(mask)
            mask_contour = cv2.drawContours(mask_contour,
                                            [max(contours, key=cv2.contourArea)],
                                            -1,
                                            255,
                                            thickness=cv2.FILLED)

        head_mask = np.copy(mask_contour)
        head_mask[int(dim[1] * upper_crop):, :] = 0
        b_head = np.copy(b_frame)
        g_head = np.copy(g_frame)
        r_head = np.copy(r_frame)
        b_head[head_mask <= 0] = 0
        g_head[head_mask <= 0] = 0
        r_head[head_mask <= 0] = 0
        bgr_head = cv2.merge([b_head, g_head, r_head])
        hsv_frame_head = cv2.cvtColor(bgr_head, cv2.COLOR_BGR2HSV)
        h_head, _, _ = cv2.split(hsv_frame_head)

        # Take only middle part from mask and calculate its hue hist:
        body_mask = np.copy(mask_contour)
        body_mask[int(dim[1] * lower_crop):, :] = 0
        body_mask[:int(dim[1] * upper_crop), :] = 0
        b_mid = np.copy(b_frame)
        g_mid = np.copy(g_frame)
        r_mid = np.copy(r_frame)
        b_mid[body_mask <= 0] = 0
        g_mid[body_mask <= 0] = 0
        r_mid[body_mask <= 0] = 0
        bgr_mid = cv2.merge([b_mid, g_mid, r_mid])
        hsv_frame_mid = cv2.cvtColor(bgr_mid, cv2.COLOR_BGR2HSV)
        h_mid, _, _ = cv2.split(hsv_frame_mid)

        # Take only lower part from mask and calculate its hue hist:
        floor_mask = np.copy(mask_contour)
        floor_mask[:int(dim[1] * lower_crop), :] = 0
        b_floor = np.copy(b_frame)
        g_floor = np.copy(g_frame)
        r_floor = np.copy(r_frame)
        b_floor[floor_mask <= 0] = 0
        g_floor[floor_mask <= 0] = 0
        r_floor[floor_mask <= 0] = 0

        h_floor, _, _ = cv2.split(hsv_frame[:int(dim[1] * lower_crop), :])
        b_prvs, g_prvs, r_prvs = cv2.split(prvs_bgr_orig)
        mask_contour = cv2.resize(mask_contour, (dim[0]*2, dim[1]*2))
        b_prvs[mask_contour <= 0] = 255
        g_prvs[mask_contour <= 0] = 255
        r_prvs[mask_contour <= 0] = 255
        bgr = cv2.merge([b_prvs, g_prvs, r_prvs])

        # save mask and bgr+mask
        mask_contour = cv2.merge([mask_contour, mask_contour, mask_contour])
        out_mask.write(mask_contour)
        out_extractes.write(bgr)

        # calc hist:
        hist_head = cv2.calcHist([h_head], [0], None, [180], [1, 180])
        hist_mid = cv2.calcHist([h_mid], [0], None, [180], [1, 180])
        hist_floor = cv2.calcHist([h_floor], [0], None, [180], [1, 180])

        # HUE
        for i in range(180):
            if hist_head[i] > 0:
                list_up[i] += 1
            if hist_floor[i] >= max(hist_floor)*0.4:
                list_down[i] += 1
            if hist_mid[i] > 0:
                list_mid[i] += 1

        prvs = next
        prev_v = v_frame
        prev_s = s_frame
        prvs_bgr = resized_frame
        prvs_bgr_orig = frame2
        progbar.update(1)

    cv2.destroyAllWindows()

    return list_up, list_mid, list_down, lower_crop, upper_crop