import cv2
import numpy as np


def nothing(x):
    pass


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Camera open failed!")
    exit()

cv2.namedWindow('Trackbars')
# 슬라이더(트랙바) 6개: Hue/Saturation/Value 각각의 최소~최대값
cv2.createTrackbar('H min', 'Trackbars', 0, 179, nothing)
cv2.createTrackbar('H max', 'Trackbars', 179, 179, nothing)
cv2.createTrackbar('S min', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('S max', 'Trackbars', 255, 255, nothing)
cv2.createTrackbar('V min', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('V max', 'Trackbars', 255, 255, nothing)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 슬라이더에서 현재 값 읽어오기
    h_min = cv2.getTrackbarPos('H min', 'Trackbars')
    h_max = cv2.getTrackbarPos('H max', 'Trackbars')
    s_min = cv2.getTrackbarPos('S min', 'Trackbars')
    s_max = cv2.getTrackbarPos('S max', 'Trackbars')
    v_min = cv2.getTrackbarPos('V min', 'Trackbars')
    v_max = cv2.getTrackbarPos('V max', 'Trackbars')

    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(hsv, lower, upper)

    cv2.imshow('Camera', frame)
    cv2.imshow('Mask', mask)  # 펜만 하얗게 남을 때까지 슬라이더 조절

    if cv2.waitKey(1) == 27:  # ESC로 종료
        print(f"lower_color = np.array([{h_min}, {s_min}, {v_min}])")
        print(f"upper_color = np.array([{h_max}, {s_max}, {v_max}])")
        break

cap.release()
cv2.destroyAllWindows()