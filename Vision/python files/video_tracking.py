import numpy as np
from cv2 import *
from cv2 import aruco
import math
import sys


# This function loads the optical coefficients of the camera to correct
# Inspired by: https://github.com/aliyasineser/GraduationProjectII/blob/master/RelativePositionTest.py
# Returns the camera matrix and the distortion matrix
def loadCoefficients():
    datadir = "../../calibration/"
    cv_file = cv2.FileStorage(datadir+"calibrationCoefficients.yaml", cv2.FILE_STORAGE_READ)
    camera_matrix = cv_file.getNode("camera_matrix").mat()
    dist_matrix = cv_file.getNode("dist_coeff").mat()
    cv_file.release()
    print("Coeff retrieved")
    return [camera_matrix, dist_matrix]


# Function that loads the camera and Aruco configuration from the configuration file :"config_file.txt" ,
# config_file.txt needs to be 2 directories up of the working directory
# Returns the camera number and the size of the Aruco used
def loadConfiguration():
    try:
        config = open("..\\..\\config_file.txt", "r+")
    except:
        print("config_file.txt could not be located!")
        input("Press Enter to continue...")
        sys.exit(1)

    line = config.readline()
    elements = line.split(':', 1)
    if len(elements) < 2:
        print("Please enter a camera number in the config_file")
        input("Press Enter to continue...")
        sys.exit(1)
    else:
        try:
            cam_num = int(elements[1].strip())
        except:
            print("Please enter a camera number in the config_file")
            input("Press Enter to continue...")
            sys.exit(1)

    line = config.readline()
    elements = line.split(':', 1)
    if len(elements) < 2:
        print("Please enter the length of an Aruco in the config_file")
        input("Press Enter to continue...")
        sys.exit(1)
    else:
        try:
            size_Aruco = float(elements[1].strip())
        except:
            print("Please enter the length of an Aruco in the config_file")
            input("Press Enter to continue...")
            sys.exit(1)

    config.close()
    return cam_num, size_Aruco


# Function that computes the Euler angles of a marker according to the XYZ convention
# Input: rotation matrix
# Output: Euler angles
def rotationMatrixToEulerAngles(R):
    x=math.atan2(-R[1, 2], R[2, 2])
    y= math.atan2(R[0, 2], math.sqrt((R[0,0]*R[0,0])+(R[0,1]*R[0,1])))
    z=math.atan2(-R[0, 1], R[0, 0])
    return np.array([x, y, z])


# Function that tracks live the Aruco position and orientation and display the information on the console
# Inspired by: https://github.com/aliyasineser/GraduationProjectII/blob/master/RelativePositionTest.py
# Input: optical camera matrix coefficients, camera distortion coefficients and the size of an Aruco marker
def track(matrix_coefficients, distortion_coefficients, size_of_aruco):
    button_pressed = 0
    markerTvecList = []
    markerRvecList = []
    counter = 0
    while True:
        if button_pressed ==1:
            break
        ret, frame = cap.read()
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        except:
            print("The camera number you enter doesn't exist")
            input("Press Enter to continue...")
            sys.exit(1)
        aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)  # Use 6x6 dictionary to find markers
        parameters = aruco.DetectorParameters_create()  # Marker detection parameters
        corners, ids, rejected_img_points = aruco.detectMarkers(gray, aruco_dict,
                                                                parameters=parameters,
                                                                cameraMatrix=matrix_coefficients,
                                                                distCoeff=distortion_coefficients)
        num = ids
        if button_pressed ==1:
            break
        if np.all(ids is not None):
            del markerTvecList[:]
            del markerRvecList[:]
            for i in range(0, len(ids)):
                rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corners[i], size_of_aruco, matrix_coefficients, distortion_coefficients)
                rot_mat=np.matrix(cv2.Rodrigues(rvec)[0])
                ypr = rotationMatrixToEulerAngles(rot_mat)
                counter = counter + 1
                if counter == 6:
                    os.system("cls")
                    print("Rotation Yaw, Pitch, Roll angles [degree]:", ypr/math.pi*180)
                    print("Position X Y Z [mm]:", tvec[0][0]*1000)
                    print("_________________________________________________________________________")
                    counter = 0

                (rvec - tvec).any()
                markerRvecList.append(rvec)
                markerTvecList.append(tvec)
                aruco.drawAxis(frame, matrix_coefficients, distortion_coefficients, rvec, tvec, 0.05)
                aruco.drawDetectedMarkers(frame, corners, num)
                if button_pressed == 1:
                    break

        cv2.imshow('video_tracking', frame)
        key = cv2.waitKey(3) & 0xFF
        if key == ord('q'):  # Quit
            break
        if cv2.getWindowProperty('video_tracking', cv2.WND_PROP_VISIBLE) < 1:
            button_pressed = 1
        if button_pressed ==1:
            break
    cap.release()
    cv2.destroyAllWindows()


# Main function
if __name__ == '__main__':

    mtx, dist = loadCoefficients()
    cam_number, aruco_size = loadConfiguration()
    cap = cv2.VideoCapture(cam_number, CAP_DSHOW)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    print("Starting tracking sequence.")
    track(mtx, dist, aruco_size)
    input("Press Enter to continue...")
    sys.exit(1)
