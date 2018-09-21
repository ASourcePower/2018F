# coding: utf-8

class Pucks:
    # 飞机转场记录类，包含转场记录的属性信息
    airport = ''  # 停靠的登机口
    temporary = 0  # 是否停靠在临时停机位，0表示没有，初始化为0

    def __init__(self, data):
        self.record = data['飞机转场记录号']  # 转场记录号
        self.arrive_time = data['到达相对时间min']  # 到达时间
        self.a_flight = data['到达航班']  # 到达航班
        self.a_type = data['到达类型']  # 航班到达类型
        self.plane_type = data['飞机型号']  # 飞机类别
        self.depart_time = data['出发相对时间min']  # 航班出发时间
        self.de_flight = data['出发航班']  # 出发航班号
        self.d_type = data['出发类型']  # 出发类型


class Airport:
    # 登机口记录类，包含登机口属性以及分配到该登机口的转场记录
    puck_records = []  # 用于存储该登机口停放的转场记录，初始化为空
    assign_flag = False

    def __init__(self, data):
        self.gate = data['登机口']  # 登机口名称
        self.terminal = data['终端厅']  # 终端厅
        self.region = data['区域']  # 区域
        self.a_type = data['到达类型']  # 到达类型
        self.d_type = data['出发类型']  # 出发类型
        self.body_type = data['机体类别']  # 机体类别
