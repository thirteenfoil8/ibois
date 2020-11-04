from cv2 import *
import numpy as np
from cv2 import aruco
import sys


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


# Function that reads the boards and computes the position X-Y of the markers' corners
# Modified a little bit from: https://mecaruco.readthedocs.io/en/latest/notebooks_rst/aruco_calibration.html#
# Input: calibration images
# Output: positions of the corners of the markers, their id, size of the board
def read_chessboards(images):
    print("CAMERA CALIBRATION")
    print("POSE ESTIMATION STARTS:")
    allCorners = []
    allIds = []
    decimator = 0
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.00001)

    for im in images:
        print("=> Processing image {0}".format(im))
        frame = cv2.imread(im)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, aruco_dict)

        if len(corners)>0:
            # SUB PIXEL DETECTION
            for corner in corners:
                cv2.cornerSubPix(gray, corner,
                                 winSize = (3,3),
                                 zeroZone = (-1,-1),
                                 criteria = criteria)
            res2 = cv2.aruco.interpolateCornersCharuco(corners,ids,gray,board)
            if res2[1] is not None and res2[2] is not None and len(res2[1])>3 and decimator%1==0:
                allCorners.append(res2[1])
                allIds.append(res2[2])
        decimator+=1
    imsize = gray.shape
    return allCorners,allIds,imsize


# Function the computes the optical coefficients with the position of each marker on the board
# Modified a little bit from: https://mecaruco.readthedocs.io/en/latest/notebooks_rst/aruco_calibration.html#
# Input: positions of the corners of the markers, their id, size of the board
# Output: Optical coefficients and rotation,position of the markers
def calibrate_camera(allCorners,allIds,imsize):
    cameraMatrixInit = np.array([[ 1000.,    0., imsize[0]/2.],
                                 [    0., 1000., imsize[1]/2.],
                                 [    0.,    0.,           1.]])

    distCoeffsInit = np.zeros((5,1))
    flags = (cv2.CALIB_USE_INTRINSIC_GUESS + cv2.CALIB_RATIONAL_MODEL + cv2.CALIB_FIX_ASPECT_RATIO)
    (ret, camera_matrix, distortion_coefficients0,
     rotation_vectors, translation_vectors,
     stdDeviationsIntrinsics, stdDeviationsExtrinsics,
     perViewErrors) = cv2.aruco.calibrateCameraCharucoExtended(
                      charucoCorners=allCorners,
                      charucoIds=allIds,
                      board=board,
                      imageSize=imsize,
                      cameraMatrix=cameraMatrixInit,
                      distCoeffs=distCoeffsInit,
                      flags=flags,
                      criteria=(cv2.TERM_CRITERIA_EPS & cv2.TERM_CRITERIA_COUNT, 10000, 1e-9))
    return ret, camera_matrix, distortion_coefficients0, rotation_vectors, translation_vectors


# Saves the optical coefficients into a .yaml
# Input: camera and distortion coefficients
def saveCoefficients(mtx, dist):
    cv_file = cv2.FileStorage(datadir + "calibrationCoefficients.yaml", cv2.FILE_STORAGE_WRITE)
    cv_file.write("camera_matrix", mtx)
    cv_file.write("dist_coeff", dist)
    cv_file.release()
    print("Camera coefficients saved!")


# Main function
if __name__ == '__main__':
    cam_number, aruco_size = loadConfiguration()
    cap = cv2.VideoCapture(cam_number,CAP_DSHOW)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    i = 0
    print("Press 'V' on your keyboard to make calibrations images and then press 'C' to calibrate the camera.")
    print("Or if you want to quit just press 'Q'")
    datadir = "../../calibration/"
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    board = aruco.CharucoBoard_create(7, 5, 1, .8, aruco_dict)

    while True:
        ret, frame = cap.read()
        try:
            cv2.imshow('Camera_calibration', frame)
        except:
            print("The camera number you enter doesn't exist")
            input("Press Enter to continue...")
            sys.exit(1)
        key = cv2.waitKey(3) & 0xFF
        if key == ord('v'):
            i = i+ 1
            print("Calibration image number {}".format(i))
            imwrite(datadir +"calibration_image_{}.png".format(i), frame)  # save image

        if key == ord('c'):  # calibration
            cap.release()
            cv2.destroyAllWindows()
            images = np.array([datadir + f for f in os.listdir(datadir) if f.endswith(".png")])
            allCorners, allIds, imsize = read_chessboards(images)
            ret, mtx, dist, rvecs, tvecs = calibrate_camera(allCorners, allIds, imsize)
            print("Calibration is completed")
            saveCoefficients(mtx, dist)
            break

        if key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            break

        if cv2.getWindowProperty('Camera_calibration', cv2.WND_PROP_VISIBLE) < 1:
            cap.release()
            cv2.destroyAllWindows()
            break
    input("Press Enter to continue...")
    sys.exit(1)
