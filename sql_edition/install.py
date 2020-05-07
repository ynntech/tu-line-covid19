#-*- coding: utf-8 -*-
import os
import subprocess


def replace(text, var):
    value = f'\"{os.environ[var]}\"'
    target = f'os.environ[\"{var}\"]'
    return text.replace(target, value)

def overwrite(path, vars):
    with open(path, "r") as f:
        text = f.read()
    for var in vars:
        text = replace(text=text, var=var)
    with open(path, "w") as f:
        f.write(text)

def executable(path, interpreter):
    with open(path, "r") as f:
        text = f.read()
    text = f"#!{interpreter}" + text
    with open(path, "w") as f:
        f.write(text)
    os.chmod(path, 0o755)


if __name__ == "__main__":
    print("installing...")
    setup = {"./api.py":["WEB_SERVER_TOKEN", "API_SERVER_PORT"],
             "./database.py":["MYSQL_HOST", "MYSQL_USER",
                              "MYSQL_PSSWD", "MYSQL_DB"],
             "./utils.py":["SLACK_WEBHOOK_URL", "HEROKU_DOMAIN"]}

    for path, vars in setup.items():
        overwrite(path=path, vars=vars)

    ## next, this will make file executable
    res = subprocess.run(["which", "python3"], stdout=subprocess.PIPE)
    interpreter = res.stdout.decode("utf-8")
    executable(path="./api.py", interpreter=interpreter)
    executable(path="./scrape.py", interpreter=interpreter)
    executable(path="./main.py", interpreter=interpreter)
    print("done!")
