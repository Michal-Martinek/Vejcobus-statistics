import os, sys
import json
import paramiko

os.chdir(os.path.dirname(__file__))
REMOTE_PATH = "/home/azureuser/vejcobus-statistics"

def getServerCredentials():
	with open('server_credentials.json') as f:
		return json.load(f)
def openSFTP():
	ssh = paramiko.SSHClient() 
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	cred = getServerCredentials()
	ssh.connect(cred['server'], username=cred['username'], password=cred['password'])
	sftp = ssh.open_sftp()
	return sftp
def uploadFile(sftp, uploadingPath):
	remotePath = f'{REMOTE_PATH}/{os.path.basename(uploadingPath)}'
	params = sftp.put(uploadingPath, remotePath, callback=None)
	sftp.close()
def getUploadingPath():
	assert len(sys.argv) > 1, 'Path argument expected'
	path = sys.argv[-1]
	assert os.path.exists(path), 'Invalid path argmuent'
	return os.path.abspath(path)
def main():
	uploadingPath = getUploadingPath()
	sftp = openSFTP()
	uploadFile(sftp, uploadingPath)

if __name__ == '__main__':
	main()
