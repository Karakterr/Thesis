# -*- coding: utf-8 -*-
"""
Created on Fri Dec  9 15:11:00 2022

@author: josh

Preprocessing pipeline for pupillometry VWM + reward task. This code isn't
intended for inferential stats, just to clean and process the individual
participant data for further analysis elsewhere.

steps overview:

    1. use edf2asc to convert the data from .EDF to two .asc files, one with
    the sample data and another with the event data
    2. read in the data using pypillometry
    3. clean the data with a few basic steps (filter, blink detection and
        interpolation, mark bad dataspans)
    4. save the clean data and extract some summary data to use in analyses
"""

import sys, os
import subprocess
import pypillometry as pp
import pandas as pd
import numpy as np
import pylab as plt
#from itertools import chain

###############################################################################
# do conversion from EDF to ASC via edf2asc using subprocess library (this 
# sometimes causes problems depending on python version etc. alternative is 
# to just put the same text commands as generated via 'converter_cmd_txt_smp'
# and 'converter_cmd_txt_ev' into the command prompt directly, which should
# always work provided edf2asc is installed.)
#
# IDs = np.arange(1,32)
# for i in IDs:
    
#     if i < 10:
#         ID = "0{}".format(i)
#     else:
#         ID = str(i)
        
#     ID = '1'
    
#     converter_cmd_txt_smp = 'edf2asc C:/Users/susge/Desktop/Thesis/ThesisData/Raw/Pupil/SG_{}'.format(ID) +\
#         ' C:/Users/susge/Desktop/Thesis/ThesisData/Raw/Pupil/SG_{}_samples.asc -s'.format(ID)
#     converter_cmd_txt_ev = 'C:/Users/susge/Desktop/Thesis/ThesisData/Raw/Pupil/SG_{}'.format(ID) +\
#         ' C:/Users/susge/Desktop/Thesis/ThesisData/Raw/Pupil/SG_{}_events.asc -e'.format(ID)
    
#     print(converter_cmd_txt_ev)
#     print(converter_cmd_txt_smp)
    
#     print("converting event data for participant {}...".format(ID))
#     subprocess.run(converter_cmd_txt_ev)
#     print("...done")
#     print("converting sample data for participant {}...".format(ID))
#     subprocess.run(converter_cmd_txt_smp)
#     print("...done")
# print("...finished")

###############################################################################

# select the participant ID and navigate to their folder
ID = '1'

os.chdir('C:/Users/susge/Desktop/Thesis/ThesisData/Raw/Pupil/')
home_dir = os.getcwd()

# output filename
out_fname = 'pupDat_{}'.format(ID)

# filepaths to access the relevant data
#behavioural_fpath = home_dir + '/exclusions_' + ID + '.csv'
sample_fpath = '{0}/SG_{1}_samples.asc'.format(home_dir, ID)
event_fpath = '{0}/SG_{1}_events.asc'.format(home_dir, ID)

# read in the ET data
df = pd.read_table(sample_fpath, index_col=False,
                   names=["time", "left_x", "left_y", "left_p",
                          "right_x", "right_y", "right_p"])

# proportion of left and right eye data which is good
right_prop = (len(df) - df['right_p'].isnull().values.sum()) / len(df)
left_prop = (len(df) - df['left_p'].isnull().values.sum()) / len(df)

if right_prop < .5 and left_prop < .5:
    sys.exit('ERROR: not enough pupil data')
elif left_prop < right_prop:
    print('no left pupil')
    mean_p = df['right_p']
elif right_prop < left_prop:
    print('no right pupil')
    mean_p = df['left_p']
else:
    print('using both pupils')
    mean_p = df[['right_p', 'left_p']].mean(axis = 1)

mean_p = df['left_p']

# get the event messages
with open(event_fpath) as f: events = f.readlines()

# keep only lines starting with "MSG"
events = [ev for ev in events if ev.startswith("MSG")]

# find the start of the experiment (block 0, trial 0 start)
experiment_start_ix =np.where(["B0_T0" in ev for ev in events])[0][0]
events = events[experiment_start_ix:]

# convert events into a separate df
df_ev = pd.DataFrame([ev.split() for ev in events])

# get rid of non-message lines (i.e. recalibrations)
# NOTE: I've used column 3 instead of 4 because there are some non-events which
# are still 'none' for column 4
df_ev = df_ev[np.array(df_ev[3]) == None][[1,2]]
df_ev.columns = ["time", "event"]

# drop the residual 'calibration' messages
df_ev.drop(df_ev[df_ev.event == '!CAL'].index, inplace = True)
df_ev.drop(df_ev[df_ev.event == 'RECALIBRATION'].index, inplace = True)

'''
### Make a pypillometry object
'''
pupi = pp.PupilData(mean_p,
                    time = df.time,
                    event_onsets = df_ev.time,
                    event_labels = df_ev.event,
                    name = 'Sub_' + ID)

# reset time to start at zero
pupi = pupi.reset_time()

pupi = pupi.lowpass_filter(10)

# Detect blinks (start with defaults but modify for each sub as necessary)
pupi = pupi.blinks_detect(units = 'ms',
                          min_duration = 2, # float (units)
                          winsize = 10, # float (units)
                          vel_onset = -12, # float (units)
                          vel_offset = 5, # float (units)
                          min_onset_len = 3, # int (samples)
                          min_offset_len = 3, # int (samples)
                          strategies = ['zero', 'velocity'])

pupi = pupi.blinks_merge(distance = 500)

### VISUALISE THE DATA TO CHECK BLINK DETECTION ACCURACY

# duration of experiment in minutes
expt_end = (pupi.event_onsets[-1]/1000)/60
# experiment in one-minute steps
fig_starts = np.arange(0, expt_end, 1)

## Interpolate blinks
pupi_interp = pupi.blinks_interp_mahot(margin = (50, 100))

#pupi_interp = pupi_interp.lowpass_filter(10)

if len(fig_starts) < 20:
    for start in fig_starts:
        plt.figure(figsize = (17, 5))
        pupi.plot((start, start+1), units = 'min')
        pupi_interp.plot((start, start+1), highlight_blinks=False, units='min')
else:
    for start in fig_starts[0:20]:
        plt.figure(figsize = (17, 5))
        pupi.plot((start, start+1), units = 'min')
        pupi_interp.plot((start, start+1), highlight_blinks=False, units='min')
    print("STILL MORE FIGURES")

# break between printing to avoid over-loading the figures
if len(fig_starts) < 40:
    for start in fig_starts[19:len(fig_starts)]:
        plt.figure(figsize = (17, 5))
        pupi.plot((start, start+1), units = 'min')
        pupi_interp.plot((start, start+1), highlight_blinks=False, units='min')
else:
    for start in fig_starts[19:39]:
        plt.figure(figsize = (17, 5))
        pupi.plot((start, start+1), units = 'min')
        pupi_interp.plot((start, start+1), highlight_blinks=False, units='min')
    print("STILL MORE FIGURES")
    
# break between printing to avoid over-loading the figures
if len(fig_starts) < 40:
    for start in fig_starts[19:len(fig_starts)]:
        plt.figure(figsize = (17, 5))
        pupi.plot((start, start+1), units = 'min')
        pupi_interp.plot((start, start+1), highlight_blinks=False, units='min')
else:
    for start in fig_starts[39:59]:
        plt.figure(figsize = (17, 5))
        pupi.plot((start, start+1), units = 'min')
        pupi_interp.plot((start, start+1), highlight_blinks=False, units='min')
    print("STILL MORE FIGURES")
    
for start in fig_starts[59:len(fig_starts)]:
    plt.figure(figsize = (17, 5))
    pupi.plot((start, start+1), units = 'min')
    pupi_interp.plot((start, start+1), highlight_blinks = False, units = 'min')


# save the preprocessed pupil data here in case it's needed later
# output filename
out_fname = 'pupDat_{}_proc.pd'.format(ID)
pupi_interp.write_file(out_fname)

# save some separate data for analysis elsewhere?
# - mean response during high vs. low reward in epoch of interest?
# - mean prestimulus size before memory onset?
# - SD of both of above (esp prestimulus)

'''plot an average to check quality'''

# start of baseline period and end of analysis window
base_start = -200
win_end = 4000

# overall
erpd = pupi_interp.get_erpd("average response locked to memory onset",\
                        event_select = "ONSET",\
                        baseline_win = (base_start, 0),\
                        time_win = (base_start-300, win_end))
erpd.plot()

# reward effect
base_start = 600
win_end = 4000

erpd_high = pupi_interp.get_erpd("high_reward",\
                        event_select = "_high_reward",\
                        baseline_win = (base_start, 1000),\
                        time_win = (base_start-300, win_end))


erpd_low = pupi_interp.get_erpd("low_reward",\
                        event_select = "_low_reward",\
                        baseline_win = (base_start, 1000),\
                        time_win = (base_start-300, win_end))

erpd_high.plot(overlays = erpd_low)
