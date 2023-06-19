'''

文件: Camera_Calibration.py
功能: 代码实现了基于Opencv进行摄像头标定的功能
作者: 李维、李昊翀、赵桓宇

'''
import numpy as np
import cv2

# 棋盘格尺寸
pattern_size = (8, 6)

# 方格块大小（单位：cm）
square_size = 2.4

# 创建棋盘格模板
pattern_points = np.zeros((np.prod(pattern_size), 3), np.float32)
pattern_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2) * square_size

# 存储图像和对象点的列表
obj_points = []
img_points = []

# 创建用于标定的窗口
cv2.namedWindow("Calibration")

# 打开摄像头
cap = cv2.VideoCapture(1)

while True:
    # 读取摄像头图像
    ret, frame = cap.read()
    if not ret:
        break

    # 寻找棋盘格角点
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    found, corners = cv2.findChessboardCorners(gray, pattern_size)

    # 如果找到棋盘格角点
    if found:
        # 绘制棋盘格角点并显示图像
        cv2.drawChessboardCorners(frame, pattern_size, corners, found)
        cv2.imshow("Calibration", frame)

        # 按下空格键进行标定
        if cv2.waitKey(1) & 0xFF == ord(" "):
            # 添加对象点和图像点到列表
            obj_points.append(pattern_points)
            img_points.append(corners)

    else:
        cv2.imshow("Calibration", frame)

    # 按下Esc键退出标定
    if cv2.waitKey(1) & 0xFF == 27:
        break

# 标定相机
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
    obj_points, img_points, gray.shape[::-1], None, None
)

# 保存标定结果
np.savez("Calibration_Results.npz", mtx=mtx, dist=dist)

# 关闭摄像头和窗口
cap.release()
cv2.destroyAllWindows()
