import subprocess
import os
import re
import json

class SystemUtils():

	def listFoldersAndFiles(self,path):

		currentDir = os.getcwd()
		os.chdir(path)
		
		fileInfo = {'id':'','name':'','path':''}
		dirInfo = {'id':'','name':'','children':[]}
		rootTree = {'id':'','name':'','children':[]}
		x=0
		rootScan = True
		for root, directories, filenames in os.walk('.'):
			directories[:] = [d for d in directories if not d.startswith('.')]

			if(rootScan):
				rootTree['id']=x+1
				rootTree['name']= root
				rootTree['type']= 'dir'
			else:
				for child in rootTree['children']:
					dirInfo = self.findChildren(root,rootTree)

				
			for directory in directories:
			
				subdirInfo = {'id':'','name':'','children':[]}
				subdirInfo['id']=directory
				subdirInfo['name']= directory
				subdirInfo['type']= 'dir'
		
				if(rootScan):
					rootTree['children'].append(subdirInfo)
				else:	
					dirInfo['children'].append(subdirInfo)
			
			for filename in filenames:
		
				fileInfo['name'] = filename
				fileInfo['id'] = os.path.join(root,filename)
				fileInfo['path'] = os.path.join(root,filename)
		
				if(rootScan):
					rootTree['children'].append(fileInfo)
				else:
					dirInfo['children'].append(fileInfo)
		
				fileInfo={'id':'','name':'','path':''}
			x = x+1
			rootScan = False
		
		#print json.dumps(rootTree,indent=4, sort_keys=False)
		#return json.dumps(rootTree)
		os.chdir(currentDir)
		return rootTree
		
	def findChildren(self,path,rootTree):

		temp = path.replace("./", "")
		if(temp.find("/") == -1):
			for child in rootTree['children']:
				if(child['name'] == temp.replace("./", "")):
					return child
		else:
			for child in rootTree['children']:
				if(child['name'] == temp[0:temp.find("/")]):
					return self.findChildren(temp[temp.find("/")+1:],child)

	def getGitStatus(self,path):
		currentDir = os.getcwd()
		os.chdir(path)
		subprocessPopen = subprocess.Popen(["git","status", "-s", "--untracked-files=all"], stdout=subprocess.PIPE)
		stdout,stderr = subprocessPopen.communicate()
		lines = stdout.split('\n')
		os.chdir(currentDir)
		return lines

	def getGitBrachName(self,path):
		currentDir = os.getcwd()
		os.chdir(path)
		subprocessPopen = subprocess.Popen(["git","branch"], stdout=subprocess.PIPE)
		stdout,stderr = subprocessPopen.communicate()
		lines = stdout.split('\n')
		os.chdir(currentDir)
		return lines[0].replace("* ","")
		
	def getGitFileDiff(self,path,fileName):
		currentDir = os.getcwd()
		os.chdir(path)
		subprocessPopen = subprocess.Popen(["git","diff",fileName], stdout=subprocess.PIPE)
		stdout,stderr = subprocessPopen.communicate()
		lines = stdout.split('\n')
		os.chdir(currentDir)
		return lines

	def addFileGit(self,path,fileName):
		currentDir = os.getcwd()
		os.chdir(path)
		subprocessPopen = subprocess.Popen(["git","add",fileName], stdout=subprocess.PIPE)
		stderr = subprocessPopen.communicate()
		os.chdir(currentDir)
		if stderr is None:
			return "File added successfully"
		else:
			return stderr

	def removeFileGit(self,path,fileName):
		currentDir = os.getcwd()
		os.chdir(path)
		print fileName
		subprocessPopen = subprocess.Popen(["git","rm",fileName], stdout=subprocess.PIPE)
		stderr = subprocessPopen.communicate()
		os.chdir(currentDir)
		if stderr is None:
			return "File removed successfully"
		else:
			return stderr

	def commitFileGit(self,path,message,description):
		currentDir = os.getcwd()
		os.chdir(path)
		subprocessPopen = subprocess.Popen(["git","commit","-m",message,"-m",description], stdout=subprocess.PIPE)
		stderr = subprocessPopen.communicate()
		os.chdir(currentDir)
		if stderr is None:
			return "Files committed successfully"
		else:
			return stderr

	def getRemoteGitUrl(self,path):
		currentDir = os.getcwd()
		os.chdir(path)
		subprocessPopen = subprocess.Popen(["git","config","--get","remote.origin.url"], stdout=subprocess.PIPE)
		stdout,stderr = subprocessPopen.communicate()
		remoteUrl = ''

		lines = stdout.split('\n')
		for line in lines:
			if(line.find('http') > -1):
				tempUrl = re.findall("http[s]?\:\/\/([^\/\s]+)", line)
				remoteUrl = tempUrl[0]
				break

		os.chdir(currentDir)

		return remoteUrl.strip()

	def checkNetrcFile(self):

		commandCheckFile = "[ -f ~/.netrc ] && echo 'Found' || echo 'Not found'"

		subprocessPopen = subprocess.Popen([commandCheckFile], stdout=subprocess.PIPE, shell=True)
		stdout,stderr = subprocessPopen.communicate()

		lines = stdout.split('\n')
		fileExist = False
		for line in lines:
			if(line == 'Found'):
				fileExist = True
				break
			
		return fileExist

	def pushFilesGit(self,path, username, password):
		currentDir = os.getcwd()
		os.chdir(path)
		
		fileExist = self.checkNetrcFile()
		remoteUrl = self.getRemoteGitUrl(path)
		branch = self.getGitBrachName(path)
		home = os.path.expanduser("~")
		netrcFile = home + "/" + ".netrc"

		if(fileExist):
			authExist = False
			file = open(netrcFile, "r")
			for line in file.readlines():
				if (line.find(remoteUrl) > -1 and line.find(username) > -1):
					authExist = True
					break
			file.close()
			if(not authExist):
				file = open(netrcFile, "a")
				file.write("machine\t" + remoteUrl + "\tlogin\t" + username + "\tpassword\t" + password)
				file.close()
			
		else:
			file = open(netrcFile, "w")
			file.write("machine\t" + remoteUrl + "\tlogin\t" + username + "\tpassword\t" + password)
			file.close()
			proc = subprocess.Popen(["chmod", "0600",netrcFile], stdout=subprocess.PIPE)
			proc.close()

		subprocessPopen = subprocess.Popen(["git","push","origin",branch], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

		stdout,stderr = subprocessPopen.communicate()
		
		os.chdir(currentDir)
		if stderr is None:
			return "Files pushed successfully"
		else:
			return stderr

