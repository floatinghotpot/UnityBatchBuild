#if UNITY_EDITOR

using UnityEngine;
using System.Collections;
using UnityEditor;

public class BatchBuildConfig {

	// --- common constants ---

	public static string XCODEBUILD_CLI = "/usr/bin/Xcodebuild";
	
	public static string PROJECT_PATH = Application.dataPath.Replace("/Assets", "");

	public static string TARGET_PATH = PROJECT_PATH + "/Target";
	public static string TARGET_PATH_ANDROID = TARGET_PATH + "/android";
	public static string TARGET_PATH_IOS = TARGET_PATH + "/ios";
	public static string TARGET_PATH_WP8 = TARGET_PATH + "/wp8";

	// --- modify for your purpose ---

	public static string SCRIPT_DEFINE_SYMBOL = "LM";
	
	public static string[] SCENES = {
		// add your scene here
	};

	public static string[] SMCS_MODES = {
		"-define:DEV_VERSION;EnableChinese;",    // debug
	    "-define:RELEASE_VERSION;EnableChinese;",   //release or daily
		"-define:DISTRIBUTION_VERSION;EnableChinese;CODESTRIPPER;" //distribution
	};

	public static string[] PROVISION_CER = {
		// change to your own provisioning file and certificate
		"com.company.app",
		"420a97b6-99ea-48f9-ac2b-5c5032e0ea66",
		"iPhone Developer: Your Name (GA52LZZ6A3)"
	};

	public static string APP_NAME = "LMDemo";
	public static string APP_ID = "com.uniq.LMDemo";
	public static string APP_VERSION = "v0.1.0";
	
	[MenuItem ("MyTools/Build Android")] 
	public static void BuildAndroid () 
	{  
		// TODO: AssetBundleBuildConfig.buildAndroidAssetBundle();
		
		BatchBuild.Build ( 
		                  BatchBuildConfig.APP_NAME, 
		                  BatchBuildConfig.APP_ID, 
		                  BatchBuildConfig.APP_VERSION, 
		                  BuildTarget.Android, 
		                  BuildOptions.Development | BuildOptions.ConnectWithProfiler);
	} 
	
	[MenuItem ("MyTools/Build IOS")] 
	public static void BuildIOS () 
	{          
		BatchBuild.Build ( 
		                  BatchBuildConfig.APP_NAME, 
		                  BatchBuildConfig.APP_ID, 
		                  BatchBuildConfig.APP_VERSION, 
		                  BuildTarget.iOS, 
		                  BuildOptions.Development | BuildOptions.ConnectWithProfiler);
	}
	
	[MenuItem ("MyTools/Build WP8")]
	public static void BuildWP8()
	{
		// TODO: AssetBundleBuildConfig.buildWP8AssetBundle();
		
		BatchBuild.Build ( 
		                  BatchBuildConfig.APP_NAME, 
		                  BatchBuildConfig.APP_ID, 
		                  BatchBuildConfig.APP_VERSION, 
		                  BuildTarget.WP8Player, 
		                  BuildOptions.Development | BuildOptions.ConnectWithProfiler);
	}
	
	[MenuItem ("MyTools/Build All")]
	public static void BuildAll() {
		BuildIOS ();
		BuildAndroid ();
	}
}

#endif
