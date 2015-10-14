using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.IO;

namespace UnityEditor.XCodeEditor
{
	public partial class XClass : System.IDisposable
	{
		private string filePath;
		private string fileContent;
		
		public XClass(string fPath)
		{
			filePath = fPath;
			if( !System.IO.File.Exists( filePath ) ) {
				Debug.LogError( "Not found file: " + filePath );
				return;
			}

			StreamReader streamReader = new StreamReader(filePath);
			fileContent = streamReader.ReadToEnd();
			streamReader.Close();
		}
		
		public void AddBelow(string below, string text)
		{
			int beginIndex = fileContent.IndexOf(below);
			if(beginIndex == -1){
				Debug.LogError("Not found code: " + below + " in " + filePath);
				return; 
			}
			
			int endIndex = fileContent.LastIndexOf("\n", beginIndex + below.Length);
			fileContent = fileContent.Substring(0, endIndex) + "\n"+text+"\n" + fileContent.Substring(endIndex);
		}
		
		public void Replace(string below, string newText)
		{
			int beginIndex = fileContent.IndexOf(below);
			if(beginIndex == -1){
				Debug.LogError("Not found code: " + below + " in " + filePath);
				return; 
			}
			
			fileContent =  fileContent.Replace(below,newText);

		}

		public void Save() {
			StreamWriter streamWriter = new StreamWriter(filePath);
			streamWriter.Write(fileContent);
			streamWriter.Close();
		}
		
		public void Dispose()
		{
			
		}
	}
}
