import os
import pandas as pd
import numpy as np
import time
import datetime


def get_now_time(nowBJTStr=datetime.datetime.today().strftime('%Y%m%d%H')):
    '''
    按当天日期和时间判断指导报起报时间
    获取当前时间，判断当前时间是否超过中午12点，如果超过则返回当天日期+'2000'，如果未超过则返回当天日期+'0800'
    :return: 起报时间
    '''
    nowHour = int(nowBJTStr[-2:])  # 字符串中获取小时并转为整数
    # 若当前时间在下午13时之前，则设置起报时间为0800，否则设置为2000
    if nowHour < 13:
        qiBaoShiJian = nowBJTStr[:-2] + '08'
    else:
        qiBaoShiJian = nowBJTStr[:-2] + '20'
    return qiBaoShiJian


def get_step_time(SlidingStep, qiBaoShiJian):
    listDaysTemp = []
    for day in range(2, SlidingStep + 2):
        startTime = datetime.datetime.strptime(qiBaoShiJian, '%Y%m%d%H')
        getTime = startTime - datetime.timedelta(days=day)
        getTimeStr = getTime.strftime('%Y%m%d%H')
        listDaysTemp.append(getTimeStr)
    return sorted(listDaysTemp)


def get_diff_dataframe(pathM, pathO, listTempM, listTempO, eStep, nowTime, jStep):
    '''
    输出偏差df，输出列以滑动步长为准
    :param pathM: 模式基本路径
    :param pathO: 实况基本路径
    :param listOfData: 滑动步长范围内的资料名称列表
    :param baseDf: 打底DF
    :return: 返回包含滑动步长范围内的实况与预报偏差
    '''
    arZero = np.zeros((161, 274))
    arOne = np.ones((161, 274))
    arZero = arZero.reshape(arZero.shape[0] * arZero.shape[1])
    arOne = arOne.reshape(arOne.shape[0] * arOne.shape[1])
    dfBase = pd.DataFrame([arZero, arOne])
    #####################计算diff
    for i in range(eStep):
        path1 = '{}{}\\{}\\TMP_{}'.format(pathM, listTempM[i][:4], listTempM[i][:8], listTempM[i])
        path2 = '{}{}\\{}\\TMP_{}.txt'.format(pathO, listTempO[i][:4], listTempO[i][:-2], listTempO[i])
        arM = np.loadtxt(path1)
        arO = np.loadtxt(path2)
        arO[arO >= 50] = np.nan
        arO[arO <= -60] = np.nan
        arM[arM >= 50] = np.nan
        arM[arM <= -60] = np.nan
        arDiff = arO - arM
        arDiff = arDiff.reshape(arDiff.shape[0] * arDiff.shape[1])
        dfBase.loc[str(i + 1)] = arDiff
        dfBase = dfBase
    ###################计算M
    dfBase.drop([0, 1], axis=0, inplace=True)
    diffDf = dfBase
    medianArray = diffDf.median()
    #################################################计算D
    diffDfDMedian = diffDf.T
    for i in range(1, eStep + 1):
        diffDfDMedian['DMedian' + str(i)] = abs(diffDfDMedian[str(i)] - medianArray)
    diffDfDMedian.drop([str(xx + 1) for xx in range(eStep)], axis=1, inplace=True)
    diffDfDMedian = diffDfDMedian.T
    DMedianArray = diffDfDMedian.median()
    #################################################计算omiga
    diffDfOmiga = diffDf.T
    for i in range(1, eStep + 1):
        diffDfOmiga['omiga' + str(i)] = (diffDfOmiga[str(i)] - medianArray) / (7.5 * DMedianArray)
        diffDfOmiga.loc[diffDfOmiga['omiga' + str(i)] > 1, 'omiga' + str(i)] = 1
        diffDfOmiga.loc[diffDfOmiga['omiga' + str(i)] < -1, 'omiga' + str(i)] = -1
    diffDfOmiga.drop([str(xx + 1) for xx in range(eStep)], axis=1, inplace=True)
    ###############################################计算分母
    diffDfadjustDeno = diffDfOmiga
    for i in range(1, eStep + 1):
        diffDfadjustDeno['adjustDeno' + str(i)] = (1 - diffDfadjustDeno['omiga' + str(i)] ** 2) ** 2
    diffDfadjustDeno.drop(['omiga' + str(xx + 1) for xx in range(eStep)], axis=1, inplace=True)
    adjustDenoResult = diffDfadjustDeno.sum(axis=1)
    #############################################计算分子
    diffDfadjustDenoTemp1 = pd.concat([diffDf.T, diffDfadjustDeno], axis=1)
    for i in range(1, eStep + 1):
        diffDfadjustDenoTemp1['adjustNumer' + str(i)] = (diffDfadjustDenoTemp1[str(i)] - medianArray) * diffDfadjustDenoTemp1['adjustDeno' + str(i)]
    diffDfadjustDenoTemp1.drop(['adjustDeno' + str(xx + 1) for xx in range(eStep)], axis=1, inplace=True)
    diffDfadjustDenoTemp1.drop([str(xx + 1) for xx in range(eStep)], axis=1, inplace=True)
    adjustNumerResult = diffDfadjustDenoTemp1.sum(axis=1)
    ########################################计算等式
    adjust = adjustNumerResult / adjustDenoResult
    adjustResult = medianArray + adjust
    adjustResult[adjustResult <= -40] = 0
    adjustResult[adjustResult >= 40] = 0
    ########################################将偏差结果与现有预报相加
    modelResult = np.loadtxt('{}{}\\{}\\TMP_{}.{}'.format(pathM, nowTime[:4], nowTime[:8], nowTime, jStep))
    modelResult = modelResult.reshape(modelResult.shape[0] * modelResult.shape[1])
    adjustResult[adjustResult == np.nan] = 0
    adjustResult = adjustResult.fillna(0)
    CorrectResult = modelResult + adjustResult
    CorrectResultAr = CorrectResult.values
    CorrectResultAr = CorrectResultAr.reshape(161, 274)
    adjustResultTemp = np.array(adjustResult)
    adjustResultTemp = adjustResultTemp.reshape(161, 274)
    #return CorrectResultAr
    return CorrectResultAr


if __name__ == '__main__':
    timeStart = time.time()
    pathM = 'F:\\work\\2020Correct\\data\\TM_md_3h_Grid\\'
    pathO = 'F:\\work\\2020Correct\\data\\TEM_ob_1h_CLDAS_GRID\\'
    listStep = ['003', '006', '009', '012', '015', '018', '021', '024']
    # listStep = ['003', '006']  # 预报时效
    slidingStep = [ 20]
     #slidingStep = [20]
    dataStart = '2020100606'
    duringDay = 10
    for eDay in range(duringDay):
        timeStart1 = time.time()
        getTime1 = datetime.datetime.strptime(dataStart, '%Y%m%d%H')
        getTime1 = getTime1 + datetime.timedelta(hours=12 * eDay)
        getTimeStrF = getTime1.strftime('%Y%m%d%H')

        for eStep in slidingStep:
            print('【正在计算%s步滑动周期】' % str(eStep))
            pathResult = 'F:\\work\\2020Correct\\data\\TM_Result_Grid_' + str(eStep) + '\\' + 'TMP\\'
            nowTime = get_now_time(getTimeStrF)
            print('     【当前起报时间为：%s】' % nowTime)
            listFile = get_step_time(eStep, nowTime)
            print(listFile)
            ######################获取不同起报时次下不同预报时间的文件名
            #########################################################################
            for jStep in listStep:
                print('     【正在计算%s预报时效结果】' % jStep)
                listTempO = []
                listTempM = []
                for i in listFile:
                    listTempM.append(i + '.' + jStep)  ######获取相应列表的模式资料名
                    timeTemp = datetime.datetime.strptime(i, '%Y%m%d%H') + datetime.timedelta(hours=int(jStep))
                    timeTempStr = timeTemp.strftime('%Y%m%d%H')
                    listTempO.append(timeTempStr)  ######获取相应列表的实况资料名
                #########################################################################
                listTempO = sorted(listTempO)
                listTempM = sorted(listTempM)
                try:
                    calResult = get_diff_dataframe(pathM, pathO, listTempM, listTempO, eStep, nowTime, jStep)
                    np.savetxt('F:\\work\\2020Correct\\data\\TMPtemp.txt', calResult, fmt='%.2f')

                    with open('F:\\work\\2020Correct\\data\\TMPtemp.txt') as f1:
                        tempStr = f1.readlines()
                    with open('{}{}.{}'.format(pathResult, nowTime[2:], jStep), 'w') as f2:
                        f2.write('diamond 4 MBysj_{}_TMP\n'.format(nowTime))
                        f2.write('{} {} {} {} {} 0\n'.format(nowTime[:4], nowTime[4:6], nowTime[6:8], nowTime[-2:], jStep))
                        thirdLine = '0.05000 0.05000 89.3 102.95 31.4 39.4 274 161 10.000000 -40.000000 40.000000 5.000000 0.000000 '
                        f2.write('%s %s' % (thirdLine, '\n'))
                        f2.writelines(tempStr)
                    os.remove('F:\\work\\2020Correct\\data\\TMPtemp.txt')
                except Exception as e:
                    print(e)
                    with open('F:\\work\\2020Correct\\data\\ErrorLogHistory.txt', 'w+') as f3:
                        f3.writelines(str(e) + '\n')

        timeEnd1 = time.time() - timeStart1
        print('【运行时间为：%.4f】' % timeEnd1)
    timeEnd = time.time() - timeStart
    print('【运行时间为：%.4f】' % timeEnd)
