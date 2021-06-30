import sys
import numpy as np
import iric
import copy
import os
import shutil
import common


def nays2dh_init(cgnsName):
    # open CGNS file to write
    common.write_fid = iric.cg_open(cgnsName, iric.CG_MODE_MODIFY)
    print(common.write_fid)
    exit()

    try:
        iric.cg_iRIC_Init(common.write_fid)
        iric.iRIC_InitOption(iric.IRIC_OPTION_CANCEL)
    except:
        print("Error: Please check if grid is imported.")
        exit()

def clearPngFolder():
    if os.path.exists('png'):
        shutil.rmtree('png')
    
    os.mkdir('png')

def main(cgnsName):
    nays2dh_init(cgnsName)
    # print('CGNS=',cgnsName)
    
    # Read Hydraulic Condition
    # print('Reading Hydraulic Condition')
    chl = iric.cg_iRIC_Read_Real('chl')
    ni = iric.cg_iRIC_Read_Integer('ni')
    chb = iric.cg_iRIC_Read_Real('chb')
    nj = iric.cg_iRIC_Read_Integer('nj')

    print(chl,ni,chb,nj)
    exit()

    # 格子のサイズを取得
    ni, nj = iric.cg_iRIC_GotoGridCoord2d()
    # print(ni,nj)

    # 格子点座標(x,y)の取得
    x1,y1=iric.cg_iRIC_GetGridCoord2d()

    x2 = np.reshape(x1,(ni,nj),order='F')
    y2 = np.reshape(y1,(ni,nj),order='F')

    # print(np.shape(x),ni,nj)
    chl=x2[ni-1,0]-x2[0,0]
    chb=y2[0,nj-1]-y2[0,0]
    # print('chl=',chl,'chb=',chb)

    # 格子サイズの決定
    nx=ni-1; ny=nj-1; nx1=nx+1; ny1=ny+1
    nx2=nx+2; ny2=ny+2
    nym=int(ny/2)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Error: CGNS file name not specified.")
        exit()

    cgnsName = sys.argv[1]
    print(cgnsName)

    main(cgnsName)
