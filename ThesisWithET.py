# experiment code file for thesis 'WHEN DOES COGNITIVE EFFORT PAY OFF? ASSESSING TASK-DEPENDENT COGNITIVE EFFORT ALLOCATION VIA PUPIL DILATION'
# written by Sus Geeraerts

# import modules
from __future__ import division, print_function
from psychopy.hardware import keyboard
from psychopy import visual, event, core, gui
import time, numpy, random, pandas, os
#from psychopy.iohub.client import launchHubServer # eye tracker
import pylink
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy

# create a dialog box
# info = {"Participant number":0, "Participant name":"Unknown", "Gender":["male", "female", "X"],"Age":0, "Handedness":["right", "left", "ambidextrous"]}
info = {"Participant nummer":0, "ET?": "yes", "Gender":["M", "V", "X"],"Leeftijd":0, "Handvoorkeur":["Rechtshandig", "Linkshandig", "Ambidexter"]}
already_exists = True 
while already_exists: 
    myDlg = gui.DlgFromDict(dictionary = info, title = "Experiment Title") #CHANGE
    file_name = "s" + str(info["Participant nummer"]) 
    if os.path.isfile(file_name+".csv"): 
        myDlg2 = gui.Dlg(title = "Error") 
        myDlg2.addText("Dit nummer is al gebruikt.") 
        myDlg2.show() 
    elif os.path.isfile(file_name+".edf"): 
        myDlg2 = gui.Dlg(title = "Error") 
        myDlg2.addText("Dit nummer is al gebruikt.") 
        myDlg2.show() 
    elif len(file_name) > 7: 
        already_exists = True 
        myDlg2 = gui.Dlg(title = "Error") 
        myDlg2.addText("Geef een participant nummer op met minder dan 7 karakters.") 
        myDlg2.show() 
    else: 
        already_exists = False 
print("OK, laten we beginnen!")

###Include practice? CHANGE, JUST FOR TESTING
practice = "yes"

# are we using the eyetracker for this session?
ET = info["ET?"] == 'yes'

### Initializing ###
# initialize the variables
nBlocks     = 8     ########## SHOULD BE 8 ########## 
nPrac       = 10     ########## IS THIS OK AMOUNT? ###
nTrials     = 40     ########## SHOULD BE 40 #########
participant = info["Participant nummer"]

# initialize a clock to measure the RT
my_clock = core.Clock()
eye_clock = core.Clock()

# initialize keyboard
kb = keyboard.Keyboard()

# initialize string that keeps track of the current condition
currentCondition = "Test"

# initialize coutner for reward
rewardCounter = 0

txt_col = 'black'
wwid = 1.3
ht = 0.06

CuePractice = ( "Gebruik de toetsen \"1\", \"2\", \"3\" en \"4\"" + "Wat is de betekennis van deze aanwijzing? \n\n" +
                "1) Moeilijke trial + hoge beloning.\n" + 
                "2) Moeilijke trial + lage beloning.\n" +
                "3) Makkelijke trial + hoge beloning.\n" +
                "4) Makkelijke trial + lage beloning.\n")

BreakTextStroop = ( "Dit was het einde van dit blok.\n\n" +
                    "Indien je wenst kan je nu een kleine pauze nemen.\n\n" +
                    "Het volgende blok bevat de taak met de bewegende stippen. \n\n" +
                    "Druk op 'rechts' om verder te gaan.")

BreakTextRDK = ("Dit was het einde van dit blok.\n\n" +
                "Indien je wenst kan je nu een kleine pauze nemen.\n\n" +
                "Het volgende blok bevat de taak met het benoemen van de kleuren. \n\n" +
                "Druk op 'rechts' om verder te gaan.")

goodbyeText =   ("Bedankt voor je deelname! \n\n" + 
                "Breng de experimentator op de hoogte dat je klaar bent alsjeblieft.")

# creating list of numbers from 1 to 40 to create conditions later
randomList=range(1,41)

# eyetracking initialization and calibration
'''
### SETUP EYETRACKER ###########################################################
'''
# eyelink setup
if ET:
    width_pix = 1920
    height_pix = 1080
    monitor_wid = 53
    view_dist = 135
    scrn = 0

    #print("starting ET setup")
    # trigger messages for eyelink
    # NOTE: the most important 'trial start' trigger is now defined by the
    # function 'write_msg' below. This carries the information about what are
    # the conditions for the present trial
    stim_msg = "STIMULUS"
    # response message and feedback message are customised to give details
    #response_msg = "RESPONSE"
    feedback_msg = "FEEDBACK"
    break_start_msg = "BREAK_START_BLOCK_" # + block number
    break_end_msg = "BREAK_END_BLOCK_" # + block number
    expt_end_msg = "END"
    recal_msg = "RECALIBRATION"
    quit_msg = "USER_QUIT"

    # tracker id
    eyelink = pylink.EyeLink('100.1.1.1')

    # file name for eye data
    ET_f_name = 'SG_{}.EDF'.format(participant)
    eyelink.openDataFile(ET_f_name)
    eyelink.sendCommand("add_file_preamble_text 'RDK Stroop CRD expt'")

    eyelink.setOfflineMode()
    # set ET parameters
    file_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
    link_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'
    file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,GAZERES,BUTTON,STATUS,INPUT'
    link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT'
    eyelink.sendCommand("file_event_filter = %s" % file_event_flags)
    eyelink.sendCommand("file_sample_data = %s" % file_sample_flags)
    eyelink.sendCommand("link_event_filter = %s" % link_event_flags)
    eyelink.sendCommand("link_sample_data = %s" % link_sample_flags)

    pylink.pumpDelay(100)
    coords_cmd = "screen_pixel_coords = 0 0 %d %d" % (width_pix-1, height_pix-1)
    eyelink.sendCommand(coords_cmd)
    coords_msg = "DISPLAY_COORDS = 0 0 %d %d" % (width_pix-1, height_pix-1)
    eyelink.sendMessage(coords_msg)

    def write_msg(trial, i, b):
        # Tsk type part of message
        if trial['TaskType'] == "Stroop":
            TaskType = 'Stroop'
        else:
            TaskType = 'RDK'

        # Condition (reward and difficulty) part of message
        condition = trial['condition']

        # one message for all of the trial parameters
        msg_out = "B{0}_T{1}_{2}_{3}".format(b, i, TaskType, condition)
        return msg_out

# initialize the window
win = visual.Window(size = [500,500], units = 'norm', fullscr = True, color = 'darkgrey')

##Initializing stuff to allow the storing of data
# retrieve the participant info
Subject    = numpy.repeat(info["Participant nummer"], nTrials)
Gender     = numpy.repeat("".join(info["Gender"]), len(Subject))
Age        = numpy.repeat(info["Leeftijd"], len(Subject))
Handedness = numpy.repeat("".join(info["Handvoorkeur"]), len(Subject))

# allow to store the task type
TaskType = numpy.repeat("", len(Subject))

# allow to store the congruence
Congruence = numpy.repeat("", len(Subject))

# allow to store the task type
RewardType = numpy.repeat("", len(Subject))

# allow to store the correct response
CorResp = numpy.repeat("", len(Subject))

# add a default response that will be overwritten during the trial loop
Resp = numpy.repeat("", len(Subject))

# allow to store the accuracy
Accuracy = numpy.repeat(numpy.nan, len(Subject))

# add a default RT that will be overwritten during the trial loop
RT = numpy.repeat(numpy.nan, len(Subject))

# add a reward counter
TotalReward = numpy.repeat(0, len(Subject))

# combine arrays in trial matrix
trials = numpy.column_stack([Subject, Gender, Age, Handedness, TaskType, Congruence, RewardType, CorResp, Resp, Accuracy, RT, TotalReward])

# repeat the trial matrix for the amount of blocks
trials = numpy.tile(trials, (nBlocks, 1))

## combine arrays to make a matrix to save practice results
#practiceResults = numpy.column_stack([Subject, Congruence, CorResp, Resp, Accuracy, RT])

# initialize graphical elements
# for general use
messageOnSCreen = visual.TextStim(win, text = "OK")
# make a blank text
blankText = visual.TextStim(win, text = " ", color = "grey")
# for cues
cueInstructionsMessage = visual.TextStim(win, text = "OK")
cueInstructionsImage = visual.ImageStim(win, image = "HighDHighR.png")
thermometerCue  = visual.ImageStim(win, image = "HighDHighR.png")
# for Stroop
StroopStim     = visual.TextStim(win, text = "red", color = "blue")
# and for RDK
dotPatchTarget = visual.DotStim(win, color= 'dimgrey', dir=0 ,
    nDots=50, fieldShape='circle', fieldPos=(0.0, 0.0), fieldSize=1,
    dotSize = 7.5,
    dotLife=-1,  # number of frames for each dot to be drawn
    signalDots='same',  # are signal dots 'same' on each frame?
    noiseDots='direction',  # do the noise dots follow random- 'walk', 'direction', or 'position'
    speed=0.01, coherence=1)

dotPatchDistractor = visual.DotStim(win, color= (1, 1, 1), dir=0 ,
    nDots=50, fieldShape='circle', fieldPos=(0.0, 0.0), fieldSize=1,
    dotSize = 7.5,
    dotLife=-1,  # number of frames for each dot to be drawn
    signalDots='same',  # are signal dots 'same' on each frame?
    noiseDots='direction',  # do the noise dots follow random- 'walk', 'direction', or 'position'
    speed=0.01, coherence=1)

### Functions ###
# make a function to display a message
def message(message_text = "", response_key = "space", duration = 0, height = None, pos = (0.0, 0.0), color = txt_col):
    
    messageOnSCreen.text    = message_text
    messageOnSCreen.height  = height
    messageOnSCreen.pos     = pos
    messageOnSCreen.color   = color
    
    messageOnSCreen.wrapWidth = 1.75
    
    messageOnSCreen.draw()
    win.flip()
    if duration == 0:
        event.waitKeys(keyList = response_key)
    else:
        time.sleep(duration)

# make a function to display the cue
def showImage(response_key = "space", duration = 0):
    
    thermometerCue.draw()
    win.flip()
    if duration == 0:
        event.waitKeys(keyList = response_key)
    else:
        time.sleep(duration)

# make a function to display a cue instruction message + image
def showCueAndText(message_text = "", response_keys = ["left", "right"], height = None, color = txt_col,  posText = (0.0, 0.0), posImage = (0.0, 0.0), image = "None"):
    
    cueInstructionsMessage.text    = message_text
    cueInstructionsMessage.height  = height
    cueInstructionsMessage.pos     = posText
    cueInstructionsMessage.color   = color
    
    cueInstructionsImage.image  = image
    cueInstructionsImage.pos    = posImage

    cueInstructionsMessage.wrapWidth = 1.75
    
    # clear the keyboard input
    event.clearEvents(eventType = "keyboard")
    
    #drawing and flippinh
    if image == "None":
        cueInstructionsMessage.draw()
    elif image != "None":
        cueInstructionsMessage.draw()
        cueInstructionsImage.draw()

    win.flip()
    
    #register the keys
    keys = event.waitKeys(keyList = response_keys)

    #prepare return
    cueInstructionsRespons = keys[0]
    
    return(cueInstructionsRespons)

# make a function to display intstructions
def instruct(image = "", response_keys = ["left", "right"], height = 2, width = 2):
    
    cueInstructionsImage.image  = image
    cueInstructionsImage.height  = height
    cueInstructionsImage.width  = width
    
    # clear the keyboard input
    event.clearEvents(eventType = "keyboard")
    
    #drawing and flipping
    cueInstructionsImage.draw()
    win.flip()
    
    #register the keys
    keys = event.waitKeys(keyList = response_keys)

    #prepare return
    cueInstructionsRespons = keys[0]
    
    return(cueInstructionsRespons)

# make a function to define word and font color for Stroop Task
def determine_Stroop_stim(x):
    
    # define ink color
    randomFontColor = int(randomFontColorList[x])
    
    if randomFontColor > 0 and randomFontColor < 11:
        StroopStim.color = "red" # displays 'red' ink color
        CorResp = "d"
    elif randomFontColor > 10 and randomFontColor < 21:
        StroopStim.color = "blue" # displays 'blue' ink color
        CorResp = "f"
    elif randomFontColor > 20 and randomFontColor < 31:
        StroopStim.color = "green" # displays 'green' ink color
        CorResp = "j"
    elif randomFontColor > 30 and randomFontColor < 41:
        StroopStim.color = "yellow" # displays 'yellow' ink color
        CorResp = "k"
    
    #define word color (congruent or incongruent = low or high demand)
    #and also determine high or low reward
    #this will then also determine the cue image
    randomColorWord = int(randomColorWordList[x])
        
    if  randomColorWord > 0 and  randomColorWord < 11:
        #low demand and low reward condition
        currentCondition = "LowDLowR"
        thermometerCue.image = "LowDLowR.png"
        Congruence = "Congruent"
        RewardType = "Low"
        
        #making text = color because congruent trial
        if randomFontColor > 0 and randomFontColor < 11:
         StroopStim.text = "rood" # displays the word 'red' 
        elif randomFontColor > 10 and randomFontColor < 21:
         StroopStim.text = "blauw" # displays the word 'blue' 
        elif randomFontColor > 20 and randomFontColor < 31:
         StroopStim.text = "groen" # displays the word 'green' 
        elif randomFontColor > 30 and randomFontColor < 41:
         StroopStim.text = "geel" # displays the word 'yellow' 

    elif randomColorWord > 10 and  randomColorWord < 21:
        #low demand and high reward condition
        currentCondition = "LowDHighR"
        thermometerCue.image = "LowDHighR.png"
        Congruence = "Congruent"
        RewardType = "High"

        #making text = color because congruent trial
        if randomFontColor > 0 and randomFontColor < 11:
         StroopStim.text = "rood" # displays the word 'red' 
        elif randomFontColor > 10 and randomFontColor < 21:
         StroopStim.text = "blauw" # displays the word 'blue' 
        elif randomFontColor > 20 and randomFontColor < 31:
         StroopStim.text = "groen" # displays the word 'green' 
        elif randomFontColor > 30 and randomFontColor < 41:
         StroopStim.text = "geel" # displays the word 'yellow'  

    elif randomColorWord > 20 and randomColorWord < 31:
        #high demand and low reward condition
        currentCondition = "HighDLowR"
        thermometerCue.image = "HighDLowR.png"
        Congruence = "Incongruent"
        RewardType = "Low"
        c = random.randint(1, 3) # select incongruent color
        
        if randomFontColor > 0 and randomFontColor < 11: # ink color = 'red'
            if c == 1:
                StroopStim.text = "blauw"
            elif c == 2:
                StroopStim.text = "groen"
            elif c == 3:
                StroopStim.text = "geel"
        elif randomFontColor > 10 and randomFontColor < 21: # ink color = 'blue'
            if c == 1:
                StroopStim.text = "rood"
            elif c == 2:
                StroopStim.text = "groen"
            elif c == 3:
                StroopStim.text = "geel"
        elif randomFontColor > 20 and randomFontColor < 31: # ink color = 'green'
            if c == 1:
                StroopStim.text = "rood"
            elif c == 2:
                StroopStim.text = "blauw"
            elif c == 3:
                StroopStim.text = "geel"
        elif randomFontColor > 30 and randomFontColor < 41: # ink color = 'yellow'
            if c == 1:
                StroopStim.text = "rood"
            elif c == 2:
                StroopStim.text = "blauw"
            elif c == 3:
                StroopStim.text = "groen"

    elif randomColorWord > 30 and randomColorWord < 41:
        #high demand and high reward condition
        currentCondition = "HighDHighR"
        thermometerCue.image = "HighDHighR.png"
        Congruence = "Incongruent"
        RewardType = "Low"
        c = random.randint(1, 3) # select incongruent color
        
        if randomFontColor > 0 and randomFontColor < 11: # ink color = 'red'
            if c == 1:
                StroopStim.text = "blauw"
            elif c == 2:
                StroopStim.text = "groen"
            elif c == 3:
                StroopStim.text = "geel"
        elif randomFontColor > 10 and randomFontColor < 21: # ink color = 'blue'
            if c == 1:
                StroopStim.text = "rood"
            elif c == 2:
                StroopStim.text = "groen"
            elif c == 3:
                StroopStim.text = "geel"
        elif randomFontColor > 20 and randomFontColor < 31: # ink color = 'green'
            if c == 1:
                StroopStim.text = "rood"
            elif c == 2:
                StroopStim.text = "blauw"
            elif c == 3:
                StroopStim.text = "geel"
        elif randomFontColor > 30 and randomFontColor < 41: # ink color = 'yellow'
            if c == 1:
                StroopStim.text = "rood"
            elif c == 2:
                StroopStim.text = "blauw"
            elif c == 3:
                StroopStim.text = "groen"
    
    return Congruence, RewardType, CorResp

# make a function to define word and font color for Stroop Practice Trial
def determine_Stroop_practice_stim(condition = ""):
    
    # define ink color
    randomFontColor = ["red", "blue", "green", "yellow"]
    random.shuffle(randomFontColor)
    StroopStim.color = randomFontColor[0]

    global CorResp

    #define word color (congruent or incongruent = low or high demand) and correct respons
    if  condition == "LowDLowR" or condition == "LowDHighR":
        #making text = color because congruent trial
        if randomFontColor[0] == "red":
         StroopStim.text = "rood" # displays the word 'red'
         CorRespTraining = "d"
        elif randomFontColor[0] == "blue":
         StroopStim.text = "blauw" # displays the word 'blue'
         CorRespTraining = "f"
        elif randomFontColor[0]== "green":
         StroopStim.text = "groen" # displays the word 'green'
         CorRespTraining = "j"
        elif randomFontColor[0] == "yellow":
         StroopStim.text = "geel" # displays the word 'yellow'
         CorRespTraining = "k"

    elif condition == "HighDLowR" or condition == "HighDHighR":
        #making text =! color because incongruent trial
        c = random.randint(1, 3) # select incongruent color
        if randomFontColor[0] == "red":
            CorRespTraining = "d"
            if c == 1:
                StroopStim.text = "blauw"
            elif c == 2:
                StroopStim.text = "groen"
            elif c == 3:
                StroopStim.text = "geel"
        elif randomFontColor[0] == "blue":
            CorRespTraining = "f"
            if c == 1:
                StroopStim.text = "rood"
            elif c == 2:
                StroopStim.text = "groen"
            elif c == 3:
                StroopStim.text = "geel"
        elif randomFontColor[0] == "green":
            CorRespTraining = "j"
            if c == 1:
                StroopStim.text = "rood"
            elif c == 2:
                StroopStim.text = "blauw"
            elif c == 3:
                StroopStim.text = "geel"
        elif randomFontColor[0] == "yellow":
            CorRespTraining = "k"
            if c == 1:
                StroopStim.text = "rood"
            elif c == 2:
                StroopStim.text = "blauw"
            elif c == 3:
                StroopStim.text = "groen"

    return CorRespTraining

# make a function to determine direction target, direction distractor and color distractor for RDM task
def determine_RDK_stim(x):

    #determine distractor color
    randomDistractorColor = int(randomDistractorColorList[x])

    if randomDistractorColor > 0 and randomDistractorColor < 11:
        dotPatchDistractor.color = (1, -1, -1) #=red
    elif randomDistractorColor > 10 and randomDistractorColor < 21:
        dotPatchDistractor.color = (-1, 1, -1) #=green
    elif randomDistractorColor > 20 and randomDistractorColor < 31:
        dotPatchDistractor.color = (-1, -1, 1) #=blue
    elif randomDistractorColor > 30 and randomDistractorColor < 41:
        dotPatchDistractor.color = (1, 1, -1) #=yellow

    #determine target direction
    randomTargetDirection = int(randomTargetDirectionList[x])
    global CorResp
    
    if  randomTargetDirection > 0 and  randomTargetDirection < 11:
        dotPatchTarget.dir = 0 #=right
        CorResp = "k"
    elif  randomTargetDirection > 10 and  randomTargetDirection < 21:
        dotPatchTarget.dir = 90 #=up
        CorResp = "j"
    elif  randomTargetDirection > 20 and  randomTargetDirection < 31:
        dotPatchTarget.dir = 180 #=left
        CorResp = "d"
    elif  randomTargetDirection > 30 and  randomTargetDirection < 41:
        dotPatchTarget.dir = 270 #=down
        CorResp = "f"

    #determine distractor direction (congruent or incongruent = low or high demand)
    #and also determine high or low reward
    #this will then also determine the cue image
    randomDistractorDirection = int(randomDistractorDirectionList[x])

    if  randomDistractorDirection > 0 and  randomDistractorDirection < 11:
        #low demand and low reward condition
        currentCondition = "LowDLowR"
        thermometerCue.image = "LowDLowR.png"
        Congruence = "Congruent"
        RewardType = "Low"
        dotPatchDistractor.dir = dotPatchTarget.dir #=congruent
        
    elif randomDistractorDirection > 10 and  randomDistractorDirection < 21:
        #low demand and high reward condition
        currentCondition = "LowDHighR"
        thermometerCue.image = "LowDHighR.png"
        Congruence = "Congruent"
        RewardType = "High"
        dotPatchDistractor.dir = dotPatchTarget.dir #=congruent
        
    elif  randomDistractorDirection > 20 and  randomDistractorDirection < 31:
        #high demand and low reward condition
        currentCondition = "HighDLowR"
        thermometerCue.image = "HighDLowR.png"
        Congruence = "Incongruent"
        RewardType = "Low"
        d = random.randint(1, 2) # select incongruent direction
        if d == 1:
            dotPatchDistractor.dir = dotPatchTarget.dir + 90 #=incongruent
        elif d == 2:
            dotPatchDistractor.dir = dotPatchTarget.dir + 180 #=incongruent
        
    elif  randomDistractorDirection > 30 and  randomDistractorDirection < 41:
        #high demand and high reward condition
        currentCondition = "HighDHighR"
        thermometerCue.image = "HighDHighR.png"
        Congruence = "Incongruent"
        RewardType = "High"
        d = random.randint(1, 2) # select incongruent direction
        if d == 1:
            e = random.randint(1, 2) # select incongruent direction 2
            if e == 1:
                dotPatchDistractor.dir = dotPatchTarget.dir + 90 #=incongruent
            elif e == 2:
                dotPatchDistractor.dir = dotPatchTarget.dir + 270 #=incongruent
        elif d == 2:
            dotPatchDistractor.dir = dotPatchTarget.dir + 180 #=incongruent
        
    return Congruence, RewardType, CorResp

def determine_RDK_practice_stim(condition = ""):
    
    # define color distractor
    randomDistractorColor = ["red", "blue", "green", "yellow"]
    random.shuffle(randomDistractorColor)
    dotPatchDistractor.color = randomDistractorColor[0]

    # define target direction
    randomTargetDirection = [0, 90, 180, 270]
    random.shuffle(randomTargetDirection)
    dotPatchTarget.dir = randomTargetDirection[0]
    
    global CorRespTraining

    if randomTargetDirection[0] == 0:
        CorRespTraining = "k"
    elif randomTargetDirection[0] == 90:
        CorRespTraining = "j"
    elif randomTargetDirection[0] == 180:
        CorRespTraining = "d"
    elif randomTargetDirection[0] == 270:
        CorRespTraining = "f"
    
    # define distractor direction
    if condition == "LowDLowR" or condition == "LowDHighR":
        #making distractor direction = target direction because congruent trial
         dotPatchDistractor.dir = dotPatchTarget.dir

    elif condition == "HighDLowR" or condition == "HighDHighR":
        #making distractor direction =! target direction because incongruent trial
        d = random.randint(1, 2) # select incongruent direction
        if d == 1:
            e = random.randint(1, 2) # select incongruent direction 2
            if e == 1:
                dotPatchDistractor.dir = dotPatchTarget.dir + 90 #=incongruent
            elif e == 2:
                dotPatchDistractor.dir = dotPatchTarget.dir + 270 #=incongruent
        elif d == 2:
            dotPatchDistractor.dir = dotPatchTarget.dir + 180 #=incongruent

    return CorRespTraining

# make a function for performing a Stroop trial
def perform_Stroop_trial():

    # present the thermometer cue (EQ)
    showImage(duration = 1)
    
    # fixation cross
    message(message_text = "+", duration = 2)
    
    # Tell the participant to get ready (AQ)
    message(message_text = "Get ready", duration = 1)
    
    # TRIGGER for start of trial cue
    if ET:
        msg = write_msg({'TaskType': TaskType, 'condition': currentCondition}, i, b)
        eyelink.sendMessage(msg)
    
    # fixation cross
    message(message_text = "+", duration = 2)
    
    # set RDMCheck to 0 before begining RDM loop
    StroopCheck = 0
    
    # clear the keyboard input
    event.clearEvents(eventType = "keyboard")
    
    # empty keys array
    keys = kb.getKeys(clear = True)
    
    # Reset the clock
    my_clock.reset()
    kb.clock.reset()
    
    # Loop for the Stroop stimuli
    # while loop untill buton press or max time
    while StroopCheck == 0:
        timer = my_clock.getTime()
        if timer < 0.5:
            StroopStim.draw()
        else:
            blankText.draw()
        win.flip()
        keys = kb.getKeys(keyList = ["d","f","j","k","escape","tab"], clear = False)
        if keys == [] and timer < 1.2:
            StroopCheck = 0
        else:
            StroopCheck = 1
    
    # initialize temporary variables to save response given and RT
    trialResp = ""
    trialRT = 0
    
    # determine the given response and RT
    if keys == []:
        trialResp = "None"
        trialRT = 2 ### see max time per trial
    else:
        for key in keys:
            trialResp = str(key.name)
            trialRT = (key.rt)
    
    # Blank screen (ITI)
    blankText.draw()
    win.flip()
    core.wait(2)
    
    return trialResp, trialRT

# make a function for performing a Stroop practice trial
def perform_Stroop_practice_trial():
    
    # fixation cross
    message(message_text = "+", duration = 2)
    
    # Tell the participant to get ready (AQ)
    message(message_text = "Get ready", duration = 1)
    
    # fixation cross
    message(message_text = "+", duration = 2)
    
    # set RDMCheck to 0 before begining RDM loop
    StroopCheck = 0
    
    # clear the keyboard input
    event.clearEvents(eventType = "keyboard")
    
    # empty keys array
    keys = kb.getKeys(clear = True)
    
    # Reset the clock
    my_clock.reset()
    kb.clock.reset()
    
    # Loop for the Stroop stimuli
    # while loop untill buton press or max time
    while StroopCheck == 0:
        timer = my_clock.getTime()
        if timer < 0.5:
            StroopStim.draw()
        else:
            blankText.draw()
        win.flip()
        keys = kb.getKeys(keyList = ["d","f","j","k","escape","tab"], clear = False)
        if keys == [] and timer < 1.2:
            StroopCheck = 0
        else:
            StroopCheck = 1
    
    # initialize temporary variables to save response given and RT
    trialResp = ""
    
    # determine the given response and RT
    if keys == []:
        trialResp = "None"
    else:
        for key in keys:
            trialResp = str(key.name)
    
    # Blank screen (ITI)
    blankText.draw()
    win.flip()
    core.wait(2)
    
    return trialResp

# make a function for performing a RDM trial
def perform_RDK_trial():
    
    # present the thermometer cue (EQ)
    showImage(duration = 1)
    
    # fixation cross
    message(message_text = "+", duration = 2)
    
    # Tell the participant to get ready (AQ)
    message(message_text = "Get ready", duration = 1)
    
    # TRIGGER for start of trial cue
    if ET:
        msg = write_msg({'TaskType': TaskType, 'condition': currentCondition}, i, b)
        eyelink.sendMessage(msg)
    
    # fixation cross
    message(message_text = "+", duration = 2)
    
    # set RDMCheck to 0 before begining RDM loop
    RDMCheck = 0
    
    # clear the keyboard input
    event.clearEvents(eventType = "keyboard")
    
    # empty keys array
    keys = kb.getKeys(clear = True)
    
    # Reset the clock
    my_clock.reset()
    kb.clock.reset()
    
    # Loop for the RDM stimuli
    # while loop untill buton press or max time
    while RDMCheck == 0:
        timer = my_clock.getTime()
        if timer < 0.5:
            dotPatchTarget.draw()
            dotPatchDistractor.draw()
        else:
            blankText.draw()
        win.flip()
        keys = kb.getKeys(keyList = ["d","f","j","k","escape","tab"], clear = False)
        if keys == [] and timer < 1.2:
            RDMCheck = 0
        else:
            RDMCheck = 1
    
    # initialize temporary variables to save response given and RT
    trialResp = ""
    trialRT = 0
    
    # determine the given response and RT
    if keys == []:
        trialResp = "None"
        trialRT = 2
    else:
        for key in keys:
            trialResp = str(key.name)
            trialRT = (key.rt)
    
    # Blank screen (ITI)
    blankText.draw()
    win.flip()
    core.wait(2)
    
    return trialResp, trialRT

# make a function for performing a RDK practice trial
def perform_RDK_practice_trial():
    
    # fixation cross
    message(message_text = "+", duration = 2)
    
    # Tell the participant to get ready (AQ)
    message(message_text = "Get ready", duration = 1)
    
    # fixation cross
    message(message_text = "+", duration = 2)
    
    # set RDMCheck to 0 before begining RDM loop
    RDMCheck = 0
    
    # clear the keyboard input
    event.clearEvents(eventType = "keyboard")
    
    # empty keys array
    keys = kb.getKeys(clear = True)
    
    # Reset the clock
    my_clock.reset()
    kb.clock.reset()
    
    # Loop for the RDM stimuli
    # while loop untill buton press or max time
    while RDMCheck == 0:
        timer = my_clock.getTime()
        if timer < 0.5:
            dotPatchTarget.draw()
            dotPatchDistractor.draw()
        else:
            blankText.draw()
        win.flip()
        keys = kb.getKeys(keyList = ["d","f","j","k","escape","tab"], clear = False)
        if keys == [] and timer < 1.2:
            RDMCheck = 0
        else:
            RDMCheck = 1
    
    # initialize temporary variables to save response given and RT
    trialResp = ""
    
    # determine the given response and RT
    if keys == []:
        trialResp = "None"
    else:
        for key in keys:
            trialResp = str(key.name)
    
    # Blank screen (ITI)
    blankText.draw()
    win.flip()
    core.wait(2)
    
    return trialResp

# make a function to save the data 
#(task type, congruence, reward type, corResp, respons, accuracy, RT, total reward)
def save_data(bSD, iSD, taskTypeSD, congruenceSD, rewardTypeSD, corRespSD, respSD, RTSD):
    numberSD = (bSD * nTrials) + iSD
    trials[numberSD, 4] = taskTypeSD
    trials[numberSD, 5] = congruenceSD
    trials[numberSD, 6] = rewardTypeSD
    trials[numberSD, 7] = corRespSD
    trials[numberSD, 8] = respSD
    
    # if function to determine and save accuracy
    if respSD == corRespSD:
        accuracySD = 1
    else:
        accuracySD = 0
    trials[numberSD, 9] = accuracySD
    
    trials[numberSD, 10] = RTSD
    
    return accuracySD

# make a function to keep track of and save the reward amount(s)
def determine_reward(bDR, iDR):

    numberSD = (bDR * nTrials) + iDR
    
    global thisTrialReward
    
    # if function to possibly increase reward counter
    if trials[numberSD, 9] == "1":
        if trials[numberSD, 6] == "High":
            possibleReward = 0.9
        elif trials[numberSD, 6] == "Low":
            possibleReward = 0.05
    else:
        possibleReward = 0
    
    thisTrialReward = round(possibleReward, 2)

    trials[numberSD, 11] = thisTrialReward
    
#make a function to determine and display the block feedback
def feedback(bFB):
    
    # Create nCorrectHighRTrials and nCorrectLowRTrials for later
    nCorrectHighRTrials = 0
    nCorrectLowRTrials = 0
    
    # Calculate mean accuracy across block
    blockAccuracyCounter = 0
    
    for i in range (nTrials):
        trialNumber = (bFB * nTrials) + i
        highOrLowRewardType = str(trials[trialNumber, 6])
        trialAccuracy = int(trials[trialNumber, 9])
        blockAccuracyCounter = blockAccuracyCounter + trialAccuracy
        # Calculate amount of high and low correct trials
        if trialAccuracy == 1:
            if highOrLowRewardType == "High":
                nCorrectHighRTrials = nCorrectHighRTrials + 1
            elif highOrLowRewardType == "Low":
                nCorrectLowRTrials = nCorrectLowRTrials + 1
        
    blockAccuracy = 100 * (blockAccuracyCounter / nTrials)
    
    ## Calculate reward amount gained across block #not necessary
    #totalRewardLastTrialLastBlock = float(trials[(bFB * nTrials) - 1, 11])
    #totalRewardLastTrialThisBlock = float(trials[(bFB * nTrials) + (nTrials - 1), 11])
    #rewardThisBlock = totalRewardLastTrialThisBlock - totalRewardLastTrialLastBlock
    
    feedbackText = ("Dit is het einde van dit blok. \n\n" +
                    "In dit blok had je een nauwkeurigheid van " + str(blockAccuracy) + "%.\n" +
                    "Je gaf een correct antwoord voor " + str(nCorrectHighRTrials) + " taken met een hoge belonging" +
                    " en " + str(nCorrectLowRTrials) + " taken met een lage belonging.\n\n" +
                    "Druk op 'rechts' om het volgende blok te starten.")
    
    message(message_text = feedbackText, response_key = "right")

# determine task order 
if participant%2 != 0:
    # Participants with an odd number get the Stroop Task first
    TaskOrder = ["Stroop","RDK","Stroop","RDK","Stroop","RDK","Stroop","RDK"]
    
else:
    # participants with an even number get the RDM Task first
    TaskOrder = ["RDK","Stroop","RDK","Stroop","RDK","Stroop","RDK","Stroop"]

'''
### Actual experiment ##########################################
'''
# display the welcome message
message(message_text = "Welkom!\n\n Druk op 'rechts' om verder te gaan.", response_key = "right")

# display introduction and practice trials
# display general instructions
instruct(image = "instructionsStart.png")

if practice == "yes":
    CorRespTraining = " " #needed later
    
    # make a while loop for the Stroop training that breaks when accuracy >= 0.8
    # In this loop show the instructions for the Stroop task
    
    # 10(?) Stroop practice trials, repeat if accuracy < 0.8
    # make an random array with every condition once plus random one
    stroopTrainingArray = [ "HighDHighR", "HighDLowR", "LowDHighR", "LowDLowR", "Random",
                            "HighDHighR", "HighDLowR", "LowDHighR", "LowDLowR", "Random"]
    stroopTrainingComplete = 0
    while stroopTrainingComplete == 0:
        # display Stroop instructions
        currentStroopInstructionTrial = 0
        while currentStroopInstructionTrial < 2:
            if currentStroopInstructionTrial == 0:
                stroopInstructionsRespons = instruct(image = "instructionsStroop.png")
            elif currentStroopInstructionTrial == 1:
                stroopInstructionsRespons = instruct(image = "instructionsStroopTrainingStart.png")
       
            if stroopInstructionsRespons == "left":
                currentStroopInstructionTrial = currentStroopInstructionTrial - 1
            elif stroopInstructionsRespons == "right":
                currentStroopInstructionTrial = currentStroopInstructionTrial + 1

            if currentStroopInstructionTrial == -1:
                currentStroopInstructionTrial = 0
            elif currentStroopInstructionTrial == 2:
                break
    
        random.shuffle(stroopTrainingArray) #shuffle array each time so it's different when participants are wrong
        accuracyStroopTraining = 0 #to determine if trial complete = 1
    
        for t in range (0, 10):
            if stroopTrainingArray[t] == "Random":
                whenStroopTrainingIsRandomArray = ["HighDHighR", "HighDLowR", "LowDHighR", "LowDLowR"]
                random.shuffle(whenStroopTrainingIsRandomArray)
                stroopTrainingArray[t] = whenStroopTrainingIsRandomArray[0]
        
            #determine Stroop stim and correct response
            CorResp = determine_Stroop_practice_stim(condition = stroopTrainingArray[t])
            # perform the Stroop trial
            Resp = perform_Stroop_practice_trial()
        
            if Resp == CorResp:
                accuracyStroopTraining = accuracyStroopTraining + 0.1
                message(message_text = "Correct", duration = 1)
            elif Resp != CorResp:
                message(message_text = "Incorrect", duration = 1)

            # to escape loop
            if Resp == "escape":
                break

        if accuracyStroopTraining >= 0.8:
            instruct(image = "instructionsStroopTrainingFinish.png")
            stroopTrainingComplete = 1
            break
        else: # display message that they have to take the training again if accuracy <0.8
            instruct(image = "instructionsTrainingFail.png")
    
        # to escape loop 
        if Resp == "escape":
            break

    # make a while loop for the RDK training that breaks when accuracy >= 0.8
    # In this loop show the instructions for the RDK task

    # 10(?) RDK practice trials, repeat if accuracy < 0.8
    # make an random array with every condition once plus random one
    RDKTrainingArray = ["HighDHighR", "HighDLowR", "LowDHighR", "LowDLowR", "Random",
                    "HighDHighR", "HighDLowR", "LowDHighR", "LowDLowR", "Random"]
    RDKTrainingComplete = 0
    while RDKTrainingComplete == 0:
        # display Stroop instructions
        currentRDKInstructionTrial = 0
        while currentRDKInstructionTrial < 2:
            if currentRDKInstructionTrial == 0:
                RDKInstructionsRespons = instruct(image = "instructionsRDK.png")
            elif currentRDKInstructionTrial == 1:
                RDKInstructionsRespons = instruct(image = "instructionsRDKTrainingStart.png")
       
            if RDKInstructionsRespons == "left":
                currentRDKInstructionTrial = currentRDKInstructionTrial - 1
            elif RDKInstructionsRespons == "right":
                currentRDKInstructionTrial = currentRDKInstructionTrial + 1

            if currentRDKInstructionTrial == -1:
                currentRDKInstructionTrial = 0
            elif currentRDKInstructionTrial == 2:
                break
    
        random.shuffle(RDKTrainingArray) #shuffle array each time so it's different when participants are wrong
        accuracyRDKTraining = 0 #to determine if trial complete = 1
    
        for u in range (0, 10):
            if RDKTrainingArray[u] == "Random":
                whenRDKTrainingIsRandomArray = ["HighDHighR", "HighDLowR", "LowDHighR", "LowDLowR"]
                random.shuffle(whenRDKTrainingIsRandomArray)
                RDKTrainingArray[u] = whenRDKTrainingIsRandomArray[0]
        
            #determine Stroop stim and correct response
            CorResp = determine_RDK_practice_stim(condition = RDKTrainingArray[u])
            # perform the Stroop trial
            Resp = perform_RDK_practice_trial()
        
            print(CorRespTraining)
            print(Resp)
        
            if Resp == CorResp:
                accuracyRDKTraining = accuracyRDKTraining + 0.1
                message(message_text = "Correct", duration = 1)
            elif Resp != CorResp:
                message(message_text = "Incorrect", duration = 1)

            # to escape loop
            if Resp == "escape":
                break

        if accuracyRDKTraining >= 0.8:
            instruct(image = "instructionsRDKTrainingFinish.png")
            RDKtrainingCompleteCheck = 1
            break
        else: # display message that they have to take the training again if accuracy <0.8
            instruct(image = "instructionsTrainingFail.png")
    
        # to escape loop 
        if Resp == "escape":
                break

    # display Cue instructions
    currentCueInstructionTrial = 0
    while currentCueInstructionTrial < 6:
        if currentCueInstructionTrial == 0:
            cueInstructionsRespons = instruct(image = "instructionsCue1.png")
        elif currentCueInstructionTrial == 1:
            cueInstructionsRespons = instruct(image = "instructionsCue2.png")
        elif currentCueInstructionTrial == 2:
            cueInstructionsRespons = instruct(image = "instructionsCue3.png")
        elif currentCueInstructionTrial == 3:
            cueInstructionsRespons = instruct(image = "instructionsCueTrainingStart.png")

        if cueInstructionsRespons == "left":
            currentCueInstructionTrial = currentCueInstructionTrial - 1
        elif cueInstructionsRespons == "right":
            currentCueInstructionTrial = currentCueInstructionTrial + 1

        if currentCueInstructionTrial == -1:
            currentCueInstructionTrial = 0
        elif currentCueInstructionTrial == 6:
            break

    # display the 4 different cues and let them answer what it is, repeat if accuracy = 1.0
    # make an random array with HighDHighR, HighDLowR, LowDHighR, LowDLowR
    cueTrainingArray = ["HighDHighR", "HighDLowR", "LowDHighR", "LowDLowR"]
    random.shuffle(cueTrainingArray)

    # make a while loop that breaks when accuracy = 1
    cueTrainingCompleteCheck = 0
    while cueTrainingCompleteCheck == 0:
        random.shuffle(cueTrainingArray) #shuffle array each time so it's different when participants are wrong
        accuracyCueTraining = 0 #to determine if trial complete = 1
        for t in range (0, 4):
            rightAnswerCueTraining = "0" #to calculate accuracy
            if cueTrainingArray[t] == "HighDHighR":
                cueInstructionsRespons = showCueAndText(message_text = CuePractice, response_keys = ["1", "2", "3", "4", "escape"], height = 0.075, posText = (0.0, -0.5), posImage = (0.0, 0.5), image = "HighDHighR.png")
                rightAnswerCueTraining = "1"
            elif cueTrainingArray[t] == "HighDLowR":
                cueInstructionsRespons = showCueAndText(message_text = CuePractice, response_keys = ["1", "2", "3", "4", "escape"], height = 0.075, posText = (0.0, -0.5), posImage = (0.0, 0.5), image = "HighDLowR.png")
                rightAnswerCueTraining = "2"
            elif cueTrainingArray[t] == "LowDHighR":
                cueInstructionsRespons = showCueAndText(message_text = CuePractice, response_keys = ["1", "2", "3", "4", "escape"], height = 0.075, posText = (0.0, -0.5), posImage = (0.0, 0.5), image = "LowDHighR.png")
                rightAnswerCueTraining = "3"
            elif cueTrainingArray[t] == "LowDLowR":
                cueInstructionsRespons = showCueAndText(message_text = CuePractice, response_keys = ["1", "2", "3", "4", "escape"], height = 0.075, posText = (0.0, -0.5), posImage = (0.0, 0.5), image = "LowDLowR.png")
                rightAnswerCueTraining = "4"
        
            if cueInstructionsRespons == rightAnswerCueTraining:
                accuracyCueTraining = accuracyCueTraining + 0.25
                message(message_text = "Correct", duration = 1)
            elif cueInstructionsRespons != rightAnswerCueTraining:
                message(message_text = "Incorrect", duration = 1)
        
            # to escape loop 
            if cueInstructionsRespons == "escape":
                cueTrainingCompleteCheck = 1
                break
        
        if accuracyCueTraining == 1:
            cueInstructionsRespons = instruct(image = "instructionsCueTrainingFinish.png")
            cueTrainingCompleteCheck = 1
            break
        else: # display message that they have to take the training again if accuracy <1
            cueInstructionsRespons = instruct(image = "instructionsTrainingFail.png")
        
        # to escape loop 
        if cueInstructionsRespons == "escape":
            cueTrainingCompleteCheck = 1
            break

# let them know the experiment will start for real
message(message_text = "Nu zullen we starten met het experiment.\n\n" +
                    "Druk op 'rechts' om verder te gaan.", response_key = "right")

# display trials
should_recal = True
for b in range(nBlocks):
    
    # reset the task type
    TaskType = "None"
    
    # deduce the task type
    TaskType = TaskOrder[b]
    
    # TRIGGERs block break
    if ET:
        eyelink.sendMessage(break_start_msg + str(b))
        eyelink.setOfflineMode()
    
    # display the trials
    if TaskType == "Stroop":
        
        # randomly "shuffling" the list made earlier to create the different, random, stimuli
        randomColorWordList = random.sample(randomList, 40)
        randomFontColorList = random.sample(randomList, 40)
        
        for i in range (nTrials):
            
            # perform calibration if first trial of block
            if ET and i == 0:
                should_recal = True

            # recalibrate if appropriate
            if ET and should_recal:
                #print("window units = {}".format(win.units))
                win.units = 'pix' # change units for calibration

                # graphics environment for calibration of ET (make sure it can be accessed)
                genv = EyeLinkCoreGraphicsPsychoPy(eyelink, win)

                genv.setTargetSize(24)

                # display calibration msg
                msg = visual.TextStim(win, text = 'Press ENTER to calibrate',
                            color = txt_col, wrapWidth = wwid, height = ht)
                msg.draw()
                win.flip()
                event.waitKeys()

                pylink.openGraphicsEx(genv)
                pylink.msecDelay(100)

                # calibrate the tracker
                eyelink.sendMessage(recal_msg)
                eyelink.doTrackerSetup()
                win.units = 'norm'
                pylink.closeGraphics()

                eyelink.startRecording(1,1,1,1)
                pylink.msecDelay(100)
                should_recal = False
            
            # define Stroop stimulus
            Congruence, RewardType, CorResp = determine_Stroop_stim(i)
        
            # perform the Stroop trial
            Resp, RT = perform_Stroop_trial()
            
            # save data
            save_data(b, i, TaskType, Congruence, RewardType, CorResp, Resp, RT)
            
            # determine and save reward
            determine_reward(b, i)
            
            # escape from the trial loop
            if Resp == "escape" or Resp == "tab":
                break
                
        # escape from the block loop
        if Resp == "escape":
            break
    
    elif TaskType == "RDK":
        
        # randomly "shuffeling" the list made earlier to create the different, random, stimuli
        randomDistractorColorList = random.sample(randomList, 40)
        randomTargetDirectionList = random.sample(randomList, 40)
        randomDistractorDirectionList = random.sample(randomList, 40)
        
        for i in range (nTrials):

            # perform calibration if first trial of block
            if ET and i == 0:
                should_recal = True

            # recalibrate if appropriate
            if ET and should_recal:
                #print("window units = {}".format(win.units))
                win.units = 'pix' # change units for calibration

                # graphics environment for calibration of ET (make sure it can be accessed)
                genv = EyeLinkCoreGraphicsPsychoPy(eyelink, win)

                genv.setTargetSize(24)

                # display calibration msg
                msg = visual.TextStim(win, text = 'Press ENTER to calibrate',
                            color = txt_col, wrapWidth = wwid, height = ht)
                msg.draw()
                win.flip()
                event.waitKeys()

                pylink.openGraphicsEx(genv)
                pylink.msecDelay(100)

                # calibrate the tracker
                eyelink.sendMessage(recal_msg)
                eyelink.doTrackerSetup()
                win.units = 'norm'
                pylink.closeGraphics()

                eyelink.startRecording(1,1,1,1)
                pylink.msecDelay(100)
                should_recal = False

            # define RDM stimulus
            Congruence, RewardType, CorResp = determine_RDK_stim(i)
        
            # perform the RDM trial
            Resp, RT = perform_RDK_trial()
            
            # save data
            save_data(b, i, TaskType, Congruence, RewardType, CorResp, Resp, RT)
            
            # determine and save reward
            determine_reward(b, i)
            
            # escape from the trial loop
            if Resp == "escape" or Resp == "tab":
                break
        
        # escape from the block loop
        if Resp == "escape":
            break
    #determine and display the block feedback (accuracy and amount of correct high and low reward trials)
    feedback(b)

    # display the text for the break
    if TaskType == "Stroop":
        message(message_text = BreakTextStroop, response_key = "right")
    elif TaskType == "RDK":
         message(message_text = BreakTextRDK, response_key = "right")

# make a final reward float
finalReward = float(0)

# determine the final reward
for b in range(nBlocks):
    randomRewardNumber = random.randint(1, nTrials)
    trialNumber = (b * nTrials) + randomRewardNumber
    print(trialNumber)
    print(trials[trialNumber, 11])
    finalReward = finalReward + float(trials[trialNumber, 11])
    
print(finalReward)

# display the final reward message
rewardText = (  "Dit is het einde van het experiment.\n\n" +
                "Je uiteindelijke beloning is de som van " + str(nBlocks) + " willekeurige trials, één per blok.\n" +
                "Je finale belong is € " + str(finalReward) + " .\n\n"
                "Druk op 'rechts' om verder te gaan.")
    
message(message_text = rewardText, response_key = "right")

# empty keys array
keys = kb.getKeys(clear = True)

# display the goodbye message
messageOnSCreen.text = goodbyeText
messageOnSCreen.draw()
win.flip()

# wait for esc key to finish experiment
keys = kb.waitKeys(keyList = ["escape", "tab", "w"], maxWait = 10)

# close up eyetracker (transfer file)
if ET:
    eyelink = pylink.getEYELINK()
    eyelink.stopRecording()

    eyelink.sendMessage(expt_end_msg)

    eyelink.setOfflineMode()
    pylink.msecDelay(100)
    eyelink.closeDataFile()

    txt = 'EDF data is being transferred to host PC...'
    edfTransfer = visual.TextStim(win, text = txt, color = txt_col)
    edfTransfer.draw()
    win.flip()
    pylink.msecDelay(500)

    results_folder = 'data'
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    session_folder = os.path.join(results_folder, 'ET')
    if not os.path.exists(session_folder):
        os.makedirs(session_folder)

    local_edf = os.path.join(session_folder, str(participant) + '.EDF')

    ### NOTE: this isn't working on the eyelink computer since the new
    # psychopy update (2022.x.x) so have to manually copy the file from the
    # eyelink pc
    #eyelink.receiveDataFile(ET_f_name, 'data', + os.sep + ET_f_name)
    #try:
        #print(eyelink)
        #ET_f_name = 'JE_98.EDF'
        #eyelink.receiveDataFile(ET_f_name, 'josh_test.EDF')
        #eyelink.receiveDataFile(ET_f_name, session_folder)
    #except RuntimeError as error:
    #        print('ERROR:', error)

    eyelink.close()
    print('eyelink.close() line')

# convert trials matrix into a dataframe
df = pandas.DataFrame(trials)

# rename the collums of the df
df.columns = ['Subject', 'Gender', 'Age', 'Handedness', 'TaskType', 'Congruence', 'RewardType', 'CorResp', 'Resp', 'Accuracy', 'RT', 'thisTrialReward']

# Check whether the specified path exists or not
path = "ThesisDataSus"
isExist = os.path.exists(path)
if not isExist:
   # Create a new directory because it does not exist
   os.makedirs(path)

# save to csv file
filepath = 'ThesisDataSus/' + 'Participant' + str(info["Participant nummer"]) + '.csv'

df.to_csv(filepath, index = False)

# close up eyetracker (transfer file)
if ET:

    eyelink = pylink.getEYELINK()
    eyelink.stopRecording()

    eyelink.sendMessage(expt_end_msg)

    eyelink.setOfflineMode()
    pylink.msecDelay(100)
    eyelink.closeDataFile()

    txt = 'EDF data is being transferred to host PC...'
    edfTransfer = visual.TextStim(win, text = txt, color = txt_col)
    edfTransfer.draw()
    win.flip()
    pylink.msecDelay(500)

    results_folder = 'data'
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    session_folder = os.path.join(results_folder, 'ET')
    if not os.path.exists(session_folder):
        os.makedirs(session_folder)

    local_edf = os.path.join(session_folder, ID + '.EDF')

    ### NOTE: this isn't working on the eyelink computer since the new
    # psychopy update (2022.x.x) so have to manually copy the file from the
    # eyelink pc
    #eyelink.receiveDataFile(ET_f_name, 'data', + os.sep + ET_f_name)
    #try:
        #print(eyelink)
        #ET_f_name = 'JE_98.EDF'
        #eyelink.receiveDataFile(ET_f_name, 'josh_test.EDF')
        #eyelink.receiveDataFile(ET_f_name, session_folder)
    #except RuntimeError as error:
    #        print('ERROR:', error)

    eyelink.close()
    print('eyelink.close() line')

# close the experiment window
win.close()
core.quit()