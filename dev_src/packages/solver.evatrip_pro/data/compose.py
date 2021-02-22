import logging
import numpy as np
import iric

import common

OUTPUT_FROUDE_NAME = 'COMP_Froude'
OUTPUT_DIAMETER_NAME = 'COMP_CriticalDiameter'
OUTPUT_STRENGTH_NAME = 'COMP_FluidForce'
OUTPUT_MANUAL_NAME = 'COMP_Manual'

DEPTH_MIN = 1.0e-8
G = 9.8

v1_name = None
v2_name = None

result_v1 = None
result_v2 = None

output_froude = None
output_diameter = None
output_strength = None
output_manual = None

manual_func = None

diameter_error = False

def init():
    global v1_name, v2_name
    global output_froude, output_diameter, output_strength
    global output_manual
    global manual_func

    output_froude = iric.cg_iRIC_Read_Integer_Mul(common.write_fid, 'comp_output_froude')
    logging.debug('output_froude = {0}'.format(output_froude))
    output_diameter = iric.cg_iRIC_Read_Integer_Mul(common.write_fid, 'comp_output_diameter')
    logging.debug('output_diameter = {0}'.format(output_diameter))
    output_strength = iric.cg_iRIC_Read_Integer_Mul(common.write_fid, 'comp_output_strength')
    logging.debug('output_strength = {0}'.format(output_strength))
    output_manual = iric.cg_iRIC_Read_Integer_Mul(common.write_fid, 'comp_output_manual')
    logging.debug('output_manual = {0}'.format(output_manual))

    if output_manual:
        v1_name = iric.cg_iRIC_Read_String_Mul(common.write_fid, 'comp_v1')
        logging.debug('v1_name = {0}'.format(v1_name))
        v2_name = iric.cg_iRIC_Read_String_Mul(common.write_fid, 'comp_v2')
        logging.debug('v2_name = {0}'.format(v2_name))

        manual_def = iric.cg_iRIC_Read_String_Mul(common.write_fid, 'comp_manual')
        logging.debug('manual_def = {0}'.format(manual_def))

        def_str = 'def f(depth, wse, vx, vy, val1, val2, v):\n'
        for line in manual_def.split('\n'):
            def_str += '    ' + line + '\n'
        def_str += 'tmpf = f'
        d = {}
        exec(def_str, globals(), d)
        manual_func = d['f']

def process_step():
    global result_v1, result_v2
    if output_manual:
        if v1_name != '':
            result_v1 = iric.cg_iRIC_Read_Sol_Real_Mul(common.read_fid, common.step, v1_name)

        if v2_name != '':
            result_v2 = iric.cg_iRIC_Read_Sol_Real_Mul(common.read_fid, common.step, v2_name)

    if output_froude:
        _process_step_froude()

    if output_diameter:
        _process_step_diameter()
    
    if output_strength:
        _process_step_strength()
    
    if output_manual:
        _process_step_manual()    

def finalize():
    if output_froude:
        _output_dummy(OUTPUT_FROUDE_NAME)

    if output_diameter and (not diameter_error):
        _output_dummy(OUTPUT_DIAMETER_NAME)
    
    if output_strength:
        _output_dummy(OUTPUT_STRENGTH_NAME)
    
    if output_manual:
        _output_dummy(OUTPUT_MANUAL_NAME)

def _process_step_froude():
    depth = np.where(common.result_depth > DEPTH_MIN, common.result_depth, DEPTH_MIN)
    fr = common.result_velocity / np.sqrt(depth * G)
    iric.cg_iRIC_Write_Sol_Real_Mul(common.write_fid, OUTPUT_FROUDE_NAME, fr)

def _process_step_diameter():
    global diameter_error

    if diameter_error: return

    try:
        wse = common.result_water_surface_elevation
        I = np.maximum(np.abs(_calc_energy_gradient_i(wse)), np.abs(_calc_energy_gradient_j(wse))) # max of gradient in i direction and j direction
        u = np.sqrt(G * common.result_depth * I) # u* = sqrt(ghI)
    except:
        logging.warning('Calculating COMP_CriticalDiameter failed. Maybe the solver uses unstructured grid.')
        diameter_error = True
        return
    
    # u2 [cm^2/s^2]
    u2 = u * u * 10000
    d = np.zeros(u2.shape)

    # d [mm]
    d += np.where(u2 < 1.469, u2 / 226.0 * 10, 0)
    d += np.where((1.469 <= u2) & (u2 < 3.1075), np.power(u2 / 8.41, 32/11) * 10, 0)
    d += np.where((3.1075 <= u2) & (u2 < 6.49), u2 / 55.0 * 10, 0)
    d += np.where((6.49 <= u2) & (u2 < 24.5127), np.power(u2 / 134.6, 22/31) * 10, 0)
    d += np.where(24.5127 <= u2, u2 / 80.9 * 10, 0)
    iric.cg_iRIC_Write_Sol_Real_Mul(common.write_fid, OUTPUT_DIAMETER_NAME, d)

def _process_step_strength():
    h = common.result_depth
    v = common.result_velocity

    strength = h * v * v
    iric.cg_iRIC_Write_Sol_Real_Mul(common.write_fid, OUTPUT_STRENGTH_NAME, strength)

# calculate energy gradient from wse
def _calc_energy_gradient_i(wse):
    isize, jsize = iric.cg_iRIC_GotoGridCoord2d_Mul(common.write_fid)
    x, y = iric.cg_iRIC_GetGridCoord2d_Mul(common.write_fid)

    x2 = x.reshape(jsize, isize)
    y2 = y.reshape(jsize, isize)
    wse2 = wse.reshape(jsize, isize)
    dx = np.diff(x2)
    dy = np.diff(y2)
    dwse = np.diff(wse2)

    ret = np.zeros(x2.shape)
    grad = dwse / np.sqrt(dx * dx + dy * dy)
    ret[:, 1:] += grad
    ret[:, :-1] += grad
    ret[:, 1:-1] /= 2 # average of two values
    ret = np.abs(ret)

    return ret.reshape(ret.size)

def _calc_energy_gradient_j(wse):
    isize, jsize = iric.cg_iRIC_GotoGridCoord2d_Mul(common.write_fid)
    x, y = iric.cg_iRIC_GetGridCoord2d_Mul(common.write_fid)

    x2 = x.reshape(jsize, isize)
    y2 = y.reshape(jsize, isize)
    wse2 = wse.reshape(jsize, isize)
    dx = np.diff(x2, axis=0)
    dy = np.diff(y2, axis=0)
    dwse = np.diff(wse2, axis=0)

    ret = np.zeros(x2.shape)
    grad = dwse / np.sqrt(dx * dx + dy * dy)
    ret[1:, :] += grad
    ret[:-1, :] += grad
    ret[1:-1, :] /= 2 # average of two values
    ret = np.abs(ret)

    return ret.reshape(ret.size)

def _process_step_manual():
    depth = common.result_depth
    wse = common.result_water_surface_elevation
    vx = common.result_velocityX
    vy = common.result_velocityY
    v1 = result_v1
    v2 = result_v2
    v = np.sqrt(vx * vx + vy * vy)

    result = manual_func(depth, wse, vx, vy, v1, v2, v)
    iric.cg_iRIC_Write_Sol_Real_Mul(common.write_fid, OUTPUT_MANUAL_NAME, result)

def _output_dummy(name):
    zeros = np.zeros(common.result_depth.shape)
    iric.cg_iRIC_Write_Sol_Real_Mul(common.write_fid, name, zeros)
