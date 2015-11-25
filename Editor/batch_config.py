#!/usr/bin/env python
# coding=UTF-8

import os

# variables:
# {xxx}             -> any key/value defined in TARGET_PACKAGES, name/id/platform/bytes_dirname
#
# for example:
# {unityproj_path}  -> /path/to/unity/project
# {target}          -> ios/android/360/xiaomi/..., the key defined in TARGET_PACKAGES
# {date}            -> YYYYmmdd
# {version}         -> vn.n.build, like v1.0.2134
# {package_ext}     -> ext name of package file, like .ipa, .apk, etc.
# {package}         -> /path/to/target/{name}.{package_ext}
#

# ----------------------------------------------
COMMON_VARS = {
    # app basic info
    "name": "HelloGame",
    "id": "com.rjfun.HelloGame",
    "major_version": "0.5",
    "unity_smcs": "-define:RJFUN;",

    # overwrite by target config
    "target" : "ios",
    "platform": "ios",
    "macro": "RJ"
}

NOTIFY_VARS = {
    # email info, need SMTP server running
    "enable_email": "no",
    "email_smtp_host": "192.168.0.200",
    "email_from": "no-reply@rjfun.com",
    "email_to": "raymond@rjfun.com",
    #"email_user": "no-reply@rjfun.com",
    #"email_passwd": "xxxxx",

    # qq info, need SmartQQ-bot running, see: https://github.com/floatinghotpot/qqbot
    "enable_qq": "no",
    "qq_sendtype": "group",
    "qq_sendto": "272923202",
    "qqbot_url": "http://localhost:3200/send",

    # message
    "success_subject": "[Notify] {name} {target} build success",
    "success_content": (
        "Dear all, the build is successful.\n\n" +
        "Installation package: {archive_download_url}\n\n" +
        "Notice：\n"+
        "Version: {version}\n" +
        "Package size: {package_size} MB\n" +
        "Game server: {gameserver_host}\n" +
        "In-game streaming assets download URL: {asset_download_url}\n\n" +
        "From [SmartQQ-bot]\n" +
        "{now}\n" +
        ""
     ),
    "fail_subject": "[Notify] {name} {target} build failed",
    "fail_content": (
        "Dear all, sorry, the build failed.\n\n" +
        "Error code: {error_code}\n" +
        "Reason: {error_message}\n\n" +
        "From [SmartQQ-bot]\n" +
        "{now}\n" +
        ""
     ),
}

# ----------------------------------------------
BUILDMODE_VARS = {
    "debug": {
        "ios_cert": "iPhone Developer: Raymond Xie (B3YVNBCEFX)",
        "provision_uuid": "3c390fb0-68c1-4613-910d-c67b9ae34991", # dev

        "unity_mode_smcs": "-define:DEV_VERSION;", 
        "unity_cmdflag": "-NoStrip -Development",

        "xcode_cmdflag": "-configuration Debug",
        "xcode_outapp": "{xcodeprojdir_path}/build/Debug-iphoneos/{name}.app",
    },
    "daily": {
        "ios_cert": "iPhone Distribution: Raymond Xie (D92BDUZHUX)",
        "provision_uuid": "1c59430e-a7cc-4b3e-8c1e-f668a25d45df", # adhoc any

        "unity_mode_smcs": "-define:DIST_VERSION;CODESTRIPPER;",
        "unity_cmdflag": "",

        "xcode_cmdflag": "-configuration Release",
        "xcode_outapp": "{xcodeprojdir_path}/build/Release-iphoneos/{name}.app",
    },
    "release": {
        "ios_cert": "iPhone Distribution: Raymond Xie (D92BDUZHUX)",
        "provision_uuid": "1c59430e-a7cc-4b3e-8c1e-f668a25d45de", # adhoc any
        #"provision_uuid": "7b2bc67c-b3a3-41eb-b164-fd70f13154a2", # dist, app-store

        "unity_mode_smcs": "-define:DIST_VERSION;CODESTRIPPER;",
        "unity_cmdflag": "",

        "xcode_cmdflag": "-configuration Release",
        "xcode_outapp": "{xcodeprojdir_path}/build/Release-iphoneos/{name}.app",
    }
}

# ----------------------------------------------
EXTRA_VARS_DEBUG = {
    "email_to": "raymond@rjfun.com",
    "enable_qq": "no",
    # for cmds
    "archive_host": "192.168.0.200",
    "archive_user": "root",
    "archive_dir": "/var/www/html/{name}/{date}",
    "archive_usergroup": "nobody:nogroup",
    "archive_download_url": "http://{archive_host}/{name}/{date}/{archive_name}",

    "assets_host": "192.168.0.200",
    "assets_user": "root",
    "assets_dir": "/var/www/html/{name}/assets",
    "assets_usergroup": "nobody:nogroup",

    # for source code
    "gameserver_host": "192.168.0.200",
    "asset_download_url": "http://{assets_host}/{name}/assets",
}

EXTRA_VARS_DAILY = {
    "email_to": "all@rjfun.com",
    # for cmds
    "archive_host": "192.168.0.200",
    "archive_user": "root",
    "archive_dir": "/var/www/html/{name}/{date}",
    "archive_usergroup": "nobody:nogroup",
    "archive_download_url": "http://{archive_host}/{name}/{date}/{archive_name}",

    "assets_host": "192.168.0.200",
    "assets_user": "root",
    "assets_dir": "/var/www/html/{name}/assets",
    "assets_usergroup": "nobody:nogroup",

    # for source code
    "gameserver_host": "192.168.0.200",
    "asset_download_url": "http://{assets_host}/{name}/assets",
}

EXTRA_VARS_RELEASE = {
    "email_to": "all@rjfun.com",
    # extra vars for cmds or sources
    "archive_host": "192.168.0.200",
    "archive_user": "root",
    "archive_dir": "/var/www/html/{name}/{date}",
    "archive_usergroup": "nobody:nogroup",
    "archive_download_url": "http://{archive_host}/{name}/{date}/{archive_name}",

    "assets_host": "120.24.243.150",
    "assets_user": "root",
    "assets_dir": "/var/www/html/{name}/assets",
    "assets_usergroup": "nobody:nogroup",

    # for source code
    "gameserver_host": "120.24.243.150",
    "asset_download_url": "http://{assets_host}/{name}/assets",
}

BUILDMODE_VARS['debug'].update( EXTRA_VARS_DEBUG )
BUILDMODE_VARS['daily'].update( EXTRA_VARS_DAILY )
BUILDMODE_VARS['release'].update( EXTRA_VARS_RELEASE )

# ----------------------------------------------
AUTO_VARS = {
    # --- auto detect ---
    #"unityprojdir_path" : "",
    #"batchpydir_path" : "",
    #"svn_revision" : "0",
    #"date" : "20150101",
    #"package_ext": ".ipa",
    #"package_size": "0",
    #"now": "2015/10/20 10:10:10",
    
    # auto expand
    "res_dir": "/Res/{target}",
    "target_dir" : "/Target/{target}",
    "target_path" : "{unityprojdir_path}{target_dir}",
    "version": "{major_version}.{svn_revision}",
    "package": "{target_path}/{name}{package_ext}",
    "archive_name": "{name}-{target}-{version}{package_ext}",
    
    # unity related
    "unity_smcs_path": "{unityprojdir_path}/Assets/smcs.rsp",
    "unity_buildmethod": "BatchBuildMenu.BuildConfig",
    "mkdir_targetdir_cmd": "mkdir -p {target_path}",
    "unity_cmd": "/Applications/Unity/Unity.app/Contents/MacOS/Unity -projectPath {unityprojdir_path} -executeMethod {unity_buildmethod} {unity_cmdflag} -batchmode -quit -logFile",
    
    # xcode related
    "xcodeprojdir_path": "{target_path}",
    "xcodeplist_path": "{target_path}/Info.plist",
    "xcode_pbxproj_path": "{xcodeprojdir_path}/Unity-iPhone.xcodeproj/project.pbxproj",
    "xcode_cmd": "/usr/bin/xcodebuild clean build -project {xcodeprojdir_path}/Unity-iPhone.xcodeproj PROVISIONING_PROFILE=\"{provision_uuid}\" CODE_SIGN_IDENTITY=\"{ios_cert}\" {xcode_cmdflag}",
    
    "xcode_outapptry": "{xcodeprojdir_path}/build/{name}.app",
    "xcode_outipa": "{xcodeprojdir_path}/{name}.ipa",
    "xcode_apptry2ipa_cmd": "/usr/bin/xcrun -sdk iphoneos PackageApplication -v {xcode_outapptry} -o {xcode_outipa}",
    "xcode_app2ipa_cmd": "/usr/bin/xcrun -sdk iphoneos PackageApplication -v {xcode_outapp} -o {xcode_outipa}",
}

# ----------------------------------------------
SOURCE_FILES = [
    # this file is required by batch build menu (unity editor only)
    {
    "filepath": "{batchpydir_path}/BatchBuildConfig.cs",
    "content": (
        "// NOTICE: Auto overwritten with batch.py when build package. Do not edit !!!\n" +
        "public class BatchBuildConfig {\n" +
        "   public static string APP_NAME = \"{name}\";\n" +
        "   public static string APP_ID = \"{id}\";\n" +
        "   public static string APP_VERSION = \"{version}\";\n" +
        "   public static string PLATFORM = \"{platform}\";\n" +
        "   public static string TARGET_DIR = \"{target_dir}\";\n" +
        "   public static string DEFINE_MACRO = \"{macro}\";\n" +
        "}"),
    },
    # this file is optional, can be referenced in your code
    {
    "filepath": "{unityprojdir_path}/Assets/Script/Config/BuildSystemConfig.cs",
    "content": (
        "// NOTICE: Auto overwritten with batch.py when build package. Do not edit !!!\n" +
        "public class BuildSystemConfig {\n" +
        "    public static string GAME_SERVER_HOST = \"{gameserver_host}\";\n" +
        "    public static string ASSETS_DOWNLOAD_URL = \"{asset_download_url}\";\n" +
        "    public static string BUILD_VERSION = \"{version}\";\n" +
        "}\n"),
    },
]

PRE_BUILD_CMDS = [
    "ls {unityprojdir_path}",
]

# ----------------------------------------------
# after build, script to copy the packages to remote host
#
# if use ssh/scp without password, need setup user ssh pub key to <host>/~/.ssh/authorized_keys
# if you need copy to public folder, may need put ssh pub key to <host>:<root_home>/.ssh/authorized_keys

PACK_ASSETS_CMDS = [
    # --- package streaming assets to tgz ---
    "mkdir ./{bytes_dirname}",
    "cp {unityprojdir_path}/Assets/StreamingAssets/{bytes_dirname}/* ./{bytes_dirname}",
    "tar cfz {target_path}/{target}-bytes.tgz {bytes_dirname}",
    "rm -r ./{bytes_dirname}",
    "ls -la {target_path}/{target}-bytes.tgz",
]

ARCHIVE_CMDS = [
    "ls -la {package}",
    "ssh {archive_user}@{archive_host} 'mkdir -p {archive_dir}'",
    "scp {package} {archive_user}@{archive_host}:{archive_dir}/{name}-{target}-{version}{package_ext}",
    "scp {target_path}/{target}-bytes.tgz {archive_user}@{archive_host}:{archive_dir}/{name}-{target}-{version}.tgz",
    "ssh {archive_user}@{archive_host} 'chown -R {archive_usergroup} {archive_dir}; ls -la {archive_dir}'",
]

DEPLOY_ASSETS_CMDS = [
    "ssh {assets_user}@{assets_host} 'mkdir -p {assets_dir}'",
    "scp {target_path}/{target}-bytes.tgz {assets_user}@{assets_host}:{assets_dir}/{target}-bytes.tgz",
    "ssh {assets_user}@{assets_host} 'cd {assets_dir}; rm -rf ./{bytes_dirname}; tar xvf {target}-bytes.tgz; chown -R {assets_usergroup} {bytes_dirname}; rm {target}-bytes.tgz; ls -la;'",
]

POST_BUILD_CMDS = PACK_ASSETS_CMDS + ARCHIVE_CMDS + DEPLOY_ASSETS_CMDS

# ----------------------------------------------
# build package for every publish channels
TARGET_PACKAGES = {
    "ios" : { # apple app store
        "enabled": True,
        "vars": {
            "platform": "ios",
            "macro": "FOR_IOS",
            "bytes_dirname": "iPhone",
        },
        "pre_build_cmds": PRE_BUILD_CMDS + [],
        "post_build_cmds": POST_BUILD_CMDS + [
            "echo 'do something else for {target}'"
        ]
    },
    "android" : { # google play
        "enabled": True,
        "vars": {
            "platform": "android",
            "macro": "FOR_ANDROID",
            "bytes_dirname": "Android",
        },
        "pre_build_cmds": PRE_BUILD_CMDS + [],
        "post_build_cmds": POST_BUILD_CMDS + [
            "echo 'do something else for {target}'"
        ]
    },
    "amazon" : { # amazon
        "enabled": False,
        "vars": {
            "id" : "com.rjfun.pokerking.amazon",
            "platform": "android",
            "macro": "FOR_AMAZON",
            "bytes_dirname": "Android",
        },
        "pre_build_cmds": PRE_BUILD_CMDS + [],
        "post_build_cmds": POST_BUILD_CMDS + [
            "echo 'do nothing for {target}'"
        ]
    },
    "360" : { # qihu 360
        "enabled": False,
        "vars": {
            "id" : "com.rjfun.pokerking.app360",
            "platform": "android",
            "macro": "FOR_360",
            "bytes_dirname": "Android",
        },
        "pre_build_cmds": PRE_BUILD_CMDS + [],
        "post_build_cmds": POST_BUILD_CMDS + [
            "echo 'do nothing for {target}'"
        ]
    },
}

# ----------------------------------------------
# put all 3pp SDK appid/appkey here
SDK_3PP_IOS = {
    "QQ" : {
        "enabled" : False,
        "appid" : "tencent100703379",
        "appkey" : "4578e54fb3a1bd18e0681bc1c734514e"
    },
    "weixin" : {
        "enabled" : False,
        "appid" : "wx5923bbc6094cc763",
        "appkey" : "eea65831dbb5eb81439bcc2e1adb3dbc"
    },
    "tencentopenapi" : {
        "enabled" : False,
        "appid" : "QQ0600678E",
        "appkey" : ""
    },
    "dengta" : {
        "enabled" : False,
        "appid" : "1001",
        "appkey" : "0I4007GJN70PS0PW"
    }
}

SDK_3PP_ANDROID = {
    "QQ" : {
        "enabled" : False,
        "appid" : "tencent100703379",
        "appkey" : "4578e54fb3a1bd18e0681bc1c734514e"
    },
    "weixin" : {
        "enabled" : False,
        "appid" : "wx5923bbc6094cc763",
        "appkey" : "eea65831dbb5eb81439bcc2e1adb3dbc"
    }
}

# ----------------------------------------------
def ModifyXcodeProject( project, buildMode ):
    # add System Framework
    project.add_file('System/Library/Frameworks/SystemConfiguration.framework', tree='SDKROOT')
    project.add_file('System/Library/Frameworks/Foundation.framework', tree='SDKROOT')
    project.add_file('System/Library/Frameworks/StoreKit.framework', tree='SDKROOT')
    #project.add_file('usr/lib/libz.dylib', tree='SDKROOT')
    
    # -all_load, some SDK use auto reference counting but some project not, 
    # this link flag will cause duplicated error
    
    # -fembed-bitcode is not supported on versions of iOS prior to 6.0
    # it's required by iWatch APP, but optional for iOS
    project.remove_flags ( {
            'ENABLE_BITCODE' : 'YES',
            #'ARCHS' : 'arm7v',
            'IPHONEOS_DEPLOYMENT_TARGET': '4.3',
            'OTHER_LDFLAGS':'-all_load'
        } );
    
    project.add_flags( {
            'ENABLE_BITCODE' : 'NO',
            #'ARCHS' : '$(ARCHS_STANDARD)',
            'IPHONEOS_DEPLOYMENT_TARGET': '6.0'
        } )

    return

# ----------------------------------------------
def ModifyPlist( plist, buildMode ):
    # landscape orientation only
    plist['UISupportedInterfaceOrientations'] = [
        'UIInterfaceOrientationLandscapeLeft',
        'UIInterfaceOrientationLandscapeRight',
    ];
    
    # --- Allow HTTP ---
    # Apple made a radical decision with iOS 9, disabling all unsecured HTT.
    plist['NSAppTransportSecurity'] = { 'NSAllowsArbitraryLoads':True }

    url_types = []
    
    # ----------------------------------------------
    need_msdk = False
    # --- QQ ---
    QQ = SDK_3PP_IOS['QQ']
    if QQ != None and QQ['enabled']:
        need_msdk = True
        plist['QQAppID'] = QQ['appid'][7:]
        plist['QQAppKey'] = QQ['appkey']
        url_types.append({
                'CFBundleTypeRole':'Editor',
                'CFBundleURLName':'QQ',
                'CFBundleURLSchemes':[ QQ['appid'] ]})
    
    # -- weixin --
    weixin = SDK_3PP_IOS['weixin']
    if weixin != None and weixin['enabled']:
        need_msdk = True
        plist['WXAppID'] = weixin['appid']
        plist['WXAppKey'] = weixin['appkey']
        url_types.append({
                'CFBundleTypeRole':'Editor',
                'CFBundleURLName':'weixin',
                'CFBundleURLSchemes':[ weixin['appid'] ]})
    
    # -- Tencent MSDK ---
    tencentopenapi = SDK_3PP_IOS['tencentopenapi']
    dengta = SDK_3PP_IOS['dengta']
    if tencentopenapi != None and tencentopenapi['enabled']:
        need_msdk = True
        plist['CHANNEL_DENGTA'] = dengta['appid']
        plist['APPKEY_DENGTA'] = dengta['appkey']
        url_types.append({
                'CFBundleTypeRole':'Editor',
                'CFBundleURLName':'tencentopenapi',
                'CFBundleURLSchemes':[ tencentopenapi['appid'] ]})

    if need_msdk:
        if buildMode != "distribution":
            plist['MSDK_URL'] = "http://msdktest.qq.com"
        else:
            plist['MSDK_URL'] = "http://msdk.qq.com"
    # ----------------------------------------------

    # TODO: --- add more SDK content here ---
            
    # ----------------------------------------------
    if len(url_types) > 0:
        plist['CFBundleURLTypes'] = url_types
    
    return










