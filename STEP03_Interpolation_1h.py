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
    print(arBase1a.shape)
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
        print(e)
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
    print(arBase.shape)
    arTMAX = np.loadtxt(pathTMAX + fileName + '.024', skiprows=3)
    arTMIN = np.loadtxt(pathTMIN + fileName + '.024', skiprows=3)
    #######################################

    for i in range(3):
        for j in range(4):
            x = arBase[:, i, j]
            print(x)
            print(arTMAX[i, j])
            print(arTMIN[i, j])

            tMaxIndex = np.where(x > arTMAX[i, j])[0]
            tMinIndex = np.where(x < arTMIN[i, j])[0]
            print(tMaxIndex)
            print(tMinIndex)
            # arBase[tMaxIndex, i, j] = arTMAX[i, j]
            # arBase[tMinIndex, i, j] = arTMIN[i, j]
            # print(x)


if __name__ == '__main__':
    # dataStart = '2020091216'
    # duringDay = 4
    # for eDay in range(duringDay):
    #     timeStart1 = time.time()
    #     getTime1 = datetime.datetime.strptime(dataStart, '%Y%m%d%H')
    #     getTime1 = getTime1 + datetime.timedelta(hours=12 * eDay)
    #     getTimeStrF = getTime1.strftime('%Y%m%d%H')
    #     print('【正在运行3h插值为1h程序】')

    pathMBase = 'F:\\work\\2020Correct\\data\\TM_Result_Grid_20\\TMP\\'
    nowTime = get_now_time()
    timeStart = time.time()
    print('【开始执行逐小时插值计算...】')
    arTemp = get_orig_3h_3Ddata(pathMBase, nowTime)
    aa = interpolation(arTemp)

    # bb = check_TmaxTmin(nowTime)
    timeEnd = time.time() - timeStart
    print('【运行时间共计%.2f分钟】' % (timeEnd / 60))
    # aa = check_TmaxTmin(nowTime)
