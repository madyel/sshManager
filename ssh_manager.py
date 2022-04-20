#!/usr/bin/env python

import os, json, pwd
import getpass
import signal
import sys, time
import uuid
from threading import Thread

path_passwd = "~/password/"
file_json = "data.json"
tmp = f"{path_passwd}fifo"
PATH_FILE_JSON = os.path.expanduser(f'{path_passwd}data.json')
# print(pwd.getpwuid(os.getuid())[0])
init_json = {
    "Manager": []
}


def install():
    dir = os.path.expanduser(path_passwd)
    if not os.path.exists(dir):
        os.makedirs(dir)
    file = os.path.expanduser(path_passwd + file_json)
    if not os.path.isfile(file):
        with open(file, 'w') as outfile:
            json.dump(init_json, outfile, indent=4)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def readInput(text="", format="int"):
    try:
        if format == "int":
            i = int(input(text))
        else:
            i = input(text)
        return i
    except ValueError as error:
        print(error)
        run()


def save(data):
    with open(PATH_FILE_JSON, 'w') as outfile:
        json.dump(data, outfile, indent=4)


def choose():
    index = 0
    for d in data['Manager']:
        print(f"{bcolors.HEADER}{index}{bcolors.ENDC} {bcolors.BOLD}{d['name']}{bcolors.ENDC}")
        index = index + 1
    i = readInput("Choose:")
    return i


def removeService():
    print(f"{bcolors.OKCYAN}{bcolors.UNDERLINE}RemoveService{bcolors.ENDC}")
    i = choose()
    services = data['Manager'][i]['service']
    printList(services)
    i = readInput()
    os.system(f"rm  {path_passwd}.{services[i]['id']}.gpg")
    del services[i]
    save(data)
    print(f"{bcolors.OKGREEN}Done{bcolors.ENDC}")
    run()


def addSerivce():
    if len(data['Manager']) == 0:
        add()
    print(f"{bcolors.OKCYAN}{bcolors.UNDERLINE}AddService{bcolors.ENDC}")
    i = choose()
    services = data['Manager'][i]['service']
    # print(data['Manager'][i])
    type_service = typeService()
    username = ""
    name = input("Name:")
    id = uuid.uuid4().hex[:6]
    if type_service == "ssh":
        username = input("UserName:")
        createPassword(id)
    host = input("Host:")
    service = createService(id, name, username, host, type_service)
    services.append(service)
    save(data)
    print(f"{bcolors.OKGREEN}Done{bcolors.ENDC}")
    run()


def typeService():
    print(f"{bcolors.HEADER}-----------------{bcolors.ENDC}")
    print(f'{bcolors.WARNING}Choose service:{bcolors.ENDC}')
    print(0, f"{bcolors.BOLD}SSH")
    print(1, f"Rdesktop")
    print(f"{bcolors.HEADER}-----------------{bcolors.ENDC}")
    i = readInput("Number:")

    return services(i)


def add():
    print(f"{bcolors.OKCYAN}{bcolors.UNDERLINE}Add{bcolors.ENDC}")
    name = input("Name:")
    a = {
        "name": f"{name}",
        "service": []
    }
    data['Manager'].append(a)
    save(data)
    print("Done")
    run()


def remove():
    print(f"{bcolors.OKCYAN}{bcolors.UNDERLINE}Remove{bcolors.ENDC}")
    i = choose()
    services = data['Manager'][i]['service']
    printList(services)
    print(f"{bcolors.WARNING}Remove all? Y/N{bcolors.ENDC}")
    cont = input()
    if cont in ("n", "y", "N", "Y"):
        if (cont == "Y") or ("y"):
            for s in services:
               os.system(f"rm  {path_passwd}.{s['id']}.gpg")
            del data['Manager'][i]
            save(data)
            print(f"{bcolors.OKGREEN}Done{bcolors.ENDC}")
        run()
    else:
        print(f"{bcolors.FAIL}Please enter 'y' or 'n'{bcolors.ENDC}")
        remove()


def createPassword(id):
    password = getpass.getpass()
    confirm = getpass.getpass("Re-Password:")
    try:
        if password == confirm:
            os.system("echo %s > %s.%s" % (password, path_passwd, id))
            os.system(f"gpg -c  {path_passwd}.{id}")
            os.system(f"rm  {path_passwd}.{id}")
        else:
            print("Error password!")
            createPassword(id)
    except Exception:
        if os.path.exists(f"{path_passwd}.{id}"):
            os.remove(f"{path_passwd}.{id}")


def createService(id, name, user=" ", host="", typeService="ssh"):
    service = None
    if typeService == "ssh":
        service = {
            'id': f'{id}',
            'name': f'{name}',
            f'{id}': {
                "cmd": f"gpg -d -q {path_passwd}.{id}.gpg > {tmp}; sshpass -f {tmp} ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=quiet {user}@{host}"
            }
        }
    if typeService == "rdesktop":
        service = {
            'id': f'{id}',
            'name': f'{name}',
            f'{id}': {
                "cmd": f"rdesktop {host}"
            }
        }
    return service


def init():
    print(f"{bcolors.HEADER}-----------------{bcolors.ENDC}")
    print(f'{bcolors.WARNING}Choose action:{bcolors.ENDC}')
    print(0, f"{bcolors.BOLD}AddService")
    print(1, f"RemoveService")
    print(2, f"Start")
    print(3, f"AddCategory")
    print(4, f"Remove")
    print(5, f"Exit")
    print(f"{bcolors.HEADER}-----------------{bcolors.ENDC}")


def printList(list):
    index = 0
    for d in list:
        print(f"{bcolors.HEADER}{index}{bcolors.ENDC} {bcolors.BOLD}{d['name']}{bcolors.ENDC}")
        index = index + 1


def start():
    print(f'{bcolors.OKBLUE} SSH Manager')
    i = choose()
    print(f"{bcolors.WARNING}Services {data['Manager'][i]['name']}:{bcolors.ENDC}")
    service = data['Manager'][i]['service']
    printList(service)
    i = readInput(f"{bcolors.WARNING}Service:{bcolors.ENDC}")
    id = service[i]['id']
    print("Wait...")
    t = Thread(target=deleteTmp)
    t.start()
    os.system(service[i][id]['cmd'])
    bye()


def deleteTmp():
    print("\n")
    time.sleep(1)
    file = os.path.expanduser(tmp)
    if os.path.isfile(file):
        os.system(f"rm {file}")


def signal_handler(sig, frame):
    deleteTmp()
    print(f'{bcolors.FAIL}Exit!')
    sys.exit(0)


def bye():
    deleteTmp()
    print(f"{bcolors.FAIL}GoodBye!{bcolors.ENDC}")
    exit()


def services(c):
    switcher = {
        0: "ssh",
        1: "rdesktop",
    }
    return switcher.get(c, "Invalid!")


def actions(c):
    switcher = {
        0: addSerivce,
        1: removeService,
        2: start,
        3: add,
        4: remove,
        5: bye
    }
    return switcher.get(c, bye)


def run():
    signal.signal(signal.SIGINT, signal_handler)
    init()
    c = readInput("Number:")
    f = actions(c)
    f()


if __name__ == '__main__':
    try:
        with open(PATH_FILE_JSON) as json_file:
            data = json.load(json_file)
            run()
    except FileNotFoundError:
        install()
