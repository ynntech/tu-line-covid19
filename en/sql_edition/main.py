#-*- coding: utf-8 -*-
import os
import subprocess

if __name__ == "__main__":
    os.makedirs("./logs", exist_ok=True)
    path1 = "./logs/api.log"
    path2 = "./logs/scrape.log"

    cmd1 = "./api.py"
    cmd2 = "./scrape.py"

    with open(path1, "w") as log1:
        with open(path2, "w") as log2:
            pipe1 = subprocess.Popen(cmd1, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            pipe2 = subprocess.Popen(cmd2, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            while (pipe1.poll() is None) and (pipe2.poll() is None):
                res1 = pipe1.stdout.readline().decode("utf-8").strip()
                res2 = pipe2.stdout.readline().decode("utf-8").strip()
                if res1:
                    print(res1, file=log1)
                if res2:
                    print(res2, file=log2)
