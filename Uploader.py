import os, sys
import json
import paramiko
import win32gui, win32con

os.chdir(os.path.dirname(__file__))
REMOTE_PATH = "/home/azureuser/vejcobus-statistics"

TERMINAL_WINDOW_NAME = 'Michal-Server'

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
	remoteFilename = os.path.basename(uploadingPath)
	if remoteFilename not in sftp.listdir(REMOTE_PATH): print(f"INFO: created new file '{remoteFilename}'")
	params = sftp.put(uploadingPath, f'{REMOTE_PATH}/{remoteFilename}', callback=None)
	print(f"Uploaded '{remoteFilename}':", params)
	sftp.close()
def getUploadingPath():
	assert len(sys.argv) > 1, 'Path argument expected'
	path = sys.argv[-1]
	assert os.path.exists(path), 'Invalid path argmuent'
	return os.path.abspath(path)
# maximize terminal ------------------------
def getTerminalWindow():
	windows = {}
	def winEnumHandler(hwnd, ctx):
		name = win32gui.GetWindowText(hwnd)
		windows[name] = hwnd
	win32gui.EnumWindows(winEnumHandler, None)
	if TERMINAL_WINDOW_NAME not in windows:
		print(f'ERROR: Terminal window not found')
		return None
	return windows[TERMINAL_WINDOW_NAME]
def maximizeTerminal():
	if (hwnd := getTerminalWindow()) is None: return
	win32gui.ShowWindow(hwnd, win32con.SW_SHOWMAXIMIZED)
	win32gui.SetForegroundWindow(hwnd)
def main():
	print()
	uploadingPath = getUploadingPath()
	sftp = openSFTP()
	uploadFile(sftp, uploadingPath)
	maximizeTerminal()

if __name__ == '__main__':
	main()
