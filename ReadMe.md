### 项目组长：李维

#### 项目成员：李昊翀、李起豪、赵桓宇



``` powershell
智能机器人设计与实践
|-- Calibration_Coordinates.txt   # 储存机械臂校准坐标的文件
|-- Calibration_Results.npz       # 摄像头标定结果参数的文件
|-- Camera_Calibration.py         # 摄像头标定的代码文件
|-- Coordinate_Transformation.py  # 机械臂的坐标校准与给定坐标准换的代码文件
|-- Goal.cpp                      # dobot机械臂执行功能指令的代码文件
|-- Main.py                       # 物块坐标捕获并转换为机械臂坐标并实现功能的代码文件
|-- Target_Coordinates            # 内含物块的机械臂坐标与功能标定
|-- run.sh                        # 起始运行文件
|-- ReadMe.md                     # 阅读文档
`-- Appendix
    |-- test.jpg
    |-- Calibration_board.pdf
    `-- Coordinate_paper.pdf

1 directory, 12 files
```



#### 代码文件使用说明：

△注意：

- 以下步骤均在***Ubuntu16.04+ROS Kinetic***环境下部署，请配置好***dobot***环境，开启***roscore***以及***dobot***初始化

- 默认运行使用存在的标定文件***Calibration_Results.npz***，如需要进行重新标定则运行***Camera_Calibration.py***

  

#### 1.自动化脚本文件运行

提示：

- 将 ***ROS_CV_CODE*** 文件夹复制到虚拟机桌面目录下，即：***/home/用户名/Desktop/ROS_CV_CODE***
- 如遇到 ***/r*** 问题请运行命令 **dos2unix *run.sh*** 后 ***dos2unix run.sh*** 即可

1. 在 ***ROS_CV_CODE*** 目录下运行终端输入 ***./run.sh*** 命令即可

   

#### 2.手动配置文件运行

提示：***username*** 均需要替换成当前使用的用户名

1. 将 ***ROS_CV_CODE*** 文件夹复制到虚拟机桌面目录下，即：***/home/username/Desktop/ROS_CV_CODE***
2. 修改 ***Goal.cpp*** 文件内第***159***行将 ***username*** 修改为你的当前用户名
3. 将文件夹内的 ***Goal.cpp*** 文件放置到 ***/home/username/dobot_ws/src/dobot/src/*** 并编写 ***CMakeLists*.txt** 文件（添加文件配置）
4. 在 ***dobot_ws ***目录下进行 ***catkin_make***
5. 在 ***shell*** 终端运行 ***python Main.py*** 命令开始执行程序

