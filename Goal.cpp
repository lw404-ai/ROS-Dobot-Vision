/*

文件: Goal.cpp
功能: 
    1. 代码实现了基于Opencv进行物块坐标捕获并转换为机械臂坐标
    2. 最后实现了全部物块执行码垛到指定点、依据物块颜色进行分拣、指定物块移动到指定点的功能
作者: 李维

*/
// 头文件的引用，包括ROS和Dobot机械臂相关的消息和服务类型
#include "ros/ros.h"
#include "std_msgs/String.h"
#include "dobot/SetCmdTimeout.h"
#include "dobot/SetQueuedCmdClear.h"
#include "dobot/SetQueuedCmdStartExec.h"
#include "dobot/SetQueuedCmdForceStopExec.h"
#include "dobot/GetDeviceVersion.h"
#include "dobot/SetEndEffectorParams.h"
#include "dobot/SetPTPJointParams.h"
#include "dobot/SetPTPCoordinateParams.h"
#include "dobot/SetPTPJumpParams.h"
#include "dobot/SetPTPCommonParams.h"
#include "dobot/SetPTPCmd.h"
#include "dobot/SetEndEffectorSuctionCup.h"

#include <iostream>  // 用于输入输出的标准库
#include <fstream>   // 用于文件输入输出的标准库
#include <vector>    // 用于存储和管理动态大小的元素序列
#include <string>    // 用于处理字符串
#include <algorithm> // 提供了各种常用算法的函数模板
#include <sstream>   // 用于字符串流的类模板

using namespace std; // 指定了当前代码使用的命名空间为'std'

// 声明函数以及结构
// 'setCup'(用于设置吸盘的状态)
// 'setGoal'(设置机械臂前进的位置)
// 'parseData'(将字符串中的数字提取出来，并以向量的形式返回)
// 'importData'(指定的文件中导入数据，并将数据按特定的格式存储在向量中)

void setCup(ros::NodeHandle &tN, int elecStatus);
void setGoal(ros::NodeHandle &tN, float x, float y, float z);
vector<double> parseData(string data);
vector<pair<string, vector<vector<double>>>> importData(string filename);

int main(int argc, char **argv)
{

    // ROS节点初始化
    // 创建ROS节点句柄'n'和服务客户端'client'
    ros::init(argc, argv, "DobotClient");
    ros::NodeHandle n;
    ros::ServiceClient client;

    // 设置命令超时
    // 创建服务客户端'client'，并调用Dobot机械臂的'SetCmdTimeout'服务，将超时时间设置为3000毫秒
    client = n.serviceClient<dobot::SetCmdTimeout>("/DobotServer/SetCmdTimeout");
    dobot::SetCmdTimeout srv1;
    srv1.request.timeout = 3000;
    if (client.call(srv1) == false)
    {
        ROS_ERROR("Failed to call SetCmdTimeout. Maybe DobotServer isn't started yet!");
        return -1; // 如果调用失败，打印错误信息并返回-1
    }

    // 清除命令
    // 创建服务客户端'client'，并调用Dobot机械臂的'SetQueuedCmdClear'服务，用于清除已经排队的命令
    client = n.serviceClient<dobot::SetQueuedCmdClear>("/DobotServer/SetQueuedCmdClear");
    dobot::SetQueuedCmdClear srv2;
    client.call(srv2);

    // 开始运行命令
    // 创建服务客户端'client'，并调用Dobot机械臂的'SetQueuedCmdStartExec'服务，用于开始执行命令
    client = n.serviceClient<dobot::SetQueuedCmdStartExec>("/DobotServer/SetQueuedCmdStartExec");
    dobot::SetQueuedCmdStartExec srv3;
    client.call(srv3);

    // 获取设备版本信息
    // 创建服务客户端'client'，并调用Dobot机械臂的'GetDeviceVersion'服务，用于获取设备版本信息
    client = n.serviceClient<dobot::GetDeviceVersion>("/DobotServer/GetDeviceVersion");
    dobot::GetDeviceVersion srv4;
    client.call(srv4);
    if (srv4.response.result == 0) // 如果获取成功，打印设备版本号；否则，打印错误信息
    {
        ROS_INFO("Device version:%d.%d.%d", srv4.response.majorVersion, srv4.response.minorVersion, srv4.response.revision);
    }
    else
    {
        ROS_ERROR("Failed to get device version information!");
    }

    // 设置末端执行器参数
    // 创建服务客户端'client'，并调用Dobot机械臂的'SetEndEffectorParams'服务，用于设置末端执行器的参数
    client = n.serviceClient<dobot::SetEndEffectorParams>("/DobotServer/SetEndEffectorParams");
    dobot::SetEndEffectorParams srv5; // 创建客户端srv5
    srv5.request.xBias = 70;          // 实例化服务并且给request赋值
    srv5.request.yBias = 0;
    srv5.request.zBias = 0;
    client.call(srv5); // 调用srv5

    // 设置PTP运动时各关节坐标轴的速度和加速度
    // 创建服务客户端'client'，并调用Dobot机械臂的'SetPTPJointParams'服务，用于设置PTP运动时各关节坐标轴的速度和加速度
    do
    {
        client = n.serviceClient<dobot::SetPTPJointParams>("/DobotServer/SetPTPJointParams");
        dobot::SetPTPJointParams srv;

        for (int i = 0; i < 4; i++)
        {
            srv.request.velocity.push_back(100); // 关节坐标轴的速度
        }
        for (int i = 0; i < 4; i++)
        {
            srv.request.acceleration.push_back(100); // 关节坐标轴的加速度
        }
        client.call(srv);
    } while (0);

    // 设置PTP运动时各笛卡尔坐标轴的速度和加速度
    // 创建服务客户端'client'，并调用Dobot机械臂的'SetPTPCoordinateParams'服务
    do
    {
        client = n.serviceClient<dobot::SetPTPCoordinateParams>("/DobotServer/SetPTPCoordinateParams");
        dobot::SetPTPCoordinateParams srv;

        srv.request.xyzVelocity = 100;     // 笛卡尔坐标轴的速度(xyz)
        srv.request.xyzAcceleration = 100; // 笛卡尔坐标轴的加速度(xyz)
        srv.request.rVelocity = 100;       // 笛卡尔坐标轴的速度(r)
        srv.request.rAcceleration = 100;   // 笛卡尔坐标轴的加速度(r)
        client.call(srv);                  // 调用客户端
    } while (0);

    // 设置JUMP模式下抬升高度和最大抬升高度
    // 创建服务客户端'client'，并调用Dobot机械臂的'SetPTPJumpParams'服务
    do
    {
        client = n.serviceClient<dobot::SetPTPJumpParams>("/DobotServer/SetPTPJumpParams");
        dobot::SetPTPJumpParams srv; // 创建客户端

        srv.request.jumpHeight = 20; // 抬升高度
        srv.request.zLimit = 200;    // 最大抬升高度
        client.call(srv);            // 调用客户端
    } while (0);

    // 设置PTP运动的速度百分比和加速度百分比
    // 创建服务客户端'client'，并调用Dobot机械臂的'SetPTPCommonParams'服务
    do
    {
        client = n.serviceClient<dobot::SetPTPCommonParams>("/DobotServer/SetPTPCommonParams");
        dobot::SetPTPCommonParams srv; // 创建客户端srv，为后续调用服务

        srv.request.velocityRatio = 50;     // PTP模式速度百分比，关节坐标轴和笛卡尔坐标轴
        srv.request.accelerationRatio = 50; // 加速度百分比
        client.call(srv);                   // 调用服务srv
    } while (0);

    // 主体解决方案 - 开始
    vector<pair<string, vector<vector<double>>>> data;             // 创建了一个名为'data'的变量
    data = importData("/home/liwei/Desktop/ROS_CV_CODE/Target_Coordinates"); // 调用'importData'函数来导入数据，并将返回的结果赋值给'data'变量

    if (data.back().first == "1") // 判断是否为 <码垛物块> 指令
    {
        //  码垛第一个物块
        setGoal(n, data[0].second[0][0], data[0].second[0][1], 30);          // 到达第一个物块的上方
        setCup(n, 1);                                                        // 开启吸盘
        setGoal(n, data[0].second[0][0], data[0].second[0][1], -47);         // 下放z轴坐标来接近物块
        setGoal(n, data[0].second[0][0], data[0].second[0][1], 30);          // 吸起物块提升到上方
        setGoal(n, data.back().second[0][0], data.back().second[0][1], 30);  // 移到目标位置的上方
        setGoal(n, data.back().second[0][0], data.back().second[0][1], -47); // 下放z轴坐标来放置第一个物块
        setCup(n, 0);                                                        // 关闭吸盘
        setGoal(n, data.back().second[0][0], data.back().second[0][1], 30);  // 提升z轴坐标来远离物块

        // 码垛第二个物块
        setGoal(n, data[1].second[0][0], data[1].second[0][1], 30);          // 到达第二个物块的上方
        setCup(n, 1);                                                        // 开启吸盘
        setGoal(n, data[1].second[0][0], data[1].second[0][1], -47);         // 下放z轴坐标来接近物块
        setGoal(n, data[1].second[0][0], data[1].second[0][1], 30);          // 吸起物块提升到上方
        setGoal(n, data.back().second[0][0], data.back().second[0][1], 30);  // 移到目标位置的上方
        setGoal(n, data.back().second[0][0], data.back().second[0][1], -20); // 下放z轴坐标来放置第二个物块(z坐标为-20.0)
        setCup(n, 0);                                                        // 关闭吸盘
        setGoal(n, data.back().second[0][0], data.back().second[0][1], 30);  // 提升z轴坐标来远离物块

        // 码垛第三个物块
        setGoal(n, data[1].second[1][0], data[1].second[1][1], 30);         // 到达第三个物块的上方
        setCup(n, 1);                                                       // 开启吸盘
        setGoal(n, data[1].second[1][0], data[1].second[1][1], -47);        // 下放z轴坐标来接近物块
        setGoal(n, data[1].second[1][0], data[1].second[1][1], 30);         // 吸起物块提升到上方
        setGoal(n, data.back().second[0][0], data.back().second[0][1], 30); // 移到目标位置的上方
        setGoal(n, data.back().second[0][0], data.back().second[0][1], 5);  // 下放z轴坐标来放置第三个物块(z坐标为5.0)
        setCup(n, 0);                                                       // 关闭吸盘
        setGoal(n, data.back().second[0][0], data.back().second[0][1], 30); // 提升z轴坐标来远离物块
        setGoal(n, 103.7, 143.2, 30);                                       // 工作完成, 使之回归原始位置
    }

    if (data.back().first == "2") // 判断是否为 <分拣物块> 指令
    {
        // 分拣第一个物块
        setGoal(n, data[0].second[0][0], data[0].second[0][1], 30);          // 到达第一个物块的上方
        setCup(n, 1);                                                        // 开启吸盘
        setGoal(n, data[0].second[0][0], data[0].second[0][1], -47);         // 下放z轴坐标来接近物块
        setGoal(n, data[0].second[0][0], data[0].second[0][1], 30);          // 吸起物块提升到上方
        setGoal(n, data.back().second[0][0], data.back().second[0][1], 30);  // 移到目标位置的上方
        setGoal(n, data.back().second[0][0], data.back().second[0][1], -47); // 下放z轴坐标来放置第一个物块
        setCup(n, 0);                                                        // 关闭吸盘
        setGoal(n, data.back().second[0][0], data.back().second[0][1], 30);  // 提升z轴坐标来远离物块

        // 分拣第二个物块
        setGoal(n, data[1].second[0][0], data[1].second[0][1], 30);          // 到达第二个物块的上方
        setCup(n, 1);                                                        // 开启吸盘
        setGoal(n, data[1].second[0][0], data[1].second[0][1], -47);         // 下放z轴坐标来接近物块
        setGoal(n, data[1].second[0][0], data[1].second[0][1], 30);          // 吸起物块提升到上方
        setGoal(n, data.back().second[1][0], data.back().second[1][1], 30);  // 移到目标位置的上方
        setGoal(n, data.back().second[1][0], data.back().second[1][1], -47); // 下放z轴坐标来放置第二个物块
        setCup(n, 0);                                                        // 关闭吸盘
        setGoal(n, data.back().second[1][0], data.back().second[1][1], 30);  // 提升z轴坐标来远离物块

        // 分拣第三个物块
        setGoal(n, data[1].second[1][0], data[1].second[1][1], 30);          // 到达第三个物块的上方
        setCup(n, 1);                                                        // 开启吸盘
        setGoal(n, data[1].second[1][0], data[1].second[1][1], -47);         // 下放z轴坐标来接近物块
        setGoal(n, data[1].second[1][0], data[1].second[1][1], 30);          // 吸起物块提升到上方
        setGoal(n, data.back().second[1][0], data.back().second[1][1], 30);  // 移到目标位置的上方
        setGoal(n, data.back().second[1][0], data.back().second[1][1], -20); // 下放z轴坐标来放置第三个物块(z坐标为-20.0)
        setCup(n, 0);                                                        // 关闭吸盘
        setGoal(n, data.back().second[1][0], data.back().second[1][1], 30);  // 提升z轴坐标来远离物块
        setGoal(n, 103.7, 143.2, 30);                                        // 工作完成, 使之回归原始位置
    }

    if (data.back().first == "3") // 判断是否为 <指定位置> 指令
    {
        // 指定位置
        setGoal(n, data[0].second[0][0], data[0].second[0][1], 30);          // 到达物块的上方
        setCup(n, 1);                                                        // 开启吸盘
        setGoal(n, data[0].second[0][0], data[0].second[0][1], -47);         // 下放z轴坐标来接近物块
        setGoal(n, data[0].second[0][0], data[0].second[0][1], 30);          // 吸起物块提升到上方
        setGoal(n, data.back().second[0][0], data.back().second[0][1], 30);  // 移到目标位置的上方
        setGoal(n, data.back().second[0][0], data.back().second[0][1], -47); // 下放z轴坐标来放置物块
        setCup(n, 0);                                                        // 关闭吸盘
        setGoal(n, data.back().second[0][0], data.back().second[0][1], 30);  // 提升z轴坐标来远离物块
        setGoal(n, 103.7, 143.2, 30);                                        // 工作完成, 使之回归原始位置
    }

    return 0;
}

// 定义'setCup'函数，用于设置吸盘的状态
void setCup(ros::NodeHandle &tN, int elecStatus)
{
    ros::ServiceClient client = tN.serviceClient<dobot::SetEndEffectorSuctionCup>("/DobotServer/SetEndEffectorSuctionCup");
    dobot::SetEndEffectorSuctionCup theSck; // 调用设置气泵状态API
    do
    {
        theSck.request.enableCtrl = 1;    // 末端使能
        theSck.request.suck = elecStatus; // 吸盘上电 1:开启  0：关闭
        theSck.request.isQueued = true;   // 将指令加入指令列队
        client.call(theSck);              // 调用设置气泵状态API

        ros::spinOnce();
        if (ros::ok() == false)
        {
            break; // 如果ros::ok() 返回false所有调用失效
        }
    } while (0);
}

// 定义'setGoal'函数，用于设置机械臂的目标位置
void setGoal(ros::NodeHandle &tN, float x, float y, float z)
{
    ros::ServiceClient client = tN.serviceClient<dobot::SetPTPCmd>("/DobotServer/SetPTPCmd");
    dobot::SetPTPCmd theSrv;
    do
    {
        theSrv.request.ptpMode = 1; // MOVJ模式，笛卡尔坐标系下目标点坐标
        theSrv.request.x = x;       // x、y、z坐标赋值给请求的x、y、z变量
        theSrv.request.y = y;
        theSrv.request.z = z;
        theSrv.request.r = 0;
        client.call(theSrv); // 调用服务theSrv
        if (theSrv.response.result == 0)
        {
            break; // 如果服务调用成功且返回的result值为0，表示设置成功，则跳出循环
        }
        ros::spinOnce();        // 消息回调处理，执行完成后执行下一步
        if (ros::ok() == false) // 如果ros::ok() 返回false所有调用失效
        {
            break;
        }
    } while (1);
}

// 定义'parseData'功能，输入的字符串数据按照逗号分隔，将每个分割后的数值转换为double类型，并存储在一个向量中，最后返回该向量
vector<double> parseData(string data)
{
    vector<double> result;          // 创建一个名为result的double类型向量，用于存储解析后的数据
    stringstream ss(data);          // 创建一个stringstream对象ss，并将输入的data参数传递给它
    string token;                   // 创建一个名为token的字符串，用于存储分割后的每个数据值
    while (getline(ss, token, ',')) // 使用getline函数从stringstream对象ss中按逗号分隔获取每个数据值，并循环处理直到数据全部解析完毕
    {
        double value = stod(token); // 将字符串token转换为double类型的数值，并将结果赋值给变量value
        result.push_back(value);    // 将value添加到向量result的末尾
    }
    return result; // 返回解析后的向量result
}

// 定义'importData'功能，从指定的文件中导入数据读取每一行的内容，并解析出颜色名称和对应的坐标数据，将它们存储在一个向量中，最后返回该向量
vector<pair<string, vector<vector<double>>>> importData(string filename)
{
    ifstream fin(filename.c_str());                    // 使用给定的文件名打开输入文件流
    vector<pair<string, vector<vector<double>>>> data; // 创建一个存储所有数据的向量，每个元素是一个pair，包含颜色和对应的坐标数据
    vector<vector<double>> temp;                       // 创建一个临时向量，用于存储每个颜色的坐标数据
    string line;                                       // 用于存储每行读取的内容的字符串
    while (getline(fin, line))                         // 循环读取输入文件中的每一行内容
    {
        cout << line << endl; // 打印当前读取的行内容（用于调试）
        if (line.empty())     // 如果当前行为空行，则跳过继续处理下一行
            continue;
        int pos = line.find(",[");              // 查找逗号和左括号的位置，用于定位颜色名称的起始和结束位置
        string color = line.substr(2, pos - 3); // 获取颜色名称，使用substr函数根据起始位置和长度提取子字符串

        int start = line.find("[", pos); // 在当前行中查找左括号的位置，用于定位坐标数据的起始位置
        int end;
        while ((end = line.find("]", start)) != string::npos) // 循环查找右括号的位置，直到找不到为止
        {
            string s = line.substr(start + 1, end - start - 1); // 提取括号内的坐标数据字符串
            vector<double> v = parseData(s);                    // 调用parseData函数解析坐标数据字符串，并得到一个存储坐标数据的向量
            temp.push_back(v);                                  // 将解析后的坐标数据向量添加到临时向量temp中
            start = line.find("[", end);                        // 在当前行中继续查找下一个左括号的位置
        }
        data.push_back({color, temp}); // 将颜色名称和对应的坐标数据向量作为一个pair添加到data向量中
        temp.clear();                  // 清空临时向量，为下一个颜色的坐标数据做准备
    }

    return data; // 返回存储所有数据的向量
}
