# -*- coding: utf-8 -*-
"""
Liyao Zhang
1/13/2022
星辰智盈自动回测系统 with Gooey V1.0

"""

import pandas as pd
from numpy import mean
import xlsxwriter
import re
from collections import Counter
from gooey import Gooey, GooeyParser

# *** 图形界面模块 *** #
@Gooey(program_name="星辰智盈自动回测系统",
       default_size=(500, 550),
       tabbed_groups=True,
       navigation='Tabbed',
       language='Chinese'
)
def main():
    parser = GooeyParser()
    group1 = parser.add_argument_group('回测分析', gooey_options={"columns": 1})
    group1.add_argument('-file', metavar='数据库文件所在路径', widget="FileChooser")
    group1.add_argument('-path', metavar='结果文件保存路径', widget="FileSaver")
    group1.add_argument('--opt1', metavar='统计历史胜率', action='store_true')  
    args = parser.parse_args()
    
    if args.file and args.path:
        df = read_file(args.file)
        search(df, args)

# *** 连接层函数 *** #    
def read_file(data):
    df = pd.read_excel(data, sheet_name = 1, converters = {'盘口': str, '竞彩': str, '比分': str})
    df['盘口数字'] = df['盘口'].astype(float)
    df['算法'] = df['算法'].fillna('球伯乐')
    df['注释'] = df['注释'].fillna('')
    df['批注胜'] = df['批注胜'].fillna('')
    df['批注平'] = df['批注平'].fillna('')
    df['批注负'] = df['批注负'].fillna('')
    df['批注让胜'] = df['批注让胜'].fillna('')
    df['批注让平'] = df['批注让平'].fillna('')
    df['批注让负'] = df['批注让负'].fillna('')
    return df

def read_fire(data):
    df = pd.read_excel(data, sheet_name = 3)
    return df
    
# *** 核心层函数 *** #
# 计算概率、判断上下盘及遗漏提示
def calc_prob(home, away, deep, result, total):        
    p_win = (len(result[result['H'] >result['A']])/total)*100
    p_tie = (len(result[result['H']==result['A']])/total)*100
    p_los = (len(result[result['H'] <result['A']])/total)*100
    if home and deep:
        p_h2 = (len(result[(result['H']-result['A']) > 1])/total)*100
        print("主胜占比:",round(p_win,2),'%',"平局占比:",round(p_tie,2),'%',"客胜占比:",round(p_los,2),'%',"主队赢得两球及以上占比:",round(p_h2,2),'%')
    elif away and deep:
        p_a2 = (len(result[(result['A']-result['H']) > 1])/total)*100
        print("主胜占比:",round(p_win,2),'%',"平局占比:",round(p_tie,2),'%',"客胜占比:",round(p_los,2),'%',"客队赢得两球及以上占比:",round(p_a2,2),'%')
    else:
        print("主胜占比:",round(p_win,2),'%',"平局占比:",round(p_tie,2),'%',"客胜占比:",round(p_los,2),'%')
    #主让上盘方向    
    if home and not deep and p_win > (p_tie+p_los):
        miss = 0
        if p_win >= 60:
            for index, row in result.iterrows():
                if row['H'] <= row['A']:
                    miss += 1
                else:
                    miss = 0
            if miss > 1:
                print("提示：主队赢盘遗漏",miss,"场")
        return p_win, 'home', miss
    #主让下盘方向
    elif home and not deep and p_win <= (p_tie+p_los):
        miss = 0
        if (p_tie+p_los) >= 60:
            for index, row in result.iterrows():
                if row['H'] > row['A']:
                    miss += 1
                else:
                    miss = 0
            if miss > 1:
                print("提示：客队赢盘遗漏",miss,"场")
        return p_tie+p_los, 'away', miss
    #客让上盘方向
    elif away and not deep and p_los > (p_tie+p_win):
        miss = 0
        if p_los >= 60:
            for index, row in result.iterrows():
                if row['H'] >= row['A']:
                    miss += 1
                else:
                    miss = 0
            if miss > 1:
                print("提示：客队赢盘遗漏",miss,"场")
        return p_los, 'away', miss
    #客让下盘方向
    elif away and not deep and p_los <= (p_tie+p_win):
        miss = 0
        if (p_tie+p_win) >= 60:
            for index, row in result.iterrows():
                if row['H'] < row['A']:
                    miss += 1
                else:
                    miss = 0
            if miss > 1:
                print("提示：主队赢盘遗漏",miss,"场")
        return p_win+p_tie, 'home', miss
    #深盘主让上盘方向
    elif home and deep and p_h2 > 50:
        miss = 0
        if p_h2 >= 60:
            for index, row in result.iterrows():
                if (row['H']-1) <= row['A']:
                    miss += 1
                else:
                    miss = 0
            if miss > 1:
                print("提示：主队赢盘遗漏",miss,"场")
        return p_h2, 'home', miss
    #深盘主让下盘方向
    elif home and deep and p_h2 <= 50:
        miss = 0
        if p_h2 <= 40:
            for index, row in result.iterrows():
                if (row['H']-1) > row['A']:
                    miss += 1
                else:
                    miss = 0
            if miss > 1:
                print("提示：客队赢盘遗漏",miss,"场")
        return 100-p_h2, 'away', miss        
    #深盘客让上盘方向
    elif away and deep and p_a2 > 50:
        miss = 0
        if p_a2 >= 60:
            for index, row in result.iterrows():
                if (row['H']+1) >= row['A']:
                    miss += 1
                else:
                    miss = 0
            if miss > 1:
                print("提示：客队赢盘遗漏",miss,"场")
        return p_a2, 'away', miss
    #深盘客让下盘方向
    elif away and deep and p_a2 <= 50:
        miss = 0
        if p_a2 <= 40:
            for index, row in result.iterrows():
                if (row['H']+1) < row['A']:
                    miss += 1
                else:
                    miss = 0
            if miss > 1:
                print("提示：主队赢盘遗漏",miss,"场")
        return 100-p_a2, 'home', miss

# 对预估概率进行修正
def laplace(temp, total):
    num = (temp/100)*total
    est_prob = (num+1)/(total+2)
    return est_prob*100
    
# 储存每一步筛选的上/下盘概率
def decision(home, away, uppr, down, temp, signal):
    if home:
        if signal == 'home':
            uppr.append(temp)
            down.append(100-temp)
        elif signal == 'away':
            down.append(temp)
            uppr.append(100-temp)
    elif away:
        if signal == 'away':
            uppr.append(temp)
            down.append(100-temp)
        elif signal == 'home':
            down.append(temp)
            uppr.append(100-temp)
    return uppr, down

# 储存60%(拉普拉斯修正后约57%)/70%/80%概率的算法数
def analysis(best_prob, count):
    if 57 < best_prob < 70:
        count[0] += 1
    elif 70 <= best_prob < 80:
        count[1] += 1
    elif best_prob >= 80:
        count[2] += 1
    return count

#判断历史比赛正误
def judge(new_score, hand, home, away, deep, signal):
    if home and not deep:
        if signal == 'uppr':
            if new_score[0] > new_score[1]:
                return True
            elif hand == 0 and new_score[0] >= new_score[1]:
                return True
            else:
                return False
        elif signal == 'down':
            if new_score[0] <= new_score[1]:
                return True
            elif hand >= 1 and (new_score[0]-1) <= new_score[1]:
                return True
            else:
                return False
    elif home and deep:
        if signal == 'uppr':
            if (new_score[0]+hand) >= new_score[1]:
                return True
            else:
                return False
        elif signal == 'down':
            if (new_score[0]+hand) <= new_score[1]:
                return True
            else:
                return False
    elif away and not deep:
        if signal == 'uppr':
            if new_score[0] < new_score[1]:
                return True
            elif hand == 0 and new_score[0] <= new_score[1]:
                return True
            else:
                return False
        elif signal == 'down':
            if new_score[0] >= new_score[1]:
                return True
            elif hand >= 1 and (new_score[0]+1) >= new_score[1]:
                return True
            else:
                return False
    elif away and deep:
        if signal == 'uppr':
            if (new_score[0]+hand) <= new_score[1]:
                return True
            else:
                return False
        elif signal == 'down':
            if (new_score[0]+hand) >= new_score[1]:
                return True
            else:
                return False
            
# 计算出现频率最高的比分            
def score_freq(score):
    line = ''
    freq = 0
    L = Counter(score).most_common(1)
    score_L = [X[0] for X in L]
    freqc_L = [X[1] for X in L]
    for Y in score_L:
        line = Y
    for Z in freqc_L:
        freq = Z
    return line, freq
    
# 回测主函数
def search(df, args):
    history = False
    if args.opt1:
        history = True
    #创建新工作簿以写入结果
    wb = xlsxwriter.Workbook(args.path)
    worksheet = wb.add_worksheet("My sheet")
    x = 0
    y = 0
    worksheet.write(x, y, '联赛')
    worksheet.write(x, y+1, '比赛')
    worksheet.write(x, y+2, '让球方')
    worksheet.write(x, y+3, '盘口')
    worksheet.write(x, y+4, '模型')
    worksheet.write(x, y+5, '平均概率')
    worksheet.write(x, y+6, '最长遗漏')
    worksheet.write(x, y+7, '高频比分')
    worksheet.write(x, y+8, '频率')
    if history:
        worksheet.write(x, y+9, '正误')
    worksheet.write(x, y+10, '注释')
    x += 1
    
    #储存每一行信息的变量
    liga = '中甲'
    prev = 'nmsl' #上一行比赛名称
    hand = 'mlgb' #上一行盘口
    num_hand = 69 #上一行盘口数字
    home = False #主让
    away = False #客让
    deep = False #深盘
    
    #储存每一场比赛信息的变量
    uppr_count = [0,0,0] #上盘三星级 四星级 五星级算法结果数量
    down_count = [0,0,0] #下盘三星级 四星级 五星级算法结果数量
    avg_uppr = [] #各算法上盘最优概率
    avg_down = [] #各算法下盘最优概率
    upprmiss = [] #上盘遗漏数量
    downmiss = [] #下盘遗漏数量
    algo = 1      #每场比赛算法数量
    score = ()    #每场比赛推荐比分
    comment = []  #每场比赛注释和批注
    
    for index, row in df[df['H'].isnull() & df['盘口'].notnull()].iterrows():
        flag = False #非竞彩客让
        rare = False #竞彩客让
        roll = False #继续筛选
        skip = False #跳过让负
        best_prob = 0 #当前算法最优概率
        temp_miss = []#当前算法遗漏数量
        uppr = [] #每次筛选后的上盘概率
        down = [] #每次筛选后的下盘概率
        
        #旧比赛
        if row['比赛'] == prev:
            algo += 1
        #新比赛
        else:
            if prev != 'nmsl':
                #计算最高频比分
                line, freq = score_freq(score)
            #上盘
            if sum(uppr_count)/algo > 0.5 and algo > 1:
                #注释和批注
                if comment:
                    com_str = ''
                    for item in comment:
                        item = str(item)
                        com_str += str(item + ",")
                    com_str = com_str[:-1]
                    worksheet.write(x, y+10, com_str)
                #写入上盘信息
                avg_best = mean(avg_uppr)
                worksheet.write(x, y, liga)
                worksheet.write(x, y+1, prev)
                if home:
                    worksheet.write(x, y+2, '主让')
                elif away:
                    worksheet.write(x, y+2, '客让')
                worksheet.write(x, y+3, hand)
                worksheet.write(x, y+5, str(round(avg_best,2))+'%')
                if upprmiss:
                    worksheet.write(x, y+6, max(upprmiss))
                worksheet.write(x, y+7, line)
                worksheet.write(x, y+8, freq)
                if history:
                    TF = judge(new_score, num_hand, home, away, deep, 'uppr')
                    if TF:
                        worksheet.write(x, y+9, '\u2714')
                    else:
                        worksheet.write(x, y+9, '\u2716')
                
                if avg_best >= 60 and uppr_count[2] > 0:
                    worksheet.write(x, y+4, '新发现！！！五星级上盘模型') 
                    print('新发现！！！五星级上盘模型：',prev,'平均概率',round(avg_best,2),'%')
                elif avg_best >= 60 and uppr_count[1] > 0:
                    worksheet.write(x, y+4, '新发现！！四星级上盘模型')
                    print('新发现！！四星级上盘模型：',prev,'平均概率',round(avg_best,2),'%')
                elif (avg_best >= 50) and ((uppr_count[0] > 1) or (uppr_count[1] > 0) or (uppr_count[2] > 0)):
                    worksheet.write(x, y+4, '新发现！三星级上盘模型')
                    print('新发现！三星级上盘模型：',prev,'平均概率',round(avg_best,2),'%')
                x += 1
            #下盘
            elif sum(down_count)/algo > 0.5 and algo > 1:
                #注释和批注
                if comment:
                    com_str = ''
                    for item in comment:
                        item = str(item)
                        com_str += str(item + ",")
                    com_str = com_str[:-1]
                    worksheet.write(x, y+10, com_str)
                #写入下盘信息
                avg_best = mean(avg_down)
                worksheet.write(x, y, liga)
                worksheet.write(x, y+1, prev)
                if home:
                    worksheet.write(x, y+2, '主让')
                elif away:
                    worksheet.write(x, y+2, '客让')
                worksheet.write(x, y+3, hand)
                worksheet.write(x, y+5, str(round(avg_best,2))+'%')
                if downmiss:
                    worksheet.write(x, y+6, max(downmiss))
                worksheet.write(x, y+7, line)
                worksheet.write(x, y+8, freq)
                if history:
                    TF = judge(new_score, num_hand, home, away, deep, 'down')
                    if TF:
                        worksheet.write(x, y+9, '\u2714')
                    else:
                        worksheet.write(x, y+9, '\u2716')
                    
                if avg_best >= 60 and down_count[2] > 0:
                    worksheet.write(x, y+4, '新发现！！！五星级下盘模型')                    
                    print('新发现！！！五星级下盘模型：',prev,'平均概率',round(avg_best,2),'%')
                elif avg_best >= 60 and down_count[1] > 0:
                    worksheet.write(x, y+4, '新发现！！四星级下盘模型')
                    print('新发现！！四星级下盘模型：',prev,'平均概率',round(avg_best,2),'%')
                elif (avg_best >= 50) and ((down_count[0] > 1) or (down_count[1] > 0) or (down_count[2] > 0)):
                    worksheet.write(x, y+4, '新发现！三星级下盘模型')
                    print('新发现！三星级下盘模型：',prev,'平均概率',round(avg_best,2),'%')
                x += 1
            print('=============================================')
            #重置上一场比赛信息
            algo = 1
            score = []
            comment = []
            uppr_count = [0,0,0]
            down_count = [0,0,0]
            avg_uppr = []
            avg_down = []
            upprmiss = []
            downmiss = []
        #清空上一行信息并更新
        liga = row['联赛']
        prev = row['比赛']
        hand = row['盘口']
        num_hand = row['盘口数字']
        home = False
        away = False
        deep = False
        
        #判断让球方
        if row['盘口'].__contains__('-'):
            if (row['盘口']=='-0.25') and (row['让胜'] <= row['平']+row['胜']+0.03) and (row['让胜'] >= row['平']+row['胜']-0.03) and (0 < (row['胜']+row['平']) < 1):
                away = True
            elif (row['盘口']=='-0') and (row['让胜'] <= row['平']+row['胜']+0.03) and (row['让胜'] >= row['平']+row['胜']-0.03) and (0 < (row['胜']+row['平'])) and (row['竞彩'] == '是'):
                away = True
            else:
                home = True

        elif row['盘口'].__contains__('+'):
            if (row['竞彩'] == '是') and (row['让负'] <= row['平']+row['负']+0.03) and (row['让负'] >= row['平']+row['负']-0.03):
                home = True
            else:
                away = True
        #深盘比赛
        if (row['盘口数字'] < -1.25) or (row['盘口数字'] > 1.25):
            deep = True

        if home:
            print("正在分析:",row['联赛'],row['比赛'],row['算法'],'主队让球:',row['盘口'],"\n")
        elif away:
            print("正在分析:",row['联赛'],row['比赛'],row['算法'],'客队让球:',row['盘口'],"\n")
            
        #第0轮筛选 胜平负
        result0 = df[(df['H'].notnull()) & (df['胜'] == row['胜']) & (df['平'] == row['平'])]
        total = len(result0)
        if total < 2:
            print("历史样本不足:",total,'场')
        elif total >= 2 and total < 8:
            temp = df[(df['H'].notnull()) & (df['胜'] == row['负']) & (df['平'] == row['平'])]
            mixed = pd.concat([result0, temp], axis=0)
            mix_total = len(mixed)
            temp_home = mixed[mixed['盘口'].str.contains('\-')]
            temp_away = mixed[mixed['盘口'].str.contains('\+')]
            p_uppr = ((len(temp_home[temp_home['H'] > temp_home['A']])+len(temp_away[temp_away['H'] < temp_away['A']])+1)/(mix_total+2))*100
            p_down = 100-p_uppr
            if mix_total >= 5:
                uppr.append(p_uppr)
                down.append(p_down)
            if len(temp)==0:
                print("按胜平负匹配历史比赛",total,"场")
                calc_prob(home, away, deep, result0, total)
            else:
                print("按双向胜平负匹配历史比赛",mix_total,"场")
                print("上盘概率:",round(p_uppr,2),'%',"下盘概率:",round(p_down,2),'%')
                
            if mix_total >= 8:
                m_result1 = mixed[(mixed['盘口数字'] <= row['盘口数字']+0.25) & (mixed['盘口数字'] >= row['盘口数字']-0.25)]
                m_result2 = mixed[(mixed['盘口数字'] <= row['盘口数字']*(-1)+0.25) & (mixed['盘口数字'] >= row['盘口数字']*(-1)-0.25)]
                m_result = pd.concat([m_result1, m_result2], axis=0)
                m_result.drop_duplicates(subset=['比赛'], keep='first', inplace=True)
                total = len(m_result)
                if total > 0:
                    print("按双向模糊盘口匹配历史比赛",total,"场")
                    temp_home = m_result[m_result['盘口'].str.contains('\-')]
                    temp_away = m_result[m_result['盘口'].str.contains('\+')]
                    p_uppr = ((len(temp_home[temp_home['H'] > temp_home['A']])+len(temp_away[temp_away['H'] < temp_away['A']])+1)/(total+2))*100
                    p_down = 100-p_uppr
                    print("上盘概率:",round(p_uppr,2),'%',"下盘概率:",round(p_down,2),'%')
                    if total >= 5:
                        uppr.append(p_uppr)
                        down.append(p_down)
                
                if total >= 8:
                    m_result3 = m_result[(m_result['盘口数字'] == row['盘口数字']) | (m_result['盘口数字'] == row['盘口数字']*(-1))]
                    total = len(m_result3)
                    if total > 0:
                        print("按精确盘口匹配历史比赛",total,"场")
                        temp_home = m_result3[m_result3['盘口'].str.contains('\-')]
                        temp_away = m_result3[m_result3['盘口'].str.contains('\+')]
                        p_uppr = ((len(temp_home[temp_home['H'] >temp_home['A']])+len(temp_away[temp_away['H'] <temp_away['A']])+1)/(total+2))*100
                        p_down = 100-p_uppr
                        print("上盘概率:",round(p_uppr,2),'%',"下盘概率:",round(p_down,2),'%')
                        if total >= 5:
                            uppr.append(p_uppr)
                            down.append(p_down)
              
        else:
            roll = True
            print("按胜平负匹配历史比赛",total,"场")
            temp, signal, num_miss = calc_prob(home, away, deep, result0, total)
            temp_miss.append(num_miss)
            temp = laplace(temp, total)
            uppr, down = decision(home, away, uppr, down, temp, signal)
            if away and (row['让负'] <= row['平']+row['负']+0.03) and (row['让负'] >= row['平']+row['负']-0.03):
                flag = True
            elif away and (row['让胜'] <= row['平']+row['胜']+0.03) and (row['让胜'] >= row['平']+row['胜']-0.03):
                rare = True

        #第1轮筛选 让球方向
        if roll:
            roll = False
            if home:
                result1 = result0[result0['盘口'].str.contains('\-')]
            elif away:
                result1 = result0[result0['盘口'].str.contains('\+')]
            total = len(result1)
            if total > 0:
                print("按让球方匹配历史比赛",total,"场")
                temp, signal, num_miss = calc_prob(home, away, deep, result1, total)
                temp_miss.append(num_miss)
                temp = laplace(temp, total)
                if total >= 5:
                    uppr, down = decision(home, away, uppr, down, temp, signal)
                
            if total >= 8:
                roll = True
                if deep or flag or rare:
                    roll = False
                    skip = True
                    result2 = result1
                            
        #第2轮筛选 让负/让胜
        if roll:
            result2 = result1[result1['让负'] == row['让负']]
            total = len(result2)
            if total >= 5:
                print("按让负匹配历史比赛",total,"场")
                temp, signal, num_miss = calc_prob(home, away, deep, result2, total)
                temp_miss.append(num_miss)
                temp = laplace(temp, total)
                uppr, down = decision(home, away, uppr, down, temp, signal)
            else:
                result2 = result1

        elif rare:
            result2 = result1[result1['让胜'] == row['让胜']]
            total = len(result2)
            if total >= 5:
                print("按让胜匹配历史比赛",total,"场")
                temp, signal, num_miss = calc_prob(home, away, deep, result2, total)
                temp_miss.append(num_miss)
                temp = laplace(temp, total)
                uppr, down = decision(home, away, uppr, down, temp, signal)
            else:
                result2 = result1
                
        #第3轮筛选 盘口±0.25    
        if roll or skip:
            roll = False
            result3 = result2[(result2['盘口数字'] >= row['盘口数字']-0.25) & (result2['盘口数字'] <= row['盘口数字']+0.25)]
            total = len(result3)
            if total > 0:
                print("按模糊盘口匹配历史比赛",total,"场")
                temp, signal, num_miss = calc_prob(home, away, deep, result3, total)
                temp_miss.append(num_miss)
                temp = laplace(temp, total)
                if total >= 5:
                    uppr, down = decision(home, away, uppr, down, temp, signal)
                
            if total >= 8:
                roll = True
                
        #第4轮筛选 盘口
        if roll:
            result4 = result3[result3['盘口数字'] == row['盘口数字']]
            total = len(result4)
            if total > 0:
                print("按精确盘口匹配历史比赛",total,"场")
                temp, signal, num_miss = calc_prob(home, away, deep, result4, total)
                temp_miss.append(num_miss)
                temp = laplace(temp, total)
                if total >= 5:
                    uppr, down = decision(home, away, uppr, down, temp, signal)
                
        #收敛与计数
        if mean(uppr) > mean(down):
            best_prob = max(uppr)
            if temp_miss:
                upprmiss.append(temp_miss[uppr.index(best_prob)])
            avg_uppr.append(best_prob)
            avg_down.append(100-best_prob)
            uppr_count = analysis(best_prob, uppr_count)
            print('综合分析看好上盘获胜，概率：',round(best_prob,2),'%')
        elif mean(down) > mean(uppr):
            best_prob = max(down)
            if temp_miss:
                downmiss.append(temp_miss[down.index(best_prob)])
            avg_down.append(best_prob)
            avg_uppr.append(100-best_prob)
            down_count = analysis(best_prob, down_count)
            print('综合分析看好下盘获胜，概率：',round(best_prob,2),'%')
        else:
            print('建议放弃')
        print('\n')
        
        #收集推荐比分
        temp_score = row['比分'].split(' ')
        temp_score = tuple(temp_score)
        score += temp_score
        
        #收集注释和批注
        if row['算法'] == '球伯乐' and row['注释']:
            comment.append(row['注释'])
        if row['批注胜']:
            comment.append('胜:'+row['批注胜'])
        if row['批注平']:
            comment.append('平:'+row['批注平'])
        if row['批注负']:
            comment.append('负:'+row['批注负'])
        if row['批注让胜']:
            comment.append('让胜:'+row['批注让胜'])
        if row['批注让平']:
            comment.append('让平:'+row['批注让平'])
        if row['批注让负']:
            comment.append('让负:'+row['批注让负'])
        
        #处理最后一行        
        if index == df[df['H'].isnull() & df['盘口'].notnull()].index[-1]:
            line, freq = score_freq(score)
            #上盘
            if sum(uppr_count)/algo > 0.5 and algo > 1:
                #注释和批注
                if comment:
                    com_str = ''
                    for item in comment:
                        item = str(item)
                        com_str += str(item + ",")
                    com_str = com_str[:-1]
                    worksheet.write(x, y+10, com_str)
                #写入上盘信息
                avg_best = mean(avg_uppr)
                worksheet.write(x, y, liga)
                worksheet.write(x, y+1, prev)
                if home:
                    worksheet.write(x, y+2, '主让')
                elif away:
                    worksheet.write(x, y+2, '客让')
                worksheet.write(x, y+3, hand)
                worksheet.write(x, y+5, str(round(avg_best,2))+'%')
                if upprmiss:
                    worksheet.write(x, y+6, max(upprmiss))
                worksheet.write(x, y+7, line)
                worksheet.write(x, y+8, freq)
                if history:
                    TF = judge(new_score, num_hand, home, away, deep, 'uppr')
                    if TF:
                        worksheet.write(x, y+9, '\u2714')
                    else:
                        worksheet.write(x, y+9, '\u2716')
                
                if avg_best >= 60 and uppr_count[2] > 0:
                    worksheet.write(x, y+4, '新发现！！！五星级上盘模型') 
                    print('新发现！！！五星级上盘模型：',prev,'平均概率',round(avg_best,2),'%')
                elif avg_best >= 60 and uppr_count[1] > 0:
                    worksheet.write(x, y+4, '新发现！！四星级上盘模型')
                    print('新发现！！四星级上盘模型：',prev,'平均概率',round(avg_best,2),'%')
                elif (avg_best >= 50) and ((uppr_count[0] > 1) or (uppr_count[1] > 0) or (uppr_count[2] > 0)):
                    worksheet.write(x, y+4, '新发现！三星级上盘模型')
                    print('新发现！三星级上盘模型：',prev,'平均概率',round(avg_best,2),'%')
                x += 1
            #下盘
            elif sum(down_count)/algo > 0.5 and algo > 1:
                #注释和批注
                if comment:
                    com_str = ''
                    for item in comment:
                        item = str(item)
                        com_str += str(item + ",")
                    com_str = com_str[:-1]
                    worksheet.write(x, y+10, com_str)
                #写入下盘信息
                avg_best = mean(avg_down)
                worksheet.write(x, y, liga)
                worksheet.write(x, y+1, prev)
                if home:
                    worksheet.write(x, y+2, '主让')
                elif away:
                    worksheet.write(x, y+2, '客让')
                worksheet.write(x, y+3, hand)
                worksheet.write(x, y+5, str(round(avg_best,2))+'%')
                if downmiss:
                    worksheet.write(x, y+6, max(downmiss))
                worksheet.write(x, y+7, line)
                worksheet.write(x, y+8, freq)
                if history:
                    TF = judge(new_score, num_hand, home, away, deep, 'down')
                    if TF:
                        worksheet.write(x, y+9, '\u2714')
                    else:
                        worksheet.write(x, y+9, '\u2716')
                    
                if avg_best >= 60 and down_count[2] > 0:
                    worksheet.write(x, y+4, '新发现！！！五星级下盘模型')                    
                    print('新发现！！！五星级下盘模型：',prev,'平均概率',round(avg_best,2),'%')
                elif avg_best >= 60 and down_count[1] > 0:
                    worksheet.write(x, y+4, '新发现！！四星级下盘模型')
                    print('新发现！！四星级下盘模型：',prev,'平均概率',round(avg_best,2),'%')
                elif (avg_best >= 50) and ((down_count[0] > 1) or (down_count[1] > 0) or (down_count[2] > 0)):
                    worksheet.write(x, y+4, '新发现！三星级下盘模型')
                    print('新发现！三星级下盘模型：',prev,'平均概率',round(avg_best,2),'%')
                x += 1
            print('=============================================')
        #提取赛果并储存
        if history:
            scoreline = re.findall('[0-9]+', row['比赛'])
            new_score = [int(s) for s in scoreline]
            df.loc[index, 'H'] = new_score[0]
            df.loc[index, 'A'] = new_score[1]
    wb.close()
    
if __name__ == "__main__":
    main()