import sys

import numpy as np

import iric

G = 9.8

OUTPUT_V_I_NAME = 'VeloI'
OUTPUT_V_J_NAME = 'VeloJ'
OUTPUT_V_NAME = 'Velocity'

# calculate energy gradient from wse
def _calc_energy_gradient_i(x, y, wse):
    dx = np.diff(x)
    dy = np.diff(y)
    dwse = np.diff(wse)

    ret = np.zeros(x.shape)
    grad = dwse / np.sqrt(dx * dx + dy * dy)
    ret[:, 1:] += grad
    ret[:, :-1] += grad
    ret[:, 1:-1] /= 2 # average of two values
    ret = np.abs(ret)

    return ret.reshape(ret.size)

def _calc_energy_gradient_j(x, y, wse):
    dx = np.diff(x, axis=0)
    dy = np.diff(y, axis=0)
    dwse = np.diff(wse, axis=0)

    ret = np.zeros(x.shape)
    grad = dwse / np.sqrt(dx * dx + dy * dy)
    ret[1:, :] += grad
    ret[:-1, :] += grad
    ret[1:-1, :] /= 2 # average of two values
    ret = np.abs(ret)

    return ret.reshape(ret.size)

def main(cgnsName):
    # open CGNS file to write
    print('Opening cgns file...')
    fid = iric.cg_open(cgnsName, iric.CG_MODE_MODIFY)
    iric.cg_iRIC_Init(fid)

    print('Reading grid and calculation condition...')
    isize, jsize = iric.cg_iRIC_GotoGridCoord2d()
    x, y = iric.cg_iRIC_GetGridCoord2d_Mul(fid)

    elevation = iric.cg_iRIC_Read_Grid_Real_Node('Elevation')
    wse = iric.cg_iRIC_Read_Grid_Real_Node('WSE')
    depth = wse - elevation

    n = iric.cg_iRIC_Read_Real('n')

    x2 = x.reshape(jsize, isize)
    y2 = y.reshape(jsize, isize)
    wse2 = wse.reshape(jsize, isize)

    print('Calculating velocity...')
    ie_i = _calc_energy_gradient_i(x2, y2, wse2) * G
    ie_j = _calc_energy_gradient_j(x2, y2, wse2) * G

    v_i = 1 / n * np.power(depth, 2/3) * np.power(ie_i, 1/2)
    v_j = 1 / n * np.power(depth, 2/3) * np.power(ie_j, 1/2)
    v = np.sqrt(v_i * v_i + v_j * v_j)

    # output result
    print('Outputting calculation result...')
    iric.cg_iRIC_Write_Sol_Time(0)
    iric.cg_iRIC_Write_Sol_Real(OUTPUT_V_I_NAME, v_i)
    iric.cg_iRIC_Write_Sol_Real(OUTPUT_V_J_NAME, v_j)
    # iric.cg_iRIC_Write_Sol_Real(OUTPUT_V_NAME, v)

    iric.cg_close(fid)
    print('Calculation success.')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Error: CGNS file name not specified.")
        exit()

    cgnsName = sys.argv[1]
    main(cgnsName)
