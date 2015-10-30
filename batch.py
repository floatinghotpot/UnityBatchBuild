#!/usr/bin/env python
# coding=UTF-8

import sys, os, commands
import datetime, time
import re, subprocess
import shutil, glob, zipfile
import smtplib
import requests

from email.mime.text import MIMEText

from Foundation import NSMutableDictionary

# See: https://github.com/kronenthaler/mod-pbxproj
from mod_pbxproj import XcodeProject

# config data
import batch_config

buildPySyntax = ("\nSyntax: batch.py <target> <mode>\n" + 
                 "<target>     ios | android | amazon | 360 | ... | all\n" +
                 "<mode>       --debug | --release | --daily | -d | -r | -l \n" +
                 "<mode>       --no-clean | --no-build | --no-archive | -nc | -nb | -na\n" +
                 "<mode>       --no-email | --no-qq | -ne | -nq\n" +
                "")

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

    cmds = [
        target_inf['vars']['mkdir_targetdir_cmd'],
        target_inf['vars']['unity_cmd']
    ]
    for cmd in cmds:
        print "    " + cmd
        ret = os.system( cmd )
        if ret != 0:
            exitWithMsg(target_inf, ret, cmd)

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
    ret = os.system(xcodeCmd)
    if ret != 0:
        exitWithMsg(target_inf, ret, xcodeCmd)

    #provisionfile = batch_config.DIR_INFO['ios_profile_dir'] + "/" + provision_cert['provision'] + ".mobileprovision"
    #targetProvision = outputApp + "/embedded.mobileprovision"
    #tmpIpa = xcodeprojPath + "/tmp.ipa"
    #rmCmd ="rm -rf " + outputApp + "/_CodeSignature/"
    #cpCmd = "cp \"" + provisionfile + "\" " + targetProvision
    #codesignCmd = "codesign -f -s \"" + provision_cert['cert'] + "\" " + outputApp

    if os.path.exists(vardict['xcode_outapptry']):
        app2ipaCmd = vardict['xcode_apptry2ipa_cmd']
    else:
        app2ipaCmd = vardict['xcode_app2ipa_cmd']
    print "\nRunning command: " + app2ipaCmd
    ret = os.system(  app2ipaCmd )
    if ret != 0:
        exitWithMsg(target_inf, ret, app2ipaCmd)

    print "---------------------------------------------------------------"
    print "------------------ Run Xcode End ------------------------------"
    print "---------------------------------------------------------------"

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
        
    print "Error: target '" + target + "' not configured in TARGET_PACKAGES\n"
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
    tmp.update( batch_config.NOTIFY_VARS )
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
def SendEmail( target_inf, subject, content ):
    vardict = target_inf['vars']
    
    msg = MIMEText( content )
    msg['Subject'] = subject
    msg['From'] = vardict['email_from']
    msg['To'] = vardict['email_to']
    
    s = smtplib.SMTP( vardict['email_smtp_host'] )
    if "email_user" in vardict and "email_passwd" in vardict:
        s.login(vardict["email_user"], vardict["email_passwd"])
        
    print "Sending email to " + vardict['email_to']
    print "---------------------------------------------------------------"
    print( content )
    print "---------------------------------------------------------------"
    s.sendmail(msg['From'], [msg['To']], msg.as_string() )
    s.quit()

    return

def SendQQMsg( target_inf, content ):
    vardict = target_inf['vars']
    r = requests.post(vardict['qqbot_url'], data = {
            "type": vardict['qq_sendtype'],
            "to": vardict['qq_sendto'],
            "msg": content
        })
    print r.text
    return

def sendMsg(target_inf, err, msg):
    vardict = target_inf['vars']
    
    subject = ""
    content = ""
    
    if err == 0:
        package_path = vardict['package']
        if os.path.exists( package_path ):
            filesize = int(os.path.getsize(package_path)/1024/1024)
        else:
            filesize = 0
        
        subject = vardict['success_subject']
        
        content = vardict['success_content']
        content = content.replace('{package_size}',str(filesize))
        content = content.replace('{now}',(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
        
    else:
        subject = vardict['fail_subject']
        
        content = vardict['fail_content']
        content = content.replace('{error_code}',str(err))
        content = content.replace('{error_message}',msg)
        content = content.replace('{now}',(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
            
    if vardict['enable_email'] == 'yes':
        SendEmail(target_inf, subject, content)

    if vardict['enable_qq'] == 'yes':
        SendQQMsg(target_inf, content)

def exitWithMsg( target_inf, err, msg ):
    sendMsg(target_inf, err, msg)
    exit(err)

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

    # ----------------------------------------------
    # parse args to get targets & build mode
    do_clean = True
    do_build = True
    do_archive = True
    do_email = True
    do_qq = True
    buildMode = "daily"
    targets = []
    for arg in argv[1:]:
        if arg == "--release" or arg == '-r':
            buildMode="release"
        elif arg == "--debug" or arg == '-d':
            buildMode="debug"
        elif arg == "--daily" or arg == '-l':
            buildMode="daily"
        
        elif arg == "--no-clean" or arg == "-nc":
            do_clean = False
        elif arg == "--no-build" or arg == '-nb':
            do_build = False
        elif arg == "--no-archive" or arg == '-na':
            do_archive = False
        elif arg == "--no-email" or arg == '-ne':
            do_email = False
        elif arg == "--no-qq" or arg == '-nq':
            do_qq = False
            
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

    # ----------------------------------------------
    if len(targets) > 0:
        print "    Package targets: " + (", ".join(targets))
        print "    Build mode: " + buildMode
    else:
        print buildPySyntax
        print "Error: no package target specified. Abort.\n"
        exit(0)

    batch_config.AUTO_VARS['batchpydir_path'] = batchPyDirPath
    batch_config.AUTO_VARS['unityprojdir_path'] = projPath
    batch_config.AUTO_VARS['date'] = datetime.datetime.today().strftime('%Y%m%d')
    batch_config.AUTO_VARS['svn_revision'] = str(getSvnRevision())
    
    for target in targets:
        target_inf = batch_config.TARGET_PACKAGES[ target ]
        prepareTargetInfo( target, buildMode, target_inf )
        
        if not do_email:
            target_inf['vars']['enable_email'] = "no"

        if not do_qq:
            target_inf['vars']['enable_qq'] = "no"

        if do_clean:
            targetDirPath = target_inf['vars']['target_path']
            cleanCmd = "rm -r " + targetDirPath + "/*"
            print "    " + cleanCmd
            if os.path.exists(targetDirPath):
                os.system( cleanCmd )
            
        if do_build:
            CallUnity( target_inf )
            platform = target_inf['vars']['platform']
            if platform == "ios":
                CallXcodeBuild( target_inf )
                pass
            elif platform == "android":
                pass
            elif platform == "wp8":
                pass
            
        if do_archive:
            cmds = target_inf['post_build_cmds']
            for cmd in cmds:
                print "    " + cmd
                status, output = commands.getstatusoutput( cmd )
                print output
                if status != 0:
                    exitWithMsg(target_inf, status, output)
                    
        sendMsg(target_inf, 0, "ok")

    print "----------------------- Done ----------------------------------"
    print "---------------------------------------------------------------"
    return

# ----------------------------------------------
main( sys.argv )
