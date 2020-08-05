from machine import Pin
import time

_PHASE1 = 26
_PHASE2 = 18
_PHASE3 = 19
_PHASE4 = 23

class steppingMotor:
    SINGLE_PHASE_FORWARD  = 0
    SINGLE_PHASE_BACKWARD = 1
    DOUBLE_PHASE_FORWARD  = 2
    DOUBLE_PHASE_BACKWARD = 3
    HALF_STEP_FORWARD     = 4
    HALF_STEP_BACKWARD    = 5
    
    def __init__(self,p1=_PHASE1,p2=_PHASE2,p3=_PHASE3,p4=_PHASE4):
        self.phaseTable=[Pin(p1,Pin.OUT),
                         Pin(p2,Pin.OUT),
                         Pin(p3,Pin.OUT),
                         Pin(p4,Pin.OUT)]

        self.singlePhaseForwardSequence= [[1,0,0,0],
                                          [0,1,0,0],
                                          [0,0,1,0],
                                          [0,0,0,1]]
        
        self.singlePhaseBackwardSequence=[[0,0,0,1],
                                          [0,0,1,0],
                                          [0,1,0,0],
                                          [1,0,0,0]]
        
        self.doublePhaseForwardSequence= [[1,1,0,0],
                                          [0,1,1,0],
                                          [0,0,1,1],
                                          [1,0,0,1]]
        
        self.doublePhaseBackwardSequence=[[1,0,0,1],
                                          [0,0,1,1],
                                          [0,1,1,0],
                                          [1,1,0,0]]
        
        self.halfStepForwardSequence=    [[1,0,0,0],
                                          [1,1,0,0],
                                          [0,1,0,0],
                                          [0,1,1,0],
                                          [0,0,1,0],
                                          [0,0,1,1],
                                          [0,0,0,1],                   
                                          [1,0,0,1]];

        self.halfStepBackwardSequence=   [[1,0,0,1],
                                          [0,0,0,1],
                                          [0,0,1,1],
                                          [0,0,1,0],
                                          [0,1,1,0],
                                          [0,1,0,0],
                                          [1,1,0,0],                   
                                          [1,0,0,0]];
        self.modeTable = {
            self.SINGLE_PHASE_FORWARD: self.singlePhaseForwardSequence,
            self.SINGLE_PHASE_BACKWARD:self.singlePhaseBackwardSequence,
            self.DOUBLE_PHASE_FORWARD: self.doublePhaseForwardSequence,
            self.DOUBLE_PHASE_BACKWARD:self.doublePhaseBackwardSequence,
            self.HALF_STEP_FORWARD: self.halfStepForwardSequence,
            self.HALF_STEP_BACKWARD: self.halfStepBackwardSequence
            }
        
        self.mode = self.SINGLE_PHASE_FORWARD # default stepping mode
        self.waitBetweenSteps = 2        # wait in ms
        
    def move(self,noOfSteps):
        steppingTable = self.modeTable[self.mode]
        if self.mode == self.HALF_STEP_FORWARD or self.mode == self.HALF_STEP_BACKWARD:
            fullCycle=8
        else:
            fullCycle=4
        cycles = noOfSteps/fullCycle # no of full cycles
        # do the full cycles
        for k in range(cycles):
            for i in range(len(steppingTable)):
                for j in range(4):
                    self.phaseTable[j].value(steppingTable[i][j])
                    time.sleep_ms(self.waitBetweenSteps)
        # do the remaining steps
        for i in range(noOfSteps%fullCycle):            
            for j in range(4):
                   self.phaseTable[j].value(steppingTable[i][j])
                   time.sleep_ms(self.waitBetweenSteps)
                   
    def clrAll(self):
        for j in range(4):
            self.phaseTable[j].value(0)

    def stepMode(self,mode=None):
        if mode == None:
            return self.mode
        if mode < self.SINGLE_PHASE_FORWARD or mode > self.HALF_STEP_BACKWARD:
            raise ValueError('Illegal mode')
        else:
            self.mode = mode
    
    def waitAfterSteps(self,ms_wait=None):
        if ms_wait == None:
            return self.waitBetweenSteps
        if ms_wait < 2 or ms_wait > 1000:
            raise ValueError('Wait must be between 2 and 1000 ms')
        else:
            self.waitBetweenSteps = ms_wait
