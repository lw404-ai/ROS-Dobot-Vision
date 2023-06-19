#!/bin/bash

# Step 0:判断当前是否为root用户/sudo权限执行脚本
if [ "$(id -u)" -eq 0 ]; then
    echo "请勿使用root用户/sudo权限执行此脚本!"
    exit 1
fi

# Step 1:获取当前用户名
username=$(whoami)

# 显示用户名
echo "当前用户名是: $username"

# 用户输入判断
read -p "是否执行初始化脚本？(如果已经进行过请输入n, 否则输入y)(y/n): " choice

if [ "$choice" == "y" ]; then
    
    # Step 2: 修改Goal.cpp文件中的用户名
    sed -i '159s/username/'"$username"'/' Goal.cpp
    echo "替换完成"
    
    # Step 3: 将Goal.cpp文件复制到dobot_ws/src/dobot/src/目录下
    cp /home/$username/Desktop/ROS_CV_CODE/Goal.cpp /home/$username/dobot_ws/src/dobot/src/
    
    # Step 4: 修改CMakeLists.txt文件
    # 指定文件路径
    file_path="/home/$username/dobot_ws/src/dobot/CMakeLists.txt"
    
    # 添加的内容
    content_to_add="SET(CMAKE_CXX_FLAGS \"\${CMAKE_CXX_FLAGS} -std=c++11\")\nadd_executable(Goal src/Goal.cpp)\ntarget_link_libraries(Goal \${catkin_LIBRARIES})\nadd_dependencies(Goal dobot_gencpp)"
    
    # 在文件末尾添加内容
    echo -e "\n$content_to_add" >> "$file_path"
    
    # 输出信息
    echo "内容已添加到 $file_path"
    
    # Step 5: 在dobot_ws目录下进行catkin_make
    cd /home/$username/dobot_ws/

    catkin_make
    
    echo "catkin_make完成"
else
    echo "已选择不执行初始化脚本"
fi

# Step 6: 在shell终端运行python Main.py命令
cd /home/$username/Desktop/ROS_CV_CODE/

# 执行Main.py文件
python Main.py

