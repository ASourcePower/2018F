# coding: utf-8

import pandas as pd
import warnings

warnings.filterwarnings('ignore')

# 文件读取
gates = pd.read_excel('./InputData.xlsx', sheet_name='Gates')
pucks = pd.read_excel('./InputData.xlsx', sheet_name='Pucks')
tickets = pd.read_excel('./InputData.xlsx', sheet_name='Tickets')

######################## 飞机航班转场 ##########################################

# 航线机体类别映射
W_list = ['332', '333', '33E', '33H', '33L', '773']
N_list = ['319', '320', '321', '323', '325', '738', '73A', '73E', '73H', '73L']
pucks['L'] = pucks.飞机型号.apply(lambda x: 1 if str(x) in W_list else 0)

# 修正时间bug
# 修正到达时刻
# [' 7:0',' 5:0',' 6:0',' 9:0',' 7:5',' 0:5']
pucks.loc[pucks['到达\n时刻'] == ' 7:0', '到达\n时刻'] = '7:00:00'
pucks.loc[pucks['到达\n时刻'] == ' 5:0', '到达\n时刻'] = '5:00:00'
pucks.loc[pucks['到达\n时刻'] == ' 6:0', '到达\n时刻'] = '6:00:00'
pucks.loc[pucks['到达\n时刻'] == ' 7:5', '到达\n时刻'] = '7:05:00'
pucks.loc[pucks['到达\n时刻'] == ' 9:0', '到达\n时刻'] = '9:00:00'
pucks.loc[pucks['到达\n时刻'] == ' 0:5', '到达\n时刻'] = '0:05:00'

# 日期时刻合成
pucks['到达时刻'] = pd.to_datetime(pucks['到达\n日期'].astype(str) + ' ' + pucks['到达\n时刻'].astype(str))

# 修正出发时刻
pucks.loc[pucks['出发\n时刻'] == ' 9:5', '出发\n时刻'] = '9:05:00'
pucks.loc[pucks['出发\n时刻'] == ' 9:0', '出发\n时刻'] = '9:00:00'
pucks.loc[pucks['出发\n时刻'] == ' 0:5', '出发\n时刻'] = '0:05:00'
pucks.loc[pucks['出发\n时刻'] == ' 8:0', '出发\n时刻'] = '8:00:00'
pucks.loc[pucks['出发\n时刻'] == ' 1:5', '出发\n时刻'] = '1:05:00'
pucks.loc[pucks['出发\n时刻'] == ' 8:5', '出发\n时刻'] = '8:05:00'
pucks.loc[pucks['出发\n时刻'] == ' 0:0', '出发\n时刻'] = '0:00:00'

# 日期时刻合成
pucks['出发时刻'] = pd.to_datetime(pucks['出发\n日期'].astype(str) + ' ' + pucks['出发\n时刻'].astype(str))

# 删失时间

# 找出到达日期或出发日期在2018年1月20日
pucks20 = pucks.loc[(pucks['到达\n日期'] == pd.to_datetime('2018-1-20')) | (pucks['出发\n日期'] == pd.to_datetime('2018-1-20'))]

"""
# 1. 考虑转机记录的到达日期在2018-1-20日前
# > 到达时刻修正为2018-1-20，即从改天00:00:00开始占用时间
#
# 2. 考虑转机记录的到达航班为*****
# > 从到达时刻开始占用时间
#
# 3. 考虑转机记录的出发占用时间在2018-1-20后，即出发航班在2018-1-20 11:15:00后
# > 出发时刻修正为2018-1-21
#
# 4. 考虑转机记录的出发航班为*****
# > 此部分转机保留不处理
"""

# 修正到达时刻在2018-1-20前
pucks20['修正到达时刻'] = pucks20.到达时刻.apply(lambda x: pd.to_datetime('2018-1-20') if x < pd.to_datetime('2018-1-20') else x)
# 偏移出发时刻
pucks20['偏移出发时刻'] = pucks20.出发时刻 + pd.to_timedelta('45 min')
# 修正出发时刻
pucks20['修正出发时刻'] = pucks20.偏移出发时刻.apply(
    lambda x: pd.to_datetime('2018-1-20 23:55:00') if x >= pd.to_datetime('2018-1-21') else x)
# 计算相对时间
pucks20['到达相对时间min'] = (pucks20.修正到达时刻 - pd.to_datetime('2018-1-20')).dt.seconds // 60
pucks20['出发相对时间min'] = (pucks20.修正出发时刻 - pd.to_datetime('2018-1-20 00:00:00')).dt.seconds // 60
# 计算时间窗索引
pucks20['占用开始索引'] = (pucks20.到达相对时间min // 5)
pucks20['占用结束索引'] = (pucks20.出发相对时间min // 5)

#######################################################

# 飞机航班到达类型
pucks['F_aI'] = pucks['到达类型'].map({'D': 0, 'I': 1})
pucks['F_aD'] = pucks['到达类型'].map({'D': 1, 'I': 0})
# 飞机航班出发类型
pucks['F_oI'] = pucks['出发类型'].map({'D': 0, 'I': 1})
pucks['F_oD'] = pucks['出发类型'].map({'D': 1, 'I': 0})

pucks20.to_csv('../data/pucks20.csv', index=False)

################################ 登机口 ###################################

# gates机体类别
# 宽体机：W；1
# 窄体机：N；0
gates['P'] = gates.机体类别.map({'N': 0, 'W': 1})

# 登机口航站楼卫星厅分类
gates['T'] = gates.终端厅.map({'T': 1, 'S': 0})
gates['S'] = gates.终端厅.map({'S': 1, 'T': 0})

# 登机口到达类型
gates.loc[gates.到达类型.str.contains('I'), 'T_aI'] = 1
gates.T_aI = gates.T_aI.fillna(0)
gates.loc[gates.到达类型.str.contains('D'), 'T_aD'] = 1
gates.T_aD = gates.T_aD.fillna(0)

# 登机口出发类型
gates.loc[gates.出发类型.str.contains('I'), 'T_oI'] = 1
gates.T_oI = gates.T_oI.fillna(0)
gates.loc[gates.出发类型.str.contains('D'), 'T_oD'] = 1
gates.T_oD = gates.T_oD.fillna(0)

gates.to_csv('../data/gates.csv', index=False)

################################## 旅客换乘信息 #########################

# 选出在20号有换乘的乘客
tickets20 = tickets.loc[
    (tickets['出发\n日期'] == pd.to_datetime('2018-1-20')) | (tickets['到达\n日期'] == pd.to_datetime('2018-1-20'))]
tickets21 = tickets20.merge(pucks[['到达\n航班', '到达类型', '到达\n日期', '飞机转场记录号']].drop_duplicates(), how='inner',
                            on=['到达\n航班', '到达\n日期']).rename(columns={'飞机转场记录号': '到达转场号'})
tickets22 = tickets21.merge(pucks[['出发\n航班', '出发类型', '出发\n日期', '飞机转场记录号']].drop_duplicates(), how='inner',
                            on=['出发\n航班', '出发\n日期']).rename(columns={'飞机转场记录号': '出发转场号'})
# tickets23表示乘客转机在同一架航班的旅客记录
tickets23 = pd.merge(tickets22, pucks20[['到达\n航班', '出发\n航班']].drop_duplicates(), on=['到达\n航班', '出发\n航班'])
tickets24 = tickets22.loc[~tickets22['旅客\n记录号'].isin(tickets23['旅客\n记录号'])]

tickets22.to_csv('./all_tickets.csv', index=False)
tickets23.to_csv('./E_tickets.csv', index=False)
tickets24.to_csv('./unE_tickets.csv', index=False)

# 将相同航班转场的旅客合并
tickets_pass_num = tickets22.groupby(['到达\n航班', '出发\n航班', '到达类型', '出发类型', '到达转场号', '出发转场号'])[
    '乘客数'].sum().reset_index().sort_values(by='乘客数', ascending=False)

# 构造指示变量E_mn,表示乘客乘坐同一架飞机
tickets_pass_num.loc[tickets_pass_num['出发转场号'] == tickets_pass_num['到达转场号'], 'E_mn'] = 1
tickets_pass_num.E_mn.fillna(0, inplace=True)

# 旅客换乘航班类型（国内国际）
tickets_pass_num['A_I'] = tickets_pass_num['到达类型'].map({'I': 1, 'D': 0})
tickets_pass_num['A_D'] = tickets_pass_num['到达类型'].map({'D': 1, 'I': 0})
tickets_pass_num['O_I'] = tickets_pass_num['出发类型'].map({'I': 1, 'D': 0})
tickets_pass_num['O_D'] = tickets_pass_num['出发类型'].map({'D': 1, 'I': 0})

# 计算旅客航班连接时间
tickets_pass_num = pd.merge(tickets_pass_num, pucks[['飞机转场记录号', '到达时刻']].drop_duplicates(), how='inner',
                            left_on='到达转场号', right_on='飞机转场记录号').drop('飞机转场记录号', axis=1)
tickets_pass_num = pd.merge(tickets_pass_num, pucks[['飞机转场记录号', '出发时刻']].drop_duplicates(), how='inner',
                            left_on='出发转场号', right_on='飞机转场记录号').drop('飞机转场记录号', axis=1)

tickets_pass_num['conn_gap_min'] = (tickets_pass_num.出发时刻 - tickets_pass_num.到达时刻).dt.seconds / 60

# 换乘最大时间
tickets_pass_num.loc[(tickets_pass_num.到达类型 == 'I') & (tickets_pass_num.出发类型 == 'I'), 'transfer_time_max'] = 53
tickets_pass_num.loc[(tickets_pass_num.到达类型 == 'I') & (tickets_pass_num.出发类型 == 'D'), 'transfer_time_max'] = 81
tickets_pass_num.loc[(tickets_pass_num.到达类型 == 'D') & (tickets_pass_num.出发类型 == 'I'), 'transfer_time_max'] = 73
tickets_pass_num.loc[(tickets_pass_num.到达类型 == 'D') & (tickets_pass_num.出发类型 == 'D'), 'transfer_time_max'] = 53

# 换乘最少时间
tickets_pass_num.loc[(tickets_pass_num.到达类型 == 'I') & (tickets_pass_num.出发类型 == 'I'), 'transfer_time_min'] = 40
tickets_pass_num.loc[(tickets_pass_num.到达类型 == 'I') & (tickets_pass_num.出发类型 == 'D'), 'transfer_time_min'] = 55
tickets_pass_num.loc[(tickets_pass_num.到达类型 == 'D') & (tickets_pass_num.出发类型 == 'I'), 'transfer_time_min'] = 55
tickets_pass_num.loc[(tickets_pass_num.到达类型 == 'D') & (tickets_pass_num.出发类型 == 'D'), 'transfer_time_min'] = 35

tickets_pass_num.to_csv('./tickets_pass_totoal.csv', index=False)
