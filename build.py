#!/usr/bin/env python
# coding=UTF-8

import sys, os, time
import re, subprocess
import shutil, glob, zipfile

from Foundation import NSMutableDictionary

# See: https://github.com/kronenthaler/mod-pbxproj
from mod_pbxproj import XcodeProject

# config data
import build_config

# ----------------------------------------------
# check project path
build_py_abspath = os.path.abspath(argv[0])
n = build_py_abspath.find("/Assets/")
if n > 0:
    projPath = build_py_abspath[0:n]
else:    
    print argv[0] + " not under Unity project Assets, abort."
    exit(0)

# make sure BatchBuildConfig_cs comes together
BatchBuildConfig_cs_abspath = build_py_abspath.replace("build.py", "BatchBuildConfig.cs");
if not os.path.exists( BatchBuildConfig_cs_abspath ):
    print "BatchBuildConfig.cs not found with build.py";
    exit(0)
    
# ----------------------------------------------
# get build number from SVN
def getSvnRevision() :
    svn_info = subprocess.Popen(['svn info'], shell=True, stdout=subprocess.PIPE).communicate()[0]
    revision = (re.search(ur"Revision:\s\d+", svn_info))
    if revision != None:
        return int(revision.group().replace("Revision: ", ""))
    else:
        return 0

# ----------------------------------------------
def ModifyUnityMacro( projPath, target, buildMode ):
    fsmcs = open( projPath + "/Assets/smcs.rsp",'w')
    
    str = build_config.UNITY_SMCS['common']
    if str != None:
        fsmcs.write(str)
        
    str = build_config.UNITY_SMCS[ buildMode ]
    if str != None:
        fsmcs.write(str)
        
    str = target_inf['smcs']
    if str != None:
        fsmcs.write(str)
        
    fsmcs.close()
    return

# ----------------------------------------------
def ModifyUnityCode( projPath, target, buildMode ):
    target_inf = build_config.TARGET_PACKAGES[ target ]
    content = "// NOTICE: python script will auto update it before build\n" +
        "public class BatchBuildConfig {\n" +
        "   public static string APP_NAME = \"" + target_inf['name'] + "\";" +
        "   public static string APP_ID = \"" + target_inf['name'] + "\";" +
        "   public static string APP_VERSION = \"" + build_config.APP_MAJOR_VERSION + "." + getSvnRevision() + "\";" +
        "   public static string TARGET_DIR = \"" + build_config.TARGET_DIR + "\";" +
        "}\n"
    
    print content
    #f = open( BatchBuildConfig_cs_abspath, "w" )
    #f.write( content )
    #f.close()
    
    return

# ----------------------------------------------
def CallUnity( projPath, target, buildMode ):
    ModifyUnityMacro( projPath, target, buildMode )
    ModifyUnityCode( projPath, target, buildMode )
    
    target_inf = build_config.TARGET_PACKAGES[ target ]
    platform = target_inf['platform']
    
    if platform == "ios":
        buildMethod="BatchBuildMenu.BuildIOS"
    elif platform == "android":
        buildMethod="BatchBuildMenu.BuildAndroid"
    elif platform == "wp8":
        buildMethod="BatchBuildMenu.BuildWP8"
    else:
        print "platform not supported: " + platform
        exit(0)
        
    unityPath = os.getenv("UNITY_PATH")
    if unityPath is None:
        unityPath = "/Applications/Unity/Unity.app"
        
    unityCmd = unityPath + "/Contents/MacOS/Unity"
    unityCmd = unityCmd + " -batchmode -quit -logFile"
    unityCmd = unityCmd + " -project " + projPath + " -executeMethod " + buildMethod
    
    if buildMode == "debug":
        unityCmd = unityCmd + " -NoStrip -Development"
        
    print "-----------------------------------------------------------------"
    print "------------------ Run Unity Begin ------------------------------"
    print "-----------------------------------------------------------------"
    
    print "UnityCmd: " + unityCmd
    
    if os.system( unityCmd ) != 0:
        exit(0)

    print "---------------------------------------------------------------"
    print "------------------ Run Unity End ------------------------------"
    print "---------------------------------------------------------------"
    
    return

# ----------------------------------------------
def ModifyXcodeProject( projPath, target, buildMode ):
    target_inf = build_config.TARGET_PACKAGES[ target ]
    filePath = projPath + build_config.TARGET_DIR + "/" + target + "/Unity-iPhone.xcodeproj/project.pbxproj"
    project = XcodeProject.Load(absProjPath)
    
    # add group test
    #testgroup = project.get_or_create_group('testGroup')
    
    build_config.PatchXcodeProject( project )
    
    if project.modified:
        project.backup()
        project.saveFormat3_2()
        
    return

# ----------------------------------------------
def ModifyPlist( projPath, target, buildMode ):
    target_inf = build_config.TARGET_PACKAGES[ target ]
    filePath = projPath + build_config.TARGET_DIR + "/" + target + "/Info.plist";
    plist = NSMutableDictionary.dictionaryWithContentsOfFile_(filePath)

    plist['CFBundleDisplayName'] = target_inf['name']
    plist['CFBundleIdentifier'] = target_inf['id']
    plist['CFBundleVersion'] = build_config.APP_MAJOR_VERSION + "." + getSvnRevision()
    
    plist['UIViewControllerBasedStatusBarAppearance'] = False
    
    build_config.PatchPlist( plist, buildMode )
        
    # save plist file
    plist.writeToFile_atomically_(path,1)
    
    return

# ----------------------------------------------
def ModifyResource( projPath, target, buildMode ):
    target_inf = build_config.TARGET_PACKAGES[ target ]
    
    # copy icons
    fromDir = projPath + build_config.APP_ICON_DIR + "/" + target
    toDir = projPath + build_config.TARGET_DIR + "/" + target
    if os.path.exists(fromDir):
        copyCmd = "cp " + fromDir + "/Icon*.png " + toDir + "/";
        if os.system( copyCmd ) != 0:
            exit(1)
    
    return

# ----------------------------------------------
def CallXcodeBuild( projPath, target, buildMode ):
    
    ModifyXcodeProject( projPath, target, buildMode )
    
    ModifyPlist( projPath, target, buildMode )
    
    ModifyResource( projPath, target, buildMode )
    
    target_inf = build_config.TARGET_PACKAGES[ target ]
    xcodeprojPath = projPath + build_config.TARGET_DIR + "/" + target
    provision_cert = build_config.IOS_PROVISION_CERT[ buildMode ]
    
    xcodeCmd = "/usr/bin/xcodebuild" + 
        " -project " + xcodeprojPath + "/Unity-iPhone.xcodeproj" +
        " PROVISIONING_PROFILE=\"" + provision_cert['provision'] + "\"" +
        " CODE_SIGN_IDENTITY=\"" + provision_cert['cert'] +"\"" +
        " clean " +
        " build " +
        #" analyze " +
        #" archive " +
        #" -list " +
        #" -target Unity-iPhone " +
        #" -scheme Unity-iPhone " + 
        #" -xcconfig configuration.xcconfig " +
        #" SYMROOT=\"" + sym_root + "\" " +
        #" DSTROOT=\"" + dst_root + "\"" +
        ""
        
    if buildMode == "debug":
        xcodeCmd = xcodeCmd + " -configuration Debug"
    else:
        xcodeCmd = xcodeCmd + " -configuration Release"
        
    outputApp = xcodeprojPath + "/build/" + target_inf['name'] + ".app"
    provisionfile = build_config.PROVISION_DIR + "/" + provision_cert['provision'] + ".mobileprovision"
    targetProvision = outputApp + "/embedded.mobileprovision"
    tmpIpa = xcodeprojPath + "/tmp.ipa"
    archiveIpa = xcodeprojPath + target_inf['name'] + '.ipa'
    
    rmCmd ="rm -rf " + outputApp + "/_CodeSignature/"
    cpCmd = "cp " + provisionfile + " " + targetProvision
    codesignCmd = "codesign -f -s \"" + provision_cert['cert'] + "\" " + outputApp
    makeIpaCmd = "xcrun -sdk iphoneos PackageApplication -v " + outputApp + " -o " + tmpIpa
    renameCmd = "mv " + tmpIpa + " " + archiveIpa
    
    print "-----------------------------------------------------------------"
    print "------------------ Run Xcode Begin ------------------------------"
    print "-----------------------------------------------------------------"
    
    Cmds = [ xcodeCmd, rmCmd, cpCmd, codesignCmd, makeIpaCmd, renameCmd ]
    for Cmd in Cmds:
        print Cmd
#        if os.system(Cmd) != 0:
#            exit(0)
    
    print "---------------------------------------------------------------"
    print "------------------ Run Xcode End ------------------------------"
    print "---------------------------------------------------------------"
    
    if os.path.exists(archiveIpa):
        ipaSize = int(os.path.getsize(archiveIpa)/1024/1024)
        print "test IPA size: " + ipaSize
    
    return

# ----------------------------------------------
def BuildPackage( projPath, target, buildMode ):
    target_inf = build_config.TARGET_PACKAGES[ target ]
    
    platform = target_inf['platform']
    if platform not in ["ios", "android", "wp8"]:
        print "platform not supported for target: " + target
        exit(0)
    
    CallUnity( projPath, target, buildMode )
    
    if platform == "ios":
        CallXcodeBuild( projPath, target, buildMode )
    elif platform == "android":
        print "TODO: "
    elif platform == "wp8":
        print "TODO: "
        
    print "---------------------------------------------------------------"
    print "------------------ Build Package End --------------------------"
    print "---------------------------------------------------------------"
    
    return

# --- main func ---
def main( argv ) :
    buildMode = "debug"
    
    targets = []
    for arg in argv[1:]:
        if arg == "release":
            buildMode="release"
        elif arg == "debug":
            buildMode="debug"
        else:
            target_inf = build_config.TARGET_PACKAGES[ arg ]
            print target_inf
            if(target_inf == None):
                print arg + " not defined in TARGET_PACKAGES"
                exit(0)
            elif(target_inf['enabled'] != True):
                print arg + " not enabled in TARGET_PACKAGES"
                exit(0)
            else:
                targets.append( arg )

    for target in targets:
        BuildPackage( projPath, target, buildMode )
    
    return

# Syntax: build.py [ios|android|xiaomi|360|...] [debug|release]

main( sys.argv )




