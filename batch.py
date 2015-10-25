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

buildPySyntax = ("\nSyntax: batch.py <action> <target> <mode>\n" + 
                 "<action>     clean | build | archive\n" +
                 "<target>     ios | android | amazon | 360 | ... | all\n" +
                 "<mode>       --debug | --release | --daily | -d | -r\n" )

# ----------------------------------------------
def ModifyUnityMacro( target_inf ):
    vardict = target_inf['vars']
    smcsPath = vardict['unity_smcs_path']
    
    smcs = []
    smcs.append( vardict['unity_smcs'] )
    smcs.append( vardict['unity_mode_smcs'] )
    text = "\n".join(smcs)

    print "\nModifying: " + smcsPath
    print "-----------------------------------------------------------------"
    print text
    print "-----------------------------------------------------------------"

    fsmcs = open( smcsPath, 'w')
    fsmcs.write( text + "\n" )
    fsmcs.close()

    return

# ----------------------------------------------
def ModifyUnityCode( target_inf ):
    vardict = target_inf['vars']
    
    for file_tmp in batch_config.SOURCE_FILES:
        filepath = expandTemplateText( file_tmp['filepath'], vardict )
        text = expandTemplateText( file_tmp['content'], vardict )
        print "\nOverwrite source file: " + filepath
        print "-----------------------------------------------------------------"
        print text
        print "-----------------------------------------------------------------"
        f = open( filepath, "w" )
        f.write( text )
        f.close()
        
    return

# ----------------------------------------------
def CallUnity( target_inf ):
    print "-----------------------------------------------------------------"
    print "------------------ Run Unity Begin ------------------------------"
    print "-----------------------------------------------------------------"

    ModifyUnityMacro( target_inf )

    ModifyUnityCode( target_inf )

    unityCmd = target_inf['vars']['unity_cmd']
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
def ModifyXcodeProject( target_inf ):
    vardict = target_inf['vars']
    filepath = vardict['xcode_pbxproj_path']
    print "\nModifying " + filepath
    project = XcodeProject.Load( filepath )

    batch_config.ModifyXcodeProject( project, vardict['build_mode'] )

    if project.modified:
        project.backup()
        project.save()

    #print "-----------------------------------------------------------------"
    #os.system("cat " + filePath)
    #print "-----------------------------------------------------------------"

    return

# ----------------------------------------------
def ModifyPlist( target_inf ):
    vardict = target_inf['vars']
    filePath = vardict['xcodeplist_path']
    print "\nModifying " + filePath

    plist = NSMutableDictionary.dictionaryWithContentsOfFile_( filePath )

    plist['CFBundleDisplayName'] = vardict['name']
    plist['CFBundleIdentifier'] = vardict['id']
    plist['CFBundleVersion'] = vardict['version']
    plist['CFBundleShortVersionString'] = vardict['major_version']

    plist['UIViewControllerBasedStatusBarAppearance'] = False

    batch_config.ModifyPlist( plist, vardict['build_mode'] )

    # save plist file
    plist.writeToFile_atomically_( filePath, 1 )

    #print "-----------------------------------------------------------------"
    #os.system("cat " + filePath)
    #print "-----------------------------------------------------------------"

    return

# ----------------------------------------------
def ModifyResource( target_inf ):
    
    # TODO: copy icons & splash

    return

# ----------------------------------------------
def CallXcodeBuild( target_inf ):
    print "-----------------------------------------------------------------"
    print "------------------ Run Xcode Begin ------------------------------"
    print "-----------------------------------------------------------------"

    ModifyXcodeProject( target_inf )

    ModifyPlist( target_inf )

    ModifyResource( target_inf )

    vardict = target_inf['vars']
    xcodeCmd = vardict['xcode_cmd']
    print "\nRunning command: " + xcodeCmd
    if os.system(xcodeCmd) != 0:
        exit(0)

    outApp = vardict['xcode_outapptry']
    if not os.path.exists(outApp):
        outApp = vardict['xcode_outapp']
        
    #provisionfile = batch_config.DIR_INFO['ios_profile_dir'] + "/" + provision_cert['provision'] + ".mobileprovision"
    #targetProvision = outputApp + "/embedded.mobileprovision"
    #tmpIpa = xcodeprojPath + "/tmp.ipa"
    #rmCmd ="rm -rf " + outputApp + "/_CodeSignature/"
    #cpCmd = "cp \"" + provisionfile + "\" " + targetProvision
    #codesignCmd = "codesign -f -s \"" + provision_cert['cert'] + "\" " + outputApp

    makeIpaCmd = "xcrun -sdk iphoneos PackageApplication -v " + outApp + " -o " + vardict['xcode_outipa']
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
def BuildPackage( target_inf ):
    CallUnity( target_inf )

    vardict = target_inf['vars']
    platform = vardict['platform']
    if platform == "ios":
        CallXcodeBuild( target_inf )
        pass
    elif platform == "android":
        pass
    elif platform == "wp8":
        pass

    return

# ----------------------------------------------
def ArchivePackage( target_inf ):
    print "Running batch commands:"
    cmds = target_inf['post_build_cmds']
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

    if target in batch_config.TARGET_PACKAGES:
        target_inf = batch_config.TARGET_PACKAGES[ target ]
        if type(target_inf) is dict:
            targets.append( target )
            return
        
    print "Error: " + arg + " not configured in TARGET_PACKAGES\n"
    exit(0)

    return

def getSvnRevision():
    # ----------------------------------------------
    # get build number from SVN
    svn_info = subprocess.Popen(['svn info'], shell=True, stdout=subprocess.PIPE).communicate()[0]
    revision_info = (re.search(ur"Revision:\s\d+", svn_info))
    if revision_info != None:
        buildNumber = int(revision_info.group().replace("Revision: ", ""))
        print "    SVN revision -> build number: ", buildNumber
    else:
        buildNumber = 0
        print "    Warning: Not SVN, build number: ", 0
    return buildNumber

# ----------------------------------------------
def printDict( vardict ):
    keys = vardict.keys()
    keys.sort()
    for i in keys:
        print '    ', i, '=', vardict[i]
    return

# ----------------------------------------------
def printList( cmds ):
    for cmd in cmds:
        print "    ", cmd
    return

# ----------------------------------------------
def expandTemplateVarDict(vartmp):
    vardict = vartmp.copy()
    keys = vardict.keys()
    for i in keys:
        v = vardict[ i ]
        for j in keys:
            v = v.replace( "{" + j + "}", vardict[j] )
        vardict[ i ] = v

    return vardict

# ----------------------------------------------
def expandTemplateText(template, vardict):
    text = template;
    for k, v in vardict.iteritems():
        text = text.replace("{"+ k +"}", v)
    return text

# ----------------------------------------------
def prepareTargetInfo( target, buildMode, target_inf ):
    tmp = {};
    tmp.update( batch_config.COMMON_VARS )
    tmp.update( batch_config.BUILDMODE_VARS[ buildMode ] )
    tmp.update( batch_config.AUTO_VARS )
    tmp.update( target_inf[ "vars" ] )

    tmp['target'] = target
    tmp['build_mode'] = buildMode

    platform = tmp['platform']
    if platform == 'android':
        tmp['package_ext'] = '.apk'
    elif platform == 'wp8':
        tmp['package_ext'] = '.exe'
    elif platform == 'ios':
        tmp['package_ext'] = '.ipa'
    else:
        print "platform not supported: " + platform
        exit(0)

    vardict = expandTemplateVarDict( expandTemplateVarDict(tmp) )
    target_inf['vars'] = vardict

    pre_cmds = []
    tmp_cmds = target_inf['pre_build_cmds']
    for tmp_cmd in tmp_cmds:
        pre_cmds.append( expandTemplateText(tmp_cmd, vardict) )
    target_inf['pre_build_cmds'] = pre_cmds
    
    post_cmds = []
    tmp_cmds = target_inf['post_build_cmds']
    for tmp_cmd in tmp_cmds:
        post_cmds.append( expandTemplateText(tmp_cmd, vardict) )
    target_inf['post_build_cmds'] = post_cmds
    
    print "---------------------------------------------------------------"
    printDict( vardict )
    print "---------------------------------------------------------------"
    printList( pre_cmds )
    print "---------------------------------------------------------------"
    printList( post_cmds )
    print "---------------------------------------------------------------"
    return
    
# ----------------------------------------------
def main( argv ) :
    # ----------------------------------------------
    batchPyDirPath = os.path.dirname(os.path.realpath(__file__))
    batchPyFile = os.path.basename(__file__)
    n = batchPyDirPath.find("/Assets/")
    if n > 0:
        projPath = batchPyDirPath[0:n]
    else:
        print buildPyFile + " not under Unity project Assets, abort."
        exit(0)

    batch_config.AUTO_VARS['batchpydir_path'] = batchPyDirPath
    batch_config.AUTO_VARS['unityprojdir_path'] = projPath
    batch_config.AUTO_VARS['date'] = datetime.datetime.today().strftime('%Y%m%d')
    batch_config.AUTO_VARS['svn_revision'] = str(getSvnRevision())

    do_clean = False
    do_build = False
    do_archive = False
    buildMode = "debug"

    # ----------------------------------------------
    # parse args to get targets & build mode
    targets = []
    for arg in argv[1:]:
        if arg == "clean":
            do_clean = True
        elif arg == "build":
            do_build = True
        elif arg == "archive":
            do_archive = True
            
        elif arg == "--release" or arg == '-r':
            buildMode="release"
        elif arg == "--debug" or arg == '-d':
            buildMode="debug"
        elif arg == "--daily":
            buildMode="daily"
        
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
        prepareTargetInfo( target, buildMode, target_inf )
        
    # ----------------------------------------------
    # build targets one by one
    if len(targets) > 0:
        print "    Package targets: " + (", ".join(targets))
        print "    Build mode: " + buildMode

    if do_clean:
        for target in targets:
            target_inf = batch_config.TARGET_PACKAGES[ target ]
            targetDirPath = target_inf['vars']['target_path']
            cleanCmd = "rm -r " + targetDirPath
            print "    " + cleanCmd
            if os.path.exists(targetDirPath):
                os.system( cleanCmd )
                pass

    if do_build:
        for target in targets:
            target_inf = batch_config.TARGET_PACKAGES[ target ]
            BuildPackage( target_inf )

    if do_archive:
        for target in targets:
            target_inf = batch_config.TARGET_PACKAGES[ target ]
            ArchivePackage( target_inf )

    print "---------------------------------------------------------------"
    print "----------------------- Done ----------------------------------"
    print "---------------------------------------------------------------"
    return

# ----------------------------------------------
main( sys.argv )
