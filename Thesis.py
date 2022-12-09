# experiment code file for thesis 'WHEN DOES COGNITIVE EFFORT PAY OFF? ASSESSING TASK-DEPENDENT COGNITIVE EFFORT ALLOCATION VIA PUPIL DILATION'
# written by Sus Geeraerts

# import modules
from __future__ import division, print_function
from psychopy.hardware import keyboard
from psychopy import visual, event, core, gui
import time, numpy, random, pandas

# create a dialog box
info = {"Participant number":0, "Participant name":"Unknown", "Gender":["male", "female", "X"],"Age":0, "Handedness":["right", "left", "ambidextrous"]}
infoDlg = gui.DlgFromDict(dictionary=info, title="Cognitive Effort Experiment")
if infoDlg.OK:  # this will be True (user hit OK) or False (cancelled)
    print(info)
else:
    print("User Cancelled")

### Initializing ###
# initialize the window
win = visual.Window(fullscr = True, units = "norm", winType='pyglet')

# initialize the variables
nBlocks     = 4     ########## SHOULD BE 8 ########## 
nPrac       = 5     ########## IS THIS OK AMOUNT? ###
nTrials     = 5     ########## SHOULD BE 40 #########
participant = info["Participant number"]

# initialize string that keeps track of the current condition
currentCondition = "Test"

# initialize coutner for reward
rewardCounter = 0

# initialize the task Instructions
TaskInstructionsStart = (   "In this experiment you will make two different tasks. A Stroop task and a RDK task.\n" +
                            "The exact instructions for each task will be explained later.\n\n" +
                            "Each block only consists of one type of task and\n" +
                            "it will be clearly indicated when a block is over and\n" +
                            "what task type the next block will be.\n\n" +
                            "First we will explain and practice these two tasks.\n\n" +
                            "Press the space bar to continue.")

StroopInstructions = (  "These are the instructions for the Stroop Task.\n\n" +
                        "In this task you will see color words (“red”, “blue”, “green” and “yellow”)\n" +
                        "presented in a random ink color (red, blue, green and yellow color).\n\n" +
                        "You have to respond to the meaning of the written word and\n" +
                        "ignore the ink color of the stimulus.\n\n" +
                        "You can use the following four response buttons (from left to right;\n" +
                        "use the index and middle finger of your left and right hand):" +
                        "“d”,“f”,“j” and “k”.\n\n" +
                        "If the written word is red, press the leftmost button “d”.\n" +
                        "If it’s blue, press “f”.\n" +
                        "If it’s green, press “j”.\n" +
                        "If it’s yellow, press “k”.\n\n" +
                        "Answer as quickly as possible, but also try to avoid mistakes.\n" +
                        "By all means ignore the ink color, you should only respond to the meaning of the words.\n\n" +
                        "Any questions?\n\nPress the space bar to continue.")

StroopTrainingInstructions = (  "First we will practice the Stroop Task.\n\n" +
                                "You will do 10 practice trials until you have a 90% accuracy.\n\n" +
                                "Press the space bar to continue.")

RDKInstructions = (     "These are the instructions for the RDK Task.\n\n" +
                        "In this task you will see a number of dots moving across the screen.\n\n" +
                        "These dots will be white and a random color (red, blue, green and yellow color).\n\n" +
                        "You have to respond to the direction of the white dots and /n" +
                        "ignore the direction of the collered dots.\n\n" + 
                        "You can use the following four response buttons (from left to right;\n" + 
                        "use the index and middle finger of your left and right hand):" + 
                        "“d”,“f”,“j” and “k”.\n\n" + 
                        "If the direction of the white dots is left, press the leftmost button “d”.\n" + 
                        "If it’s up, press “f”.\n" +
                        "If it’s down, press “j”.\n" +
                        "If it’s right, press “k”.\n\n" +
                        "Answer as quickly as possible, but also try to avoid mistakes.\n\n" +
                        "Any questions?\n\nPress the space bar to continue.")

RDKTrainingInstructions = ( "Now we will practice the RDK Task.\n\n" +
                            "You will do 10 practice trials until you have a 90% accuracy.\n\n" +
                            "Press the space bar to continue.")

CueInstructions = ( "Before each trial in the experiment you will see on of four possible ques.\n\n" +
                    "The cue is a thermometer. And it can either indicate a high or low temperature. " +
                    "The high temperature means that the following trial will be hard and require you to think more. " +
                    "A low temperature means the next trial will be easy.\n\n" +
                    "The cue can aslo have an orange or a purple color. " +
                    "The orange color means that the reward for succesfully completing the next trial is high. " +
                    "The purple color means that the reward will be low.\n\n" +
                    "Any questions?\n\nPress the space bar to continue.")

CueTrainingInstructions = ( "We will now practice these cues to make sure you understand them.")

BreakTextStroop = ( "This was the end of this Block\n\n" +
                    "You can take a small break if you want\n\n" +
                    "The next block will be a RDK block\n\n"
                    "Press the space bar to continue.")

BreakTextRDK = (    "This was the end of this Block\n\n" +
                    "You can take a small break if you want\n\n" +
                    "The next block will be a Stroop block\n\n"
                    "Press the space bar to continue.")

# creating list of numbers from 1 to 40 to create conditions later
randomList=range(1,41)

# initialize a clock to measure the RT
my_clock = core.Clock()

# initialize keyboard
kb = keyboard.Keyboard()

##Initializing stuff to allow the storing of data
# retrieve the participant info
Subject    = numpy.repeat(info["Participant number"], nTrials)
Gender     = numpy.repeat("".join(info["Gender"]), len(Subject))
Age        = numpy.repeat(info["Age"], len(Subject))
Handedness = numpy.repeat("".join(info["Handedness"]), len(Subject))

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
thermometerCue  = visual.ImageStim(win, image = "HighDHighR.jpg")
# for Stroop
StroopStim     = visual.TextStim(win, text = "red", color = "blue")
# and for RDK
dotPatchTarget = visual.DotStim(win, color=(1, 1, 1), dir=0 ,
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
def message(message_text = "", response_key = "space", duration = 0, height = None, pos = (0.0, 0.0), color = "white"):
    
    messageOnSCreen.text    = message_text
    messageOnSCreen.height  = height
    messageOnSCreen.pos     = pos
    messageOnSCreen.color   = color
    
    messageOnSCreen.draw()
    win.flip()
    if duration == 0:
        event.waitKeys(keyList = response_key)
    else:
        time.sleep(duration)

# make a function to display an image
def showImage(response_key = "space", duration = 0):
    
    thermometerCue.draw()
    win.flip()
    if duration == 0:
        event.waitKeys(keyList = response_key)
    else:
        time.sleep(duration)

# make a function to define word and font color for Stroop Task
def determine_Stroop_stim(x):
    
    # define word color
    randomColorWord = int(randomColorWordList[x])
        
    if randomColorWord > 0 and randomColorWord < 11:
        StroopStim.text = "red" # displays the word 'red'
    elif randomColorWord > 10 and randomColorWord < 21:
        StroopStim.text = "green" # displays the word 'green'
    elif randomColorWord > 20 and randomColorWord < 31:
        StroopStim.text = "blue" # displays the word 'blue'
    elif randomColorWord > 30 and randomColorWord < 41:
        StroopStim.text = "yellow" # displays the word 'yellow'
        
    #define font color (congruent or incongruent = low or high demand)
    #and also determine high or low reward
    #this will then also determine the cue image
    randomFontColor = int(randomFontColorList[x])
        
    if  randomFontColor > 0 and  randomFontColor < 11:
        #low demand and low reward condition
        currentCondition = "LowDLowR"
        thermometerCue.image = "LowDLowR.jpg"
        Congruence = "Congruent"
        RewardType = "Low"
        StroopStim.color = StroopStim.text # = congruent
        global CorResp
        if StroopStim.color == "red":
            CorResp = "d"
        elif StroopStim.color == "blue":
            CorResp = "f"
        elif StroopStim.color == "green":
            CorResp = "j"
        elif StroopStim.color == "yellow":
            CorResp = "k"

    elif randomFontColor > 10 and  randomFontColor < 21:
        #low demand and high reward condition
        currentCondition = "LowDHighR"
        thermometerCue.image = "LowDHighR.jpg"
        Congruence = "Congruent"
        RewardType = "High"
        StroopStim.color = StroopStim.text # = congruent
        if StroopStim.color == "red":
            CorResp = "d"
        elif StroopStim.color == "blue":
            CorResp = "f"
        elif StroopStim.color == "green":
            CorResp = "j"
        elif StroopStim.color == "yellow":
            CorResp = "k"

    elif  randomFontColor > 20 and  randomFontColor < 31:
        #high demand and low reward condition
        currentCondition = "HighDLowR"
        thermometerCue.image = "HighDLowR.jpg"
        Congruence = "Incongruent"
        RewardType = "Low"
        c = random.randint(1, 3) # select incongruent color
        if StroopStim.text == "red":
            CorResp = "d"
            if c == 1:
                StroopStim.color = "green"
            elif c == 2:
                StroopStim.color = "blue"
            elif c == 3:
                StroopStim.color = "yellow"
        elif StroopStim.text == "green":
            CorResp = "j"
            if c == 1:
                StroopStim.color = "red"
            elif c == 2:
                StroopStim.color = "blue"
            elif c == 3:
                StroopStim.color = "yellow"
        elif StroopStim.text == "blue":
            CorResp = "f"
            if c == 1:
                StroopStim.color = "red"
            elif c == 2:
                StroopStim.color = "green"
            elif c == 3:
                StroopStim.color = "yellow"
        elif StroopStim.text == "yellow":
            CorResp = "k"
            if c == 1:
                StroopStim.color = "red"
            elif c == 2:
                StroopStim.color = "green"
            elif c == 3:
                StroopStim.color = "blue"

    elif  randomFontColor > 30 and  randomFontColor < 41:
        #high demand and high reward condition
        currentCondition = "HighDHighR"
        thermometerCue.image = "HighDHighR.jpg"
        Congruence = "Incongruent"
        RewardType = "Low"
        c = random.randint(1, 3) # select incongruent color
        if StroopStim.text == "red":
            CorResp = "d"
            if c == 1:
                StroopStim.color = "green"
            elif c == 2:
                StroopStim.color = "blue"
            elif c == 3:
                StroopStim.color = "yellow"
        elif StroopStim.text == "green":
            CorResp = "j"
            if c == 1:
                StroopStim.color = "red"
            elif c == 2:
                StroopStim.color = "blue"
            elif c == 3:
                StroopStim.color = "yellow"
        elif StroopStim.text == "blue":
            CorResp = "f"
            if c == 1:
                StroopStim.color = "red"
            elif c == 2:
                StroopStim.color = "green"
            elif c == 3:
                StroopStim.color = "yellow"
        elif StroopStim.text == "yellow":
            CorResp = "k"
            if c == 1:
                StroopStim.color = "red"
            elif c == 2:
                StroopStim.color = "green"
            elif c == 3:
                StroopStim.color = "blue"
    
    return Congruence, RewardType, CorResp

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
        thermometerCue.image = "LowDLowR.jpg"
        Congruence = "Congruent"
        RewardType = "Low"
        dotPatchDistractor.dir = dotPatchTarget.dir #=congruent
        
    elif randomDistractorDirection > 10 and  randomDistractorDirection < 21:
        #low demand and high reward condition
        currentCondition = "LowDHighR"
        thermometerCue.image = "LowDHighR.jpg"
        Congruence = "Congruent"
        RewardType = "High"
        dotPatchDistractor.dir = dotPatchTarget.dir #=congruent
        
    elif  randomDistractorDirection > 20 and  randomDistractorDirection < 31:
        #high demand and low reward condition
        currentCondition = "HighDLowR"
        thermometerCue.image = "HighDLowR.jpg"
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
        thermometerCue.image = "HighDHighR.jpg"
        Congruence = "Incongruent"
        RewardType = "High"
        d = random.randint(1, 2) # select incongruent direction
        if d == 1:
            dotPatchDistractor.dir = dotPatchTarget.dir + 90 #=incongruent
        elif d == 2:
            dotPatchDistractor.dir = dotPatchTarget.dir + 180 #=incongruent
        
    return Congruence, RewardType, CorResp

# make a function for performing a Stroop trial
def perform_Stroop_trial():

    # start with a fixation cross
    message(message_text = "+", duration = 0.25)
    
    # present the thermometer cue
    showImage(duration = 1)
    
    # show fixation cross again
    message(message_text = "+", duration = 0.25)
    
    # draw the stimulus on the back buffer
    StroopStim.draw()
    
    # clear the keyboard input
    event.clearEvents(eventType = "keyboard")
    
    # display the stimulus on the screen
    win.flip()
    
    # Now that the stimulus is on the screen, reset the clock
    my_clock.reset()
    
    # Wait for the response
    keys = event.waitKeys(keyList = ["d","f","j","k","escape","tab"], maxWait = 1)
    
    # Register the RT
    RT = my_clock.getTime()
    
    if keys == None:
        keys = [0]
    
    Resp = keys[0]
    
    return Resp, RT

# make a function for performing a RDM trial
def perform_RDK_trial():
    
    # start with a fixation cross
    message(message_text = "+", duration = 0.25)
    
    # present the thermometer cue
    showImage(duration = 1)
    
    # show fixation cross again
    message(message_text = "+", duration = 0.25)
    
    # set RDMCheck to 0 before begining RDM loop
    RDMCheck = 0
    
    # clear the keyboard input
    event.clearEvents(eventType = "keyboard")
    
    # empty keys array
    keys = kb.getKeys(clear = True)
    
    # Reset the clock
    my_clock.reset()
    kb.clock.reset()
    
    # while loop for the RDM stimuli
    # while loop untill buton press or max time
    while RDMCheck == 0:
        dotPatchTarget.draw()
        dotPatchDistractor.draw()
        win.flip()
        keys = kb.getKeys(keyList = ["d","f","j","k","escape","tab"], clear = False)
        timer = my_clock.getTime()
        if keys == [] and timer < 3: #### max time for RDM trial is ???
            RDMCheck = 0
        else:
            RDMCheck = 1
    
    # initialize temporary variables to save response given and RT
    trialResp = ""
    trialRT = 0
    
    # determine the given response and RT
    if keys == []:
        trialResp = "None"
        trialRT = 3 ### see max time per trial
    else:
        for key in keys:
            trialResp = str(key.name)
            trialRT = (key.rt)
    
    return trialResp, trialRT

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
    
    global rewardCounter
    
    # if function to possibly increase reward counter
    if trials[numberSD, 9] == "1":
        if trials[numberSD, 6] == "High":
            possibleReward = 3          ##### What should be the exact amount?
        elif trials[numberSD, 6] == "Low":
            possibleReward = 1          ##### What should be the exact amount?
        
        rewardCounter = rewardCounter + possibleReward

    trials[numberSD, 11] = rewardCounter
    
#make a function to determine and display the block feedback
def feedback(bFB):
    
    # Calculate mean accuracy across block
    blockAccuracyCounter = 0
    
    for i in range (nTrials):
        trialNumber = (bFB * nTrials) + i
        blockAccuracyCounter = blockAccuracyCounter + int(trials[trialNumber, 9])
    
    blockAccuracy = 100 * (blockAccuracyCounter / nTrials)
    
    # Calculate reward amount gained across block
    totalRewardLastTrialLastBlock = int(trials[(bFB * nTrials) - 1, 11])
    totalRewardLastTrialThisBlock = int(trials[(bFB * nTrials) + (nTrials - 1), 11])
    rewardThisBlock = totalRewardLastTrialThisBlock - totalRewardLastTrialLastBlock
    
    feedbackText = ("This is the end of this block. \n\n" +
                    "In this block you had an accuracy of " + str(blockAccuracy) + "%.\n" +
                    "You earned a reward of €" + str(rewardThisBlock) + " in this block.\n\n" +
                    "Press the spacebar to start the next block.")
    
    message(message_text = feedbackText, response_key = "space")

# determine task order 
if participant%2 != 0:
    # Participants with an odd number get the Stroop Task first
    TaskOrder = ["Stroop","RDK","Stroop","RDK","Stroop","RDK","Stroop","RDK"]
    
else:
    # participants with an even number get the RDM Task first
    TaskOrder = ["RDK","Stroop","RDK","Stroop","RDK","Stroop","RDK","Stroop"]

### Actual experiment ###
# display the welcome message
message(message_text = "Welcome " + info["Participant name"] + "!\n\nPress the space bar to continue.", response_key = "space")

# display introduction and practice trials
# display general instructions
message(message_text = TaskInstructionsStart, response_key = "space")

# display Stroop instructions
message(message_text = StroopInstructions, response_key = "space", height = 0.05)

## display Stroop training instructions
#message(message_text = StroopTrainingInstructions, response_key = "space")

# 5(?) Stroop practice trials, repeat if accuracy < 0.8

# display RDK instructions
message(message_text = RDKInstructions, response_key = "space", height = 0.05)

## display RDK training instructions
#message(message_text = RDKTrainingInstructions, response_key = "space")

# 5(?) RDK practice trials, repeat if accuracy < 0.8

# display Cue instructions
message(message_text = CueInstructions, response_key = "space", height = 0.05)

## display Cue training instructions
#message(message_text = CueTrainingInstructions, response_key = "space")

# display the 4 different cue's and let them answer what it is
#repeat if accuracy < 1.0

# let them know the experiment will start for real
message(message_text =  "Now we will start with the experiment.\n\n" +
                        "Press the space bar to continue.", response_key = "space")

# display trials
for b in range(nBlocks):
    
    # reset the task type
    TaskType = "None"
    
    # deduce the task type
    TaskType = TaskOrder[b]
    
    # display the trials
    if TaskType == "Stroop":
        
        # randomly "shuffeling" the list made earlier to create the different, random, stimuli
        randomColorWordList = random.sample(randomList, 40)
        randomFontColorList = random.sample(randomList, 40)
        
        for i in range (nTrials):
            
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
    #determine and display the block feedback (accuracy and reward gained)
    feedback(b)

    # display the text for the break
    if TaskType == "Stroop":
        message(message_text = BreakTextStroop, response_key = "space")
    elif TaskType == "RDK":
         message(message_text = BreakTextRDK, response_key = "space")
    
# display the goodbye message
message(message_text = "Thank you for participating \n\n" + 
                       "Please notify the experimenter that you are finished", duration = 1)
###########Should not finish after 1 s but after button press that only experimenter knows or esc

# convert trials matrix into a dataframe
df = pandas.DataFrame(trials)

# rename the collums of the df
df.columns = ['Subject', 'Gender', 'Age', 'Handedness', 'TaskType', 'Congruence', 'RewardType', 'CorResp', 'Resp', 'Accuracy', 'RT', 'TotalReward']

# save to xlsx file
filepath = 'Participant' + str(info["Participant number"]) + '.xlsx'

df.to_excel(filepath, index = False)

# close the experiment window
win.close()
core.quit()