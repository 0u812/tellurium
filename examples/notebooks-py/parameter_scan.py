
# coding: utf-8

# Back to the main [Index](../index.ipynb)

# In[1]:

#!!! DO NOT CHANGE !!! THIS FILE WAS CREATED AUTOMATICALLY FROM NOTEBOOKS !!! CHANGES WILL BE OVERWRITTEN !!! CHANGE CORRESPONDING NOTEBOOK FILE !!!


# ### Parameter scan
# Perform a parameter scan.

# In[2]:

from __future__ import print_function
import tellurium as te

r = te.loada('''
    J1: $Xo -> x; 0.1 + k1*x^4/(k2+x^4);
    x -> $w; k3*x;

    k1 = 0.9;
    k2 = 0.3;
    k3 = 0.7;
    x = 0;
''')

# parameter scan
p = te.ParameterScan.ParameterScan(r)
# settings
p.startTime = 0
p.endTime = 15
p.numberOfPoints = 50
p.polyNumber = 10
p.endValue = 1.8
p.alpha = 0.8
p.value = "x"
p.selection = "x"
p.color = ['#0F0F3D', '#141452', '#1A1A66', '#1F1F7A', '#24248F', '#2929A3',
           '#2E2EB8', '#3333CC', '#4747D1', '#5C5CD6']
# plot
p.plotPolyArray()


# In[3]:

r = te.loada('''
    $Xo -> S1; vo;
    S1 -> S2; k1*S1 - k2*S2;
    S2 -> $X1; k3*S2;
    
    vo = 1
    k1 = 2; k2 = 0; k3 = 3;
''')

# parameter scan
p = te.ParameterScan.ParameterScan(r)
# settings
p.startTime = 0
p.endTime = 6
p.numberOfPoints = 50
p.startValue = 1
p.endValue = 5
p.colormap = "cool"
p.independent = ["Time", "k1"]
p.dependent = "S1"
p.xlabel = "Time"
p.ylabel = "x"
p.title = "Model"
# plot
p.plotSurface()


# In[4]:



