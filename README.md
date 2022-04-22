
### How do I use sshpass with gpg encrypted file?

First, create a file as follows:
```
$ echo 'mySshPasswordHere' > .sshpassword
```

Now, encrypt a file using gpg command:

```
$ gpg -c .sshpassword
$ rm .sshpassword
```

Finally, use it as follows:

```
$ gpg -d -q .sshpassword.gpg > fifo; sshpass -f fifo ssh root@10.10.10.5
```

### How to Install

If you want you can change path of the password (DropBox, Pcloud, ...) and name of the file json.

```python
path_passwd = "~/password/"
file_json = "data.json"
```

```shell
git clone git@github.com:madyel/sshManager.git
```

```shell
sudo cp sshManager/ssh_manager.py /usr/bin/ssh-manager
```

```shell
rm -rf sshManager
```

### Result

[![asciicast](https://asciinema.org/a/m7e4qtxMlYp5v5h7vJMWUMzFk.svg)](https://asciinema.org/a/m7e4qtxMlYp5v5h7vJMWUMzFk)