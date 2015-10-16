#!/usr/bin/env python
# coding=UTF-8

import os

#from Foundation import NSMutableDictionary

# See: https://github.com/kronenthaler/mod-pbxproj
#from mod_pbxproj import XcodeProject

UNITY_SMCS = {
    "common": "-define:LMGAME;",
    "debug":"-define:DEV_VERSION;EnableChinese;", 
    "release":"-define:DISTRIBUTION_VERSION;EnableChinese;CODESTRIPPER;"
}

IOS_PROVISION_PATH = os.path.expanduser("~") +"/Library/MobileDevice/Provisioning Profiles"

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

# build package for every publish channels

TARGET_PACKAGES = {
    "ios" : { # apple app store
        "enabled": True,
        "platform": "ios",
        "name" : "LMDemo",
        "id" : "com.uniq.LMDemo",
        "macro": "LM;AUTOBUILD"
    },
    "android" : { # google play
        "enabled": True,
        "platform": "android",
        "name" : "LMDemo",
        "id" : "com.uniq.LMDemo",
        "macro": "LM"
    },
    "360" : { # qihu 360
        "enabled": False,
        "platform": "android",
        "name" : "LMDemo",
        "id" : "com.uniq.LMDemo.app360",
        "macro" : "FOR_360"
    },
    "xiaomi" : { # xiao mi
        "enabled": False,
        "platform": "android",
        "name" : "LMDemo",
        "id" : "com.uniq.LMDemo.mi",
        "macro": "FOR_XIAOMI"
    }
}

APP_MAJOR_VERSION = "0.5"; # will get build number from svn revision

# icons put under APP_ICON_SPLASH_DIR/<target>/icons/, like
# ./Res/360/icons/Icon-57.png, 
# ./Res/360/splash/Default-568h@2x~iphone, 
APP_ICON_SPLASH_DIR = "/Res"

# actual target will be "/Target/<target>", like ./Target/ios, /Target/360, etc.
TARGET_DIR = "/Target"

# TODO: put all 3pp SDK appid/appkey here

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
    project.add_file('System/Library/Frameworks/CoreTelephony.framework', tree='SDKROOT')
    project.add_file('System/Library/Frameworks/SystemConfiguration.framework', tree='SDKROOT')
    project.add_file('System/Library/Frameworks/UIKit.framework', tree='SDKROOT')
    project.add_file('System/Library/Frameworks/Foundation.framework', tree='SDKROOT')
    project.add_file('System/Library/Frameworks/CoreGraphics.framework', tree='SDKROOT')
    project.add_file('System/Library/Frameworks/CFNetwork.framework', tree='SDKROOT')
    project.add_file('System/Library/Frameworks/StoreKit.framework', tree='SDKROOT')
    project.add_file('System/Library/Frameworks/MobileCoreServices.framework', tree='SDKROOT')
    project.add_file('System/Library/Frameworks/AdSupport.framework', tree='SDKROOT',weak=True)
    project.add_file('usr/lib/libz.dylib', tree='SDKROOT')
    
    # -all_load, some SDK use auto reference counting but some project not, 
    # this link flag will cause duplicated error
    
    # -fembed-bitcode is not supported on versions of iOS prior to 6.0
    # it's required by iWatch APP, but optional for iOS
    project.remove_flags ( {
            'IPHONEOS_DEPLOYMENT_TARGET': '4.3',
            'OTHER_CFLAGS':'-fembed-bitcode',
            'OTHER_LDFLAGS':'-all_load'
        });
    
    project.add_flags( {
            'IPHONEOS_DEPLOYMENT_TARGET': '6.0'
        } )

    return

# ----------------------------------------------
def ModifyPlist( plist, buildMode ):
    # --- Allow HTTP ---
	# Apple made a radical decision with iOS 9, disabling all unsecured HTTP traffic from iOS apps, as a part of App Transport Security.
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










