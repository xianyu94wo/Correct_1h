import os
import pandas as pd
import numpy as np
import time
import datetime
import shutil

#####CG为copy grid的缩写
def get_now_time(nowBJTStr=datetime.datetime.today().strftime('%Y%m%d%H')):
    '''
    按当天日期和时间判断指导报起报时间
    获取当前时间，判断当前时间是否超过中午12点，如果超过则返回当天日期+'2000'，如果未超过则返回当天日期+'0800'
    :return: 起报时间
    '''
    nowHour = int(nowBJTStr[-2:])  # 字符串中获取小时并转为整数
    # 若当前时间在下午13时之前，则设置起报时间为0800，否则设置为2000
    if nowHour < 13:
        nowTimeStr = nowBJTStr[:-2] + '08'
        timeTemp = datetime.datetime.strptime(nowTimeStr, '%Y%m%d%H')
        previousTime = timeTemp - datetime.timedelta(days=1)
        previousBeforeTime = timeTemp - datetime.timedelta(days=2)
        previousTimeS = previousTime.strftime('%Y%m%d%H')
        previousBeforeTimeS = previousBeforeTime.strftime('%Y%m%d%H')
    else:
        nowTimeStr = nowBJTStr[:-2] + '20'
        timeTemp = datetime.datetime.strptime(nowTimeStr, '%Y%m%d%H')
        previousTime = timeTemp - datetime.timedelta(days=1)
        previousBeforeTime = timeTemp - datetime.timedelta(days=2)
        previousTimeS = previousTime.strftime('%Y%m%d%H')
        previousBeforeTimeS = previousBeforeTime.strftime('%Y%m%d%H')
    return nowTimeStr, previousTimeS, previousBeforeTimeS


def check_data(timeStr , pathG, pathS, jStep):
    '''
    本函数是拷贝TMP逐三小时SCMOC文件至相应文件夹
    :param timeStrHistory:
    :param pathG:
    :param pathS:
    :param jStep:
    :return:
    '''
    timeStr = get_now_time(timeStr)
    print('{}{}\\{}'.format(pathS, timeStr[0][:4], timeStr[0][:-2]))
    if os.path.exists('{}{}\\{}'.format(pathS, timeStr[0][:4], timeStr[0][:-2])) == False:
        os.mkdir('{}{}\\{}'.format(pathS, timeStr[0][:4], timeStr[0][:-2]))
    if os.path.exists('{}{}\\{}\\TMP_{}.{}'.format(pathG, timeStr[0][:4], timeStr[0][:-2], timeStr[0], jStep)):
        gridDataPath = '{}{}\\{}\\TMP_{}.{}'.format(pathG, timeStr[0][:4], timeStr[0][:-2], timeStr[0], jStep)
        savePath = '{}{}\\{}\\TMP_{}.{}'.format(pathS, timeStr[0][:4], timeStr[0][:-2], timeStr[0], jStep)
        # print('源文件地址为%s' % gridDataPath)
        # print('保存地址为%s' % savePath)
        shutil.copyfile(gridDataPath, savePath)
        print('【当前%s指导预报存在，已完成拷贝】' % timeStr[0])
    elif os.path.exists('{}{}\\{}\\TMP_{}.{}'.format(pathG, timeStr[1][:4], timeStr[1][:-2], timeStr[1], str(int(jStep) + 24).zfill(3))):
        gridDataPath = '{}{}\\{}\\TMP_{}.{}'.format(pathG, timeStr[1][:4], timeStr[1][:-2], timeStr[1], str(int(jStep) + 24).zfill(3))
        savePath = '{}{}\\{}\\TMP_{}.{}'.format(pathS, timeStr[0][:4], timeStr[0][:-2], timeStr[0], jStep)
        shutil.copyfile(gridDataPath, savePath)
        print('【当前%s指导预报不存在，已完成拷贝前一天%s指导预报拷贝】' % (timeStr[0], timeStr[1]))

    elif os.path.exists('{}{}\\{}\\TMP_{}.{}'.format(pathG, timeStr[2][:4], timeStr[2][:-2], timeStr[2], str(int(jStep) + 48).zfill(3))):
        gridDataPath = '{}{}\\{}\\TMP_{}.{}'.format(pathG, timeStr[2][:4], timeStr[2][:-2], timeStr[2], str(int(jStep) + 48).zfill(3))
        savePath = '{}{}\\{}\\TMP_{}.{}'.format(pathS, timeStr[0][:4], timeStr[0][:-2], timeStr[0], jStep)
        shutil.copyfile(gridDataPath, savePath)
        print('【今日、昨日指导预报不存在，已完成拷贝%s指导预报拷贝】' % timeStr[2])
    else:
        print('近三个时次无资料')


if __name__ == '__main__':
    pathG = 'F:\\work\\2020Correct\\data\\GRID\\'
    pathS = 'F:\\work\\2020Correct\\data\\TM_md_3h_Grid\\'
    listStep = ['003', '006', '009', '012', '015', '018', '021', '024']
    ######################################实时
    timeStr = datetime.datetime.today().strftime('%Y%m%d%H')
    for jStep in listStep:
        bb = check_data(timeStr, pathG, pathS, jStep)
    print('*' * 50)



###############获取历史#########################
    # timeStr = '2020072006'
    # for days in range(80):
    #     getTime1 = datetime.datetime.strptime(timeStr, '%Y%m%d%H')
    #     getTime1 = getTime1 + datetime.timedelta(hours=12 * days)
    #     getTimeStrF = getTime1.strftime('%Y%m%d%H')
    #     for jStep in listStep:
    #         bb = check_data(getTimeStrF, pathG, pathS, jStep)
    #     print('*' * 50)
