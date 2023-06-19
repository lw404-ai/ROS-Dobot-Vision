'''

文件: Main.py
功能: 
    1. 代码实现了基于Opencv进行物块坐标捕获并转换为机械臂坐标
    2. 最后实现了全部物块执行码垛到指定点、依据物块颜色进行分拣、指定物块移动到指定点的功能
作者: 李维

'''
#++++++++++++++++++++ 1. 导入所需的包文件 ++++++++++++++++++++
import sys

# 通过从sys.path中移除Kinetic版本的Python库该路径，为了避免导入cv2引起环境冲突
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')

import numpy as np
import cv2
import os
import subprocess
from Coordinate_Transformation import xy_main

#++++++++++++++++++++ 2. 定义基础的使用函数 ++++++++++++++++++++
red_list = ["red"]      # 用于储存红色物块的机械臂坐标
green_list = ["green"]  # 用于储存绿色物块的机械臂坐标

# 定义command_use()函数, 用于将"rosrun dobot Goal"指令传入shell终端并运行
def command_use():
    # 要执行的命令
    command = "rosrun dobot Goal"

    # 使用subprocess模块调用shell命令
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    # 输出命令执行结果
    if output:
        print("\n\nshell命令输出:\n", output.decode('utf-8', errors='ignore'))
    if error:
        print("\n\nshell错误信息:\n", error.decode('utf-8', errors='ignore'))

# 定义file_replace()函数, 用于去除文本文件中的全部空格
def file_replace(file_path):
    # 读取文件内容
    with open(file_path, 'r') as file:
        content = file.read()

    # 去除空格
    content = content.replace(' ', '')

    # 将修改后的内容写回文件
    with open(file_path, 'w') as file:
        file.write(content)

# 定义mouse_click()函数, 将鼠标指定点的机械臂坐标写入到Target_Coordinates文件
def mouse_click(event, x, y, flags, para):
    # def_list值含义: (1: 全部物块执行码垛到指定点, 2: 依据物块颜色进行分拣)
    # 判断条件: 左键鼠标点击且def_list中值为1或2
    if event == cv2.EVENT_LBUTTONDOWN and (def_list == ["1"] or def_list == ["3"]):
        print(f"指定坐标点: {x},{y}")
        goal_x = ((set_goal1 - x) / set_xy)             # 指定点的机械臂坐标goal_x
        goal_y = ((y - set_goal2) / set_xy)             # 指定点的机械臂坐标goal_y
        def_list.append(list(xy_main(goal_x, goal_y)))  # 将坐标加入到def_list
        file_path = 'Target_Coordinates'
        file = open(file_path, 'a')
        file.write(f"\n{def_list}")                     # 将def_list写入Target_Coordinates文件
        file.close()
        file_replace(file_path)                         # 调用file_replace()函数, 去除文本文件中的全部空格
        command_use()                                   # 调用command_use()函数, 将"rosrun dobot Goal"指令传入shell终端并运行

        return 0

#++++++++++++++++++++ 3. 定义基础的参数变量 ++++++++++++++++++++
# 指定在图像上绘制文本时使用简单而清晰的字体样式
font = cv2.FONT_HERSHEY_SIMPLEX

# 定义各种颜色阈值范围用于颜色检测(红色存在两部分)
lower_red1 = np.array([0, 100, 100])      # 红色阈值下限
higher_red1 = np.array([10, 255, 255])    # 红色阈值上限

lower_red2 = np.array([160, 100, 100])    # 红色阈值下限
higher_red2 = np.array([179, 255, 255])   # 红色阈值上限

lower_yellow = np.array([11, 43, 36])     # 黄色阈值下限
higher_yellow = np.array([34, 255, 255])  # 黄色阈值上限

lower_blue = np.array([90, 43, 43])       # 蓝色阈值下限
higher_blue = np.array([140, 255, 255])   # 蓝色阈值上限

lower_green = np.array([35, 43, 46])      # 绿色阈值下限
higher_green = np.array([77, 255, 255])   # 绿色阈值上限

# 加载摄像头标定结果参数
calibration_data = np.load('Calibration_Results.npz')
mtx = calibration_data['mtx']
dist = calibration_data['dist']

# 加载摄像头
cap = cv2.VideoCapture(0) # 依据实际情况修改

# 定义使用的全局变量
global set_xy, ycx, ycy, set_goal1, set_goal2

#++++++++++++++++++++ 4. 最终功能的解决方案 ++++++++++++++++++++
while True:
    # 读取摄像头画面
    ret, frame_no_calibration = cap.read()

    # 应用摄像头标定结果
    # frame = cv2.undistort(frame_no_calibration, mtx, dist)
    
    frame = frame_no_calibration
    # *可选* 指定照片作为图像传入
    # frame = cv2.imread('test.jpg')

    # 图像像素缩放尺寸到(648, 486)
    image = cv2.resize(frame, dsize=(648, 486))

    # 将图像的颜色格式BGR转换成HSV, 便于颜色检测的使用
    img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    mask_red1 = cv2.inRange(img_hsv, lower_red1, higher_red1)        # 过滤出红色部分，获得红色的掩膜
    mask_red2 = cv2.inRange(img_hsv, lower_red2, higher_red2)        # 过滤出红色部分，获得红色的掩膜
    mask_red = cv2.medianBlur(mask_red1 + mask_red2, 7)              # 使用中值滤波，去除图像中的噪点

    mask_yellow = cv2.inRange(img_hsv, lower_yellow, higher_yellow)  # 过滤出黄色部分，获得黄色的掩膜
    mask_yellow = cv2.medianBlur(mask_yellow, 7)                     # 使用中值滤波，去除图像中的噪点

    mask_blue = cv2.inRange(img_hsv, lower_blue, higher_blue)        # 过滤出蓝色部分，获得蓝色的掩膜
    mask_blue = cv2.medianBlur(mask_blue, 7)                         # 使用中值滤波，去除图像中的噪点

    mask_green = cv2.inRange(img_hsv, lower_green, higher_green)     # 过滤出绿色部分，获得绿色的掩膜
    mask_green = cv2.medianBlur(mask_green, 7)                       # 使用中值滤波，去除图像中的噪点

    cnts1, hierarchy1 = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)     # 轮廓检测-红色
    cnts2, hierarchy2 = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)    # 轮廓检测-蓝色
    cnts3, hierarchy3 = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测-黄色
    cnts4, hierarchy4 = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)   # 轮廓检测-绿色

    image = image.copy() # 创建image的副本，在后续的处理中使用

    for cnt in cnts3:    # 对黄色区域进行检测定位并处理
        (x, y, w, h) = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
        rect = cv2.minAreaRect(cnt)           # 得到完全包围轮廓的最小面积外界矩形的(中心坐标(x, y), (宽,高), 旋转角度)
        area = cv2.contourArea(cnt)           # 获得该区域的的面积
        if area < 2000:                       # 区域面积小于2000就跳过
            continue

        box = cv2.boxPoints(rect)             # 获取最小面积外接矩形的4个顶点坐标
        box = np.intp(box)                    # 取整计算

        # 计算坐标纸的方格-长-像素值
        set_x1 = box[1][0] - box[0][0]
        set_x2 = box[2][0] - box[3][0]

        # 计算坐标纸的方格-宽-像素值
        set_y1 = box[3][1] - box[0][1]
        set_y2 = box[2][1] - box[1][1]

        # 求平均值, 为接下来像素坐标转换坐标纸视角做准备
        set_xy = (set_x1 + set_x2 + set_y1 + set_y2) / 4

        ycx = int(rect[0][0])  # 获取中心点x坐标
        ycy = int(rect[0][1])  # 获取中心点y坐标
        print(f"标定点坐标: {int(rect[0][0])}, {int(rect[0][1])}")

        set_goal1 = ycx + (set_xy / 2)               # 像素坐标下的坐标纸原点坐标的x值
        set_goal2 = ycy - (set_xy * 2 + set_xy / 2)  # 像素坐标下的坐标纸原点坐标的y值

        image = cv2.drawContours(image, [box], 0, (0, 255, 255), 2)                  # 将检测对象用方框圈出来
        image = cv2.circle(image, (ycx, ycy), 4, (0, 255, 255), 1)                   # 将中心点标注出来(圆形)
        image = cv2.line(image, (ycx + 10, ycy), (ycx - 10, ycy), (0, 255, 255), 2)  # 将中心点标注出来(十字形)
        image = cv2.line(image, (ycx, ycy + 10), (ycx, ycy - 10), (0, 255, 255), 2)  # 将中心点标注出来(十字形)
        cv2.putText(image, 'yellow-set', (x, y - 5), font, 0.7, (0, 255, 255), 2)    # 在图像上绘制黄色的标注文本

    for cnt in cnts1:  # 对红色区域进行检测定位并处理
        (x, y, w, h) = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
        rect = cv2.minAreaRect(cnt)           # 得到完全包围轮廓的最小面积外界矩形的(中心坐标(x, y), (宽,高), 旋转角度)
        area = cv2.contourArea(cnt)           # 获得该区域的的面积
        if area < 2000:                       # 区域面积小于2000就跳过
            continue

        box = cv2.boxPoints(rect)             # 获取最小面积外接矩形的4个顶点坐标
        box = np.intp(box)                    # 取整计算

        cx = int(rect[0][0])  # 获取中心点x坐标
        cy = int(rect[0][1])  # 获取中心点y坐标
        
        goal_x = ((set_goal1 - (rect[0][0])) / set_xy)  # 坐标纸视角下坐标的x值
        goal_y = (((rect[0][1]) - set_goal2) / set_xy)  # 坐标纸视角下坐标的y值

        print("----------------")
        print(f"red-像素点坐标: {int(rect[0][0])}, {int(rect[0][1])}")
        print(f"red-坐标纸坐标: {goal_x:.4f},{goal_y:.4f}")
        print("red-机械臂坐标:", xy_main(goal_x, goal_y))

        red_list.append(list(xy_main(goal_x, goal_y)))  # 储存红色物块的机械臂坐标

        image = cv2.drawContours(image, [box], 0, (0, 0, 255), 2)              # 将检测对象用方框圈出来
        image = cv2.circle(image, (cx, cy), 4, (0, 0, 255), 1)                 # 将中心点标注出来(圆形)
        image = cv2.line(image, (cx + 10, cy), (cx - 10, cy), (0, 0, 255), 2)  # 将中心点标注出来(十字形)
        image = cv2.line(image, (cx, cy + 10), (cx, cy - 10), (0, 0, 255), 2)  # 将中心点标注出来(十字形)
        cv2.putText(image, 'red', (x, y - 5), font, 0.7, (0, 0, 255), 2)       # 在图像上绘制红色的标注文本

    for cnt in cnts2:  # 对蓝色区域进行检测定位并处理
        (x, y, w, h) = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
        rect = cv2.minAreaRect(cnt)           # 得到完全包围轮廓的最小面积外界矩形的(中心坐标(x, y), (宽,高), 旋转角度)
        area = cv2.contourArea(cnt)           # 获得该区域的的面积
        if area < 2000:                       # 区域面积小于2000就跳过
            continue

        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)        # 将检测到的蓝色区域框起来
        cv2.putText(image, 'blue', (x, y - 5), font, 0.7, (255, 0, 0), 2)   # 在图像上绘制蓝色的标注文本

    for cnt in cnts4:  # 对绿色区域进行检测定位并处理
        (x, y, w, h) = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
        rect = cv2.minAreaRect(cnt)           # 得到完全包围轮廓的最小面积外界矩形的(中心坐标(x, y), (宽,高), 旋转角度)
        area = cv2.contourArea(cnt)           # 获得该区域的的面积
        if area < 2000:                       # 区域面积小于2000就跳过
            continue
        
        box = cv2.boxPoints(rect)             # 获取最小面积外接矩形的4个顶点坐标
        box = np.intp(box)                    # 取整计算
        cx = int(rect[0][0])  # 获取中心点x坐标
        cy = int(rect[0][1])  # 获取中心点y坐标

        goal_x = ((set_goal1 - (rect[0][0])) / set_xy)  # 坐标纸视角下坐标的x值
        goal_y = (((rect[0][1]) - set_goal2) / set_xy)  # 坐标纸视角下坐标的y值

        print("----------------")
        print(f"green-像素点坐标: {int(rect[0][0])}, {int(rect[0][1])}")
        print(f"green-坐标纸坐标: {goal_x:.4f},{goal_y:.4f}")
        print("green-机械臂坐标:", xy_main(goal_x, goal_y))

        green_list.append(list(xy_main(goal_x, goal_y)))  # 储存绿色物块的机械臂坐标

        image = cv2.drawContours(image, [box], 0, (0, 255, 0), 2)              # 将检测对象用方框圈出来
        image = cv2.circle(image, (cx, cy), 4, (0, 255, 0), 1)                 # 将中心点标注出来(圆形)
        image = cv2.line(image, (cx + 10, cy), (cx - 10, cy), (0, 255, 0), 2)  # 将中心点标注出来(十字形)
        image = cv2.line(image, (cx, cy + 10), (cx, cy - 10), (0, 255, 0), 2)  # 将中心点标注出来(十字形)
        cv2.putText(image, 'green', (x, y - 5), font, 0.7, (0, 255, 0), 2)     # 在图像上绘制红色的标注文本

    cv2.namedWindow("image", cv2.WINDOW_AUTOSIZE)  # 窗口命名
    cv2.imshow("image", image)                     # 窗口显示

    while True:
        key = cv2.waitKey(10)       # 等待按键

        if int(key) == 32:          # 如果按一次空格键, 将打断监听键盘循环, 传输下一刻的图像
            red_list = ["red"]      # 清除列表中储存的红色物块的机械臂坐标
            green_list = ["green"]  # 清除列表中储存的绿色物块的机械臂坐标
            break                   # 打断监听键盘的循环

        elif int(key) == 27:        # 按下esc键退出此程序
            print("\n!!!退出程序!")
            cv2.destroyAllWindows()
            exit()

        elif int(key) == 13:        # 按下回车键将进行功能的选择, 传输列表中物块的机械臂坐标数据
            choose = int(input("++++++++++++++++\n"
                               "@ 请选择要实现的功能:\n"
                               "数字1:执行全部物块码垛到指定点(鼠标点击)\n"
                               "数字2:依据物块颜色进行分拣\n"
                               "数字3:指定物块移动到指定点(鼠标点击)\n"
                               "++++++++++++++++\n"))

            # 数字1:执行全部物块码垛到指定点(鼠标点击)
            if choose == 1:  # 输入数字1
                file_path = 'Target_Coordinates'
                file1 = open(file_path, 'w')                # 打开Target_Coordinates, 用于储存指定的机械臂坐标
                file1.write(f"{red_list}\n{green_list}")    # 写入红色物块、绿色物块的机械臂坐标
                file1.close()                               # 关闭文件
                def_list = ["1"]                            # 功能标志设置为1
                print("!!! 请指定坐标点")
                cv2.setMouseCallback("image", mouse_click)  # 调用mouse_click(), 监听鼠标, 将指定点的机械臂坐标写入到Target_Coordinates文件
                

            # 数字2:依据物块颜色进行分拣
            if choose == 2:  # 输入数字2
                file_path = 'Target_Coordinates'
                file2 = open(file_path, 'w')                                        # 打开Target_Coordinates, 用于储存指定的机械臂坐标
                def_list = ["2", list(xy_main(1.4, 2.5)), list(xy_main(2.6, 2.5))]  # 功能标志设置为2, 同时指定两点坐标用于分拣
                file2.write(f"{red_list}\n{green_list}\n{def_list}")                # 写入红色物块、绿色物块的机械臂坐标
                file2.close()                                                       # 关闭文件
                file_replace(file_path)                                             # 去除文本文件中的全部空格
                command_use()                                                       # 将"rosrun dobot Goal"指令传入shell终端并运行
                

            # 数字3:指定物块移动到指定点(鼠标点击)
            if choose == 3:  # 输入数字3
                file_path = 'Target_Coordinates'
                file3 = open(file_path, 'w')                                           # 打开Target_Coordinates, 用于储存指定的机械臂坐标
                def_list = ["3"]                                                       # 功能标志设置为3
                choose_cube = input("!!! 请指定要移动的物块(r1/g1/g2)\n")
                if choose_cube[0] == "r":                                              # r表示选择红色物块
                    file3.write(f"{[red_list[0],red_list[int(choose_cube[1])]]}")      # 写入rx物块的机械臂坐标

                elif choose_cube[0] == "g":                                            # g表示选择绿色物块
                    file3.write(f"{[green_list[0],green_list[int(choose_cube[1])]]}")  # 写入gx物块的机械臂坐标

                file3.close()                                                          # 关闭文件
                print("!!! 请指定坐标点")
                cv2.setMouseCallback("image", mouse_click)                             # 调用mouse_click(), 将指定点的机械臂坐标写入到Target_Coordinates文件
                
