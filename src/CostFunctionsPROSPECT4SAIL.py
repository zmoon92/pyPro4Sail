# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 13:36:24 2015

@author: hector
"""    
from FourSAIL import FourSAIL_wl, CalcLIDF_Campbell
from Prospect5 import Prospect5_wl

def FCost_RMSE_ProSail_wl(x0,*args):
    ''' Cost Function for inverting PROSPEC5 + 4SAIL based on the Root Mean
        Square Error of observed vs. modeled reflectances
        
    Parameters
    ----------
    x0 : list with the a priori PROSAIL values to be retrieved during the inversion
    args : Dictionary with the additional arguments to be parsed in the inversion:
        'ObjParam': list of the PROSAIL parameters to be retrieved during the inversion, 
            sorted in the same order as in the param list
            ObjParam'=['N_leaf','Cab','Car','Cbrown', 'Cw','Cm', 'LAI', 'leaf_angle','hotspot']
        'FixedValues' : dictionary with the values of the parameters that are fixed
            during the inversion. The dictionary must complement the list from ObjParam
        'N_obs' : integer with the total number of observations used for the inversion
            N_Obs=1
        'rho_canopy': list with the observed surface reflectances. 
            The size of this list be wls*N_obs
        'vza' : list with the View Zenith Angle for each one of the observations.
            The size must be equal to N_obs
        'sza' : list with the Sun Zenith Angle for each one of the observations.
            The size must be equal to N_obs
        'psi' : list with the Relative View-Sun Angle for each one of the observations.
            The size must be equal to N_obs
        'skyl' : list with the ratio of diffuse radiation for each one of the observations.
            The size must be equal to N_obs
        'rsoil' : list with the background (soil) reflectance. 
            The size must be equal to the size of wls
         'wls' : list with wavebands used in the inversion
          Bounds : minimum and maximum tuple [min,max] for each objective parameter (Unused)
    
    Returns
    -------
    rmse : Root Mean Square Error of observed vs. modelled surface reflectance.
        This is the function to be minimized'''
    

    import numpy as np
    
    param_list=['N_leaf','Cab','Car','Cbrown', 'Cw','Cm', 'LAI', 'leaf_angle','hotspot']
    #Extract all the values needed
    ObjParam=args[0]
    FixedValues=args[1]
    n_obs=args[2]
    rho_canopy=args[3]
    vza=args[4]
    sza=args[5]
    psi=args[6]
    skyl=args[7]
    rsoil=args[8]
    wls=args[9]
    #bounds=args[10]
    # Get the a priori parameters and fixed parameters for the inversion
    input_parameters=dict()
    i=0
    j=0
    for param in param_list:
        if param in ObjParam:
            input_parameters[param]=x0[i]
            i=i+1
        else:
            input_parameters[param]=FixedValues[j]
            j=j+1
    # Start processing    
    n_wl=len(wls)
    error= np.zeros(n_obs*n_wl)
    #Calculate LIDF
    lidf=CalcLIDF_Campbell(float(input_parameters['leaf_angle']))
    i=0
    for obs in range(0,n_obs):
        j=0
        for wl in wls:
            [l,r,t]=Prospect5_wl(wl,input_parameters['N_leaf'],
                input_parameters['Cab'],input_parameters['Car'],input_parameters['Cbrown'], 
                input_parameters['Cw'],input_parameters['Cm'])
            [tss,too,tsstoo,rdd,tdd,rsd,tsd,rdo,tdo,rso,rsos,rsod,rddt,rsdt,rdot,
                 rsodt,rsost,rsot,gammasdf,gammasdb,gammaso]=FourSAIL_wl(input_parameters['LAI'],
               input_parameters['hotspot'],lidf,float(sza[obs]),float(vza[obs]),
                float(psi[obs]),r,t,float(rsoil[j]))
            r2=rdot*float(skyl[obs])+rsot*(1-float(skyl[obs]))
            error[i]=(rho_canopy[i]-r2)**2
            i+=1
            j+=1

    rmse=np.sqrt(np.mean(error,dtype=np.float64))

    return rmse

def FCostScaled_RMSE_ProSail_wl(x0,*args):
    ''' Cost Function for inverting PROSPEC5 + 4SAIL based on the Root Mean
        Square Error of observed vs. modeled reflectances and scaled [0,1] parameters
        
    Parameters
    ----------
    x0 : list with the a priori PROSAIL values to be retrieved during the inversion
    args : List with the additional arguments to be parsed in the inversion:
        ObjParam': list of the PROSAIL parameters to be retrieved during the inversion, 
            sorted in the same order as in the param list
            ObjParam'=['N_leaf','Cab','Car','Cbrown', 'Cw','Cm', 'LAI', 'leaf_angle','hotspot']
        FixedValues : dictionary with the values of the parameters that are fixed
            during the inversion. The dictionary must complement the list from ObjParam
        n_obs : integer with the total number of observations used for the inversion
            N_Obs=1
        rho_canopy: list with the observed surface reflectances. 
            The size of this list be wls*N_obs
        vza : list with the View Zenith Angle for each one of the observations.
            The size must be equal to N_obs
        sza : list with the Sun Zenith Angle for each one of the observations.
            The size must be equal to N_obs
        psi : list with the Relative View-Sun Angle for each one of the observations.
            The size must be equal to N_obs
        skyl : list with the ratio of diffuse radiation for each one of the observations.
            The size must be equal to N_obs
        rsoil : list with the background (soil) reflectance. 
            The size must be equal to the size of wls
        wls : list with wavebands used in the inversion
        Bounds : minimum and maximum tuple [min,max] for each objective parameter, used to unscale the 
            values
            
    Returns
    -------
    rmse : Root Mean Square Error of observed vs. modelled surface reflectance.
        This is the function to be minimized'''
    
    import numpy as np
    param_list=['N_leaf','Cab','Car','Cbrown', 'Cw','Cm', 'LAI', 'leaf_angle','hotspot']
    #Extract all the values needed
    ObjParam=args[0]
    FixedValues=args[1]
    n_obs=args[2]
    rho_canopy=args[3]
    vza=args[4]
    sza=args[5]
    psi=args[6]
    skyl=args[7]
    rsoil=args[8]
    wls=args[9]
    bounds=args[10]
    # Get the a priori parameters and fixed parameters for the inversion
    input_parameters=dict()
    i=0
    j=0
    for param in param_list:
        if param in ObjParam:
            #Transform the random variables (0-1) into biophysical variables 
            input_parameters[param]=x0[i]*float((bounds[i][1]-bounds[i][0]))+float(bounds[i][0])
            i=i+1
        else:
            input_parameters[param]=FixedValues[j]
            j=j+1
    # Start processing    
    n_wl=len(wls)
    error= np.zeros(n_obs*n_wl)
    #Calculate LIDF
    lidf=CalcLIDF_Campbell(float(input_parameters['leaf_angle']))
    i=0
    for obs in range(0,n_obs):
        j=0
        for wl in wls:
            [l,r,t]=Prospect5_wl(wl,input_parameters['N_leaf'],
                input_parameters['Cab'],input_parameters['Car'],input_parameters['Cbrown'], 
                input_parameters['Cw'],input_parameters['Cm'])
            [tss,too,tsstoo,rdd,tdd,rsd,tsd,rdo,tdo,rso,rsos,rsod,rddt,rsdt,rdot,
                 rsodt,rsost,rsot,gammasdf,gammasdb,gammaso]=FourSAIL_wl(input_parameters['LAI'],
                 input_parameters['hotspot'],lidf,float(sza[obs]),float(vza[obs]),
                float(psi[obs]),r,t,float(rsoil[j]))
            r2=rdot*float(skyl[obs])+rsot*(1-float(skyl[obs]))
            error[i]=(rho_canopy[i]-r2)**2
            i+=1
            j+=1
    rmse=np.sqrt(np.mean(error,dtype=np.float64))

    return rmse

def FCostScaled_RMSE_PROSPECT5_wl(x0,*args):
    ''' Cost Function for inverting PROSPECT5  the Root MeanSquare Error of 
    observed vs. modeled reflectances and scaled [0,1] parameters
        
    Parameters
    ----------
    x0 : list with the a priori PROSAIL values to be retrieved during the inversion
    args : List with the additional arguments to be parsed in the inversion:
        ObjParam': list of the PROSPECT5 parameters to be retrieved during the inversion, 
            sorted in the same order as in the param list
            ObjParam'=['N_leaf','Cab','Car','Cbrown', 'Cw','Cm']
        FixedValues : dictionary with the values of the parameters that are fixed
            during the inversion. The dictionary must complement the list from ObjParam
        n_obs : integer with the total number of observations used for the inversion
            N_Obs=1
        rho_leaf: list with the observed surface reflectances. 
            The size of this list be wls*N_obs
        wls : list with wavebands used in the inversion
        Bounds : minimum and maximum tuple [min,max] for each objective parameter, used to unscale the 
            values
            
    Returns
    -------
    rmse : Root Mean Square Error of observed vs. modelled surface reflectance.
        This is the function to be minimized'''
    
    import numpy as np
    param_list=['N_leaf','Cab','Car','Cbrown', 'Cw','Cm']
    #Extract all the values needed
    ObjParam=args[0]
    FixedValues=args[1]
    rho_leaf=args[2]
    wls=args[3]
    bounds=args[4]
    # Get the a priori parameters and fixed parameters for the inversion
    input_parameters=dict()
    i=0
    j=0
    for param in param_list:
        if param in ObjParam:
            #Transform the random variables (0-1) into biophysical variables 
            input_parameters[param]=x0[i]*float((bounds[i][1]-bounds[i][0]))+float(bounds[i][0])
            i=i+1
        else:
            input_parameters[param]=FixedValues[j]
            j=j+1
    # Start processing    
    n_wl=len(wls)
    error= np.zeros(n_wl)
    for i,wl in enumerate(wls):
        [l,r,t]=Prospect5_wl(wl,input_parameters['N_leaf'],
            input_parameters['Cab'],input_parameters['Car'],input_parameters['Cbrown'], 
            input_parameters['Cw'],input_parameters['Cm'])
        error[i]=(rho_leaf[i]-r)**2
    rmse=np.sqrt(np.mean(error,dtype=np.float64))

    return rmse

def FCostScaled_RRMSE_PROSPECT5_wl(x0,*args):
    ''' Cost Function for inverting PROSPECT5  the Relative Root MeanSquare Error of 
    observed vs. modeled reflectances and scaled [0,1] parameters
        
    Parameters
    ----------
    x0 : list with the a priori PROSAIL values to be retrieved during the inversion
    args : List with the additional arguments to be parsed in the inversion:
        ObjParam': list of the PROSPECT5 parameters to be retrieved during the inversion, 
            sorted in the same order as in the param list
            ObjParam'=['N_leaf','Cab','Car','Cbrown', 'Cw','Cm']
        FixedValues : dictionary with the values of the parameters that are fixed
            during the inversion. The dictionary must complement the list from ObjParam
        n_obs : integer with the total number of observations used for the inversion
            N_Obs=1
        rho_leaf: list with the observed surface reflectances. 
            The size of this list be wls*N_obs
        wls : list with wavebands used in the inversion
        Bounds : minimum and maximum tuple [min,max] for each objective parameter, used to unscale the 
            values
            
    Returns
    -------
    rmse : Root Mean Square Error of observed vs. modelled surface reflectance.
        This is the function to be minimized'''
    
    import numpy as np
    param_list=['N_leaf','Cab','Car','Cbrown', 'Cw','Cm']
    #Extract all the values needed
    ObjParam=args[0]
    FixedValues=args[1]
    rho_leaf=args[2]
    wls=args[3]
    bounds=args[4]
    # Get the a priori parameters and fixed parameters for the inversion
    input_parameters=dict()
    i=0
    j=0
    for param in param_list:
        if param in ObjParam:
            #Transform the random variables (0-1) into biophysical variables 
            input_parameters[param]=x0[i]*float((bounds[i][1]-bounds[i][0]))+float(bounds[i][0])
            i=i+1
        else:
            input_parameters[param]=FixedValues[j]
            j=j+1
    # Start processing    
    n_wl=len(wls)
    error= np.zeros(n_wl)
    for i,wl in enumerate(wls):
        [l,r,t]=Prospect5_wl(wl,input_parameters['N_leaf'],
            input_parameters['Cab'],input_parameters['Car'],input_parameters['Cbrown'], 
            input_parameters['Cw'],input_parameters['Cm'])
        error[i]=((rho_leaf[i]-r)**2)/rho_leaf[i]

    rmse=np.sqrt(np.mean(error,dtype=np.float64))

    return rmse