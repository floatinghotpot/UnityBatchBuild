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
    "name": "PokerKing",
    "id": "com.rjfun.pokerking",
    "major_version": "0.5",
    "unity_smcs": "-define:MYGAME;EnableChinese;",
    
    # overwrite by target config
    "target" : "ios",
    "platform": "ios",
    "macro": "LM"
}

NOTIFY_VARS = {
    # email info
    "enable_email": "no",
    "email_smtp_host": "192.168.0.200",
    "email_from": "no-reply@rjfun.com",
    "email_to": "all@rjfun.com",
    #"email_user": "no-reply@rjfun.com",
    #"email_passwd": "xxxxx",
    
    # qq info
    "enable_qq": "no",
    
    # message
    "success_subject": "[Good news] {name} {target} Build Success",
    "success_content": (
        "Dir all,\n\n" +
        "Congratulations, the build is succesful.\n\n" +
        "Packge download URL: {archive_download_url}\n\n" +
        "Note: \n"+
        "Version: {version}\n" +
        "Size: {package_size} MB\n" +
        "From [BatchBuild]\n" +
        "{now}\n" +
        ""
     ),
    "fail_subject": "[Bad news] {name} {target} Build Failed",
    "fail_content": (
        "Dear all,\n\n" +
        "Sorry, the build failed!\n\n" +
        "Error Code: {error_code}\n" +
        "Reason: {error_message}\n\n" +
        "From [BatchBuild]\n" +
        "{now}\n" +
        ""
     ),
}

# ----------------------------------------------
BUILDMODE_VARS = {
    "debug": {
        "ios_cert": "iPhone Developer: Liming Xie (B3YVNBCEFU)",
        "provision_uuid": "08cb9450-c4b4-4a56-8123-8cf1b46d7e56",
        
        "unity_mode_smcs": "-define:DEV_VERSION;", 
        "unity_cmdflag": "-NoStrip -Development",
        
        "xcode_cmdflag": "-configuration Debug",
        "xcode_outapp": "{xcodeprojdir_path}/build/Debug-iphoneos/{name}.app",
    },
    "release": {
        "ios_cert": "iPhone Distribution: Liming Xie (D92BDUZHUG)",
        "provision_uuid": "aedff668-2431-4f2d-9199-c87c5a25be91",
        
        "unity_mode_smcs": "-define:DIST_VERSION;CODESTRIPPER;",
        "unity_cmdflag": "",
        
        "xcode_cmdflag": "-configuration Release",
        "xcode_outapp": "{xcodeprojdir_path}/build/Release-iphoneos/{name}.app",
    },
}

BUILDMODE_VARS["daily"] = BUILDMODE_VARS["release"].copy()

# ----------------------------------------------
EXTRA_VARS_DEBUG = {
    # for cmds
    "archive_host": "localhost",
    "archive_user": "liming",
    "archive_dir": "~/tmp",
    "archive_usergroup": "liming:staff",

    "assets_host": "192.168.0.200",
    "assets_user": "liming",
    "assets_dir": "~/public_html",
    "assets_usergroup": "liming:staff",

    # for source code
    "gameserver_host": "192.168.0.200",
    "asset_download_url": "http://{assets_host}/~{assets_user}",
}

EXTRA_VARS_DAILY = {
    # for cmds
    "archive_host": "192.168.0.200",
    "archive_user": "root",
    "archive_dir": "/var/www/html/{date}",
    "archive_usergroup": "nobody:nogroup",
    "archive_download_url": "http://{archive_host}/{date}/{archive_name}",

    "assets_host": "192.168.0.200",
    "assets_user": "root",
    "assets_dir": "/var/www/html/assets",
    "assets_usergroup": "nobody:nogroup",

    # for source code
    "gameserver_host": "192.168.0.200",
    "asset_download_url": "http://{assets_host}/assets",
}

EXTRA_VARS_RELEASE = {
    # for cmds
    "archive_host": "192.168.0.200",
    "archive_user": "root",
    "archive_dir": "/var/www/html/{date}",
    "archive_usergroup": "nobody:nogroup",
    "archive_download_url": "http://{archive_host}/{date}/{archive_name}",

    "assets_host": "192.168.0.200",
    "assets_user": "root",
    "assets_dir": "/var/www/html/assets",
    "assets_usergroup": "nobody:nogroup",

    # for source code
    "gameserver_host": "192.168.0.200",
    "asset_download_url": "http://{assets_host}/assets",
}

BUILDMODE_VARS['debug'].update(EXTRA_VARS_DEBUG)
BUILDMODE_VARS['daily'].update(EXTRA_VARS_DAILY)
BUILDMODE_VARS['release'].update(EXTRA_VARS_RELEASE)

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
    {
    "filepath": "{batchpydir_path}/BatchBuildConfig.cs",
    "content": (
        "// NOTICE: Auto overwritten with batch.py. Do not edit !!!\n" +
        "public class BatchBuildConfig {\n" +
        "   public static string APP_NAME = \"{name}\";\n" +
        "   public static string APP_ID = \"{id}\";\n" +
        "   public static string APP_VERSION = \"{version}\";\n" +
        "   public static string PLATFORM = \"{platform}\";\n" +
        "   public static string TARGET_DIR = \"{target_dir}\";\n" +
        "   public static string DEFINE_MACRO = \"{macro}\";\n" +
        "}"),
    }
]

# ----------------------------------------------
# after build, script to copy the packages to remote host
#
# if use ssh/scp without password, need setup user ssh pub key to <host>/~/.ssh/authorized_keys
# if you need copy to public folder, may need put ssh pub key to <host>:<root_home>/.ssh/authorized_keys

PACK_ASSETS_CMDS = [
    # --- package streaming assets to tgz ---
    "mkdir ./{bytes_dirname}",
    #"cp {unityproj_path}/Assets/StreamingAssets/{bytes_dirname}/* ./{bytes_dirname}",
    "tar cfz {target_path}/bytes.tgz {bytes_dirname}",
    "rm -r ./{bytes_dirname}",
    "ls -la {target_path}/bytes.tgz",
]

ARCHIVE_CMDS = [
    "ls -la {package}",
    "ssh {archive_user}@{archive_host} 'mkdir -p {archive_dir}'",
    "scp {package} {archive_user}@{archive_host}:{archive_dir}/{name}-{target}-{version}{package_ext}",
    "scp {target_path}/bytes.tgz {archive_user}@{archive_host}:{archive_dir}/{name}-{target}-{version}.tgz",
    "ssh {archive_user}@{archive_host} 'chown -R {archive_usergroup} {archive_dir}; ls -la {archive_dir}'",
]

DEPLOY_ASSETS_CMDS = [
    "ssh {assets_user}@{assets_host} 'mkdir -p {assets_dir}'",
    "scp {target_path}/bytes.tgz {assets_user}@{assets_host}:{assets_dir}/bytes.tgz",
    "ssh {assets_user}@{assets_host} 'cd {assets_dir}; rm -rf ./{bytes_dirname}; tar xvf bytes.tgz; chown -R {assets_usergroup} {bytes_dirname}; rm bytes.tgz; ls -la;'",
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
            "channel": "appstore",
        },
        "pre_build_cmds": [],
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
            "channel": "googleplay",
        },
        "pre_build_cmds": [],
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
            "channel": "amazon_appstore",
        },
        "pre_build_cmds": [],
        "post_build_cmds": [
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
            "channel": "360_appstore",
        },
        "pre_build_cmds": [],
        "post_build_cmds": [
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










