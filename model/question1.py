# 导入程序所需要的包
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
    airport_type = airport_type.split(',')
    if puck_type in airport_type:
        return 1
    else:
        return 0


def classify_airport(all_airports):
    # airport 是所有的登机口
    # classes: 字典用于存储每种类别的登机口
	# 第一问我们将登机口按照到达类型，出发类型，允许降落的飞机类型分类
    classes = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [],
               9: [], 10: [], 11: [], 12: [], 13: [], 14: [], 15: [], 16: [], 17: []}

    for airport in all_airports:
		# 登机口的飞机类型为窄体机
        if airport['body_type'] == 'N':
            if airport['a_type'] == 'D':
                if airport['d_type'] == 'D':
                    classes[0].append(airport)
                elif airport['d_type'] == 'I':
                    classes[1].append(airport)
                else:
                    classes[2].append(airport)
            elif airport['a_type'] == 'I':
                if airport['d_type'] == 'D':
                    classes[3].append(airport)
                elif airport['d_type'] == 'I':
                    classes[4].append(airport)
                else:
                    classes[5].append(airport)
            else:
                if airport['d_type'] == 'D':
                    classes[6].append(airport)
                elif airport['d_type'] == 'I':
                    classes[7].append(airport)
                else:
                    classes[8].append(airport)
        else:
            if airport['a_type'] == 'D':
                if airport['d_type'] == 'D':
                    classes[9].append(airport)
                elif airport['d_type'] == 'I':
                    classes[10].append(airport)
                else:
                    classes[11].append(airport)
            elif airport['a_type'] == 'I':
                if airport['d_type'] == 'D':
                    classes[12].append(airport)
                elif airport['d_type'] == 'I':
                    classes[13].append(airport)
                else:
                    classes[14].append(airport)
            else:
                if airport['d_type'] == 'D':
                    classes[15].append(airport)
                elif airport['d_type'] == 'I':
                    classes[16].append(airport)
                else:
                    classes[17].append(airport)

    return classes


def classify_puck(all_pucks):
    # all_pucks: 列表，所有转场记录的飞机航班
    # puck_classes: 字典，每种类别的转场记录飞机航班

    puck_classes = {0: [], 1: [], 2: [], 3: [],
                    4: [], 5: [], 6: [], 7: []}
    for puck in all_pucks:
        if puck['plane_type'] == 'N':
            if puck['a_type'] == 'D':
                if puck['d_type'] == 'D':
                    puck_classes[0].append(puck)
                else:
                    puck_classes[1].append(puck)
            else:
                if puck['d_type'] == 'D':
                    puck_classes[2].append(puck)
                else:
                    puck_classes[3].append(puck)
        else:
            if puck['a_type'] == 'D':
                if puck['d_type'] == 'D':
                    puck_classes[4].append(puck)
                else:
                    puck_classes[5].append(puck)
            else:
                if puck['d_type'] == 'D':
                    puck_classes[6].append(puck)
                else:
                    puck_classes[7].append(puck)

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
	# 本函数的功能是将飞机专场记录中的飞机型号转换为飞机类型
	# 宽体积的飞机类型
    Wide_body = ['332', '333', '33E', '33H', '33L', '773']
	#窄体机的飞机类型
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


def greedyselector(sort_puck_class, airport):
	# 该函数的功能是采用贪心算法分配航班到登机口
    # sort_puck_class: 排序好的转场记录，列表形式
    # airport: 一个登机口
    if airport['assign_flag'] == False:  # 登机口没有被分配
        start_times = [puck['arrive_time'] for puck in sort_puck_class]
        depart_times = [puck['depart_time'] for puck in sort_puck_class]
        j = 0    # 在输入的航班中，出发时间最早的航班下标
        while (sort_puck_class[j]['airport'] != ''):
		# 此while循环找到输入的所有航班中第一个没有被分配的航班下标
            j = j + 1
		# 将没有分配的航班分配给登机口
        sort_puck_class[j]['airport'] = airport['gate']
        airport['puck_records'].append(sort_puck_class[j]['record'])
        k = j
        for i in range(j + 1, len(sort_puck_class)):
            if start_times[i] >= depart_times[k]:
                if sort_puck_class[i]['airport'] == '':  # 如果该转场记录没有被分配
                    sort_puck_class[i]['airport'] = airport['gate']
                    k = i
                    airport['puck_records'].append(sort_puck_class[k]['record'])

        airport['assign_flag'] = True
        print('gates{} is {}'.format(airport['gate'], airport['puck_records']))
    return sort_puck_class, airport


def greedyselector1(sort_puck_class, airport):
	# 该函数的功能是采用贪心算法分配航班到登机口
    # sort_puck_class: 排序好的转场记录，列表形式
    # airport: 一个登机口
	# airport['busy_time']表示该登机口的被占用时间，初始化为所有元素均为0的数组
	# 数组长度为288，我们将一天24小时按照5分钟分段，一共有288段。0表示该段时间没有被
	# 占用，1表示该段时间被占用了。比如，如果一个登机口0:00-1:00之间被航班占用，那么该
	# 登机口的'busy_time'前12个元素为1
	
	
    start_times = [puck['arrive_time'] for puck in sort_puck_class]
    depart_times = [puck['depart_time'] for puck in sort_puck_class]

    j = 0
    while (sort_puck_class[j]['airport'] != ''):
	# 此while循环找到输入的所有航班中第一个没有被分配的航班下标
        j = j + 1

    if airport['assign_flag'] == False:  # 登机口没有被分配
		# 登机口被占用时间，初始化为空闲，24小时一共有288个5min段
        airport['busy_time'] = np.zeros(288)
		if start_times[j]==0:
			sp_ind = 0
		else:
			sp_ind = int(start_times[j] / 5) - 1
        ep_ind = int(depart_times[j] / 5)
		# 将没有分配的第j个航班分配给登机口
        sort_puck_class[j]['airport'] = airport['gate']
        airport['puck_records'].append(sort_puck_class[j]['record'])
        airport['busy_time'][sp_ind:ep_ind] = 1   # 将航班占用的时间段标记为繁忙（1）

        k = j
        for i in range(j + 1, len(sort_puck_class)):
            if start_times[i] >= depart_times[k]:
                if sort_puck_class[i]['airport'] == '':  # 如果该转场记录没有被分配
                    sort_puck_class[i]['airport'] = airport['gate']
                    k = i
                    airport['puck_records'].append(sort_puck_class[k]['record'])
                    s_ind = max(int(start_times[i] / 5) - 1, 0)
                    e_ind = int(depart_times[i] / 5)
                    airport['busy_time'][s_ind:e_ind] = 1
        airport['assign_flag'] = True
    else:
        for i in range(j + 1, len(sort_puck_class)):
            if sort_puck_class[i]['airport'] == '':  # 如果该转场记录没有被分配
                puck_time = np.zeros(288)
                s_ind = max(int(start_times[i] / 5) - 1, 0)
                e_ind = int(depart_times[i] / 5)
                puck_time[s_ind:e_ind] = 1
                temp_time = puck_time + airport['busy_time']
                if np.max(temp_time) <= 1:
                    airport['busy_time'] = temp_time
                    sort_puck_class[i]['airport'] = airport['gate']
                    airport['puck_records'].append(sort_puck_class[k]['record'])

    print('gates{} has assigned {}'.format(airport['gate'], airport['puck_records']))
    return sort_puck_class, airport


def assign_puck(puck_class, gate_class):
	# 该函数的功能是分配航班到登机口
    if len(puck_class) == 0 or len(gate_class) == 0:
        return puck_class, gate_class
    sort_puck_class = sort_pucks(puck_class)
    puck = sort_puck_class[0]
    gate = gate_class[0]
    if puck['plane_type'] == gate['body_type']:
        if (type_is_same(puck['a_type'], gate['a_type']) & (type_is_same(puck['d_type'], gate['d_type']))):
            # final_gates = []    #; final_pucks = []
            for i in range(len(gate_class)):
                puck_not_assign = [puck for puck in sort_puck_class if puck['airport'] == '']
                if len(puck_not_assign) == 0:
                    break
                sort_puck_class, airport = greedyselector1(sort_puck_class, gate_class[i])
                gate_class[i] = airport
                # final_pucks.extend(assign_pucks)
            return sort_puck_class, gate_class
        else:
            return sort_puck_class, gate_class
    else:
        return sort_puck_class, gate_class


# 读取文件
gates = pd.read_csv('../data/gates (1).csv')
new_gates = gates[['登机口', '终端厅', '区域', '到达类型', '出发类型', '机体类别']]

puck_data = pd.read_csv('../data/puck_data.csv', encoding='gbk')
cols = ['飞机转场记录号', '到达相对时间min', '到达航班', '到达类型',
        '飞机型号', '出发相对时间min', '出发航班', '出发类型']
puck_data = puck_data[cols]

# 创建登机口列表和专场航班记录列表，每个元素为一个登机口或者航班，类型为字典类型
airports = create_gates(new_gates)
allpucks = create_pucks(puck_data)

# 将登机口和转场记录航班分类
puck_classes = classify_puck(allpucks)
gate_classes = classify_airport(airports)

# 出发类型和到达类型均为单类型的登机口类别在gate_classes的下标
single_type_gate = [0, 1, 3, 4, 9, 10, 12, 13]
# 出发类型或到达类型至少有一个为国内和国际的登机口类别在gate_classes的下标
multi_type_gate = [2, 5, 6, 7, 8, 11, 14, 15, 16, 17]
single_gate_classes = [gate_classes[code] for code in single_type_gate]
multi_gate_classes = [gate_classes[code] for code in multi_type_gate]

# 用于存储登机口和转场记录被分配的情况
assign_pucks = [];
assign_gates = []

# 先将所有类别的转场记录按照贪心算法分配到对应的单类型登机口
for i in range(len(puck_classes)):
    as_puck, as_gate = assign_puck(puck_classes[i], single_gate_classes[i])
    assign_pucks.append(as_puck)
    assign_gates.append(as_gate)

# 将更新后的飞机转场记录分配到多类型登机口
for j in range(len(multi_type_gate)):
    print(len(multi_gate_classes[j]))
    for k in range(len(puck_classes)):
        am_puck, am_gate = assign_puck(assign_pucks[k], multi_gate_classes[j])
        ass_puck = [puck for puck in am_puck if puck['airport'] != '']
        print('has assigned ' + str(len(ass_puck)))
        print(len(am_puck))
        print('-------------------------------')
        assign_pucks[k] = am_puck
        multi_gate_classes[j] = am_gate
        # print(len(multi_gate_classes[j]))
    print('=================================')
    assign_gates.append(multi_gate_classes[j])

# assign_gates记录了所有的登机口分配的情况
assign_gates = [assign_gates[i] for i in range(len(assign_gates)) if len(assign_gates[i]) > 0]

gate_sum = 0  # 计数被分配的登机口数量
puck_sum = 0  # 计数被分配的转场飞机记录数量

final_assign_pucks = []   # 记录最终被分配到每个登机口的转场记录
final_assign_gates = []   # 记录使用的登机口

for i in range(len(assign_gates)):
    for j in range(len(assign_gates[i])):
        num_pucks = len(assign_gates[i][j]['puck_records'])
        puck_sum += num_pucks
        if num_pucks > 0:
            gate_sum += 1
            print(assign_gates[i][j]['puck_records'])
            final_assign_gates.append(assign_gates[i][j]['gate'])
            final_assign_pucks.append(assign_gates[i][j]['puck_records'])

# 将使用的登机口与该登机口分配的转场飞机记录对应起来，存储成一个字典
assign_dict = dict(zip(final_assign_gates, final_assign_pucks))

# 从字典写入csv文件

csvFile3 = open('../result/问题一答案.csv', 'w', newline='')
writer2 = csv.writer(csvFile3)
for key in assign_dict:
    writer2.writerow([key, assign_dict[key]])
csvFile3.close()

###################### 画图 ##################

num_assign_pucks = [len(pucks) for pucks in final_assign_pucks]  # 每个登机口分配的飞机转场记录数量
assign_dict = dict(zip(final_assign_gates, final_assign_pucks))
assign_dict1 = dict(zip(final_assign_gates, num_assign_pucks))
assigns = pd.DataFrame(assign_dict1, index=[0])
assigns = assigns.T

###
# 画出被使用的登机口安排的航班数量图
plt.figure(figsize=(20, 10))
x = list(assigns.index)
plt.bar(x, assigns[0] * 2, facecolor='b')
plt.xlabel('登机口', fontsize=18)
plt.ylabel('登机口分配的总航班数量', fontsize=18)
plt.xticks(rotation=90, fontsize=16)
plt.title('登机口航班分配情况', fontsize=18)
plt.yticks(fontsize=16)
plt.show()

# 按照宽体机和窄体机画出登机口安排的航班数量
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

# 窄体登机口航班分配
plt.figure(figsize=(20, 10))
x = list(narrow_assign_num.index)
plt.bar(x, narrow_assign_num[0] * 2, facecolor='b')
plt.xlabel('窄体机登机口', fontsize=18)
plt.ylabel('每个登机口分配航班数量', fontsize=18)
plt.xticks(rotation=90, fontsize=16)
plt.yticks(fontsize=16)
plt.title('窄体登机口航班分配情况', fontsize=18)
plt.show()

# 宽体机登机口航班分
plt.figure(figsize=(20, 10))
x = list(wide_assign_num.index)
plt.bar(x, wide_assign_num[0] * 2, facecolor='b')
plt.xlabel('宽体机登机口', fontsize=18)
plt.ylabel('每个登机口分配航班数量', fontsize=18)
plt.xticks(rotation=90, fontsize=14)
plt.yticks(fontsize=14)
plt.title('宽体机登机口航班分配情况', fontsize=18)
plt.show()

######## 按照卫星厅和航站楼登机口画出登机口的使用数目和登机口的平均使用率 #############

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

# 航站楼登机口航班分配
plt.figure(figsize=(20, 10))
x = list(t_gates_assign.index)
plt.bar(x, t_gates_assign[0] * 2, facecolor='b')
plt.xlabel('航站楼登机口', fontsize=18)
plt.ylabel('每个登机口分配航班数量', fontsize=18)
plt.xticks(rotation=90, fontsize=16)
plt.yticks(fontsize=16)
plt.title('航站楼登机口航班分配情况', fontsize=18)
plt.show()

# 卫星厅登机口航班分配
plt.figure(figsize=(20, 10))
x = list(s_gates_assign.index)
plt.bar(x, s_gates_assign[0] * 2, facecolor='b')
plt.xlabel('卫星厅登机口', fontsize=18)
plt.ylabel('每个登机口分配航班数量', fontsize=18)
plt.xticks(rotation=90, fontsize=16)
plt.yticks(fontsize=16)
plt.title('卫星厅登机口航班分配情况', fontsize=18)
plt.show()

#################### 登机口使用情况 ######################

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

# 卫星厅登机口使用情况
plt.figure(figsize=(20, 10))
x = list(s_busy_ratio.index)
plt.bar(x, s_busy_ratio[0], facecolor='b')
plt.xlabel('卫星厅登机口', fontsize=18)
plt.ylabel('每个登机口使用率(%)', fontsize=18)
plt.xticks(rotation=90, fontsize=16)
plt.yticks(fontsize=16)
plt.title('卫星厅登机口使用情况', fontsize=18)
plt.show()

# 航站楼登机口使用情况
plt.figure(figsize=(20, 10))
x = list(t_busy_ratio.index)
plt.bar(x, t_busy_ratio[0], facecolor='b')
plt.xlabel('航站楼登机口', fontsize=18)
plt.ylabel('每个登机口使用率(%)', fontsize=18)
plt.xticks(rotation=90, fontsize=16)
plt.yticks(fontsize=16)
plt.title('航站楼登机口使用情况', fontsize=18)
plt.show()
