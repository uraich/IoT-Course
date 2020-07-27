from stepper import steppingMotor
stepper = steppingMotor()

print("Moving forward in single phase mode")
stepper.move(400)
    
stepper.stepMode(stepper.SINGLE_PHASE_BACKWARD)
stepper.waitAfterSteps(4)
print("Moving backward in single phase mode and decreasing movement speed by a factor 2")
stepper.move(400)
    
stepper.stepMode(stepper.DOUBLE_PHASE_BACKWARD)
print("Moving backward in double phase mode and coming back to max speed")
stepper.waitAfterSteps(2)
stepper.move(400)
    
print("Moving forward in double phase mode") 
stepper.stepMode(stepper.DOUBLE_PHASE_FORWARD)
stepper.move(400)

print("Moving forward in half step mode") 
stepper.stepMode(stepper.HALF_STEP_FORWARD)
stepper.move(800)

print("Moving backward in half step mode") 
stepper.stepMode(stepper.HALF_STEP_BACKWARD)
stepper.move(800)   

stepper.clrAll()            
