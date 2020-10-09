
import os
import shutil



# pathInput = 'F:\\work\\2020Correct\\data\\TM_Result_Grid_1h\\'
# pathOutput = 'F:\\work\\2020Correct\\data\\NC_data\\MB_20\\TMP\\'
# meb.copy_m4_to_nc(pathInput,pathOutput,effectiveNum = 2,recover= False,grid = None)

'20200902200000_000-024.nc'

pathOutput = 'F:\\work\\2020Correct\\data\\NC_data\\MB_20\\TMIN\\'
list1 = os.listdir(pathOutput)

for i in list1:
    print(i.split('.')[0])
    print(pathOutput + 'MODP_QHQX_MBTY_TMAX_AFQH_000_DT_20' + (i.split('.')[0] + '0000_000-024.nc'))
    shutil.move(pathOutput + i , pathOutput + 'MODP_QHQX_MBTY_TMIN_AFQH_000_DT_20' + (i.split('.')[0] + '0000_000-024.nc'))
print('test')
