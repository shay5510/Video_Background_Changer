import matplotlib.pyplot as plt
import numpy as np
import cv2
from sklearn.neighbors import KernelDensity
import json
from tqdm import tqdm
import time
from final_project_stages import *
from stable.stabilize import stabilize
from background_subtraction.background_subtraction import background_subtraction

# Inputs:
input_video="../Input/INPUT.mp4"
background="../Input/background.jpg"

# Outputs:

# stabilization stage:
stabilized_video="../Outputs/stabilize.avi"
projective_transform="../Temp/data.txt"

# daniel stabilized video:
daniel_stabilized_video ="../Input/Stabilized_Example_INPUT.avi"
# daniel_stabilized_video="../Input/INPUT.mp4"


# background subtraction:
extracted_video = "../Outputs/extracted.avi"
binary_video = "../Outputs/binary.avi"

# matting:
matted_video="../Outputs/matted.avi"
alpha_video="../Outputs/alpha.avi"
unstabilized_alpha_video="../Outputs/unstabilized_alpha.avi"

# tracking:
output_video="../Outputs/OUTPUT.avi"

# RunTimeLog :
output_log="../Outputs/RunTimeLog.txt"

# initial time:
list_of_times=["Stabilization : -1 ", "Background Subtraction : -1", "Matting : -1 ", "Tracking : -1"]


def main():
    start_time = time.time()

    """
     ########################
     #     Stabilization    #
     ########################
    """
    # stabilize_total_time=stabilize(input_video, stabilized_video, projective_transform)
    # list_of_times[0] = stabilize_total_time


    #################################
    #     Background Subtraction    #
    #################################

    # background_subtraction_total_time = background_subtraction(daniel_stabilized_video, extracted_video, binary_video)
    # list_of_times[1] = background_subtraction_total_time
    #


    ##################
    #    Matting     #
    ##################
    #
    # matting_total_time = matting(projective_transform,
    #                     background,
    #                     binary_video,
    #                     extracted_video,
    #                     daniel_stabilized_video,
    #                     matted_video,
    #                     alpha_video,
    #                     unstabilized_alpha_video)
    #
    # list_of_times[2] =matting_total_time
    ###################
    #    Tracking     #
    ###################

    #choose mode : manual or automatic :
    #mode="manual"
    mode="automatic"
    tracking_total_time=tracking(mode,matted_video,output_video)
    list_of_times[3] = tracking_total_time

    #####################
    #     RunTimeLog    #
    #####################

    finish_time=time.time()
    total_time_seconds=finish_time-start_time
    write_times_to_log(total_time_seconds,list_of_times,output_log)
    return

if __name__=="__main__":
    main()



