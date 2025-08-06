#! /usr/bin/python
# ==============================================================================================
# Name        : su2story
# Author      : Ettore Saetta
# Version     : 1.0.3 - Python
# Date        : 02/10/2020
# Copyright   : 
# Description : Plot the SU2 convergence history.
# Note        : Python 3 or higher needed.
# Installation: chmod +x su2story.py
#               This will create the executable.
# Input       : If no input, su2story looks for history.dat file.
#               Esle, it is possible to specify an history file name:
#               >> su2story.py FileName.dat
#
# Modified    : 05/10/2020
# What's new  : .csv files supported. File read improved. Caption input available.
# ==============================================================================================

import sys
import csv
import matplotlib.pyplot as plt
plt.style.use('default')
from datetime import date
import time

# ------ Read Column Function ------ #
def read_column(col_value):
    f = open(fileName, "r")
    linestoken = f.readlines()
    del linestoken[0]
    tokens_column_number = col_value
    resulttoken = []
    for x in linestoken:
        resulttoken.append(x.split()[tokens_column_number])
    resulttoken = [w.replace(',', '') for w in resulttoken]
    if csvFile == False:
        del resulttoken[0]
    f.close()
    return resulttoken

# ------ Plotting Function ------ #
def plotFigures(caption):
    position_plot = 0

    plotDate = date.today()
    plotDate = plotDate.strftime("%d/%m/%Y")
    plotTime = time.localtime()
    plotTime = time.strftime("%H:%M:%S", plotTime)

    fig = plt.figure()
    fig.suptitle('SU2 Convergence History', fontweight="bold")
    fig.text(.85, .98, 'Date: '+str(plotDate)+', Time: '+str(plotTime), ha='center', fontweight="bold")
    fig.text(.5, .05, caption, ha='center', fontweight="bold")
    fig.set_size_inches(30,10)

    for i in var:
        if i == '\"rms[Rho]\"':

            position_plot = position_plot + 1
            ax1 = fig.add_subplot(row,col,position_plot)
            ax1.plot(iterations, rho, 'k')
            ax1.grid(True)
            ax1.title.set_text('rms[Rho]')
            ax1.set_xlabel('$Iter$')
            ax1.set_ylabel('$res[\\rho]$')
        
        if i == '\"rms[RhoU]\"':

            position_plot = position_plot + 1
            ax2 = fig.add_subplot(row,col,position_plot)
            ax2.plot(iterations, rhoU, 'k')
            ax2.title.set_text('rms[RhoU]')
            ax2.grid(True)
            ax2.set_xlabel('$Iter$')
            ax2.set_ylabel('$res[\\rho U]$')
        
        if i == '\"rms[RhoE]\"' or i == '\"rms[RhoE]\"\n':
            
            position_plot = position_plot + 1
            ax3 = fig.add_subplot(row,col,position_plot)
            ax3.plot(iterations, rhoE, 'k')
            ax3.title.set_text('rms[RhoE]')
            ax3.grid(True)
            ax3.set_xlabel('$Iter$')
            ax3.set_ylabel('$res[\\rho E]$')
        
        if i == '\"CD\"':

            position_plot = position_plot + 1
            ax4 = fig.add_subplot(row,col,position_plot)
            ax4.plot(iterations, cd, 'k')
            ax4.title.set_text('Drag Coefficient')
            ax4.grid(True)
            ax4.set_xlabel('$Iter$')
            ax4.set_ylabel('$CD$')
        
        if i == '\"CL\"':
        
            position_plot = position_plot + 1
            ax5 = fig.add_subplot(row,col,position_plot) 
            ax5.plot(iterations, cl, 'k')
            ax5.title.set_text('Lift Coefficient')
            ax5.grid(True)
            ax5.set_xlabel('$Iter$')
            ax5.set_ylabel('$CL$')
        
        if i == '\"CMz\"':
            
            position_plot = position_plot + 1
            ax6 = fig.add_subplot(row,col,position_plot)
            ax6.plot(iterations, cmz, 'k')
            ax6.title.set_text('Pitch Coefficient')
            ax6.grid(True)
            ax6.set_xlabel('$Iter$')
            ax6.set_ylabel('$CMz$')

    plt.show()

# ------ MAIN ------ #
fileName = "history.dat"

if len(sys.argv) == 2:
    fileName = str(sys.argv[1])
if len(sys.argv) > 2:
    print("Only 1 file needed in input!")
    sys.exit()

csvFile = False
try:
    if fileName.endswith('.csv'):
        h = open(fileName, 'r')
        csvFile = True
    else:
        h = open(fileName, "r")
except IOError:
    print(fileName+" file not found.")
    sys.exit()

if csvFile:
    reader = csv.reader(h)
    var = next(reader)
    var = [w.replace(' ', '') for w in var]
    var = [w.replace('\t', '') for w in var]

else:
    var = h.readline()
    var = h.readline()
    var = var.replace(" ", "")
    var = var.replace("\t", "")
    var = var.split(",")

col = 3
row = 1
for i in var:       
    if i == '\"CD\"':
        col = 3
        row = 2
h.close()

numi = 0

for i in var:
    if i == 'Inner_Iter' or i == '\"Inner_Iter\"':
        iterations = read_column(numi)
        iterations = [int(i) for i in iterations]
        
    if i == '\"rms[Rho]\"':
        rho = read_column(numi)
        rho = [float(i) for i in rho]
        
    if i == '\"rms[RhoU]\"':
        rhoU = read_column(numi)
        rhoU = [float(i) for i in rhoU]
        
    if i == '\"rms[RhoE]\"' or i == '\"rms[RhoE]\"\n':
        rhoE = read_column(numi)
        rhoE = [float(i) for i in rhoE]
        
    if i == '\"CD\"':
        cd = read_column(numi)
        cd = [float(i) for i in cd]
        
    if i == '\"CL\"':
        cl = read_column(numi)
        cl = [float(i) for i in cl]
        
    if i == '\"CMz\"':
        cmz = read_column(numi)
        cmz = [float(i) for i in cmz]

    numi = numi+1

plotFigures('')

if sys.version_info[0] == 3:
    captionBool = input('Insert caption? y/<n>: ')
else:
    captionBool = raw_input('Insert caption? y/<n>: ')
if captionBool == 'y' or captionBool == 'Y':
    if sys.version_info[0] == 3:
        caption = input('Caption: ')
    else:
        caption = raw_input('Caption: ')
    plotFigures(caption)
