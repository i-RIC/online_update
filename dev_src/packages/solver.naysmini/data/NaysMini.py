import sys
import numpy as np
import iric
import copy
import os
import shutil
import common,geometry
import initial,boundary,stgg,cfxy,rhs,diffusion
import newgrd,cip2d,uxvx,fric,mkzero,hcal


def nays2dh_init(cgnsName):
    # open CGNS file to write
    common.write_fid = iric.cg_open(cgnsName, iric.CG_MODE_MODIFY)
    # print(common.write_fid)

    try:
        iric.cg_iRIC_Init(common.write_fid)
        iric.iRIC_InitOption(iric.IRIC_OPTION_CANCEL)
    except:
        print("Error: Please check if grid is imported.")
        exit()


def main(cgnsName):
    nays2dh_init(cgnsName)

    qp = iric.cg_iRIC_Read_Real('qp')
    snm = iric.cg_iRIC_Read_Real('snm')
    snu_0 = iric.cg_iRIC_Read_Real('snu_0')
    hmin = iric.cg_iRIC_Read_Real('hmin')
    cw = iric.cg_iRIC_Read_Real('cw')
    ep_alpha = iric.cg_iRIC_Read_Real('ep_alpha')
    g = 9.8; g_sqrt = np.sqrt(g)
    errmax=hmin
    j_west = iric.cg_iRIC_Read_Integer('j_west')
    j_east = iric.cg_iRIC_Read_Integer('j_east')
    j_hdown = iric.cg_iRIC_Read_Integer('j_hdown')
    h_down = iric.cg_iRIC_Read_Real('h_down')
    slope = iric.cg_iRIC_Read_Real('slope')
    etime = iric.cg_iRIC_Read_Real('etime')
    tuk = iric.cg_iRIC_Read_Real('tuk')
    dt = iric.cg_iRIC_Read_Real('dt')
    alh = iric.cg_iRIC_Read_Real('alh')
    lmax = iric.cg_iRIC_Read_Integer('lmax')
    it_out=int(tuk/dt)


    ni, nj = iric.cg_iRIC_GotoGridCoord2d()
    x1,y1=iric.cg_iRIC_GetGridCoord2d()
    x2 = np.reshape(x1,(ni,nj),order='F')
    y2 = np.reshape(y1,(ni,nj),order='F')
    chl=x2[ni-1,0]-x2[0,0]
    chb=y2[0,nj-1]-y2[0,0]
    nx=ni-1; ny=nj-1; nx1=nx+1; ny1=ny+1
    nx2=nx+2; ny2=ny+2
    nym=int(ny/2)
    xl=chl;yl=chb

    x = np.linspace(0, chl, nx1)
    y = np.linspace(0, chb, ny1)
    Y,X= np.meshgrid(y,x)

    ds=np.zeros([nx2,ny2]); dn=np.zeros([nx2,ny2])
    d_area=np.zeros([nx2,ny2])

    ds,dn=geometry.dsdn(x2,y2,ds,dn,nx,ny)
    d_area[:,:]=ds[:,:]*dn[:,:]

    dx=ds[1:-1,0:-1].mean()
    dy=dn[0:-1,1:-1].mean()
    area=d_area[1:-1,1:-1].mean()
    ijh1 = iric.cg_iRIC_Read_Grid_Integer_Cell('Obstacle')
    ijh2=np.reshape(ijh1,(ni-1,nj-1),order='F')
    ijh=np.zeros([nx2,ny2],dtype=int)
    ijh[1:-1,1:-1]=ijh2[0:,0:]

    u=np.zeros([nx2,ny2]); un=np.zeros([nx2,ny2]); v=np.zeros([nx2,ny2]); vn=np.zeros([nx2,ny2])
    hs=np.zeros([nx2,ny2]);  h=np.zeros([nx2,ny2]); hn=np.zeros([nx2,ny2])
    v_up=np.zeros([nx2,ny2]); hs_up=np.zeros([nx2,ny2]); u_vp=np.zeros([nx2,ny2]); hs_vp=np.zeros([nx2,ny2])
    eta=np.zeros([nx2,ny2]); ep=np.zeros([nx2,ny2]); ep_x=np.zeros([nx2,ny2]); usta=np.zeros([nx2,ny2])
    up=np.zeros([nx2,ny2]); vp=np.zeros([nx2,ny2])
    qu=np.zeros([nx2,ny2]); qv=np.zeros([nx2,ny2]); qc=np.zeros([nx2])
    qu_center=np.zeros([nx2]);hs_center=np.zeros([nx2])
    gux=np.zeros([nx2,ny2]); guy=np.zeros([nx2,ny2]); gvx=np.zeros([nx2,ny2]); gvy=np.zeros([nx2,ny2])
    gux_n=np.zeros([nx2,ny2]); guy_n=np.zeros([nx2,ny2])
    gvx_n=np.zeros([nx2,ny2]); gvy_n=np.zeros([nx2,ny2])
    cfx=np.zeros([nx2,ny2]); cfy=np.zeros([nx2,ny2]); qbx=np.zeros([nx2,ny2]); qby=np.zeros([nx2,ny2])
    uvis=np.zeros([nx2,ny2]);uvis_x=np.zeros([nx2,ny2]);uvis_y=np.zeros([nx2,ny2])
    vvis=np.zeros([nx2,ny2]);vvis_x=np.zeros([nx2,ny2]);vvis_y=np.zeros([nx2,ny2])
    fn=np.zeros([nx2,ny2]);gxn=np.zeros([nx2,ny2]);gyn=np.zeros([nx2,ny2])
    ux=np.zeros([nx1,ny1]);vx=np.zeros([nx1,ny1]); uv2=np.zeros([nx1,ny1])
    hx=np.zeros([nx1,ny1]);hsx=np.zeros([nx1,ny1]);vor=np.zeros([nx1,ny1])
    eta_center=np.zeros([nx2]); x_center=np.zeros([nx2]); h_center=np.zeros([nx2])

    eta=initial.eta_init(eta,nx,ny,slope,dx,chl) 
    x_center,eta_center=initial.xe_center(x_center,eta_center,nx,slope,dx,chl)

    hs0=(snm*qp/chb/np.sqrt(slope))**(3/5)
    u0=qp/(hs0*chb)
    qu0=u0*hs0*dy
 

    # Downstream Uniform Flow Depth
    if j_east==0 and j_hdown==1:
        h_down=eta_center[nx+1]+hs0


    u=initial.u_init(u,u0,nx,ny); un=copy.copy(u)
    h,hs=initial.h_init(h,hs,eta,hs0,nx,ny); hn=copy.copy(h) 
    ep,ep_x=initial.ep_init(ep,ep_x,nx,ny,snu_0)
    h,hs=boundary.h_bound(h,hs,eta,nx,ny,j_west,j_east,j_hdown,h_down)
    h_center[:]=h[:,nym]
    hn=copy.copy(h) 
    u=boundary.u_bound(u,nx,ny,j_west,j_east,ijh,u0)
    un=copy.copy(u)
    v=boundary.v_bound(v,nx,ny,ijh)
    vn=copy.copy(v)
    hs_up=stgg.hs_up_c(hs_up,hs,nx,ny)
    hs_vp=stgg.hs_vp_c(hs_vp,hs,nx,ny)
    qu,qc=rhs.qu_cal(qu,qc,u,nx,ny,dy,hs_up)
    qv=rhs.qv_cal(qv,v,nx,ny,dx,hs_vp)
    qadj=qc[0]/qp
    u_input=u0/qadj
    u_vp=stgg.u_vp_c(u_vp,u,nx,ny)
    hs_vp=stgg.hs_vp_c(hs_vp,hs,nx,ny)
    v_up=stgg.v_up_c(v_up,v,nx,ny)
    hs_up=stgg.hs_up_c(hs_up,hs,nx,ny)

    time=0.
    icount=0
    nfile=0
    iskip=1
    l=0
    while time<= etime:
        usta,ep,ep_x = fric.us_cal(usta,ep,ep_x,u,v,hs,nx,ny,snm,g_sqrt,hmin,ep_alpha)
        if icount%it_out==0:
            iric.iRIC_Check_Cancel()
            print('time=',np.round(time,3),l)
            iric.cg_iRIC_Write_Sol_Time(time)
            iric.cg_iRIC_Write_Sol_BaseIterative_Real("Discharge", qp)
            nfile=nfile+1
            ux,vx,uv2,hx,hsx=uxvx.uv(ux,vx,uv2,hx,hsx,u,v,h,hs,nx,ny)
            vor=uxvx.vortex(vor,u,v,nx,ny,dx,dy)
            uxx=np.reshape(ux,(ni*nj),order='F')
            iric.cg_iRIC_Write_Sol_Real("VelocityX", uxx)
            vxx=np.reshape(vx,(ni*nj),order='F')
            iric.cg_iRIC_Write_Sol_Real("VelocityY", vxx)
            hsxx=np.reshape(hsx,(ni*nj),order='F')
            iric.cg_iRIC_Write_Sol_Real("Depth", hsxx)
            hxx=np.reshape(hx,(ni*nj),order='F')
            iric.cg_iRIC_Write_Sol_Real("WaterSurface", hxx)
            vorx=np.reshape(vor,(ni*nj),order='F')
            iric.cg_iRIC_Write_Sol_Real("Vorticity", vorx)
            common.write_fid = iric.cg_iRIC_Flush(cgnsName, common.write_fid)

        l=0
        while l<lmax:
            v_up=stgg.v_up_c(v_up,vn,nx,ny)
            hs_up=stgg.hs_up_c(hs_up,hs,nx,ny)
            cfx=cfxy.cfxc(cfx,nx,ny,hs,un,g,snm,v_up,hs_up)
            un=rhs.un_cal(un,u,nx,ny,dx,cfx,hn,g,dt)
            un=boundary.u_bound(un,nx,ny,j_west,j_east,ijh,u_input)
            qu,qc=rhs.qu_cal(qu,qc,un,nx,ny,dy,hs_up)
            u_vp=stgg.u_vp_c(u_vp,un,nx,ny)
            hs_vp=stgg.hs_vp_c(hs_vp,hs,nx,ny)
            cfy=cfxy.cfyc(cfy,nx,ny,hs,vn,g,snm,u_vp,hs_vp)
            vn=rhs.vn_cal(vn,v,nx,ny,dy,cfy,hn,g,dt)
            vn=boundary.v_bound(vn,nx,ny,ijh)
            qv=rhs.qv_cal(qv,vn,nx,ny,dx,hs_vp)
            hn,hs,err=hcal.hh(hn,h,hs,eta,qu,qv,ijh,area,alh,hmin,nx,ny,dt)
            hn,hs=boundary.h_bound(hn,hs,eta,nx,ny,j_west,j_east,j_hdown,h_down)
            if err < errmax:
                break
            l=l+1
        un=diffusion.diff_u(un,uvis,uvis_x,uvis_y,nx,ny,dx,dy,dt,ep,ep_x,cw)
        un=boundary.u_bound(un,nx,ny,j_west,j_east,ijh,u_input)
        vn=diffusion.diff_v(vn,vvis,vvis_x,vvis_y,nx,ny,dx,dy,dt,ep,ep_x)
        vn=boundary.v_bound(vn,nx,ny,ijh)
        gux,guy=newgrd.ng_u(gux,guy,u,un,nx,ny,dx,dy)
        gux,guy=boundary.gbound_u(gux,guy,ijh,nx,ny)
        gvx,gvy=newgrd.ng_v(gvx,gvy,v,vn,nx,ny,dx,dy)
        gvx,gvy=boundary.gbound_v(gvx,gvy,ijh,nx,ny)
        fn,gxn,gyn=mkzero.z0(fn,gxn,gyn,nx,ny)
        v_up=stgg.v_up_c(v_up,v,nx,ny) 
        fn,gxn,gyn=cip2d.u_cal1(un,gux,guy,u,v_up,fn,gxn,gyn,nx,ny,dx,dy,dt)
        un,gux,guy=cip2d.u_cal2(fn,gxn,gyn,u,v_up,un,gux,guy,nx,ny,dx,dy,dt)
        un=boundary.u_bound(un,nx,ny,j_west,j_east,ijh,u_input)
        gux,guy=boundary.gbound_u(gux,guy,ijh,nx,ny)
        fn,gxn,gyn=mkzero.z0(fn,gxn,gyn,nx,ny)
        u_vp=stgg.u_vp_c(u_vp,u,nx,ny)
        fn,gxn,gyn=cip2d.v_cal1(vn,gvx,gvy,u_vp,v,fn,gxn,gyn,nx,ny,dx,dy,dt)
        vn,gvx,gvy=cip2d.v_cal2(fn,gxn,gyn,u_vp,v,vn,gvx,gvy,nx,ny,dx,dy,dt)
        vn=boundary.v_bound(vn,nx,ny,ijh)
        gvx,gvy=boundary.gbound_v(gvx,gvy,ijh,nx,ny)
        h=copy.copy(hn); u=copy.copy(un); v=copy.copy(vn)
        time=time+dt
        icount=icount+1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Error: CGNS file name not specified.")
        exit()

    cgnsName = sys.argv[1]
    main(cgnsName)
