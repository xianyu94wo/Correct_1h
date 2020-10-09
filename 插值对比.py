import numpy as np
from scipy import interpolate
import pylab as pl
import pandas as pd

pathM = 'F:\\work\\2020Correct\\data\\TM_md_3h_Grid\\2020\\20200831\\'
arZero = np.zeros((161, 274))
arOne = np.ones((161, 274))
arBase = np.array([arZero, arOne])

pathM1 = 'F:\\work\\2020Correct\\data\\TM_md_3h_Grid\\2020\\20200830\\TMP_2020083020.012'
arTemp = np.loadtxt(pathM1)
data1 = np.append(arBase, arTemp)
dim1 = arBase.shape
data2 = data1.reshape(dim1[0] + 1, dim1[1], dim1[2])
arBase = data2.copy()



name1 = 'TMP_2020083108'
list1 = [str(3 * i).zfill(3) for i in range(1, 9)]
print(list1)
list2 = map(lambda x: name1 + '.' + x, list1)

for i in list2:
    path1 = '{}{}'.format(pathM, i)
    arTemp = np.loadtxt(path1)
    data1 = np.append(arBase, arTemp)

    dim1 = arBase.shape
    data2 = data1.reshape(dim1[0] + 1, dim1[1], dim1[2])
    arBase = data2.copy()

arBase = np.delete(arBase, [0, 1], axis=0)
print(arBase.shape)
print('*' * 50)


x = np.linspace(0, 23, 9)
y = arBase[:, 0, 0]
print(x)
print(y)
xnew = np.linspace(0, 23, 24)



#for kind in ["nearest", "zero", "slinear", "quadratic", "cubic"]:  # 插值方式
for kind in ["nearest", "zero", "slinear", "quadratic", "cubic"]:
    # "nearest","zero"为阶梯插值
    # slinear 线性插值
    # "quadratic","cubic" 为2阶、3阶B样条曲线插值
    f = interpolate.interp1d(x, y, kind=kind)
    # ‘slinear’, ‘quadratic’ and ‘cubic’ refer to a spline interpolation of first, second or third order)
    ynew = f(xnew)
    pl.plot(xnew, ynew, label=str(kind))
    pl.plot(x, y, "ro")
    pl.plot(xnew, ynew, "gx")
    print('xnew为{}'.format(xnew))
    np.savetxt('F:\\work\\2020Correct\\data\\'+kind+'.txt',ynew,format('%.2f'))
    print('【{}插值后结果为{}】'.format(kind,ynew))
    pl.legend()
    pl.show()

#pl.show()


