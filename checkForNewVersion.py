import os
import subprocess
import requests
import re
import jdk

version_regex = r"(?<=Release Version )\d+\.\d+"
release_url = "https://github.com/TSerious/QuickFioriTimeEvents/releases/latest"

def get_latest_version() -> str:
    response = requests.get(release_url)
    match = re.search(version_regex, response.text)
    
    if not match:
        return ""

    return match.group(0)   

def get_installed_java_version():
   
    try:
        p = subprocess.Popen("java -version",
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT)
        javaVersion = iter(p.stdout.readline, b'')
        return list(javaVersion)
    except:
        return ''
    
print(f"Current version is: {get_latest_version()}")
print(f"The currently installed java version is: {get_installed_java_version()}")

installJave = input('Install java? [y/n]')
if installJave == 'y':
    jdk.install('11', jre=True)
else:
    print("Java wasn't installed")

installDriver = input('Install chrome driver? [y/n]')
if installDriver == 'y':
    os.system('java -jar webdrivermanager-5.3.2-fat.jar resolveDriverFor chrome')
else:
    print("Driver wasn't installed")

print("Press any key to exit...")
input()


