import os
import random
import psutil
import subprocess

PROCESS = None

def get_ovpn(folder):
	files = os.listdir(folder) 
	files = [file for file in files if file[-5:] == '.ovpn'] 

	return files

def random_file(folder):
	files = get_ovpn(folder)
	return random.choice(files)

def connect(folder):
	global PROCESS
	file = random_file(folder)
	query = f"sudo openvpn --config {folder}/{file} --auth-user-pass {folder}/credentials"
	query = query.split(' ')

	FNULL = open(os.devnull, 'w')
	PROCESS = subprocess.Popen(query,stdout=FNULL)

def kill():
	global PROCESS
	if PROCESS:
		parent = psutil.Process(PROCESS.pid)
		children = parent.children(recursive=True) 
		for child in children:
			os.system(f"sudo kill {child.pid}")
		os.system(f"sudo kill {parent.pid}")
		PROCESS = None