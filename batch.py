#!/usr/bin/env python
# coding=UTF-8

import sys, os, commands
import datetime, time
import re, subprocess
import shutil, glob, zipfile
import ftplib, socket

from Foundation import NSMutableDictionary

# See: https://github.com/kronenthaler/mod-pbxproj
from mod_pbxproj import XcodeProject

# config data
import batch_config

buildPySyntax = "Syntax: batch.py [clean|build|archive] [ios|android|xiaomi|360|...|all] [--debug|--release]"

# ----------------------------------------------
def ModifyUnityMacro( projPath, target, buildMode, target_inf ):
    smcs = []

    if 'common' in batch_config.UNITY_SMCS:
        smcs.append( batch_config.UNITY_SMCS['common'] )

    if buildMode in batch_config.UNITY_SMCS:
        smcs.append( batch_config.UNITY_SMCS[ buildMode ] )

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
        "   public static string TARGET_DIR = \"" + batch_config.DIR_INFO['target_dir'] + "\";\n" +
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

    # the called buildMethod are defined in BatchBuildMenu.cs
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
    unityCmd = unityCmd + " -projectPath " + projPath + " -executeMethod " + buildMethod
    unityCmd = unityCmd + " -logFile"

    if buildMode == "debug":
        unityCmd = unityCmd + " -NoStrip -Development"

    print "\nRunning command: " + unityCmd
    print "-----------------------------------------------------------------"
    ret = os.system( unityCmd )
    if ret != 0:
        os.system("cat ~/Library/Logs/Unity/Editor.log");
        exit(0)

    print "-----------------------------------------------------------------"
    print "------------------ Run Unity End --------------------------------"
    print "-----------------------------------------------------------------"

    return

# ----------------------------------------------
def ModifyXcodeProject( xcodeprojPath, target, buildMode, target_inf ):
    filePath = xcodeprojPath + "/Unity-iPhone.xcodeproj/project.pbxproj"
    print "\nModifying " + filePath
    project = XcodeProject.Load( filePath )

    batch_config.ModifyXcodeProject( project, buildMode )

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
    plist['CFBundleShortVersionString'] = batch_config.APP_MAJOR_VERSION

    plist['UIViewControllerBasedStatusBarAppearance'] = False

    batch_config.ModifyPlist( plist, buildMode )

    # save plist file
    plist.writeToFile_atomically_( filePath, 1 )

    #print "-----------------------------------------------------------------"
    #os.system("cat " + filePath)
    #print "-----------------------------------------------------------------"

    return

# ----------------------------------------------
def ModifyResource( projPath, target, buildMode, target_inf ):
    # icons & splash located here
    iconPathSrc = projPath + batch_config.DIR_INFO['res_dir'] + "/" + target + "/icons"
    splashPathSrc = projPath + batch_config.DIR_INFO['res_dir'] + "/" + target + "/splash"

    xcodeprojPath = projPath + batch_config.DIR_INFO['target_dir'] + "/" + target
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

    target_inf = batch_config.TARGET_PACKAGES[ target ]
    xcodeprojPath = projPath + batch_config.DIR_INFO['target_dir'] + "/" + target

    ModifyXcodeProject( xcodeprojPath, target, buildMode, target_inf )

    ModifyPlist( xcodeprojPath, target, buildMode, target_inf )

    ModifyResource( xcodeprojPath, target, buildMode, target_inf )

    provision_cert = batch_config.IOS_PROVISION_CERT[ buildMode ]
    xcodeCmd = ("/usr/bin/xcodebuild" +
        " clean " +
        " build " +
        " -project " + xcodeprojPath + "/Unity-iPhone.xcodeproj" +
        " PROVISIONING_PROFILE=\"" + provision_cert['provision'] + "\" " +
        " CODE_SIGN_IDENTITY=\"" + provision_cert['cert'] +"\" " +
        #" analyze " +
        #" archive " +
        #" -list " +
        #" -target Unity-iPhone " +
        #" -scheme Unity-iPhone " +
        #" -xcconfig configuration.xcconfig " +
        #" SYMROOT=\"" + symroot + "\" " +
        #" DSTROOT=\"" + dstroom + "\" " +
        "")

    if buildMode == "debug":
        xcodeCmd = xcodeCmd + " -configuration Debug"
    else:
        xcodeCmd = xcodeCmd + " -configuration Release"

    print "\nRunning command: " + xcodeCmd
    if os.system(xcodeCmd) != 0:
        exit(0)

    appFile = target_inf['name'] + ".app"
    outputApp = xcodeprojPath + "/build/" + appFile
    outputDebugApp = xcodeprojPath + "/build/Debug-iphoneos/" + appFile
    outputReleaseApp = xcodeprojPath + "/build/Release-iphoneos/" + appFile
    if (buildMode == "debug") and os.path.exists(outputDebugApp):
        outputApp = outputDebugApp
    elif (buildMode == "release") and os.path.exists(outputReleaseApp):
        outputApp = outputReleaseApp

    #provisionfile = batch_config.DIR_INFO['ios_profile_dir'] + "/" + provision_cert['provision'] + ".mobileprovision"
    #targetProvision = outputApp + "/embedded.mobileprovision"
    #tmpIpa = xcodeprojPath + "/tmp.ipa"
    #rmCmd ="rm -rf " + outputApp + "/_CodeSignature/"
    #cpCmd = "cp \"" + provisionfile + "\" " + targetProvision
    #codesignCmd = "codesign -f -s \"" + provision_cert['cert'] + "\" " + outputApp

    # TODO: we can also replace the app icon & spash here

    archiveIpa = xcodeprojPath + "/" + target_inf['name'] + '.ipa'
    makeIpaCmd = "xcrun -sdk iphoneos PackageApplication -v " + outputApp + " -o " + archiveIpa

    #Cmds = [ rmCmd, cpCmd, codesignCmd, makeIpaCmd ]
    Cmds = [ makeIpaCmd ]
    for Cmd in Cmds:
        print "\nRunning command: " + Cmd
        if os.system(Cmd) != 0:
            exit(0)

    print "---------------------------------------------------------------"
    print "------------------ Run Xcode End ------------------------------"
    print "---------------------------------------------------------------"

    return

# ----------------------------------------------
def BuildPackage( projPath, target, buildMode, target_inf ):
    print "\nBuilding package target: "
    for key, value in target_inf.iteritems():
        print "    ", key, ": ", value

    #CallUnity( projPath, target, buildMode, target_inf )

    platform = target_inf['platform']
    if platform == "ios":
        CallXcodeBuild( projPath, target, buildMode, target_inf )
    elif platform == "android":
        pass
    elif platform == "wp8":
        pass

    return

# ----------------------------------------------
def ArchivePackage( projPath, target, buildMode, target_inf ):
    packagePath = target_inf['package']
    print "\nPackage: ", packagePath
    print "    version: ", target_inf['version']
    print "    size: ", int(os.path.getsize(packagePath)/1024/1024), "MB"

    # if not defined in target info, then use default
    if "post_build_cmds" in target_inf:
        print "post_build_cmds found for target " + target
        post_build_cmds = target_inf['post_build_cmds']
    else:
        print "using default post_build_cmds"
        post_build_cmds = batch_config.POST_BUILD_SCRIPTS

    # if not dict, or not enabled, ignore
    if type(post_build_cmds) is dict:
        if ('enabled' in post_build_cmds) and (post_build_cmds['enabled'] == False):
            print "post_build_cmds not enabled, skip."
            return
    else:
        print "post_build_cmds not configured, skip."
        return

    # make sure command list defined for current build mode
    if buildMode in post_build_cmds:
        template_cmds = post_build_cmds[ buildMode ]
        if not type(template_cmds) is list:
            print "template commands list expected."
            return
    else:
        print "post_build_cmds for " + buildMode + " not configured, skip."
        return

    # create commands from template
    cmds = []
    for template_cmd in template_cmds:
        cmd = template_cmd
        for key, value in target_inf.iteritems():
            if type(key) is str and type(value) is str:
                cmd = cmd.replace("{"+key+"}", value)
        cmds.append( cmd )

    # run commands
    print "Running batch commands:"
    for cmd in cmds:
        print "    " + cmd
        status, output = commands.getstatusoutput( cmd )
        print output
        if status != 0:
            exit(0)

    return

# ----------------------------------------------
def addTargetToList(target, targets):
    if target in targets:
        return

    target_inf = batch_config.TARGET_PACKAGES[ target ]
    if type(target_inf) is dict:
        targets.append( target )
    else:
        print "Error: " + arg + " not configured in TARGET_PACKAGES\n"
        exit(0)

    return

# ----------------------------------------------
def main( argv ) :
    # ----------------------------------------------
    # check project path
    global buildPyPath
    buildPyPath = os.path.abspath(argv[0])
    buildPyFile = os.path.basename(buildPyPath)
    n = buildPyPath.find("/Assets/")
    if n > 0:
        projPath = buildPyPath[0:n]
        print "Project to build: " + projPath
    else:
        print buildPyFile + " not under Unity project Assets, abort."
        exit(0)

    # ----------------------------------------------
    # make sure BatchBuildConfig_cs comes together
    global BatchBuildConfig_cs_abspath
    BatchBuildConfig_cs_abspath = buildPyPath.replace(buildPyFile, "BatchBuildConfig.cs");
    if (os.path.basename(BatchBuildConfig_cs_abspath) != "BatchBuildConfig.cs") or (not os.path.exists( BatchBuildConfig_cs_abspath) ):
        print "BatchBuildConfig.cs not found with " + buildPyFile;
        exit(0)

    do_clean = False
    do_build = False
    do_archive = False
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
        if arg == "clean" or arg == "-c":
            do_clean = True
        elif arg == "build" or arg == "-b":
            do_build = True
        elif arg == "archive" or arg == "-a":
            do_archive = True
        elif arg == "release" or arg == '-r':
            buildMode="release"
        elif arg == "debug" or arg == '-d':
            buildMode="debug"
        elif arg == "all":
            for key, target_inf in batch_config.TARGET_PACKAGES.iteritems():
                enabled = target_inf['enabled']
                if type(enabled) is bool and enabled == False:
                    continue
                else:
                    addTargetToList(key, targets)
            pass
        else:
            addTargetToList(arg, targets)

    if len(targets) == 0:
        print buildPySyntax
        print "Error: no package target specified. Abort.\n"
        exit(0)

    # --- prepare target info ---
    for target in targets:
        target_inf = batch_config.TARGET_PACKAGES[ target ]

        target_inf['target'] = target
        target_inf['unityproj_path'] = projPath
        target_inf['target_path'] = projPath + batch_config.DIR_INFO['target_dir'] + "/" + target

        platform = target_inf['platform']
        if platform == "ios":
            target_inf['package'] = target_inf['target_path'] + "/" + target_inf['name'] + ".ipa"
        elif platform == "android":
            target_inf['package'] = target_inf['target_path'] + "/" + target_inf['name'] + ".apk"
        elif platform == "wp8":
            target_inf['package'] = target_inf['target_path'] + "/" + target_inf['name'] + ".exe"
        else:
            print "platform not supported: " + platform
            exit(0)

        filename, file_extension = os.path.splitext( target_inf['package'] )
        target_inf['package_ext'] = file_extension
        target_inf['version'] = "v" + batch_config.APP_MAJOR_VERSION + "." + str(buildNumber)
        target_inf['date'] = datetime.datetime.today().strftime('%Y%m%d')

    # ----------------------------------------------
    # build targets one by one
    if len(targets) > 0:
        print "    Package targets: " + (", ".join(targets))
        print "    Build mode: " + buildMode

    if do_clean:
        for target in targets:
            target_inf = batch_config.TARGET_PACKAGES[ target ]
            targetDirPath = target_inf['target_path']
            cleanCmd = "rm -r " + targetDirPath
            print "    " + cleanCmd
            if os.path.exists(targetDirPath):
                os.system( cleanCmd )

    if do_build:
        for target in targets:
            target_inf = batch_config.TARGET_PACKAGES[ target ]
            BuildPackage( projPath, target, buildMode, target_inf )

    if do_archive:
        for target in targets:
            target_inf = batch_config.TARGET_PACKAGES[ target ]
            ArchivePackage( projPath, target, buildMode, target_inf )

    print "---------------------------------------------------------------"
    print "----------------------- Done ----------------------------------"
    print "---------------------------------------------------------------"
    return

# ----------------------------------------------
main( sys.argv )
