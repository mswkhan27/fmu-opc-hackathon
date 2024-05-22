# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 12:49:17 2024

@author: emrkay
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 14:04:47 2024

@author: emrkay
"""
############################
from matplotlib import pyplot as plt
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk) 
#%matplotlib qt
import tkinter as tk


from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
#from fmpy.util import plot_result, download_test_file
import numpy as np
import shutil

import hx_gui_globz as globz

############INITIAL CONFIGURATION

#init_dict = {
init_keys = ['T1_ini', 'T2_ini','mdot1_ini', 'mdot2_ini']
input_keys =[init_key[:-1] for init_key in init_keys]
output_keys = ['T1_out','mdot1_out','T2_out','mdot2_out']

#param_dict = {'A': 380.0, 'cp1': 4190.0, 'cp2': 4190.0, 'h': 6800.0, 'm1': 400.0, 'm2': 400.0}
param_keys = ['K', 'cp1', 'cp2', 'm1', 'm2']


#meta_param_dict = {'T1_decay':0, 'mdot1_decay':0}
meta_param_keys = ['T1_decay', 'mdot1_decay','T2_decay', 'mdot2_decay']

fmu_init_keys = ['T1_ini','T2_ini'] + list(param_keys)#list(np.setdiff1d(slider_names,meta_param_keys))


globz.config_dict = {'nFMUs':2, 'T1_ini':91, 'T1_decay':0, 'T2_ini':68,'T2_decay':0,'mdot1_ini':56.27 ,'mdot1_decay':0, 'mdot2_ini': 46.22,'mdot2_decay':0, 
                     'K': 2584000, 'cp1': 4190.0, 'cp2': 4190.0, 'm1': 400.0, 'm2': 400.0 }


init_config_keys = globz.config_dict.keys()
globz.outputplot_fmuid=0
##########################


# define the model name and simulation parameters

start_time = 0.0
#threshold = 2.0
stop_time = 100.0
step_size = 0.1
n_steps = int((stop_time- start_time)//step_size)+1
times = np.arange(start_time,stop_time,step_size)




fmu_filename= 'models/hx/hex_delta.fmu'
#############################################
#nfmus = 10
# read the model description
model_description = read_model_description(fmu_filename)
# extract the FMU
unzipdir = extract(fmu_filename)



#regertgret

# collect the value references
vrs = {}
for variable in model_description.modelVariables:
    vrs[variable.name] = variable.valueReference





window = tk.Tk()

sliders = dict()

slider_lims = { 'nFMUs': [1,100],'T1_ini':[0,120],'T1_decay':[-0.1,0.1],
               'T2_ini':[0,120], 'T2_decay':[-0.1,0.1],
               'mdot1_ini':[0,120],  'mdot1_decay':[-0.5,0.5] ,
               'mdot2_ini': [0,120],'mdot2_decay':[-0.5,0.5] , 
               'K': [0,2584000*1.5], 'cp1': [0,10000],
               'cp2': [0,10000], 'm1': [0,2000], 'm2': [0,2000]}


slider_names = list(slider_lims.keys())
slider_st_col = 0
slider_st_row = 0
nsliders = len(slider_names)
nsliderrows = 2#int(np.ceil(np.sqrt(nsliders)))
nslidercols = int(np.ceil(nsliders/nsliderrows))
for i,slider_name in enumerate(slider_names):
    reso = 1
    if 'decay' in slider_name:
        reso=0.001
    slider = tk.Scale(window, from_=slider_lims[slider_name][0], to=slider_lims[slider_name][1], resolution=reso,orient=tk.HORIZONTAL)
    slider.set(globz.config_dict[slider_name])
    sliders[slider_name]=slider
    row_ind,col_ind = np.unravel_index(i,(nsliderrows,nslidercols))
    slider.grid(row=2*(row_ind+slider_st_row), column=col_ind+slider_st_col)
    label=tk.Label(window,text=slider_name) 
    label.grid(row=2*(row_ind+slider_st_row)+1, column=col_ind+slider_st_col)


# get the value references for the variables we want to get/set
#vr_inputs = [vrs[inkey] for inkey in input_keys]
#vr_outputs =[vrs[outkey] for outkey in output_keys]#[4,5,6,7]  # 
# outvr2iout=dict()
# for iout in range(len(vr_outputs)):
#     outvr = vr_outputs[iout]
#     outvr2iout[outvr] = iout


globz.outputplot_fmuid
# dimensions of the main window 
window.geometry("500x500") 
  


def simulate_model():

    globz.nfmus = sliders['nFMUs'].get()
    fmus=[]
    for ifmu in range(globz.nfmus ):
        fmus.append(FMU2Slave(guid=model_description.guid,
                        unzipDirectory=unzipdir,
                        modelIdentifier=model_description.coSimulation.modelIdentifier,
                        instanceName='instance'+str(ifmu)))


    for slider_name in slider_names:
        
        globz.config_dict[slider_name] = sliders[slider_name].get()

    ##prepARE THE INPUTS:
    for init_name in init_keys:
        globz.config_dict[init_name[:-1]] = globz.config_dict[init_name]*np.ones(n_steps)
        
    globz.config_dict['T1_in'] = globz.config_dict['T1_ini'] - globz.config_dict['T1_decay']*np.arange(n_steps)
    globz.config_dict['mdot1_in'] = globz.config_dict['mdot1_ini'] - globz.config_dict['mdot1_decay']*np.arange(n_steps)
    globz.config_dict['T2_in'] = globz.config_dict['T2_ini'] - globz.config_dict['T2_decay']*np.arange(n_steps)
    globz.config_dict['mdot2_in'] = globz.config_dict['mdot2_ini'] - globz.config_dict['mdot2_decay']*np.arange(n_steps)
    #######
    
    
    
    for fmu in fmus:
        # initialize
        fmu.instantiate()
        fmu.setupExperiment(startTime=start_time)


    # clean up
    shutil.rmtree(unzipdir, ignore_errors=True)


    #time = start_time
    
    for fmu in fmus:
        for initkey in fmu_init_keys:
            fmu.setReal([vrs[initkey]], [globz.config_dict[initkey]]) 
    

        fmu.enterInitializationMode()
        fmu.exitInitializationMode()
    
    
    #[]#dict() #{0:[],1:[]}#[]  # list to record the results
    # for ifmu in range(globz.nfmus):
    #     results[ifmu]=[]
    #inputs = dict()
    #outputs = dict()
    #initialize the latents :
    # T2_in0 = globz.config_dict['T2_ini']
    # mdot2_in0 = globz.config_dict['mdot2_ini']
    #T1_in1 = globz.config_dict['T1_ini']
    #mdot1_in1 = globz.config_dict['mdot1_ini']
    # simulation loop
    times = np.arange(start_time,stop_time,step_size)
    ntimes = len(times)
    results = np.zeros((ntimes,3))
    results[:,0] = times
    #INITIALIZE LATENTS:
    T1_ins = np.zeros((globz.nfmus,))
    mdot1_ins = np.zeros((globz.nfmus,))
    T2_ins = globz.config_dict['T2_ini']*np.ones((globz.nfmus,))
    mdot2_ins = globz.config_dict['mdot2_ini']*np.ones((globz.nfmus,))
    for itime,time in enumerate(times):
        #inputs for the initial and final FMU are fed from the config_dict
        T1_ins[0] = globz.config_dict['T1_in'][int(time//step_size)]
        mdot1_ins[0] = globz.config_dict['mdot1_in'][int(time//step_size)]
        T2_ins[globz.nfmus-1] = globz.config_dict['T2_in'][int(time//step_size)]
        mdot2_ins[globz.nfmus-1] = globz.config_dict['mdot2_in'][int(time//step_size)]
        
        for ifmu in range(globz.nfmus):
            ###FEED THE INPUTS:
            fmus[ifmu].setReal([vrs['T1_in']],[T1_ins[ifmu]])
            fmus[ifmu].setReal([vrs['m1_in']],[mdot1_ins[ifmu]])
            fmus[ifmu].setReal([vrs['T2_in']],[T2_ins[ifmu]])
            fmus[ifmu].setReal([vrs['m2_in']],[mdot2_ins[ifmu]])
        
            # perform one step
            fmus[ifmu].doStep(currentCommunicationPoint=time, communicationStepSize=step_size)
        
            # get the 'outputs':
            T1_out_i = fmus[ifmu].getReal([vrs['T1_out']])[0] 
            mdot1_out_i = fmus[ifmu].getReal([vrs['m1_out']])[0]
            T2_out_i = fmus[ifmu].getReal([vrs['T2_out']])[0]
            mdot2_out_i = fmus[ifmu].getReal([vrs['m2_out']])[0]
            ## record the outputs to the input arrays:

            if ifmu<(globz.nfmus-1):
                T1_ins[ifmu+1] = T1_out_i
                mdot1_ins[ifmu+1] = mdot1_out_i
            if ifmu==0:
                results[itime,2] = T2_out_i
            if ifmu>0:
                T2_ins[ifmu-1] = T2_out_i
                mdot2_ins[ifmu-1] = mdot2_out_i
                
            if ifmu==(globz.nfmus-1):
                results[itime,1] = T1_out_i


    return results
            
        
        ##Collect the results:
        #results[itime,2] = T2_out0
        # if globz.nfmus==1:
        #     results[itime,1] = T1_out0
        #     T2_in0 = globz.config_dict['T2_in'][itime]
        #     mdot2_in0 = globz.config_dict['mdot2_in'][itime]
        # elif globz.nfmus==2:
        #     ####################################################################################
        #     ifmu = 1
        #     fmus[ifmu].setReal([vrs['T2_in']],[globz.config_dict['T2_in'][itime]])
        #     fmus[ifmu].setReal([vrs['m2_in']],[globz.config_dict['mdot2_in'][itime]])
        #     ### feed the latents
        #     fmus[ifmu].setReal([vrs['T1_in']],[T1_out0])
        #     fmus[ifmu].setReal([vrs['m1_in']],[mdot1_out0])
                            
            
        #     # perform one step
        #     fmus[ifmu].doStep(currentCommunicationPoint=time, communicationStepSize=step_size)
            
        #     # get the 'outputs':
        #     T1_out1 = fmus[ifmu].getReal([vrs['T1_out']])[0]
        #     #mdot1_out1 = fmus[ifmu].getReal(vrs['m1_out']) 
        #     T2_out1 = fmus[ifmu].getReal([vrs['T2_out']])[0] 
        #     mdot2_out1 = fmus[ifmu].getReal([vrs['m2_out']])[0] 
            
        #     #Set the latent inputs for hex_delta0:
        #     T2_in0 = T2_out1
        #     mdot2_in0 = mdot2_out1
            
        #     ##Collect the results:
            
        #     results[itime,1] = T1_out1
    


        

fig,ax1 = plt.subplots(figsize = (5, 5),  dpi = 100)    
canvas = FigureCanvasTkAgg(fig, 
                           master = window)   

seq_keys = ['T1_in','mdot1_in','T2_in','mdot2_in']
#ninps = len(seq_keys)
figinps,axinps = plt.subplots(2,figsize = (6, 5),  dpi = 100)    

figinps.suptitle('Input Temperatures and Flow Rates')
seqs_cnvs = FigureCanvasTkAgg(figinps, master = window)   
#drghdrgd

noutfigcols=8;noutfigrows=5

def plot_seqs_vs_time(seqs,ax,ylabel,seq_names):
    ax.clear()
    #ax.set_ylim(0,np.max(seq))
    ax.grid() 
    
    for i,seq in enumerate(seqs):
        ax.plot(times,seq,'*',label=seq_names[i])



    ax.legend()
    ax.set_ylabel(ylabel)
    ax.set_xlabel('time(s)')
  



plotrow = 2*nsliderrows+2


ymaxbox = tk.Entry(window) 
ymaxlabel = tk.Label(window,text='max temp')
ymaxlabel.grid(row=plotrow+noutfigrows,column=2)
ymaxbox.insert(0, "200")
ymaxbox.grid(row=plotrow+noutfigrows,column=3)

yminbox = tk.Entry(window) 
yminlabel = tk.Label(window,text='min temp')
yminlabel.grid(row=plotrow+noutfigrows,column=0)
yminbox.insert(0, "0")
yminbox.grid(row=plotrow+noutfigrows,column=1)
globz.set_ylim = True

def plot_output_temps():
    
    fig.suptitle('Output Temperatures:') #Fmu ID:'+str(globz.outputplot_fmuid))    
    #results = globz.results#[globz.nfmus-1]
    #globz.outputplot_fmuid = 1-globz.outputplot_fmuid
    ax1.clear()
    if globz.set_ylim:
        ax1.set_ylim(int(yminbox.get()),int(ymaxbox.get()))
    ax1.grid() 
    #time = []
    #T1_out = []
    #T2_out = []
    # for result in globz.results:
    #     time.append(result[0])
    #     T1_out.append(result[2][0])
    #     T2_out.append(result[2][2])
    times = globz.results[:,0]
    T1_outs = globz.results[:,1]
    T2_outs = globz.results[:,2]
    ax1.plot(times,T1_outs,'o',label='T1_out')
    ax1.plot(times,T2_outs,'o',label='T2_out')


    ax1.legend()
    ax1.set_ylabel('Temperature(°C)')
    ax1.set_xlabel('time(s)')


     
    canvas.draw()
    # placing the canvas on the Tkinter window 
    canvas.get_tk_widget().grid(row=plotrow, column=0,columnspan=noutfigcols,rowspan=noutfigrows)
    

    #canvas.get_tk_widget().grid(row=plotrow,column=0,columnspan=noutfigcols,rowspan=noutfigrows)
    
    canvas.flush_events()

def plot_with_autoylim():
    globz.set_ylim = False
    plot_output_temps()    

def plot_with_specylim():
    globz.set_ylim = True
    plot_output_temps()    
    
def simulate_and_plot():
    
    globz.results = simulate_model()

    
    #for iseq,seq_key in enumerate(seq_keys):
        # seqaxid = seqaxids[iseq]
        # seq_ax = axinps[seqaxid](seqs,ax,ylabel,seq_names)
    plot_seqs_vs_time([globz.config_dict['T1_in'],globz.config_dict['T2_in']] ,axinps[0],'Temperature(°C)',['T1_in','T2_in'])
    plot_seqs_vs_time([globz.config_dict['mdot1_in'],globz.config_dict['mdot2_in']] ,axinps[1],'Flow Rate',['mdot1_in','mdot2_in'])
    
    seqs_cnvs.draw()
    # placing the canvas on the Tkinter window 
    seqs_cnvs.get_tk_widget().grid(row=plotrow, column=noutfigcols)
     
    seqs_cnvs.flush_events()  
    
    plot_output_temps()

    
    
# button that simulates and displays the input plot s
plot_button = tk.Button(master = window,  
                     command = simulate_and_plot, 
                     height = 2,  
                     width = 10, 
                     text = "Simulate and \n Plot") 
  
# place the button  
# in main window 
plot_button.grid(row=0, column=8)
# # button that displays the output plot
# oplot_button = tk.Button(master = window,  
#                      command = plot_output_temps, 
#                      height = 2,  
#                      width = 10, 
#                      text = "plot outputs") 
  
# # place the button  
# # in main window 
# oplot_button.grid(row=0, column=9)

####################
aplot_button = tk.Button(master = window,  
                     command = plot_with_autoylim, 
                     height = 1,  
                     width = 20, 
                     text = "Plot with auto limits") 
  

aplot_button.grid(row=plotrow+noutfigrows,column=4)
######################################
splot_button = tk.Button(master = window,  
                     command = plot_with_specylim, 
                     height = 1,  
                     width = 20, 
                     text = "Plot with spec limits") 
  

splot_button.grid(row=plotrow+noutfigrows,column=5)
######################################
window.mainloop()

# fmu.terminate()
# fmu.freeInstance()