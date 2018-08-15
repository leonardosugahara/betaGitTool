import sys
from flask import Flask, render_template, request, redirect, url_for,jsonify,abort
from systemUtils import SystemUtils

app = Flask(__name__)

@app.route('/')
def index():
	
	return render_template('showFiles.html')

@app.route('/setpath', methods=['GET'])
def setPath():
	pathProject = request.args.get('pathProject', type=str)
	print pathProject
	print request.method
	if pathProject != "":
		systemUtils = SystemUtils()
		lines = systemUtils.listFoldersAndFiles(pathProject)

		return jsonify(result = lines)
				
	return render_template('showFiles.html')

@app.route('/getStatus', methods=['GET'])
def getStatus():
	pathProject = request.args.get('pathProject', type=str)
	if pathProject != "":
		systemUtils = SystemUtils()
		lines = systemUtils.getGitStatus(pathProject)
		outputHtml = ""
		for line in lines:
			if(line[0:3].find("M") > -1):
				outputHtml = outputHtml + '<option value="' + line + '" style="color:green;">' + line[line.find("M")+1:] + '</option>'
			elif(line[0:3].find("D")  > -1): 
				outputHtml = outputHtml + '<option value="' + line + '" style="color:red;">' + line[line.find("D")+1:] + '</option>' 
			elif(line[0:4].find("??") > -1):
				outputHtml = outputHtml + '<option value="' + line + '" style="color:blue;">' + line[line.find("??")+3:] + '</option>' 
		
		return jsonify(result = outputHtml)
		
@app.route('/getBranchName', methods=['GET'])
def getBranchName():
	pathProject = request.args.get('pathProject', type=str)
	if pathProject != "":
		systemUtils = SystemUtils()
		branchName = systemUtils.getGitBrachName(pathProject)
		return jsonify(result = branchName)


@app.route('/getDiffFile', methods=['GET'])
def getDiffFile():
	pathProject = request.args.get('pathProject', type=str)
	fileName = request.args.get('fileName', type=str)
	if pathProject != "" and fileName != "" :
		systemUtils = SystemUtils()
		lines = systemUtils.getGitFileDiff(pathProject,fileName)
		outputHtml = ""		
		for line in lines:
			if(line.find("@@") > -1):
				outputHtml = outputHtml + "<tr><td style='color: #0080ff'><![CDATA[" + line + "]]></td></tr>"
			elif line.find("---") > -1:
				outputHtml = outputHtml + "<tr><td style='color: #ff9999'><![CDATA[" + line + "]]></td></tr>"
			elif line.find("+++") > -1:
				outputHtml = outputHtml + "<tr><td style='color: #00ff40'><![CDATA[" + line + "]]></td></tr>"
			else:
				outputHtml = outputHtml + "<tr><td><![CDATA[" + line + "]]></td></tr>"		
		
		return jsonify(result = outputHtml)

@app.route('/pushToGit', methods=['POST'])
def sendToGit():
	try:
		systemUtils = SystemUtils()
		fileList  = request.form["fileList"].split(",")
		message = request.form["message"]
		description = request.form["description"]
		pathProject = request.form["path"]
		username = request.form["username"]
		password = request.form["password"]

		for file in fileList:
			if (file[0:3].find("M") > -1):
				systemUtils.addFileGit(pathProject,file[file.find("M")+1:].strip())
				print "add"
			elif (file[0:3].find("D") > -1):
				systemUtils.removeFileGit(pathProject,file[file.find("D")+1:].strip())
				print "remove"
			elif (file[0:4].find("??") > -1):
				systemUtils.addFileGit(pathProject,file[file.find("??")+3:].strip())
				print "add new"

		systemUtils.commitFileGit(pathProject,message,description)
		systemUtils.pushFilesGit(pathProject,username,password)

		return jsonify(result = "Files push successful")

	except:
		print sys.exc_info()[0] 
		print sys.exc_info()[1]
		print "Error push files to Git"
		abort(500)


if __name__ == '__main__':
	app.run(debug=True)
