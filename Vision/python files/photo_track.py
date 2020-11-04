from cv2 import *
from cv2 import aruco
import sys
import math


# Function that loads the camera and Aruco configuration from the configuration file :"config_file.txt" ,
# config_file.txt needs to be 2 directories up of the working directory
# Returns the camera number and the size of the Aruco used
def loadConfiguration():
    try:
        config = open("..\\..\\config_file.txt", "r+")
    except:
        output = open("..\\..\\output.txt", "w")
        print("Error:0000", file=output)
        print("config_file.txt could not be located!", file=output)
        output.close()
        sys.exit(1)

    line = config.readline()
    elements = line.split(':', 1)
    if len(elements) < 2:
        output = open("..\\..\\output.txt", "w")
        print("Error:0000", file=output)
        print("Please enter a camera number in the config_file", file=output)
        output.close()
        sys.exit(1)
    else:
        try:
            cam_num = int(elements[1].strip())
        except:
            output = open("..\\..\\output.txt", "w")
            print("Error:0000", file=output)
            print("Please enter a camera number in the config_file", file=output)
            output.close()
            sys.exit(1)

    line = config.readline()
    elements = line.split(':', 1)
    if len(elements) < 2:
        output = open("..\\..\\output.txt", "w")
        print("Error:0000", file=output)
        print("Please enter the length of an Aruco in the config_file", file=output)
        output.close()
        sys.exit(1)
    else:
        try:
            size_Aruco = float(elements[1].strip())
        except:
            output = open("..\\..\\output.txt", "w")
            print("Error:0000", file=output)
            print("Please enter the length of an Aruco in the config_file", file=output)
            output.close()
            sys.exit(1)

    config.close()
    return cam_num, size_Aruco


# This function loads the optical coefficients of the camera to correct
# Inspired by: https://github.com/aliyasineser/GraduationProjectII/blob/master/RelativePositionTest.py
# Returns the camera matrix and the distortion matrix
def loadCoefficients():
    datadir = "../../calibration/"
    cv_file = cv2.FileStorage(datadir+"calibrationCoefficients.yaml", cv2.FILE_STORAGE_READ)
    camera_matrix = cv_file.getNode("camera_matrix").mat()
    dist_matrix = cv_file.getNode("dist_coeff").mat()
    cv_file.release()
    return [camera_matrix, dist_matrix]


# Functions detects the Aruco markers using a special dictionary and computes their position and orientation
# Inspired by: https://mecaruco.readthedocs.io/en/latest/notebooks_rst/aruco_calibration.html#
# Input: Image taken by the camera, size of an Aruco marker
# Returns the position, rotation, an ID of the closest marker relative to the camera
def aruco_detection(frame, size_of_marker):
    mtx, dist = loadCoefficients()
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    except:
        output = open("..\\..\\output.txt", "w")
        print("Error:0000", file=output)
        print("The camera number you enter doesn't exist", file=output)
        output.close()
        sys.exit(1)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    parameters = aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    if ids is None:
        imwrite('..\\..\\vision_aruco.png', frame)
        output = open("..\\..\\output.txt", "w")
        print("Error:0000", file=output)
        print("No markers detected", file=output)
        output.close()
        cam.release()
        cv2.destroyAllWindows()
        sys.exit(1)

    closest = 0
    marker_index = 0
    for i in range(len(ids)):
        rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(corners, size_of_marker, mtx, dist)

        if (norm(tvecs[i][0]) < closest) or (i == 0):
            closest = norm(tvecs[i][0])
            marker_index = i
    return rvecs[marker_index][0], tvecs[marker_index][0], ids[marker_index][0]


# Main function
if __name__ == '__main__':
    cam_number, aruco_size = loadConfiguration()
    cam = VideoCapture(cam_number, CAP_DSHOW)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    s, frame = cam.read()
    rvec, tvec, marker_id = aruco_detection(frame, aruco_size)
    cam.release()
    cv2.destroyAllWindows()

    theta = norm(rvec)
    quaternions = [math.cos(theta/2), rvec[0]*math.sin(theta/2)/norm(rvec), rvec[1]*math.sin(theta/2)/norm(rvec), rvec[2]*math.sin(theta/2)/norm(rvec)]
    x_coord = tvec[0]*1000
    y_coord = tvec[1]*1000
    z_coord = tvec[2]*1000

    output = open("..\\..\\output.txt", "w")
    print("Position X Y Z [mm]:", x_coord, y_coord, z_coord, file=output)
    print("Quaternion q0 q1 q2 q3:", quaternions[0], quaternions[1], quaternions[2], quaternions[3], file=output)
    print("Marker_ID:", marker_id, file=output)
    output.close()
    imwrite('..\\..\\vision_aruco.png', frame)
    sys.exit(1)
