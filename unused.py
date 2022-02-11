            #判断历史样本让球方
            '''
            result0['主不败'] = result0['胜']+result0['平']
            sub1 = result0[(result0['盘口'] == '-0.25') & (result0['让胜'].between(result0['平']+result0['胜']-0.03, result0['平']+result0['胜']+0.03)) & (result0['主不败'].between(0,1,inclusive=False))]
            sub2 = result0[(result0['盘口'] == '-0') & (result0['让胜'].between(result0['平']+result0['胜']-0.03, result0['平']+result0['胜']+0.03)) & (0 < result0['胜']+result0['平']) & (result0['竞彩'] == '是')]
            sub3 = result0[(result0['盘口'].str.contains('\-'))]
            df_temp = sub3.merge(sub1, on=['算法','联赛','比赛','胜','平','负','H','A','让胜','让平','让负','盘口','注释','比分','竞彩','批注胜','批注平','批注负','批注让胜','批注让平','批注让负'], how='left', indicator=True)
            df_temp = df_temp[df_temp['_merge'] == 'left_only']
            del df_temp['_merge']
            df_all = df_temp.merge(sub2, on=['算法','联赛','比赛','胜','平','负','H','A','让胜','让平','让负','盘口','注释','比分','竞彩','批注胜','批注平','批注负','批注让胜','批注让平','批注让负'], how='left', indicator=True)
            df_all = df_all[df_all['_merge'] == 'left_only']
            del df_all['_merge']
            sub3 = df_all
            sub4 = result0[(result0['盘口'].str.contains('\+')) & (result0['竞彩'] == '是') & (result0['让负'] <= (result0['平']+result0['负']+0.03)) & (result0['让负'] >= (result0['平']+result0['负']-0.03))]
            sub5 = result0[(result0['盘口'].str.contains('\+'))]
            df_all = sub5.merge(sub4, on=['算法','联赛','比赛','胜','平','负','H','A','让胜','让平','让负','盘口','注释','比分','竞彩','批注胜','批注平','批注负','批注让胜','批注让平','批注让负'], how='left', indicator=True)
            df_all = df_all[df_all['_merge'] == 'left_only']
            del df_all['_merge']
            sub5 = df_all
            
            result1 = pd.concat([sub3, sub4], axis=0)
            result1.drop_duplicates(subset=['比赛'], keep='first', inplace=True)
            
            result1 = pd.concat([sub1, sub2, sub5], axis=0)
            result1.drop_duplicates(subset=['比赛'], keep='first', inplace=True)
            '''
