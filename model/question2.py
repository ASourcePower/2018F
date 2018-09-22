import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
# 下面这三行代码是为了画图可以显示中文
from pylab import *

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False


def type_is_same(puck_type, airport_type):
    # 判断飞机的到达（或起飞）类型是否与登机口的到达（或起飞）类型相同
    airport_type = airport_type.replace(' ', '')
    airport_type = airport_type.split(',')
    # airport_type = [s.split() for s in airport_type]
    # print('puck type is {}'.format(puck_type))
    # print('gate type is {}'.format(airport_type))
    if puck_type in airport_type:
        return True
    else:
        return False


def classify_airport2(all_airports):
    # airport 是所有的登机口
    # classes: 字典用于存储每种类别的登机口
    # classes: 0存储航空楼的登机口， 1存储卫星厅的登机口
    classes = {0: [], 1: []}

    for airport in all_airports:
        if 'T' in airport['gate']:  # 卫星厅的登机口
            classes[0].append(airport)
        if 'S' in airport['gate']:
            classes[1].append(airport)

    return classes


def classify_puck2(all_pucks):
    # all_pucks: 列表，所有转场记录的飞机航班
    # puck_classes: 字典，每种类别的转场记录飞机航班
    # 此函数将all_pucks进行分类，并且按照优先级依次放入puck_classes字典中，
    # 字典中的键值越小，该类别的优先级越高

    puck_classes = {0: [], 1: [], 2: [], 3: []}
    for puck in all_pucks:
        if puck['a_type'] == 'I':
            if puck['d_type'] == 'D':
                puck_classes[0].append(puck)
        if puck['a_type'] == 'D':
            if puck['d_type'] == 'D':
                puck_classes[1].append(puck)
        if puck['a_type'] == 'D':
            if puck['d_type'] == 'I':
                puck_classes[2].append(puck)
        if puck['a_type'] == 'I':
            if puck['d_type'] == 'I':
                puck_classes[3].append(puck)

    return puck_classes


def create_gates(gates):
    # puck_data : puck_dataFrame类型，包含全部登机口的信息
    # puck_data的形状是[num_gates, 6]
    # 返回：airports: 包含全部登机口的列表，每一个元素是一个登机口
    airports = []
    for i in range(gates.shape[0]):
        gate_data = gates.loc[i, :]
        gate = {'gate': gate_data['登机口'], 'terminal': gate_data['终端厅'], 'region': gate_data['区域'],
                'a_type': gate_data['到达类型'],
                'd_type': gate_data['出发类型'], 'body_type': gate_data['机体类别'], 'puck_records': [], 'assign_flag': False}
        airports.append(gate)

    return airports


def create_pucks(pucks):
    # puck_data : puck_dataFrame类型，包含全部转场记录的信息
    # puck_data的形状是[num_pucks, 8]
    # 返回：allpucks: 包含全部转场记录的列表，每一个元素是一个转场记录
    allpucks = []
    for i in range(pucks.shape[0]):
        puck_data = pucks.loc[i, :]
        puck = {'record': puck_data['飞机转场记录号'], 'arrive_time': puck_data['到达相对时间min'], 'a_flight': puck_data['到达航班'],
                'a_type': puck_data['到达类型'],
                'plane_type': puck_data['飞机型号'], 'depart_time': puck_data['出发相对时间min'], 'de_flight': puck_data['出发航班'],
                'd_type': puck_data['出发类型'],
                'airport': '', 'temporary': 0}

        allpucks.append(puck)

    return allpucks


def plane_type_map(plane_type):
    Wide_body = ['332', '333', '33E', '33H', '33L', '773']
    Narrow_body = ['319', '320', '321', '323', '325', '738', '73A', '73E', '73H', '73L']
    plane_type = str(plane_type)
    if (plane_type in Wide_body):
        return 'W'
    else:
        return 'N'


def sort_pucks(puck_class):
    # 此函数将同一类别的转场记录按照起飞时间的先后排序
    # puck_class：列表
    # sort_puckclass: 排序好的转场记录，按照起飞时间非递减排序
    de_times = [puck['depart_time'] for puck in puck_class]
    sort_index = np.argsort(de_times)
    sort_puckclass = [puck_class[ind] for ind in sort_index]

    return sort_puckclass


def greedyselector2(sort_puck_class, airport):
    # 本函数采用贪心算法进行分配航班到登机口
	# sort_puck_class: 排序好的转场记录，列表形式，以转场记录起飞时间从早到晚排序
    # airport: 一个登机口类实例
    start_times = [puck['arrive_time'] for puck in sort_puck_class]
    depart_times = [puck['depart_time'] for puck in sort_puck_class]

    j = 0
    while (sort_puck_class[j]['airport'] != ''):
	# 该循环寻找第一个没有被分配的转场记录
        j = j + 1

    if airport['assign_flag'] == False:  # 登机口没有被分配
        airport['busy_time'] = np.zeros(288)
        sp_ind = max(int(start_times[j] / 5) - 1, 0)
        ep_ind = int(depart_times[j] / 5)
        if sort_puck_class[j]['plane_type'] == airport['body_type']:
            if (type_is_same(sort_puck_class[j]['a_type'], airport['a_type']) &
                    (type_is_same(sort_puck_class[j]['d_type'], airport['d_type']))):
                print('类型相匹配...')
                sort_puck_class[j]['airport'] = airport['gate']
                airport['puck_records'].append(sort_puck_class[j]['record'])
                airport['busy_time'][sp_ind:ep_ind] = 1
                airport['assign_flag'] = True

        k = j
        for i in range(j + 1, len(sort_puck_class)):
            if sort_puck_class[i]['plane_type'] == airport['body_type']:  # 飞机类型与登机口的机体类别相同
                # 飞机到达的类型与出发类型和登机口类型均吻合
                if (type_is_same(sort_puck_class[i]['a_type'], airport['a_type']) &
                        (type_is_same(sort_puck_class[i]['d_type'], airport['d_type']))):
						
                    if start_times[i] >= depart_times[k]:
                        if sort_puck_class[i]['airport'] == '':  # 如果该转场记录没有被分配
                            sort_puck_class[i]['airport'] = airport['gate']
                            k = i
                            airport['puck_records'].append(sort_puck_class[k]['record'])
                            if start_times[i] == 0:
                                s_ind = 0
                            else:
                                s_ind = int(start_times[i] / 5)
                            e_ind = int(depart_times[i] / 5)
                            airport['busy_time'][s_ind:e_ind] = 1
                            airport['assign_flag'] = True
    else:
        for i in range(j + 1, len(sort_puck_class)):
            if sort_puck_class[i]['plane_type'] == airport['body_type']:  # 飞机类型与登机口的机体类别相同
                # 飞机到达的类型与出发类型和登机口类型均吻合
                if (type_is_same(sort_puck_class[i]['a_type'], airport['a_type']) &
                        (type_is_same(sort_puck_class[i]['d_type'], airport['d_type']))):
                    if sort_puck_class[i]['airport'] == '':  # 如果该转场记录没有被分配
                        puck_time = np.zeros(288)
                        if start_times[i] == 0:
                            s_ind = 0
                        else:
                            s_ind = int(start_times[i] / 5)
                        e_ind = int(depart_times[i] / 5)
                        # print('该记录的起止时间下标分别是{}和{}'.format(s_ind, e_ind))
                        puck_time[s_ind:e_ind] = 1
                        temp_time = puck_time + airport['busy_time']
                        if np.max(temp_time) <= 1:
                            print('可以安排插入航班......')
                            airport['busy_time'] = temp_time
                            sort_puck_class[i]['airport'] = airport['gate']
                            airport['puck_records'].append(sort_puck_class[i]['record'])

    print('gates{} has assigned {}'.format(airport['gate'], airport['puck_records']))
    return sort_puck_class, airport


def assign_puck2(puck_class, gate_class):
	# 该函数是分配登机口和转场记录
    if len(puck_class) == 0 or len(gate_class) == 0:
		# 如果该类别的登机口数量为0或者该类别的飞机转场记录数量为0
        return puck_class, gate_class
    sort_puck_class = sort_pucks(puck_class) # 将飞机转场记录按照起飞时间排序

    for i in range(len(gate_class)):
        puck_not_assign = [puck for puck in sort_puck_class if puck['airport'] == '']
        if len(puck_not_assign) == 0:
            break
        sort_puck_class, airport = greedyselector2(sort_puck_class, gate_class[i])
        gate_class[i] = airport

    return sort_puck_class, gate_class


gates = pd.read_csv('../data/gates (1).csv')
new_gates = gates[['登机口', '终端厅', '区域', '到达类型', '出发类型', '机体类别']]

puck_data = pd.read_csv('../data/puck_data.csv', encoding='gbk')
cols = ['飞机转场记录号', '到达相对时间min', '到达航班', '到达类型',
        '飞机型号', '出发相对时间min', '出发航班', '出发类型']
puck_data = puck_data[cols]

airports = create_gates(new_gates)
allpucks = create_pucks(puck_data)

puck_classes = classify_puck2(allpucks)
gate_classes = classify_airport2(airports)

# single_type_gate = [0, 1, 3, 4, 9, 10, 12, 13]
# multi_type_gate = [2, 5, 6, 7, 8, 11, 14, 15, 16, 17]
# single_gate_classes = [gate_classes[code] for code in single_type_gate]
# multi_gate_classes = [gate_classes[code] for code in multi_type_gate]

# 用航空楼的登机口尽可能先安排到达类型为国际，出发类型为国内的转场飞机
at_puck, at_gate = assign_puck2(puck_classes[0], gate_classes[0])
puck_classes[0] = at_puck;
gate_classes[0] = at_gate

# 用航空楼的登机口尽可能先安排到达类型和出发类型均为国内的转场飞机
at_puck, at_gate = assign_puck2(puck_classes[1], gate_classes[0])
puck_classes[1] = at_puck;
gate_classes[0] = at_gate

# 用卫星厅的登机口尽可能先安排到达类型为国内，出发类型为国际的转场飞机
at_puck, at_gate = assign_puck2(puck_classes[2], gate_classes[1])
puck_classes[2] = at_puck;
gate_classes[1] = at_gate

# 用卫星厅的登机口尽可能先安排到达类型和出发类型均为国际的转场飞机
at_puck, at_gate = assign_puck2(puck_classes[3], gate_classes[1])
puck_classes[3] = at_puck;
gate_classes[1] = at_gate

# 用卫星厅的登机口尽可能安排到达类型为国际且出发类型为国内，目前还没有安排的转场飞机
at_puck, at_gate = assign_puck2(puck_classes[0], gate_classes[1])
puck_classes[0] = at_puck;
gate_classes[1] = at_gate

# 用卫星厅的登机口尽可能安排到达类型和出发类型均为国内，目前还没有安排的转场飞机
at_puck, at_gate = assign_puck2(puck_classes[1], gate_classes[1])
puck_classes[1] = at_puck;
gate_classes[1] = at_gate

# 用航空楼的登机口尽可能安排到达类型为国内且出发类型为国际，目前还没有安排的转场飞机
at_puck, at_gate = assign_puck2(puck_classes[2], gate_classes[0])
puck_classes[2] = at_puck;
gate_classes[0] = at_gate

# 用航空楼的登机口尽可能安排到达类型和出发类型均为国际，目前还没有安排的转场飞机
at_puck, at_gate = assign_puck2(puck_classes[3], gate_classes[0])
puck_classes[3] = at_puck;
gate_classes[0] = at_gate

gate_sum = 0
puck_sum = 0

assign_pucks = [];
assign_gates = []
for clas in gate_classes.keys():
    for gate in gate_classes[clas]:
        if gate['assign_flag'] == True:
            assign_pucks.append(gate['puck_records'])
            assign_gates.append(gate['gate'])
            gate_sum += 1
            puck_sum += len(gate['puck_records'])

assign_dict = dict(zip(assign_gates, assign_pucks))

# 从字典写入csv文件
csvFile3 = open('../result/问题二答案.csv', 'w', newline='')
writer2 = csv.writer(csvFile3)
for key in assign_dict:
    writer2.writerow([key, assign_dict[key]])
csvFile3.close()

############################## 画图 ################################

num_assign_pucks = [len(pucks) for pucks in assign_pucks]
assign_dict = dict(zip(assign_gates, assign_pucks))
assign_dict1 = dict(zip(assign_gates, num_assign_pucks))
assigns = pd.DataFrame(assign_dict1, index=[0])
assigns = assigns.T

# 画出被使用的登机口安排的航班数量图
plt.figure(figsize=(20, 10))
x = list(assigns.index)
plt.bar(x, assigns[0] * 2, facecolor='b')
plt.xlabel('登机口', fontsize=18)
plt.ylabel('登机口分配的总航班数量', fontsize=18)
plt.xticks(rotation=90, fontsize=16)
plt.yticks(fontsize=16)
plt.title('登机口航班分配情况', fontsize=18)
plt.show()

############### 按照宽体机和窄体机画出登机口安排的航班数量 ####################

wide_gates = [airport['gate'] for airport in airports if airport['body_type'] == 'W']
narrow_gates = [airport['gate'] for airport in airports if airport['body_type'] == 'N']

narrow_assign_num = {};
wide_assign_num = {}
for gate in assign_dict.keys():
    if gate in wide_gates:
        # print(len(assign_dict[gate]))
        wide_assign_num[gate] = len(assign_dict[gate])
    else:
        # print('narrow'+str(len(assign_dict[gate])))
        narrow_assign_num[gate] = len(assign_dict[gate])

narrow_assign_num = pd.DataFrame(narrow_assign_num, index=[0]).T
wide_assign_num = pd.DataFrame(wide_assign_num, index=[0]).T

plt.figure(figsize=(20, 10))
x = list(narrow_assign_num.index)
plt.bar(x, narrow_assign_num[0] * 2, facecolor='b')
plt.xlabel('窄体机登机口', fontsize=18)
plt.ylabel('每个登机口分配航班数量', fontsize=18)
plt.xticks(rotation=90, fontsize=16)
plt.yticks(fontsize=16)
plt.title('窄体登机口航班分配情况', fontsize=18)
plt.show()

plt.figure(figsize=(20, 10))
x = list(wide_assign_num.index)
plt.bar(x, wide_assign_num[0] * 2, facecolor='b')
plt.xlabel('宽体机登机口', fontsize=18)
plt.ylabel('每个登机口分配航班数量', fontsize=18)
plt.xticks(rotation=90, fontsize=14)
plt.yticks(fontsize=14)
plt.title('宽体机登机口航班分配情况', fontsize=18)
plt.show()

########## 按照卫星厅和航站楼登机口画出登机口的使用数目和登机口的平均使用率 #############

s_gates = [airport['gate'] for airport in airports if 'S' in airport['gate']]
t_gates = [airport['gate'] for airport in airports if 'T' in airport['gate']]

s_gates_assign = {};
t_gates_assign = {}
for gate in assign_dict.keys():
    if gate in s_gates:
        # print(len(assign_dict[gate]))
        s_gates_assign[gate] = len(assign_dict[gate])
    else:
        # print('narrow'+str(len(assign_dict[gate])))
        t_gates_assign[gate] = len(assign_dict[gate])

s_gates_assign = pd.DataFrame(s_gates_assign, index=[0]).T
t_gates_assign = pd.DataFrame(t_gates_assign, index=[0]).T

# 航站楼登机口航班分配情况
plt.figure(figsize=(20, 10))
x = list(t_gates_assign.index)
plt.bar(x, t_gates_assign[0] * 2, facecolor='b')
plt.xlabel('航站楼登机口', fontsize=18)
plt.ylabel('每个登机口分配航班数量', fontsize=18)
plt.xticks(rotation=90, fontsize=16)
plt.yticks(fontsize=16)
plt.title('航站楼登机口航班分配情况', fontsize=18)
plt.show()

# 卫星厅登机口航班分配情况
plt.figure(figsize=(20, 10))
x = list(s_gates_assign.index)
plt.bar(x, s_gates_assign[0] * 2, facecolor='b')
plt.xlabel('卫星厅登机口', fontsize=18)
plt.ylabel('每个登机口分配航班数量', fontsize=18)
plt.xticks(rotation=90, fontsize=16)
plt.yticks(fontsize=16)
plt.title('卫星厅登机口航班分配情况', fontsize=18)
plt.show()

###################### 航站楼和卫星厅登机口使用情况 ##################

s_airports = [airport for airport in airports if 'S' in airport['gate']]
t_airports = [airport for airport in airports if 'T' in airport['gate']]

s_busy_ratio = {};
t_busy_ratio = {}
assign_airport = list(assign_dict.keys())
for s_airport in s_airports:
    if s_airport['gate'] in assign_airport:
        all_time = len(s_airport['busy_time'])
        num_pucks = len(s_airport['puck_records'])
        busy_ratio = np.round((np.sum(s_airport['busy_time']) - 9 * num_pucks) / all_time, 4) * 100
        s_busy_ratio[s_airport['gate']] = busy_ratio

for t_airport in t_airports:
    if t_airport['gate'] in assign_airport:
        all_timet = len(t_airport['busy_time'])
        num_pucks = len(t_airport['puck_records'])
        busy_ratio = np.round((np.sum(t_airport['busy_time']) - 9 * num_pucks) / all_timet, 4) * 100
        t_busy_ratio[t_airport['gate']] = busy_ratio

s_busy_ratio = pd.DataFrame(s_busy_ratio, index=[0]).T
t_busy_ratio = pd.DataFrame(t_busy_ratio, index=[0]).T

plt.figure(figsize=(20, 10))
x = list(s_busy_ratio.index)
plt.bar(x, s_busy_ratio[0], facecolor='b')
plt.xlabel('卫星厅登机口', fontsize=18)
plt.ylabel('每个登机口使用率(%)', fontsize=18)
plt.xticks(rotation=90, fontsize=16)
plt.yticks(fontsize=16)
plt.title('卫星厅登机口使用情况', fontsize=18)
plt.show()

plt.figure(figsize=(20, 10))
x = list(t_busy_ratio.index)
plt.bar(x, t_busy_ratio[0], facecolor='b')
plt.xlabel('航站楼登机口', fontsize=18)
plt.ylabel('每个登机口使用率(%)', fontsize=18)
plt.xticks(rotation=90, fontsize=16)
plt.yticks(fontsize=16)
plt.title('航站楼登机口使用情况', fontsize=18)
plt.show()

# 计算中转失败乘客数量和比例

all_assign_pucks = []  # 所有已经分配的飞机转场记录号
for pucks in assign_pucks:
    all_assign_pucks.extend(pucks)

tickets = pd.read_csv('../data/tickets_pass_totoal (1).csv')


def is_assign_pucks(puck):
    if puck in all_assign_pucks:
        return 1
    else:
        return 0


tickets['到达分配登机口'] = tickets['到达转场号'].map(is_assign_pucks)
tickets['出发分配登机口'] = tickets['出发转场号'].map(is_assign_pucks)
tickets['均分配到登机口'] = (tickets['到达分配登机口'] & tickets['出发分配登机口'])

tmpsum = tickets[(tickets.到达分配登机口 == 0) & (tickets.出发分配登机口 == 1)]['乘客数'].sum()
tmprate = tmpsum / 2833
print(tmpsum)
print(tmprate)
