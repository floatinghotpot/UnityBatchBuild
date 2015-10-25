#if UNITY_EDITOR

using UnityEngine;
using System.Collections;
using UnityEditor;

public class BatchBuildMenu {
	
	// --- modify for your purpose ---
	
	public static string[] SCENES = {
		// add your scene here
	};
	
	// --- build method & menu ---
	
	[MenuItem ("LMTools/Build Android")] 
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
	
	[MenuItem ("LMTools/Build IOS")] 
	public static void BuildIOS () 
	{          
		BatchBuild.Build ( 
		                  BatchBuildConfig.APP_NAME, 
		                  BatchBuildConfig.APP_ID, 
		                  BatchBuildConfig.APP_VERSION, 
		                  BatchBuild.BuildTarget_iOS, 
		                  BuildOptions.Development | BuildOptions.ConnectWithProfiler);
	}
	
	[MenuItem ("LMTools/Build WP8")]
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

	[MenuItem ("LMTools/Build Current Configured")]
	public static void BuildConfig()
	{
		switch (BatchBuildConfig.PLATFORM) {
		case "ios":
			BuildIOS();
			break;
		case "android":
			BuildAndroid();
			break;
		case "wp8":
			BuildWP8();
			break;
		default:
			break;
		}
	}
}

#endif
