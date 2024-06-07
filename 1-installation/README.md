# if you got `System locale` error install the folowing pakages:

```

dnf install glibc-langpack-en

```
[ref](https://www.tecmint.com/fix-failed-to-set-locale-defaulting-to-c-utf-8-in-centos/)

## Disable selinux permanently
```
vi /etc/sysconfig/selinux

###

SELINUX=disabled

###


then reboot your system


# finally run below command to ensure the selinux disables

sestatus
```