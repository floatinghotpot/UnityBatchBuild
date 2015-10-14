#!/usr/bin/env python
# coding=UTF-8

import sys, os, time

# Class.Method in Unity code
buildMethod="BatchBuildMenu.BuildIOS"
buildMode="release"

# --- run unity in batch mode ---
def BuildUnityProject( projPath ):
    unityPath = os.getenv("UNITY_PATH")
    if unityPath is None:
        unityPath = "/Applications/Unity/Unity.app"
        
    unityCmd = unityPath + "/Contents/MacOS/Unity"
    unityCmd = unityCmd + " -batchmode -quit -logFile"
    unityCmd = unityCmd + " -project " + projPath + " -executeMethod " + buildMethod
    
    if buildMode == "debug":
        unityCmd = unityCmd + " -NoStrip -Development"
        
    print "------------------------------------------------------------------------"
    print "------------------ Build iOS Begin -------------------------------------"
    print "------------------------------------------------------------------------"
    
    print "UnityCmd: " + unityCmd
    os.system( unityCmd );

    print "----------------------------------------------------------------------"
    print "------------------ Build iOS End -------------------------------------"
    print "----------------------------------------------------------------------"

# --- main func ---
pyPath = sys.argv[0]
pyAbsPath = os.path.abspath(pyPath)
n = pyAbsPath.find("/Assets/")
if n < 0:
    print pyPath + " not under Unity project Assets, abort."
    exit(0)
else:
    projPath = pyAbsPath[0:n]
    
    for arg in sys.argv:
        if arg == "release":
            buildMode="release"
        elif arg == "debug":
            buildMode="debug"
            
    BuildUnityProject( projPath )

