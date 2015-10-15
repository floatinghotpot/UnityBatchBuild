
#if UNITY_EDITOR
using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System;
using System.IO;
using System.Text;

using UnityEditor;
using UnityEditor.Callbacks;
using UnityEditor.XCodeEditor;

public static class XcodeBuild {

	public static void Patch( string XcodeProjectPath ) {

		PatchXCProject (XcodeProjectPath);

		PatchPlist (XcodeProjectPath);

		PatchSourceCode (XcodeProjectPath);

	}
	
	public static void PatchXCProject( string pathToBuiltProject ) {
		XCProject project = new XCProject( pathToBuiltProject );

		// TODO implement generic settings as a module option
		// project.overwriteBuildSetting("CODE_SIGN_IDENTITY[sdk=iphoneos*]", "iPhone Distribution", "Release");
		
		// TODO: patch for error: -fembed-bitcode is not supported on versions of iOS prior to 6.0

		// Finally save the xcode project
		project.Save();
		
	}
	
	private static void PatchPlist(string filePath) {
		filePath = filePath + "/Info.plist";

		if( !System.IO.Directory.Exists( filePath ) ) {
			Debug.LogWarning( "Plist path does not exist: " + filePath );
			return;
		}

		XCPlist plist = new XCPlist(filePath);
		Hashtable entries = new Hashtable ();
		plist.Process ( entries );
	}

	private static void PatchSourceCode(string filePath) {
		XClass UnityAppController = new XClass(filePath + "/Classes/UnityAppController.mm");

		// Example: ShareSDK.h
		//UnityAppController.AddBelow("#include \"PluginBase/AppDelegateListener.h\"", "#import <ShareSDK/ShareSDK.h>");
		//UnityAppController.Replace("return YES;", "return [ShareSDK handleOpenURL:url sourceApplication:sourceApplication annotation:annotation wxDelegate:nil];");
		//UnityAppController.AddBelow("UnityCleanup();\n}", @"\r- (BOOL)application:(UIApplication *)application handleOpenURL:(NSURL *)url\r{\rreturn [ShareSDK handleOpenURL:url wxDelegate:nil];\r}\r" );
		
		//UnityAppController.Save();
	}

	public static void Build( string pathToBuiltProject ) {
		// Running: /usr/bin/Xcodebuild build  -project /Users/liming/workspace/LMGame/Client/Target/ios/Unity-iPhone.xcodeproj 

		String build_args = 
			" build " +
				//" analyze " +
				//" archive " +
				" -project " + pathToBuiltProject + "/Unity-iPhone.xcodeproj " +
				//" -list " +
				//" -target Unity-iPhone " +
				//" -scheme Unity-iPhone " + 
				//" -xcconfig configuration.xcconfig " +
				//" -configuration Debug" +
				" -configuration Release" +
				//" PROVISIONING_PROFILE=\"" + PROVISION_CER[bundleIdIndex][1] + "\"" + 
				//" CODE_SIGN_IDENTITY=\"" + PROVISION_CER[bundleIdIndex][2] +
				//" SYMROOT=\"" + dst_root + "\" " +
				//" DSTROOT=\"" + dst_root + "\""
				"";

		System.Diagnostics.Process proc = new System.Diagnostics.Process();
		proc.StartInfo.FileName = "/usr/bin/Xcodebuild";
		proc.StartInfo.Arguments = build_args;
		proc.StartInfo.UseShellExecute = true;
		proc.Start();
		
		proc.WaitForExit();
	}
}

#endif

