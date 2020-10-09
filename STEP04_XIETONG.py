import numpy as np
from scipy import interpolate
import pylab as pl
import pandas as pd
from numba import jit
import time
import os
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
    qiantui12h = datetime.datetime.strptime(qiBaoShiJian, '%Y%m%d%H')
    qiantui12h = qiantui12h - datetime.timedelta(hours=12)
    qiantui12hS = qiantui12h.strftime('%Y%m%d%H')
    return qiBaoShiJian, qiantui12hS


def get_orig_3h_3Ddata(pathMBase, nowTime):
    print('【当前起报时间为%s】' % nowTime[0])
    #############################起报时间的资料路径pathM
    pathM = pathMBase
    #############################前一起报时间12h预报结果的资料路径pathM0
    pathM0 = '{}{}.012'.format(pathMBase, nowTime[1][2:])
    #####################################定义文件名和后缀（预报时效）
    fileName = nowTime[0][2:]
    listYubaoshixiao = [str(3 * i).zfill(3) for i in range(1, 9)]
    #################################生成起报时间8个预报时次的文件名，其结果为可迭代对象
    listfileName = map(lambda x: fileName + '.' + x, listYubaoshixiao)
    ##############################用zero和one矩阵生成基础三维数据矩阵
    arZero = np.zeros((161, 274))
    arOne = np.ones((161, 274))
    arBase = np.array([arZero, arOne])
    ###############################前一时次预报的12h结果代替000场，用基础三维数据矩阵和其结合为三维矩阵arTemp
    ar0 = np.loadtxt(pathM0, skiprows=3)
    ar0 = np.append(arBase, ar0)
    dim = arBase.shape
    dataBase = ar0.reshape(dim[0] + 1, dim[1], dim[2])
    arTemp = dataBase.copy()
    ##################将列表内的文件读取出来并同arTemp合并成一个三维数组
    for i in listfileName:
        path1 = '{}{}'.format(pathM, i)
        arr1 = np.loadtxt(path1, skiprows=3)
        data1 = np.append(arTemp, arr1)
        dim1 = arTemp.shape
        data2 = data1.reshape(dim1[0] + 1, dim1[1], dim1[2])
        arTemp = data2.copy()
    arTemp = np.delete(arTemp, [0, 1], axis=0)
    return arTemp


def interpolation(arTemp):
    '''
    插值计算
    :param arTemp:9*161*274的三维矩阵
    :return:
    '''
    x = np.linspace(0, 24, 9)
    xnew = np.linspace(0, 24, 25)
    ###################################用zero和one矩阵生成基础一维数据矩阵
    arZero1 = np.zeros((25))
    arOne1 = np.ones((25))
    arBase1 = np.array([arZero1, arOne1])
    #######################################9个时次插值为25个时次
    print('【正在执行插值程序】')
    for j in range(arTemp.shape[1]):
        for k in range(arTemp.shape[2]):
            # for j in range(2):
            #     for k in range(3):
            y = arTemp[:, j, k]
            # for kind in ["nearest", "zero", "slinear", "quadratic", "cubic"]:  # 插值方式"nearest","zero"为阶梯插值,"slinear"线性插值,"quadratic","cubic" 为2阶、3阶B样条曲线插值
            f = interpolate.interp1d(x, y, kind='cubic')
            ynew = f(xnew)
            arrTemp = np.append(arBase1, ynew)
            arBase1Dim = arBase1.shape
            arrConbin = arrTemp.reshape(arBase1Dim[0] + 1, arBase1Dim[1])
            arBase1 = arrConbin.copy()
    #########################################输出逐小时报文
    arBase1a = np.delete(arBase1, [0, 1], axis=0)
    for i in range(25):
        arResult = arBase1a[:, i].reshape(161, 274)
        np.savetxt('F:\\work\\2020Correct\\data\\test\\' + nowTime[0][2:] + '.' + str(i).zfill(3), arResult, format('%.2f'))


def check_TmaxTmin(nowTime):
    ##################################删除000时次报文
    pathR = 'F:\\work\\2020Correct\\data\\test\\'
    pathTMAX = 'F:\\work\\2020Correct\\data\\TM_Result_Grid_20\\TMAX\\'
    pathTMIN = 'F:\\work\\2020Correct\\data\\TM_Result_Grid_20\\TMIN\\'
    try:
        os.remove(pathR + nowTime[0][2:] + '.000')
    except Exception as e:
        print('无法删除，原因：%s' % e)
    fileName = nowTime[0][2:]
    listYubaoshixiao = [str(1 * i).zfill(3) for i in range(1, 25)]
    #################################生成起报时间24个预报时次的文件名，其结果为可迭代对象
    listfileName = map(lambda x: fileName + '.' + x, listYubaoshixiao)
    #############################用zero和one矩阵生成基础三维数据矩阵
    arZero = np.zeros((161, 274))
    arOne = np.ones((161, 274))
    arBase = np.array([arZero, arOne])
    # ##################将列表内的文件读取出来并同arTemp合并成一个三维数组
    for i in listfileName:
        path1 = '{}{}'.format(pathR, i)
        arr1 = np.loadtxt(path1)
        data1 = np.append(arBase, arr1)
        dim1 = arBase.shape
        data2 = data1.reshape(dim1[0] + 1, dim1[1], dim1[2])
        arBase = data2.copy()
    arBase = np.delete(arBase, [0, 1], axis=0)
    print('【执行最低气温协同...】')
    ###############################################################y通过偏差订正求出的最低气温
    arTMIN = np.loadtxt(pathTMIN + fileName + '.024', skiprows=3)
    #######################################

    for i in range(161):
        for j in range(274):
            x = arBase[:, i, j]
            ##############判断单点上最值出现的索引位置
            tMinIndex = np.where(x == np.nanmin(arBase[:, i, j]))[0]
            ##############判断单点上超过最值的索引位置
            tMinNoMatch = np.where(x < arTMIN[i, j])[0]
            ############################如果单点结果无不符合超过的值，则不管；如有，则需进一步处理

            if len(tMinNoMatch) > 0:  #######大于0表明有不符合最值的值
                # print('【原数据为\n{}】'.format(x))
                # print('【原最小值位置为{}】'.format(tMinIndex))
                # print('【原始最低气温为{}】'.format(arTMIN[i, j]))
                # print('【原有不符合的位置为{}】'.format(tMinNoMatch))
                # print(i, j)
                listTMinIndex = list(tMinNoMatch)  #############将逐小时数据内最值位置array信息转为列表
                #################计算最值前后各两位的位置
                listTMinIndex.append(listTMinIndex[0] - 2)
                listTMinIndex.append(listTMinIndex[0] - 1)
                listTMinIndex = sorted(listTMinIndex)
                listTMinIndex.append(listTMinIndex[-1] + 1)
                listTMinIndex.append(listTMinIndex[-1] + 1)
                listTMinIndex = sorted(list(set(listTMinIndex)))

                ############################将最值及前后两位位置信息的列表存入listTemp中，超过23及作废
                listTempTmin = []
                for kk in listTMinIndex:
                    if kk <= 23:
                        listTempTmin.append(kk)
                ########################计算最值与其他位置值的比例，并将最值替换为偏差最值，基于比例求其他位置的值
                listReplaceTmin, listReplaceRateTmin, listXTmin = [], [], []
                for k in listTempTmin:
                    listXTmin.append(x[k])
                    if x[k] == 0:
                        x[k] = 0.01  ###############此处防止最值为0
                    if x[tMinIndex[0]] == 0:
                        x[tMinIndex[0]] = 0.01  ###############此处防止比例为0
                    rate = x[tMinIndex[0]] / x[k]
                    result = arTMIN[i, j] / rate
                    listReplaceRateTmin.append(rate)
                    listReplaceTmin.append(result)
                # print(('【订正前为{}】'.format(listXTmin)))
                # print(('【订正率为{}】'.format(listReplaceRateTmin)))
                # print(('【订正后为{}】'.format(listReplaceTmin)))

                for index, value in enumerate(listTempTmin):
                    x[value] = listReplaceTmin[index]
                arBase[:, i, j] = x
    #             print(x)
    # print(arBase[:, 0, 0])
    # print('*' * 50)
    ##############################与上面相同 只不过求最高
    ###############################################################y通过偏差订正求出的最高最高气温
    print('【执行最高气温协同...】')
    arTMAX = np.loadtxt(pathTMAX + fileName + '.024', skiprows=3)
    for ii in range(161):
        for jj in range(274):
            xx = arBase[:, ii, jj]
            ##############判断单点上最值出现的索引位置
            tMaxIndex = np.where(xx == np.nanmax(arBase[:, ii, jj]))[0]
            ##############判断单点上超过最值的索引位置
            tMaxNoMatch = np.where(xx > arTMAX[ii, jj])[0]
            ############################如果单点结果无不符合超过的值，则不管；如有，则需进一步处理

            if len(tMaxNoMatch) > 0:  #######大于0表明有不符合最值的值
                # print('【原数据为\n{}】'.format(xx))
                # print('【原最大值位置为{}】'.format(tMaxIndex))
                # print('【原始最高气温为{}】'.format(arTMAX[ii, jj]))
                # print('【原有不符合的位置为{}】'.format(tMaxNoMatch))
                # print(i, j)
                listTMaxIndex = list(tMaxNoMatch)  #############将逐小时数据内最值位置array信息转为列表
                # print(listTMaxIndex)
                #################计算最值前后各两位的位置
                listTMaxIndex.append(listTMaxIndex[0] - 2)
                listTMaxIndex.append(listTMaxIndex[0] - 1)
                listTMaxIndex = sorted(listTMaxIndex)
                listTMaxIndex.append(listTMaxIndex[-1] + 1)
                listTMaxIndex.append(listTMaxIndex[-1] + 1)
                listTMaxIndex = sorted(list(set(listTMaxIndex)))
                ############################将最值及前后两位位置信息的列表存入listTemp中，超过23及作废
                listTempTmax = []
                for uu in listTMaxIndex:
                    if uu <= 23 and uu >= 0:
                        listTempTmax.append(uu)
                # print(listTempTmax)
                ########################计算最值与其他位置值的比例，并将最值替换为偏差最值，基于比例求其他位置的值
                listReplaceTmax, listReplaceRateTmax, listXTmax = [], [], []
                for a in listTempTmax:
                    listXTmax.append(xx[a])
                    if xx[a] == 0:
                        xx[a] = 0.01  ###############此处防止最值为0
                    if xx[tMaxIndex[0]] == 0:
                        xx[tMaxIndex[0]] = 0.01  ###############此处防止比例为0
                    rate = xx[tMaxIndex[0]] / xx[a]
                    result = arTMAX[ii, jj] / rate
                    listReplaceRateTmax.append(rate)
                    listReplaceTmax.append(result)
                # print(('【订正前为{}】'.format(listXTmax)))
                # print(('【订正率为{}】'.format(listReplaceRateTmax)))
                # print(('【订正后为{}】'.format(listReplaceTmax)))
                for index, value in enumerate(listTempTmax):
                    xx[value] = listReplaceTmax[index]
                arBase[:, ii, jj] = xx
    return arBase


def toTXT(arResult):
    for time24 in range(24):
        #np.savetxt('F:\\work\\2020Correct\\data\\TM_Result_Grid_1h\\' + nowTime[0][2:] + '.' + str(time24 + 1).zfill(3), arResult[time24, :, :], format('%.2f'))
        np.savetxt('F:\\work\\2020Correct\\data\\TM_Result_Grid_1h\\1hTemp.txt', arResult[time24, :, :], format('%.2f'))

        with open('F:\\work\\2020Correct\\data\\TM_Result_Grid_1h\\1hTemp.txt') as f1:
            tempStr = f1.readlines()
        with open('F:\\work\\2020Correct\\data\\TM_Result_Grid_1h\\' + nowTime[0][2:] + '.' + str(time24 + 1).zfill(3), 'w') as f2:
            f2.write('diamond 4 MBysj_20%s_%s_TMP\n' % (nowTime[0][2:], str(time24 + 1)))
            f2.write('20%s %s %s %s %s 0 \n' % (nowTime[0][2:4], nowTime[0][4:6], nowTime[0][6:8], nowTime[0][-2:],str(time24 + 1)))
            thirdLine = '0.05000 0.05000 89.3 102.95 31.4 39.4 274 161 10.000000 -40.000000 40.000000 2.000000 0.000000 '
            f2.write('%s %s' % (thirdLine, '\n'))
            f2.writelines(tempStr)
        os.remove('F:\\work\\2020Correct\\data\\TM_Result_Grid_1h\\1hTemp.txt')




if __name__ == '__main__':
    pathMBase = 'F:\\work\\2020Correct\\data\\TM_Result_Grid_20\\TMP\\'

    # timeStr = '2020091406'
    # for eDay in range(4):
    #     getTime1 = datetime.datetime.strptime(timeStr, '%Y%m%d%H')
    #     getTime1 = getTime1 + datetime.timedelta(hours=12 * eDay)
    #     getTimeStrF = getTime1.strftime('%Y%m%d%H')
    #     print(getTimeStrF)

    nowTime = get_now_time()
    timeStart = time.time()
    print('【开始执行协同计算...】')
    # arTemp = get_orig_3h_3Ddata(pathMBase, nowTime)
    # aa = interpolation(arTemp)
    arResult = check_TmaxTmin(nowTime)
    txt = toTXT(arResult)
    timeEnd = time.time() - timeStart
    print('【计算完毕，运行时间共计%.2f分钟】' % (timeEnd / 60))
