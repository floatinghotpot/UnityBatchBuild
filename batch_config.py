#!/usr/bin/env python
# coding=UTF-8

import os

UNITY_SMCS = {
    "common": "-unsafe\n-define:LMGAME;",
    "debug":"-define:DEV_VERSION;EnableChinese;", 
    "release":"-define:DISTRIBUTION_VERSION;EnableChinese;CODESTRIPPER;"
}

# ----------------------------------------------
IOS_PROVISION_CERT = {
    "debug": {
        "id": "com.uniq.LMDemo", 
        "provision": "08cb9450-c4b4-4a56-8123-8cf1b46d7e56",
        "cert": "iPhone Developer: Liming Xie (B3YVNBCEFU)"
    },
    "release": {
        "id": "com.uniq.LMDemo", 
        "provision": "aedff668-2431-4f2d-9199-c87c5a25be91",
        "cert": "iPhone Distribution: Liming Xie (D92BDUZHUG)"
    }
}

# ----------------------------------------------
APP_MAJOR_VERSION = "0.5"; # will get build number from svn revision

# ----------------------------------------------
DIR_INFO = {
    # icons put under APP_ICON_SPLASH_DIR/<target>/icons/, like
    # ./Res/360/icons/Icon-57.png, 
    # ./Res/360/splash/Default-568h@2x~iphone, 
    "res_dir": "/Res",
    
    # target build projects will be "/Target/<target>", like ./Target/ios, /Target/360, etc.
    "target_dir": "/Target",
    
    # xcode provision files located here, by default
    "ios_profile_dir": os.path.expanduser("~") +"/Library/MobileDevice/Provisioning Profiles"
}

# ----------------------------------------------
# after build, script to copy the packages to remote host
#
# variables:
# {unityproj_path}  -> /path/to/unity/project
# {target}          -> ios/android/360/xiaomi/..., the key defined in TARGET_PACKAGES
# {xxx}             -> any key/value defined in TARGET_PACKAGES, name/id/platform/bytes_dirname
# {date}            -> YYYYmmdd
# {version}         -> vn.n.build, like v1.0.2134
# {package_ext}     -> ext name of package file, like .ipa, .apk, etc.
# {package}         -> /path/to/target/{name}.{package_ext}
#
POST_BUILD_SCRIPTS = {
    "enabled": True,
    "debug": [
        "ls -la {package}",
        "scp {package} raymond@192.168.0.200:~/tmp/{name}-{target}-{version}{package_ext}",
        
        # --- package streaming assets to tgz ---
        #"mkdir ./{bytes_dirname}",
        #"cp {unityproj_path}/Assets/StreamingAssets/{bytes_dirname}/* ./{bytes_dirname}",
        #"tar cfz {target_path}/bytes.tgz {bytes_dirname}",
        #"rm -r ./{bytes_dirname}",
        #"ls -la {target_path}/bytes.tgz",
        #"scp {target_path}/bytes.tgz raymond@192.168.0.200:~/tmp/{name}-{target}-{version}.tgz",
        
        "ssh raymond@192.168.0.200 'ls -la ~/tmp'"
    ],
    "release": [
        # if use ssh/scp without password, need setup user ssh pub key to <host>/~/.ssh/authorized_keys
        # if you need copy to public folder, may need put ssh pub key to <host>:<root_home>/.ssh/authorized_keys
        
        # --- archive package ---
        "ls -la {package}",
        #"ssh root@192.168.0.200 'mkdir -p /home/public/版本归档/{date}'",
        #"scp {package} root@192.168.0.200:/home/public/版本归档/{date}/{name}-{version}.{package_ext}",
        #"scp {target_path}/bytes.tgz root@192.168.0.200:/home/public/版本归档/{date}/{target}-{version}.tgz"
        #"ssh root@192.168.0.200 'chown -R nobody:nogroup /home/public/版本归档/{date}'",
        
        # --- package streaming assets to tgz ---
        #"mkdir ./{bytes_dirname}",
        #"cp {unityproj_path}/Assets/StreamingAssets/{bytes_dirname}/* ./{bytes_dirname}",
        #"tar cfz {target_path}/bytes.tgz {bytes_dirname}",
        #"rm -r ./{bytes_dirname}",
        #"ls -la {target_path}/bytes.tgz",

        # --- upload streaming assets tgz to update server ---
        #"scp bytes.tgz root@us.rjfun.com:/var/www/html/bytes.tgz",
        #"ssh root@us.rjfun.com 'cd /var/www/html; rm -r {bytes_dirname}; tar xvf bytes.tgz; chown -R nobody:nogroup {bytes_dirname};'",
        
    ]
}

# ----------------------------------------------
# build package for every publish channels
TARGET_PACKAGES = {
    "ios" : { # apple app store
        "enabled": True,
        "platform": "ios",
        "name" : "LMDemo",
        "id" : "com.uniq.LMDemo",
        "macro": "LM;AUTOBUILD",
        "bytes_dirname": "iPhone" # see: /Assets/StreamingAssets/ and download URL
    },
    "android" : { # google play
        "enabled": True,
        "platform": "android",
        "name" : "LMDemo",
        "id" : "com.uniq.LMDemo",
        "macro": "LM",
        "bytes_dirname": "Android",
    },
    "360" : { # qihu 360
        "enabled": False,
        "platform": "android",
        "name" : "LMDemo",
        "id" : "com.uniq.LMDemo.app360",
        "macro" : "FOR_360",
        "bytes_dirname": "Android",
        "post_build_cmds": {
            "enabled": False
            # override the default post build scripts
        }
    },
    "xiaomi" : { # xiao mi
        "enabled": False,
        "platform": "android",
        "name" : "LMDemo",
        "id" : "com.uniq.LMDemo.mi",
        "macro": "FOR_XIAOMI",
        "bytes_dirname": "Android",
        "post_build_cmds": {
            "enabled": False
            # override the default post build scripts
        }
    }
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
            'ARCHS' : 'arm7v',
            'IPHONEOS_DEPLOYMENT_TARGET': '4.3',
            'OTHER_LDFLAGS':'-all_load'
        } );
    
    project.add_flags( {
            'ENABLE_BITCODE' : 'NO',
            'ARCHS' : '$(ARCHS_STANDARD)',
            'IPHONEOS_DEPLOYMENT_TARGET': '6.0'
        } )

    return

# ----------------------------------------------
def ModifyPlist( plist, buildMode ):
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










