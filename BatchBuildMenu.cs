
#if UNITY_EDITOR
using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System;
using System.IO;
using System.Text;

using UnityEditor;

public class BatchBuildMenu : MonoBehaviour {

	[MenuItem ("LMTools/Build Android")] 
	public static void BuildAndroid () 
	{  
		// TODO: AssetBundleBuildConfig.buildAndroidAssetBundle();

		BatchBuild.Build ("LMAndroidDemo", 
		              "com.uniq.LMDemo", 
		              "v0.1.0", 
		              BuildTarget.Android, 
		              BuildOptions.Development | BuildOptions.ConnectWithProfiler);
	} 

	[MenuItem ("LMTools/Build IOS")] 
	public static void BuildIOS () 
	{          
		BatchBuild.Build ("LMIOSDemo", 
		              "com.uniq.LMDemo", 
		              "v0.1.0", 
		              BuildTarget.iPhone, 
		              BuildOptions.Development | BuildOptions.ConnectWithProfiler);
	}

	[MenuItem ("LMTools/Build WP8")]
    public static void BuildWP8()
    {
        // TODO: AssetBundleBuildConfig.buildWP8AssetBundle();

		BatchBuild.Build ("LMWP8Demo", 
		              "com.uniq.LMDemo",
		              "v0.1.0", 
		              BuildTarget.WP8Player, 
		              BuildOptions.Development | BuildOptions.ConnectWithProfiler);
    }

	[MenuItem ("LMTools/Build All")]
	public static void BuildAll() {
		BuildIOS ();
		BuildAndroid ();
	}
}

#endif
