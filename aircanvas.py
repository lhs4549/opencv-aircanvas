import cv2
import numpy as np

# 1. 추적할 색상 범위 (HSV 트랙바로 직접 캘리브레이션한 값)
lower_color = np.array([9, 75, 134])
upper_color = np.array([21, 134, 255])

# 2. 상단 팔레트 구성: (라벨, 색상) - 첫 칸은 지우개
palette = [
    ("CLEAR", (100, 100, 100)),
    ("BLUE",  (255, 0, 0)),
    ("GREEN", (0, 255, 0)),
    ("RED",   (0, 0, 255)),
    ("YELLOW", (0, 255, 255)),
]
bar_height = 60
current_color = palette[3][1]  # 기본 선택 색상: 빨간색
prev_center = None  # 바로 이전 프레임에서의 물체 위치 (선을 이어그리기 위함)
    
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Camera open failed!")
    exit()

ret, frame = cap.read()
if not ret:
    print("웹캠에서 영상을 가져올 수 없습니다.")
    exit()

frame_h, frame_w = frame.shape[:2]
swatch_w = frame_w // len(palette)

canvas = np.zeros_like(frame)  # 그려진 선들을 계속 누적해서 저장하는 도화지


def draw_palette(img):
    for i, (label, color) in enumerate(palette):
        x1 = i * swatch_w
        x2 = x1 + swatch_w
        cv2.rectangle(img, (x1, 0), (x2, bar_height), color, -1)
        cv2.putText(img, label, (x1 + 10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # 거울처럼 좌우 반전

    # 3. 색상 검출
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # 4. 노이즈 제거
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # 5. 물체 위치 찾기
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        largest = max(contours, key=cv2.contourArea)

        if cv2.contourArea(largest) > 300:
            (x, y), radius = cv2.minEnclosingCircle(largest)
            center = (int(x), int(y))

            if center[1] < bar_height:
                # 팔레트 영역에 들어왔다면: 어느 칸인지 계산해서 선택 처리
                index = min(center[0] // swatch_w, len(palette) - 1)
                label, color = palette[index]

                if label == "CLEAR":
                    canvas = np.zeros_like(frame)
                else:
                    current_color = color

                prev_center = None  # 팔레트를 고르는 동안은 그림을 이어그리지 않음
            else:
                if prev_center is not None:
                    # 이전 위치와 현재 위치를 선으로 이어서 펜으로 그리듯 부드럽게 연결
                    cv2.line(canvas, prev_center, center, current_color, 5)
                prev_center = center

            # 현재 추적 위치를 노란 원으로 표시 (커서 역할)
            cv2.circle(frame, center, int(radius), (0, 255, 255), 2)
    else:
        prev_center = None  # 물체가 안 보이면(펜을 뗀 상태) 다음에 엉뚱하게 안 이어지도록 초기화

    # 6. 원본 위에 캔버스를 마스크 방식으로 자연스럽게 합성 (크로마키와 같은 원리)
    canvas_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, canvas_mask = cv2.threshold(canvas_gray, 1, 255, cv2.THRESH_BINARY)
    canvas_mask_inv = cv2.bitwise_not(canvas_mask)

    frame_bg = cv2.bitwise_and(frame, frame, mask=canvas_mask_inv)
    canvas_fg = cv2.bitwise_and(canvas, canvas, mask=canvas_mask)
    result = cv2.add(frame_bg, canvas_fg)

    draw_palette(result)  # 팔레트는 항상 맨 위에 보이도록 마지막에 그림

    cv2.imshow('Air Canvas', result)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):
        canvas = np.zeros_like(frame)
        prev_center = None
    elif key == ord('p'):
        # 팔레트 없이 키보드만으로도 색상 순환 변경 가능
        colors_only = [c for _, c in palette[1:]]
        idx = (colors_only.index(current_color) + 1) % len(colors_only) if current_color in colors_only else 0
        current_color = colors_only[idx]
    elif key == ord('q') or key == 27:
        break

cap.release()
cv2.destroyAllWindows()