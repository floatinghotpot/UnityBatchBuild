#!/usr/bin/env python
# coding=UTF-8

import sys, os, commands, time
import re, subprocess
import shutil, glob, zipfile
import ftplib, socket

from Foundation import NSMutableDictionary

# See: https://github.com/kronenthaler/mod-pbxproj
from mod_pbxproj import XcodeProject

# config data
import build_config

buildPySyntax = "Syntax: build.py [ios|android|xiaomi|360|...|all] [debug|release]"

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
        "   public static string TARGET_DIR = \"" + build_config.DIR_INFO['target_dir'] + "\";\n" + 
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
    unityCmd = unityCmd + " -project " + projPath + " -executeMethod " + buildMethod
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
    iconPathSrc = projPath + build_config.DIR_INFO['res_dir'] + "/" + target + "/icons"
    splashPathSrc = projPath + build_config.DIR_INFO['res_dir'] + "/" + target + "/splash"

    xcodeprojPath = projPath + build_config.DIR_INFO['target_dir'] + "/" + target
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
    xcodeprojPath = projPath + build_config.DIR_INFO['target_dir'] + "/" + target
    
    ModifyXcodeProject( xcodeprojPath, target, buildMode, target_inf )
    
    ModifyPlist( xcodeprojPath, target, buildMode, target_inf )
    
    ModifyResource( xcodeprojPath, target, buildMode, target_inf )
    
    provision_cert = build_config.IOS_PROVISION_CERT[ buildMode ]
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
    
    #provisionfile = build_config.DIR_INFO['ios_profile_dir'] + "/" + provision_cert['provision'] + ".mobileprovision"
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
def genNameForArchive( target_inf ):
    packagePath = target_inf['package']
    filename = os.path.basename(packagePath)
    words = filename.split('.')
    count = len(words)
    if count >= 2:
        words[ count -2 ] = words[ count -2 ] + "-" + target_inf['version']
        filename = ".".join(words)
    return filename

# ----------------------------------------------
def scpToRemote(localPath, filename):
    host = build_config.REMOTE_INFO['host']
    username = build_config.REMOTE_INFO['username']
    remote_dir = build_config.REMOTE_INFO['remote_dir']
    scpCmd = "scp " + localPath + " " + username + "@" + host + ":" + remote_dir + "/" + filename
    print "\nRunning command: " + scpCmd
    os.system( scpCmd )
    return

# ----------------------------------------------
def ftpToRemote(ftp, localPath, filename):
    fd = open(localPath, "rb")
    ftp.storbinary("STOR %" % filename, fd)
    fd.close()
    return

# ----------------------------------------------
def prepareFTP():
    host = build_config.REMOTE_INFO['host']
    username = build_config.REMOTE_INFO['username']
    password = build_config.REMOTE_INFO['password']
    remote_dir = build_config.REMOTE_INFO['remote_dir']
    passiveMode = build_config.REMOTE_INFO['passiveMode']
    
    ftp = None
    # ----------------------------------------------
    try:
        ftp = ftplib.FTP(host)
    except (socket.error, socket.gaierror):
        print 'ERROR:cannot reach " %s"' % host  
        return
    # ----------------------------------------------
    try:
        ftp.login(username, password)
    except ftplib.error_perm:  
        print 'ERROR: login to FTP failed'

    print ftp.getwelcome()
    # ----------------------------------------------
    try:
        ftp.cwd( remote_dir )
    except ftplib.error_perm:
        print 'ERROR: cannot chdir to "%s"' % remote_dir
        ftp.quit()
        return
    # ----------------------------------------------
    if passiveMode:
        ftp.set_pasv(1)
    else:
        ftp.set_sasv(0)
    
    return ftp

# ----------------------------------------------
def ArchivePackage( targets ):
    enabled = build_config.REMOTE_INFO['enabled']
    if not enabled: 
        return
    
    ftp = None
    tool = build_config.REMOTE_INFO['tool']
    if tool == "ftp":
        ftp = prepareFTP()
        
    # ----------------------------------------------
    # print summary of targets one by one
    for target in targets:
        target_inf = build_config.TARGET_PACKAGES[ target ]
        packagePath = target_inf['package']
        if type(packagePath) is str and os.path.exists(packagePath):
            print "\nPackage: ", packagePath
            print "    version: ", target_inf['version']
            print "    size: ", int(os.path.getsize(packagePath)/1024/1024), "MB"
            filename = genNameForArchive( target_inf )
            
            host = build_config.REMOTE_INFO['host']
            username = build_config.REMOTE_INFO['username']
            remote_dir = build_config.REMOTE_INFO['remote_dir']

            if tool != "scp" and tool != "ftp":
                continue
            
            pre_ssh_shell = build_config.REMOTE_INFO['pre_ssh_shell'].replace("{filename}", filename)
            post_ssh_shell = build_config.REMOTE_INFO['post_ssh_shell'].replace("{filename}", filename)
            
            if len(pre_ssh_shell) > 0:
                preRemoteCmd = "ssh " + host + " '" + pre_ssh_shell + "'"
                print "\nRunning commands on remote host (" + host + "): " + pre_ssh_shell
                print commands.getoutput(preRemoteCmd)
        
            if tool == "scp":
                scpToRemote( packagePath, filename )
                pass
            elif tool == "ftp" and ftp != None:
                print "\nFTP to: " + host + ":" + remote_dir + "/" + filename
                ftpToRemote( ftp, packagePath, filename )
                pass
    
            if len(post_ssh_shell) > 0:
                postRemoteCmd = "ssh " + host + " '" + post_ssh_shell + "'"
                print "\nRunning commands on remote host (" + host + "): " + post_ssh_shell
                print commands.getoutput(postRemoteCmd)
                
    if ftp != None:
        ftp.quit()
        
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

    # ----------------------------------------------
    # call unity in batch mode
    CallUnity( projPath, target, buildMode, target_inf )

    # ----------------------------------------------
    # call xcode or other post build process in batch mode
    targetDirPath = projPath + build_config.DIR_INFO['target_dir'] + "/" + target
    if platform == "ios":
        CallXcodeBuild( projPath, target, buildMode, target_inf )
        packagePath = targetDirPath + "/" + target_inf['name'] + ".ipa"
        
    elif platform == "android":
        packagePath = targetDirPath + "/" + target_inf['name'] + ".apk"
        
    elif platform == "wp8":
        print "TODO: "
    
    # store package path for later summary
    if os.path.exists(packagePath):
        target_inf['package'] = packagePath
    else:
        del target_inf['package']
        
    return

def addTargetToList(target, targets):
    if target in targets:
        return
    
    target_inf = build_config.TARGET_PACKAGES[ target ]
    if not type(target_inf) is dict:
        print "Error: " + arg + " not defined in TARGET_PACKAGES (build_config.py)\n"
        exit(0)

    targets.append( target )
        
    return
    
# --- main func ---
def main( argv ) :
    # ----------------------------------------------
    # check project path
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
        elif arg == "all":
            for key, target_inf in build_config.TARGET_PACKAGES.iteritems():
                enabled = target_inf['enabled']
                if type(enabled) is bool and enabled == False:
                    continue
                else:
                    addTargetToList(key, targets)
            pass
        else:
            addTargetToList(arg, targets)

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
    
    ArchivePackage( targets )

    print "\n---------------------------------------------------------------"
    print "----------------------- Done ----------------------------------"
    print "---------------------------------------------------------------"
    return

# ----------------------------------------------
# main entry

main( sys.argv )




