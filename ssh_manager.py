#!/usr/bin/env python

import os, json, pwd
import getpass
import signal
import sys
import subprocess


path_passwd = "~/.ssh-manager/"
tmp = "~/.ssh-manager/fifo"


file_json = "data.json"

init_json = {
    "Manager": []
}

def install():
    dir = os.path.expanduser(path_passwd)
    if not os.path.exists(dir):
        os.makedirs(dir)
    file = os.path.join(dir, file_json)
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
        return int(input(text)) if format == "int" else input(text)
    except ValueError as error:
        print(error)
        run()

def save(data):
    with open(my_dir, 'w') as outfile:
        json.dump(data, outfile, indent=4)

def select_interactive(options):
    try:
        result = subprocess.run(['fzf'], input="\n".join(options), text=True, capture_output=True)
        return result.stdout.strip() if result.returncode == 0 else None
    except FileNotFoundError:
        pass

    try:
        result = subprocess.run(['rofi', '-dmenu', '-p', 'Scegli:'], input="\n".join(options), text=True, capture_output=True)
        return result.stdout.strip() if result.returncode == 0 else None
    except FileNotFoundError:
        pass

    for i, option in enumerate(options):
        print(f"{i}. {option}")
    try:
        index = int(input("Seleziona [numero]: "))
        return options[index] if 0 <= index < len(options) else None
    except ValueError:
        return None

def choose():
    if not data['Manager']:
        print("Nessun manager trovato. Aggiungine uno prima.")
        add()
        return len(data['Manager']) - 1
    options = [d['name'] for d in data['Manager']]
    selected = select_interactive(options)
    if selected is None:
        print("Selezione non valida.")
        run()
    return options.index(selected)

def removeService():
    print(f"{bcolors.OKCYAN}{bcolors.UNDERLINE}RemoveService{bcolors.ENDC}")
    i = choose()
    services = data['Manager'][i]['service']
    if not services:
        print("Nessun servizio disponibile da rimuovere.")
        run()
        return
    printList(services)
    selected = select_interactive([s['name'] for s in services])
    if selected:
        s_index = [s['name'] for s in services].index(selected)
        os.system(f"rm {os.path.expanduser(path_passwd)}.{services[s_index]['name']}.gpg")
        del services[s_index]
        save(data)
    print("Done")
    run()

def addService():
    print(f"{bcolors.OKCYAN}{bcolors.UNDERLINE}AddService{bcolors.ENDC}")
    i = choose()
    type_service = typeService()
    username = ""
    name = input("Name:")
    if type_service == "ssh":
        username = input("UserName:")
        createPassword(name)
    host = input("Host:")
    services = data['Manager'][i]['service']
    service = createService(name, username, host, type_service)
    services.append(service)
    save(data)
    print("Done")
    run()

def typeService():
    print(f"{bcolors.HEADER}-----------------{bcolors.ENDC}")
    print(f'{bcolors.WARNING}Choose service:{bcolors.ENDC}')
    print(0, f"{bcolors.BOLD}SSH")
    print(1, f"Rdesktop")
    print(f"{bcolors.HEADER}-----------------{bcolors.ENDC}")
    i = int(input())
    return services_type(i)

def add():
    print(f"{bcolors.OKCYAN}{bcolors.UNDERLINE}Add{bcolors.ENDC}")
    name = input("Name:")
    a = {"name": f"{name}", "service": []}
    data['Manager'].append(a)
    save(data)
    print("Done")
    run()

def remove():
    print(f"{bcolors.OKCYAN}{bcolors.UNDERLINE}Remove{bcolors.ENDC}")
    i = choose()
    del data['Manager'][i]
    save(data)
    print("Done")
    run()

def createPassword(name):
    while True:
        password = getpass.getpass()
        confirm = getpass.getpass("Re-Password:")
        if password == confirm:
            full_path = os.path.expanduser(f"{path_passwd}.{name}")
            with open(full_path, 'w') as f:
                f.write(password)
            os.system(f"gpg -c {full_path}")
            os.remove(full_path)
            break
        else:
            print("Password mismatch. Try again.")

def createService(name, user="", host="", type="ssh"):
    if type == "ssh":
        return {
            'name': name,
            name: {
                "cmd": f"gpg -d -q {os.path.expanduser(path_passwd)}.{name}.gpg > {tmp}; sshpass -f {tmp} ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no {user}@{host}"
            }
        }
    elif type == "rdesktop":
        return {
            'name': name,
            name: {
                "cmd": f"rdesktop {host}"
            }
        }

def init():
    print(f"{bcolors.HEADER}-----------------{bcolors.ENDC}")
    print(f'{bcolors.WARNING}Choose action:{bcolors.ENDC}')
    print(0, f"{bcolors.BOLD}AddService")
    print(1, f"RemoveService")
    print(2, f"Start")
    print(3, f"Add")
    print(4, f"Remove")
    print(5, f"Exit")
    print(f"{bcolors.HEADER}-----------------{bcolors.ENDC}")

def printList(lst):
    for i, d in enumerate(lst):
        print(f"{bcolors.HEADER}{i}{bcolors.ENDC} {bcolors.BOLD}{d['name']}{bcolors.ENDC}")

def start():
    print(f'{bcolors.OKBLUE} SSH Manager')
    i = choose()
    services = data['Manager'][i]['service']
    if not services:
        print("Nessun servizio disponibile per questo manager.")
        run()
        return
    print(f"{bcolors.WARNING}Services {data['Manager'][i]['name']}:{bcolors.ENDC}")
    options = [s['name'] for s in services]
    selected = select_interactive(options)
    if selected:
        s_index = options.index(selected)
        name = services[s_index]['name']
        print("Wait...")
        os.system(services[s_index][name]['cmd'])
    bye()

def deleteTmp():
    file = os.path.expanduser(tmp)
    if os.path.isfile(file):
        os.remove(file)

def signal_handler(sig, frame):
    deleteTmp()
    print(f'{bcolors.FAIL}Exit!')
    sys.exit(0)

def bye():
    deleteTmp()
    print(f"{bcolors.FAIL}GoodBye!{bcolors.ENDC}")
    sys.exit(0)

def services_type(c):
    return {0: "ssh", 1: "rdesktop"}.get(c, "Invalid!")

def actions(c):
    return {
        0: addService,
        1: removeService,
        2: start,
        3: add,
        4: remove,
        5: bye
    }.get(c, bye)

def run():
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        init()
        c = readInput("Number:")
        f = actions(c)
        f()

if __name__ == '__main__':
    try:
        my_dir = os.path.expanduser(os.path.join(path_passwd, file_json))
        with open(my_dir) as json_file:
            data = json.load(json_file)
            run()
    except FileNotFoundError:
        install()
