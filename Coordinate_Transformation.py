'''

文件: Coordinate_Transformation.py
功能: 代码实现了机械臂的坐标校准和给定坐标进行基于机械臂视角转换功能
作者: 李维、李启豪

'''
#++++++++++++++++++++ 1. 导入所需的包文件 ++++++++++++++++++++
import numpy as np
import math
import os

#++++++++++++++++++++ 2. 机械臂校准坐标文件的检查与写入 ++++++++++++++++++++
# 设置用于储存机械臂校准坐标的文件
filename = "Calibration_Coordinates.txt"

# 定义write_file()函数用于写入校准坐标值
def write_file(filename):
    with open(filename, "w") as file:
        coordinates = [
            "原点在机械臂上的坐标",
            "点位1在坐标纸上的坐标",
            "点位2在坐标纸上的坐标",
            "点位1在机械臂上的坐标",
            "点位2在机械臂上的坐标",
        ]

        for coord in coordinates:    # 依次进行坐标导入
            line = input(f"请输入{coord}: (空格分割)\n")
            file.write(line + "\n")  # 写入并换行

        print("内容已写入文件。")

    return 0

# 定义check_file_content()函数用于检查机械臂校准坐标文件是否存在内容
def check_file_content(filename):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            content = file.read()
            if content:
                print("机械臂校准坐标文件准备完成！")
                return 0
            else:
                print("机械臂校准坐标文件存在但没有内容。")
                write_file(filename)
                return 0
    else:
        print("文件不存在。")
        write_file(filename)
        return 0

check_file_content(filename)

#++++++++++++++++++++ 3. 导入机械臂校准坐标进行矩阵系数求解 ++++++++++++++++++++
# 建立两个空列表用于分别储存(x, y)坐标值
x_values, y_values = [], []

# 读取Calibration_Coordinates文件内的坐标并传入到x_values, y_values
with open("Calibration_Coordinates.txt", "r") as file:
    for line in file:
        line = line.strip()                 # 去除行末的换行符和空格
        x, y = map(float, line.split(" "))  # 将每行按空格分隔为 x 和 y
        x_values.append(x)                  # 将 x 添加到 x_values 列表中
        y_values.append(y)                  # 将 y 添加到 y_values 列表中

# 输出两个列表x_values, y_values的结果
print(f"x_values: {x_values}\ny_values: {y_values}")

# 赋值:原点坐标(机械臂)
x0, y0 = float(x_values[0]), float(y_values[0])

# 赋值:两个校准点坐标(坐标纸)
m1, n1 = float(x_values[1]), float(y_values[1])
m2, n2 = float(x_values[2]), float(y_values[2])

# 赋值:两个校准点坐标(机械臂)
p1, q1 = float(x_values[3]), float(y_values[3])
p2, q2 = float(x_values[4]), float(y_values[4])

# 求解坐标转换矩阵的系数值, 为接下来进行给定坐标转换做准备
A = np.array([[m1, n1], [m2, n2]])     # 定义矩阵A
B1 = np.array([[p1 - x0], [p2 - x0]])  # 定义矩阵B1
X1 = np.linalg.solve(A, B1)            # 求解线性方程组 A * X1 = B1
a = X1[0][0]                           # 坐标转换矩阵系数a
b = X1[1][0]                           # 坐标转换矩阵系数b
B2 = np.array([[q1 - y0], [q2 - y0]])  # 定义矩阵B2
X2 = np.linalg.solve(A, B2)            # 求解线性方程组 A * X2 = B2
c = X2[0][0]                           # 坐标转换矩阵系数c
d = X2[1][0]                           # 坐标转换矩阵系数d
print(f"矩阵系数a, b为: {a:.4f}, {b:.4f}")
print(f"矩阵系数c, d为: {c:.4f}, {d:.4f}")


#++++++++++++++++++++ 4. 给定坐标进行基于机械臂视角转换 ++++++++++++++++++++
# 定义xy_main(m, n)函数, 对于给定的(m, n)坐标进行基于机械臂视角的坐标转换并返回x_over, y_over
def xy_main(m, n):
    mn = np.array([[m], [n]])        # 创建一个2x1的矩阵mn，元素为m和n
    Az = np.array([[a, b], [c, d]])  # 创建一个2x2的矩阵Az，元素为a、b、c和d
    o = np.array([[x0], [y0]])       # 创建一个2x1的矩阵o，元素为x0和y0
    pq = Az.dot(mn) + o              # 计算矩阵乘法 Az * mn + o，并存储结果在pq中
    x_over = round(float(pq[0]), 4)  # 将pq的第一个元素四舍五入并转换为浮点数，保留四位小数，存储在x_over中
    y_over = round(float(pq[1]), 4)  # 将pq的第二个元素四舍五入并转换为浮点数，保留四位小数，存储在y_over中
    return x_over, y_over            # 返回x_over和y_over作为转换为基于机械臂坐标系后的结果
