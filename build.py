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

buildPySyntax = "Syntax: build.py [ios|android|xiaomi|360|...] [debug|release]"

# ----------------------------------------------
def ModifyUnityMacro( projPath, target, buildMode, target_inf ):
    smcs = []
    
    if 'common' in build_config.UNITY_SMCS:
        smcs.append( build_config.UNITY_SMCS['common'] )
        
    if buildMode in build_config.UNITY_SMCS:
        smcs.append( build_config.UNITY_SMCS[ buildMode ] )
     
    if 'smcs' in target_inf:
        smcs.append( target_inf['smcs'] )
    
    text = "\n".join(smcs)
    
    smcsPath = projPath + "/Assets/smcs.rsp"
    print "\nModifying: " + smcsPath
    print "-----------------------------------------------------------------"
    print text
    print "-----------------------------------------------------------------"
    
    fsmcs = open( smcsPath, 'w')
    fsmcs.write( text + "\n" )
    fsmcs.close()
    
    return

# ----------------------------------------------
def ModifyUnityCode( projPath, target, buildMode, target_inf ):
    macro_text = "";
    if "macro" in target_inf:
        macro_text = target_inf['macro']
        
    text = ("// NOTICE: build.py will auto overwrite it before every build\n" + 
        "public class BatchBuildConfig {\n" + 
        "   public static string APP_NAME = \"" + target_inf['name'] + "\";\n" + 
        "   public static string APP_ID = \"" + target_inf['id'] + "\";\n" + 
        "   public static string APP_VERSION = \"" + target_inf['version'] + "\";\n" + 
        "   public static string TARGET_DIR = \"" + build_config.TARGET_DIR + "\";\n" + 
        "   public static string DEFINE_MACRO = \"" + macro_text + "\";\n" + 
        "}")
    
    global BatchBuildConfig_cs_abspath
    print "\nModifying: " + BatchBuildConfig_cs_abspath
    print "-----------------------------------------------------------------"
    print text
    print "-----------------------------------------------------------------"
    
    f = open( BatchBuildConfig_cs_abspath, "w" )
    f.write( text + "\n" )
    f.close()
    
    return

# ----------------------------------------------
def CallUnity( projPath, target, buildMode, target_inf ):
    print "-----------------------------------------------------------------"
    print "------------------ Run Unity Begin ------------------------------"
    print "-----------------------------------------------------------------"
    
    ModifyUnityMacro( projPath, target, buildMode, target_inf )
    ModifyUnityCode( projPath, target, buildMode, target_inf )
    
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
        
    unityCmd = unityPath + "/Contents/MacOS/Unity -batchmode -quit"
    unityCmd = unityCmd + " -project " + projPath + " -executeMethod " + buildMethod
    #unityCmd = unityCmd + " -logFile"
    
    if buildMode == "debug":
        unityCmd = unityCmd + " -NoStrip -Development"
    
    print "\nRunning command: " + unityCmd
    print "-----------------------------------------------------------------"
    if os.system( unityCmd ) != 0:
        exit(0)
    print "-----------------------------------------------------------------"
    os.system("cat ~/Library/Logs/Unity/Editor.log");
    print "-----------------------------------------------------------------"
    print "------------------ Run Unity End --------------------------------"
    print "-----------------------------------------------------------------"
    
    return

# ----------------------------------------------
def ModifyXcodeProject( xcodeprojPath, target, buildMode, target_inf ):
    filePath = xcodeprojPath + "/Unity-iPhone.xcodeproj/project.pbxproj"
    print "\nModifying " + filePath
    project = XcodeProject.Load( filePath )
    
    # add group test
    #testgroup = project.get_or_create_group('testGroup')
    
    build_config.ModifyXcodeProject( project, buildMode )
    
    if project.modified:
        project.backup()
        project.save()
        
    #print "-----------------------------------------------------------------"
    #os.system("cat " + filePath)
    #print "-----------------------------------------------------------------"
    
    return

# ----------------------------------------------
def ModifyPlist( xcodeprojPath, target, buildMode, target_inf ):
    filePath = xcodeprojPath + "/Info.plist";
    print "\nModifying " + filePath
    
    plist = NSMutableDictionary.dictionaryWithContentsOfFile_( filePath )

    plist['CFBundleDisplayName'] = target_inf['name']
    plist['CFBundleIdentifier'] = target_inf['id']
    plist['CFBundleVersion'] = target_inf['version']
    plist['CFBundleShortVersionString'] = build_config.APP_MAJOR_VERSION
    
    plist['UIViewControllerBasedStatusBarAppearance'] = False
    
    build_config.ModifyPlist( plist, buildMode )
        
    # save plist file
    plist.writeToFile_atomically_( filePath, 1 )
    
    #print "-----------------------------------------------------------------"
    #os.system("cat " + filePath)
    #print "-----------------------------------------------------------------"
    
    return

# ----------------------------------------------
def ModifyResource( projPath, target, buildMode, target_inf ):
    # icons & splash located here
    iconPathSrc = projPath + build_config.APP_ICON_SPLASH_DIR + "/" + target + "/icons"
    splashPathSrc = projPath + build_config.APP_ICON_SPLASH_DIR + "/" + target + "/splash"

    xcodeprojPath = projPath + build_config.TARGET_DIR + "/" + target
    resPath = xcodeprojPath + "/Res"

    iconPath = resPath + "/icons"
    copyCmd = "cp " + iconPathSrc + "/*.png " + iconPath + "/";
    print "\nCopy Icons: " + copyCmd
    if os.path.exists(iconPathSrc):
        os.mkdirs(iconPath)
        os.system( copyCmd )
        
    splashPath = resPath + "/splash"
    copyCmd = "cp " + splashPathSrc + "/*.png " + splashPath + "/";
    print "\nCopy Splash Images: " + copyCmd
    if os.path.exists(iconPathSrc):
        os.mkdirs(splashPath)
        os.system( copyCmd )
        
    # TODO: modify icons & splash entry in Plist
    
    return

# ----------------------------------------------
def CallXcodeBuild( projPath, target, buildMode, target_inf ):
    print "-----------------------------------------------------------------"
    print "------------------ Run Xcode Begin ------------------------------"
    print "-----------------------------------------------------------------"
    
    target_inf = build_config.TARGET_PACKAGES[ target ]
    xcodeprojPath = projPath + build_config.TARGET_DIR + "/" + target
    
    ModifyXcodeProject( xcodeprojPath, target, buildMode, target_inf )
    ModifyPlist( xcodeprojPath, target, buildMode, target_inf )
    ModifyResource( xcodeprojPath, target, buildMode, target_inf )
    
    provision_cert = build_config.IOS_PROVISION_CERT[ buildMode ]
    
    xcodeCmd = ("/usr/bin/xcodebuild" + 
        " clean " +
        " build " +
        " -project " + xcodeprojPath + "/Unity-iPhone.xcodeproj" +
        " PROVISIONING_PROFILE=\"" + provision_cert['provision'] + "\"" +
        " CODE_SIGN_IDENTITY=\"" + provision_cert['cert'] +"\"" +
        #" analyze " +
        #" archive " +
        #" -list " +
        #" -target Unity-iPhone " +
        #" -scheme Unity-iPhone " + 
        #" -xcconfig configuration.xcconfig " +
        #" SYMROOT=\"" + sym_root + "\" " +
        #" DSTROOT=\"" + dst_root + "\"" +
        "")
        
    if buildMode == "debug":
        xcodeCmd = xcodeCmd + " -configuration Debug"
    else:
        xcodeCmd = xcodeCmd + " -configuration Release"
        
    outputApp = xcodeprojPath + "/build/" + target_inf['name'] + ".app"
    provisionfile = build_config.IOS_PROVISION_PATH + "/" + provision_cert['provision'] + ".mobileprovision"
    targetProvision = outputApp + "/embedded.mobileprovision"
    tmpIpa = xcodeprojPath + "/tmp.ipa"
    archiveIpa = xcodeprojPath + "/" + target_inf['name'] + '.ipa'
    
    rmCmd ="rm -rf " + outputApp + "/_CodeSignature/"
    cpCmd = "cp \"" + provisionfile + "\" " + targetProvision
    codesignCmd = "codesign -f -s \"" + provision_cert['cert'] + "\" " + outputApp
    
    makeIpaCmd = "xcrun -sdk iphoneos PackageApplication -v " + outputApp + " -o " + tmpIpa
    renameCmd = "mv " + tmpIpa + " " + archiveIpa
    
    #Cmds = [ xcodeCmd, rmCmd, cpCmd, codesignCmd, makeIpaCmd, renameCmd ]
    
    Cmds = [ xcodeCmd, makeIpaCmd, renameCmd ]
    for Cmd in Cmds:
        print "\nRunning command: " + Cmd
        if os.system(Cmd) != 0:
            exit(0)
    
    print "---------------------------------------------------------------"
    print "------------------ Run Xcode End ------------------------------"
    print "---------------------------------------------------------------"
    
    if os.path.exists(archiveIpa):
        print archiveIpa
        ipaSize = int(os.path.getsize(archiveIpa)/1024/1024)
        print "IPA size: " + str(ipaSize) + "MB" 
    
    return

# ----------------------------------------------
def BuildPackage( projPath, target, buildMode, target_inf ):
    print "\nBuilding package target: "
    for key, value in target_inf.iteritems():
        print "    ", key, ": ", value
    
    platform = target_inf['platform']
    if platform not in ["ios", "android", "wp8"]:
        print "platform not supported for target: " + target
        exit(0)
    
    CallUnity( projPath, target, buildMode, target_inf )

    if platform == "ios":
        CallXcodeBuild( projPath, target, buildMode, target_inf )
        
    elif platform == "android":
        print "TODO: "
        
    elif platform == "wp8":
        print "TODO: "
    
    return

# --- main func ---
def main( argv ) :
    # ----------------------------------------------
    # pre-check project path
    global buildPyPath
    buildPyPath = os.path.abspath(sys.argv[0])
    n = buildPyPath.find("/Assets/")
    if n > 0:
        projPath = buildPyPath[0:n]
        print "Project to build: " + projPath
    else:    
        print argv[0] + " not under Unity project Assets, abort."
        exit(0)

    # ----------------------------------------------
    # make sure BatchBuildConfig_cs comes together
    global BatchBuildConfig_cs_abspath 
    BatchBuildConfig_cs_abspath = buildPyPath.replace("build.py", "BatchBuildConfig.cs");
    if not os.path.exists( BatchBuildConfig_cs_abspath ):
        print "BatchBuildConfig.cs not found with build.py";
        exit(0)

    buildMode = "debug"
    buildNumber = 0
    
    # ----------------------------------------------
    # get build number from SVN
    svn_info = subprocess.Popen(['svn info'], shell=True, stdout=subprocess.PIPE).communicate()[0]
    revision_info = (re.search(ur"Revision:\s\d+", svn_info))
    if revision_info != None:
        buildNumber = int(revision_info.group().replace("Revision: ", ""))
        print "    SVN revision -> build number: ", buildNumber
    else:
        buildNumber = 0
        print "    Not SVN, build number: ", 0

    # ----------------------------------------------
    # parse args to get targets & build mode
    targets = []
    for arg in argv[1:]:
        if arg == "release":
            buildMode="release"
        elif arg == "debug":
            buildMode="debug"
        else:
            target_inf = build_config.TARGET_PACKAGES[ arg ]
            if(target_inf == None):
                print "Error: " + arg + " not defined in TARGET_PACKAGES (build_config.py)\n"
                exit(0)
            elif(target_inf['enabled'] != True):
                print "Error: " + arg + " not enabled in TARGET_PACKAGES (build_config.py)\n"
                exit(0)
            else:
                targets.append( arg )

    # ----------------------------------------------
    # build targets one by one
    if len(targets) > 0:
        print "    Package targets: " + (", ".join(targets))
        print "    Build mode: " + buildMode
        for target in targets:
            target_inf = build_config.TARGET_PACKAGES[ target ]
            target_inf['version'] = "v" + build_config.APP_MAJOR_VERSION + "." + str(buildNumber)
            BuildPackage( projPath, target, buildMode, target_inf )
    else:
        print buildPySyntax
        print "Error: no package target specified. Abort.\n"
    
    return

# ----------------------------------------------
# main entry

main( sys.argv )




