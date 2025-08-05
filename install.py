import os
import subprocess
import sys
import urllib.request

# Optional: requirements (add more if needed)
required = []

def install_requirements():
    for package in required:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def download_main():
    url = "https://raw.githubusercontent.com/OftenNotKnown/SimplicIDLE/main/main.py"
    file_name = "main.py"
    print("Downloading main.py from GitHub...")
    urllib.request.urlretrieve(url, file_name)
    print("Download complete.")

def run_main():
    print("Running main.py...")
    os.system(f"{sys.executable} main.py")

if __name__ == "__main__":
    install_requirements()
    download_main()
    run_main()
