# -*- coding: utf-8 -*-
"""
Created on Wed May 22 15:01:21 2024

@author: emrkay
"""

""" This example demonstrates how to use the FMU.get*() and FMU.set*() functions

 to set custom input and control the simulation """

from matplotlib import pyplot as plt
%matplotlib qt
from fmpy import read_model_description, extract

from fmpy.fmi2 import FMU2Slave

from fmpy.util import plot_result, download_test_file

import numpy as np

import shutil




#def simulate_custom_input(show_plot=True):


    # define the model name and simulation parameters

fmu_filename = 'fmus/hex_delta.fmu'

start_time = 0.0


stop_time = 10.0
step_size = 1e-1


# download the FMU

#download_test_file('2.0', 'CoSimulation', 'MapleSim', '2016.2', 'CoupledClutches', fmu_filename)


# read the model description

model_description = read_model_description(fmu_filename)

print(model_description)

# collect the value references

vrs = {}

for variable in model_description.modelVariables:

    vrs[variable.name] = variable.valueReference

    print(variable.name + ':' +str(variable.valueReference))

# get the value references for the variables we want to get/set

vr_inputs   = []#vrs['inputs']      # normalized force on the 3rd clutch

for var in ['T1_in','T2_in','m1_in','m2_in']:

    vr_inputs.append(vrs[var])

input_values = [33,89,56,156]


vr_inits   = []#vrs['inputs']      # normalized force on the 3rd clutch

for var in ['K','T1_ini','T2_ini','cp1','cp2','m1','m2']:

    vr_inits.append(vrs[var])

init_values = [1000000,33,89,4190,4190,400,400]




   

#vr_outputs4 = vrs['outputs[4]']  # angular velocity of the 4th inertia

vr_outputs = []

for var in ['T1_out','T2_out']:

    vr_outputs.append(vrs[var])

# extract the FMU

unzipdir = extract(fmu_filename)


fmu = FMU2Slave(guid=model_description.guid,

                unzipDirectory=unzipdir,

                modelIdentifier=model_description.coSimulation.modelIdentifier,

                instanceName='instance1')



# initialize

fmu.instantiate()

fmu.setupExperiment(startTime=start_time)



for ivar, var in enumerate(vr_inits):
    fmu.setReal([var,],  [init_values[ivar]])

fmu.enterInitializationMode()

fmu.exitInitializationMode()


time = start_time


#rows = []  # list to record the results

data = np.zeros((10000,3))

# simulation loop

itime = 0

while time < stop_time:


    # NOTE: the FMU.get*() and FMU.set*() functions take lists of

    # value references as arguments and return lists of values


    # set the input

    fmu.setReal(vr_inputs, input_values)


    # perform one step

    fmu.doStep(currentCommunicationPoint=time, communicationStepSize=step_size)


    # advance the time

    time += step_size


    # get the values for 'inputs' and 'outputs[4]'

    outputs = fmu.getReal(vr_outputs)

    inputs = fmu.getReal(vr_inputs)

    # append the results

    #rows.append(outputs)

    data[itime,0] = time

    #for i in range(4):

    #    data[itime,i+1] = inputs[i]

    for i in range(2):

        data[itime,i+1] = outputs[i]

    itime=itime+1


fmu.terminate()

fmu.freeInstance()


# clean up

shutil.rmtree(unzipdir, ignore_errors=True)


# convert the results to a structured NumPy array

#result = np.array(rows, dtype=np.dtype([('time', np.float64), ('inputs', np.float64), ('outputs[4]', np.float64)]))

print(data[0:10,0:7])

# plot the results


fig,ax = plt.subplots()

ax.plot(data[:,0],data[:,1],'*',label='T1_out')
ax.plot(data[:,0],data[:,2],'*',label='T2_out')
ax.legend()
ax.grid()


