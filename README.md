
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

[![asciicast](https://asciinema.org/a/m7e4qtxMlYp5v5h7vJMWUMzFk.svg)](https://asciinema.org/a/m7e4qtxMlYp5v5h7vJMWUMzFk)