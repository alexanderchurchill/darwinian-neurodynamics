from naoqi import *
import math
import almath
from time import time, sleep

class NaoMotorFunction(ALModule):
  """
  Create a basic motor function instance
  """
  
  def __init__(self,name,ip="ctf.local"):
    ALModule.__init__(self,name)
    self.isRunning=True
    self.motion = ALProxy("ALMotion", ip, 9559)
    self.Body = self.motion.getLimits("Body")
    self.set_stiffness(1.0)


  def set_stiffness(self, val):
         self.motion.setStiffnesses("Body", val)
    
  def rest(self):
         fractionMaxSpeed  = 1.0
         bodyLyingDefaultAngles = [-0.20406389236450195, 0.16256213188171387, 1.5784441232681274,
                                   0.2469320297241211, 0.5199840068817139, -0.052114009857177734,
                                   -1.1029877662658691, 0.1711999773979187, 0.013848066329956055,
                                   0.13503408432006836, 0.0061779022216796875, 0.47856616973876953,
                                   0.9225810170173645, 0.04912996292114258, 0.013848066329956055,
                                   -0.14568805694580078, 0.3021559715270996, -0.09232791513204575,
                                   0.9320058226585388, 0.0031099319458007812, 1.7718119621276855,
                                   -0.13503408432006836, 1.515550136566162, 0.12429594993591309,
                                   1.348344087600708, 0.14719998836517334]
         motorAngles = bodyLyingDefaultAngles
         
         #Check that the specified angles are within limits
         for index,i in enumerate(self.Body):
              if motorAngles[index] < i[0]/2:
                   motorAngles[index] = i[0]/2
              if motorAngles[index] > i[1]/2:
                   motorAngles[index] = i[1]/2
                   
         self.motion.setAngles("Body", motorAngles, fractionMaxSpeed)
         sleep(0.3)

 
  def start(self):
    """Start basic motor function module"""
    try:
        pass
    except:
        pass
   
  def finish(self):
    """module bla"""
    try:
        pass
    except:
        pass
    self.isRunning = False

  def exit(self):
    print "Exit basic motor function module"
    try:
        pass
    except:
        pass
    self.isRunning=False
    ALModule.exit(self)

class NaoMemory(ALModule):
  """Create memoryManagerClass instance"""
  
  def __init__(self,name):
    ALModule.__init__(self,name)
    self.isRunning=True
    self.memory = ALProxy("ALMemory")
    self.motion = ALProxy("ALMotion")

    #Get the position of robot top camera and write it to sensor Memory
    name            = "CameraTop"
    space           = motion.FRAME_WORLD
    useSensorValues = True
    result          = self.motion.getPosition(name, space, useSensorValues)
    print "Position of", name, " in World is:"
    print result
    self.memory.insertData("PositionCamera", result)
    

    #Converts a genotype number to a data name in ALMemory 
    self.numToSensor = {1: "Device/SubDeviceList/ChestBoard/Button/Sensor/Value",
                   2: "Device/SubDeviceList/LFoot/Bumper/Left/Sensor/Value",
                   3: "Device/SubDeviceList/LFoot/Bumper/Right/Sensor/Value",
                   4: "Device/SubDeviceList/RFoot/Bumper/Left/Sensor/Value",
                   5: "Device/SubDeviceList/RFoot/Bumper/Right/Sensor/Value",
                   6: "Device/SubDeviceList/HeadPitch/Position/Actuator/Value",
                   7: "Device/SubDeviceList/HeadYaw/Position/Actuator/Value",
                   8: "Device/SubDeviceList/LAnklePitch/Position/Actuator/Value",
                   9: "Device/SubDeviceList/LAnkleRoll/Position/Actuator/Value",
                   10: "Device/SubDeviceList/LElbowRoll/Position/Actuator/Value",
                   11: "Device/SubDeviceList/LElbowYaw/Position/Actuator/Value",
                   12: "Device/SubDeviceList/LHand/Position/Actuator/Value",
                   13: "Device/SubDeviceList/LHipPitch/Position/Actuator/Value",
                   14: "Device/SubDeviceList/LHipRoll/Position/Actuator/Value",
                   15: "Device/SubDeviceList/LHipYawPitch/Position/Actuator/Value",
                   16: "Device/SubDeviceList/LKneePitch/Position/Actuator/Value",
                   17: "Device/SubDeviceList/LShoulderPitch/Position/Actuator/Value",
                   18: "Device/SubDeviceList/LShoulderRoll/Position/Actuator/Value",
                   19: "Device/SubDeviceList/LWristYaw/Position/Actuator/Value",
                   20: "Device/SubDeviceList/RAnklePitch/Position/Actuator/Value",
                   21: "Device/SubDeviceList/RAnkleRoll/Position/Actuator/Value",
                   22: "Device/SubDeviceList/RElbowRoll/Position/Actuator/Value",
                   23: "Device/SubDeviceList/RElbowYaw/Position/Actuator/Value",
                   24: "Device/SubDeviceList/RHand/Position/Actuator/Value",
                   25: "Device/SubDeviceList/RHipPitch/Position/Actuator/Value",
                   26: "Device/SubDeviceList/RHipRoll/Position/Actuator/Value",
                   27: "Device/SubDeviceList/RHipRoll/Position/Actuator/Value",
                   28: "Device/SubDeviceList/RKneePitch/Position/Actuator/Value",
                   29: "Device/SubDeviceList/RShoulderPitch/Position/Actuator/Value",
                   30: "Device/SubDeviceList/RShoulderRoll/Position/Actuator/Value",
                   31: "Device/SubDeviceList/RWristYaw/Position/Actuator/Value",
                   32: "Device/SubDeviceList/HeadPitch/Hardness/Actuator/Value",
                   33: "Device/SubDeviceList/HeadYaw/Hardness/Actuator/Value",
                   34: "Device/SubDeviceList/LAnklePitch/Hardness/Actuator/Value",
                   35: "Device/SubDeviceList/LAnkleRoll/Hardness/Actuator/Value",
                   36: "Device/SubDeviceList/LElbowRoll/Hardness/Actuator/Value",
                   37: "Device/SubDeviceList/LElbowYaw/Hardness/Actuator/Value",
                   38: "Device/SubDeviceList/LHand/Hardness/Actuator/Value",
                   39: "Device/SubDeviceList/LHipPitch/Hardness/Actuator/Value",
                   40: "Device/SubDeviceList/LHipRoll/Hardness/Actuator/Value",
                   41: "Device/SubDeviceList/LHipYawPitch/Hardness/Actuator/Value",
                   42: "Device/SubDeviceList/LKneePitch/Hardness/Actuator/Value",
                   43: "Device/SubDeviceList/LShoulderPitch/Hardness/Actuator/Value",
                   44: "Device/SubDeviceList/LShoulderRoll/Hardness/Actuator/Value",
                   45: "Device/SubDeviceList/LWristYaw/Hardness/Actuator/Value",
                   46: "Device/SubDeviceList/RAnklePitch/Hardness/Actuator/Value",
                   47: "Device/SubDeviceList/RAnkleRoll/Hardness/Actuator/Value",
                   48: "Device/SubDeviceList/RElbowRoll/Hardness/Actuator/Value",
                   49: "Device/SubDeviceList/RElbowYaw/Hardness/Actuator/Value",
                   50: "Device/SubDeviceList/RHand/Hardness/Actuator/Value",
                   51: "Device/SubDeviceList/RHipPitch/Hardness/Actuator/Value",
                   52: "Device/SubDeviceList/RHipRoll/Hardness/Actuator/Value",
                   53: "Device/SubDeviceList/RHipRoll/Hardness/Actuator/Value",
                   54: "Device/SubDeviceList/RKneePitch/Hardness/Actuator/Value",
                   55: "Device/SubDeviceList/RShoulderPitch/Hardness/Actuator/Value",
                   56: "Device/SubDeviceList/RShoulderRoll/Hardness/Actuator/Value",
                   57: "Device/SubDeviceList/RWristYaw/Hardness/Actuator/Value",
                   58: "Device/SubDeviceList/HeadPitch/Position/Sensor/Value",
                   59: "Device/SubDeviceList/HeadYaw/Position/Sensor/Value",
                   60: "Device/SubDeviceList/LAnklePitch/Position/Sensor/Value",
                   61: "Device/SubDeviceList/LAnkleRoll/Position/Sensor/Value",
                   62: "Device/SubDeviceList/LElbowRoll/Position/Sensor/Value",
                   63: "Device/SubDeviceList/LElbowYaw/Position/Sensor/Value",
                   64: "Device/SubDeviceList/LHand/Position/Sensor/Value",
                   65: "Device/SubDeviceList/LHipPitch/Position/Sensor/Value",
                   66: "Device/SubDeviceList/LHipRoll/Position/Sensor/Value",
                   67: "Device/SubDeviceList/LHipYawPitch/Position/Sensor/Value",
                   68: "Device/SubDeviceList/LKneePitch/Position/Sensor/Value",
                   69: "Device/SubDeviceList/LShoulderPitch/Position/Sensor/Value",
                   70: "Device/SubDeviceList/LShoulderRoll/Position/Sensor/Value",
                   71: "Device/SubDeviceList/LWristYaw/Position/Sensor/Value",
                   72: "Device/SubDeviceList/RAnklePitch/Position/Sensor/Value",
                   73: "Device/SubDeviceList/RAnkleRoll/Position/Sensor/Value",
                   74: "Device/SubDeviceList/RElbowRoll/Position/Sensor/Value",
                   75: "Device/SubDeviceList/RElbowYaw/Position/Sensor/Value",
                   76: "Device/SubDeviceList/RHand/Position/Sensor/Value",
                   77: "Device/SubDeviceList/RHipPitch/Position/Sensor/Value",
                   78: "Device/SubDeviceList/RHipRoll/Position/Sensor/Value",
                   79: "Device/SubDeviceList/RHipRoll/Position/Sensor/Value",
                   80: "Device/SubDeviceList/RKneePitch/Position/Sensor/Value",
                   81: "Device/SubDeviceList/RShoulderPitch/Position/Sensor/Value",
                   82: "Device/SubDeviceList/RShoulderRoll/Position/Sensor/Value",
                   83: "Device/SubDeviceList/RWristYaw/Position/Sensor/Value",
                   84: "Device/SubDeviceList/HeadPitch/ElectricCurrent/Sensor/Value",
                   85: "Device/SubDeviceList/HeadYaw/ElectricCurrent/Sensor/Value",
                   86: "Device/SubDeviceList/LAnklePitch/ElectricCurrent/Sensor/Value",
                   87: "Device/SubDeviceList/LAnkleRoll/ElectricCurrent/Sensor/Value",
                   88: "Device/SubDeviceList/LElbowRoll/ElectricCurrent/Sensor/Value",
                   89: "Device/SubDeviceList/LElbowYaw/ElectricCurrent/Sensor/Value",
                   90: "Device/SubDeviceList/LHand/ElectricCurrent/Sensor/Value",
                   91: "Device/SubDeviceList/LHipPitch/ElectricCurrent/Sensor/Value",
                   92: "Device/SubDeviceList/LHipRoll/ElectricCurrent/Sensor/Value",
                   93: "Device/SubDeviceList/LHipYawPitch/ElectricCurrent/Sensor/Value",
                   94: "Device/SubDeviceList/LKneePitch/ElectricCurrent/Sensor/Value",
                   95: "Device/SubDeviceList/LShoulderPitch/ElectricCurrent/Sensor/Value",
                   96: "Device/SubDeviceList/LShoulderRoll/ElectricCurrent/Sensor/Value",
                   97: "Device/SubDeviceList/LWristYaw/ElectricCurrent/Sensor/Value",
                   98: "Device/SubDeviceList/RAnklePitch/ElectricCurrent/Sensor/Value",
                   99: "Device/SubDeviceList/RAnkleRoll/ElectricCurrent/Sensor/Value",
                   100: "Device/SubDeviceList/RElbowRoll/ElectricCurrent/Sensor/Value",
                   101: "Device/SubDeviceList/RElbowYaw/ElectricCurrent/Sensor/Value",
                   102: "Device/SubDeviceList/RHand/ElectricCurrent/Sensor/Value",
                   103: "Device/SubDeviceList/RHipPitch/ElectricCurrent/Sensor/Value",
                   104: "Device/SubDeviceList/RHipRoll/ElectricCurrent/Sensor/Value",
                   105: "Device/SubDeviceList/RHipRoll/ElectricCurrent/Sensor/Value",
                   106: "Device/SubDeviceList/RKneePitch/ElectricCurrent/Sensor/Value",
                   107: "Device/SubDeviceList/RShoulderPitch/ElectricCurrent/Sensor/Value",
                   108: "Device/SubDeviceList/RShoulderRoll/ElectricCurrent/Sensor/Value",
                   109: "Device/SubDeviceList/RWristYaw/ElectricCurrent/Sensor/Value",
                   110: "Device/SubDeviceList/HeadPitch/Temperature/Sensor/Value",
                   111: "Device/SubDeviceList/HeadYaw/Temperature/Sensor/Value",
                   112: "Device/SubDeviceList/LAnklePitch/Temperature/Sensor/Value",
                   113: "Device/SubDeviceList/LAnkleRoll/Temperature/Sensor/Value",
                   114: "Device/SubDeviceList/LElbowRoll/Temperature/Sensor/Value",
                   115: "Device/SubDeviceList/LElbowYaw/Temperature/Sensor/Value",
                   116: "Device/SubDeviceList/LHand/Temperature/Sensor/Value",
                   117: "Device/SubDeviceList/LHipPitch/Temperature/Sensor/Value",
                   118: "Device/SubDeviceList/LHipRoll/Temperature/Sensor/Value",
                   119: "Device/SubDeviceList/LHipYawPitch/Temperature/Sensor/Value",
                   120: "Device/SubDeviceList/LKneePitch/Temperature/Sensor/Value",
                   121: "Device/SubDeviceList/LShoulderPitch/Temperature/Sensor/Value",
                   122: "Device/SubDeviceList/LShoulderRoll/Temperature/Sensor/Value",
                   123: "Device/SubDeviceList/LWristYaw/Temperature/Sensor/Value",
                   124: "Device/SubDeviceList/RAnklePitch/Temperature/Sensor/Value",
                   125: "Device/SubDeviceList/RAnkleRoll/Temperature/Sensor/Value",
                   126: "Device/SubDeviceList/RElbowRoll/Temperature/Sensor/Value",
                   127: "Device/SubDeviceList/RElbowYaw/Temperature/Sensor/Value",
                   128: "Device/SubDeviceList/RHand/Temperature/Sensor/Value",
                   129: "Device/SubDeviceList/RHipPitch/Temperature/Sensor/Value",
                   130: "Device/SubDeviceList/RHipRoll/Temperature/Sensor/Value",
                   131: "Device/SubDeviceList/RHipRoll/Temperature/Sensor/Value",
                   132: "Device/SubDeviceList/RKneePitch/Temperature/Sensor/Value",
                   133: "Device/SubDeviceList/RShoulderPitch/Temperature/Sensor/Value",
                   134: "Device/SubDeviceList/RShoulderRoll/Temperature/Sensor/Value",
                   135: "Device/SubDeviceList/RWristYaw/Temperature/Sensor/Value",
                   136: "Device/SubDeviceList/US/Left/Sensor/Value",
                   137: "Device/SubDeviceList/US/Right/Sensor/Value",
                   138: "Device/SubDeviceList/InertialSensor/GyroscopeX/Sensor/Value",
                   139: "Device/SubDeviceList/InertialSensor/GyroscopeY/Sensor/Value",
                   140: "Device/SubDeviceList/InertialSensor/GyroscopeZ/Sensor/Value",
                   141: "Device/SubDeviceList/InertialSensor/AccelerometerX/Sensor/Value",
                   142: "Device/SubDeviceList/InertialSensor/AccelerometerY/Sensor/Value",
                   143: "Device/SubDeviceList/InertialSensor/AccelerometerZ/Sensor/Value",
                   144: "Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value",
                   145: "Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value",
                   146: "Device/SubDeviceList/LFoot/FSR/FrontLeft/Sensor/Value",
                   147: "Device/SubDeviceList/LFoot/FSR/FrontRight/Sensor/Value",
                   148: "Device/SubDeviceList/LFoot/FSR/RearLeft/Sensor/Value",
                   149: "Device/SubDeviceList/LFoot/FSR/RearRight/Sensor/Value",
                   150: "Device/SubDeviceList/LFoot/FSR/TotalWeight/Sensor/Value",
                   151: "Device/SubDeviceList/RFoot/FSR/FrontLeft/Sensor/Value",
                   152: "Device/SubDeviceList/RFoot/FSR/FrontRight/Sensor/Value",
                   153: "Device/SubDeviceList/RFoot/FSR/RearLeft/Sensor/Value",
                   154: "Device/SubDeviceList/RFoot/FSR/RearRight/Sensor/Value",
                   155: "Device/SubDeviceList/RFoot/FSR/TotalWeight/Sensor/Value",
                   156: "Device/SubDeviceList/LFoot/FSR/CenterOfPressure/X/Sensor/Value",
                   157: "Device/SubDeviceList/LFoot/FSR/CenterOfPressure/Y/Sensor/Value",
                   158: "Device/SubDeviceList/RFoot/FSR/CenterOfPressure/X/Sensor/Value",
                   159: "Device/SubDeviceList/RFoot/FSR/CenterOfPressure/Y/Sensor/Value",
                   160: "Device/SubDeviceList/Head/Touch/Front/Sensor/Value",
                   161: "Device/SubDeviceList/Head/Touch/Middle/Sensor/Value",
                   162: "Device/SubDeviceList/Head/Touch/Rear/Sensor/Value",
                   163: "Device/SubDeviceList/LHand/Touch/Back/Sensor/Value",
                   164: "Device/SubDeviceList/LHand/Touch/Left/Sensor/Value",
                   165: "Device/SubDeviceList/LHand/Touch/Right/Sensor/Value",
                   166: "Device/SubDeviceList/RHand/Touch/Back/Sensor/Value",
                   167: "Device/SubDeviceList/RHand/Touch/Left/Sensor/Value",
                   168: "Device/SubDeviceList/RHand/Touch/Right/Sensor/Value",
                   169: "footContact",
                   170: "leftFootContact",
                   171: "rightFootContact",
                   172: "leftFootTotalWeight",
                   173: "rightFootTotalWeight",
                   174: "BodyStiffnessChanged",
                   175: "RightBumperPressed",
                   176: "LeftBumperPressed",
                   177: "ChestButtonPressed",
                   178: "FrontTactilTouched",
                   179: "RearTactilTouched",
                   180: "MiddleTactilTouched",
                   181: "HotJoinDetected",
                   182: "HandRightBackTouched",
                   183: "HandRightLeftTouched",
                   184: "HandRightRightTouched",
                   185: "HandLeftBackTouched",
                   186: "HandLeftLeftTouched",
                   187: "HandLeftRightTouched",
                   188: "PositionCamera"} #,
 #                  188: "WordRecognized"}

    
    bodyNames = self.motion.getBodyNames("Body")
    self.numToMotor = {}
    j = 1
##  1 HeadYaw
##  2 HeadPitch
##  3 LShoulderPitch
##  4 LShoulderRoll
##  5 LElbowYaw
##  6 LElbowRoll
##  7 LWristYaw
##  8 LHand
##  9 LHipYawPitch
##  10 LHipRoll
##  11 LHipPitch
##  12 LKneePitch
##  13 LAnklePitch
##  14 LAnkleRoll
##  15 RHipYawPitch
##  16 RHipRoll
##  17 RHipPitch
##  18 RKneePitch
##  19 RAnklePitch
##  20 RAnkleRoll
##  21 RShoulderPitch
##  22 RShoulderRoll
##  23 RElbowYaw
##  24 RElbowRoll
##  25 RWristYaw
##  26 RHand
    for index, i in enumerate(bodyNames):
      self.numToMotor[index] = i
   

  def getRandomMotor(self):
      return random.randint(1,25)

  def getRandomSensor(self):
      return random.randint(1,187)
      
  def putMemory(self, ident, value):
      self.memory.insertData(str(ident), value)

  def putGameMemory(self, ident, value):
      self.memory.insertData("g" + str(ident), value)
      
  def getSensorValue(self, num):
      return self.memory.getData(self.numToSensor[num])

  def getMessageValue(self, num):
      return self.memory.getData(str(num))

  def getMotorName(self, num):
      return self.numToMotor[num]

  def exit(self):
    print "Exiting sharedData"
    try:
        pass
    except:
        pass
    self.isRunning=False
    ALModule.exit(self)
