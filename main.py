import cv2
import numpy as np

fg = cv2.imread('chroma.jpg')
bg = cv2.imread('lena.jpg')

# 배경 크기에 맞춰 전경을 리사이즈함 (합성하려면 크기가 같아야 함)
fg = cv2.resize(fg, (bg.shape[1], bg.shape[0]))

# 2. 배경 제거: 녹색 영역 찾기
hsv = cv2.cvtColor(fg, cv2.COLOR_BGR2HSV)

# 녹색의 HSV 범위
lower_green = (40, 80, 80)
upper_green = (80, 255, 255)
mask_green = cv2.inRange(hsv, lower_green, upper_green)

# 3. 전경 추출: 마스크를 반전시켜 피사체(사람)만 남기기
mask_fg = cv2.bitwise_not(mask_green)           # 녹색이 아닌 부분(사람)만 흰색
person = cv2.bitwise_and(fg, fg, mask=mask_fg)  # 사람 영역만 남기고 나머지는 검은색

# 4. 배경 구멍 뚫기: lena.jpg에서 사람이 들어갈 자리를 검은색으로 비움
# mask_green은 "녹색이었던 부분(=사람이 아닌 부분)"만 255이므로,
# 이 마스크로 bg를 걸러내면 사람 자리만 자동으로 검은색(구멍)이 됨
background_hole = cv2.bitwise_and(bg, bg, mask=mask_green)

# 5. 합성: 사람 영역 + 구멍 뚫린 배경 영역을 더하기
dst = cv2.add(person, background_hole)

cv2.imshow('Hole', background_hole)
cv2.imshow('Person', person)
cv2.imshow('Result', dst)
cv2.waitKey(0)
cv2.destroyAllWindows()