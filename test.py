import subprocess
import glob

for filepath in glob.glob('./*.bin'):
    print(filepath)
    t = subprocess.run(["python3","app.py",filepath], capture_output = 1, text = 1)
    print(t.stdout)