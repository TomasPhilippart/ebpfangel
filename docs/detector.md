# Detector

The detector currently uses BCC (BPF Compiler Collection) and consists of 2 parts:
- kernel space: eBPF program written in C and attached to various hooks, see [detection methods](overview.md#detection-methods)
    - tracepoints on open/openat and unlink/unlinkat syscall
    - uprobe on libcrypto.so functions (EVP_EncryptInit_ex, EVP_CipherInit_ex and EVP_SealInit)
- user space: python program that reads data from the eBPF ring buffer output map

This data can then be post-processed in python by a machine learning algorithm like k-NN, SVM, RNN and others (eg. with scikit-learn or tensorflow).

Note: as an exercise these programs could also be implemented with 
- [libbpf-bootstrap](https://github.com/libbpf/libbpf-bootstrap) - both kernel & user space written in C
- or [libbpfgo](https://github.com/aquasecurity/libbpfgo) - only for the user-space program (replacing python)

```shell
# generate vmlinux.h when using libbpf
bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h
```

## Install BCC

Follow: https://github.com/iovisor/bcc

```bash
# example for debian
echo deb http://cloudfront.debian.net/debian sid main >> /etc/apt/sources.list
sudo apt-get install -y bpfcc-tools libbpfcc libbpfcc-dev linux-headers-$(uname -r)
```

## Introduction to BCC

See explanations, sample programs, available hooks and format in [bcc](https://github.com/iovisor/bcc/blob/master/README.md).

See also [BCC reference guide](https://github.com/iovisor/bcc/blob/master/docs/reference_guide.md).

## Run the detector

```shell
sudo ./detector.py
```

## Sample output

Displays file access events with:
- PID: process ID
- TYPE: type of event (0=open, 1=create, 2=delete)
- FLAG: indicates the event severity
- PATT: indicates a pattern match (for example a sequence of open, create, delete)
- TRESH: indicate which types of event exceed the threshold (number of events > 50)
- FILENAME: file name or crypto function in question

```rb
Printing file & crypto events, ctrl-c to exit.
PID    TYPE FLAG PATT TRESH FILENAME
26858  Enc  MIN  -     ---E EVP_EncryptInit_ex
26858  Enc  MIN  -     ---E EVP_EncryptInit_ex
26858  Enc  MIN  -     ---E EVP_EncryptInit_ex
26858  Enc  MIN  -     ---E EVP_EncryptInit_ex
28178  Del  MAJ  Match OCD- /tmp/tmp8imczwuu/Asia/Shanghai
28178  Open MIN  -     OCD- /tmp/tmp8imczwuu/Asia/Jayapura
28178  Crea MIN  -     OCD- /tmp/tmp8imczwuu/Asia/Jayapura.aes
28178  Del  MAJ  Match OCD- /tmp/tmp8imczwuu/Asia/Jayapura
28178  Open MIN  -     OCD- /tmp/tmp8imczwuu/Asia/Harbin
28178  Crea MIN  -     OCD- /tmp/tmp8imczwuu/Asia/Harbin.aes
28178  Del  MAJ  Match OCD- /tmp/tmp8imczwuu/Asia/Harbin
28178  Open MIN  -     OCD- /tmp/tmp8imczwuu/Asia/Irkutsk
28178  Crea MIN  -     OCD- /tmp/tmp8imczwuu/Asia/Irkutsk.aes
28178  Del  MAJ  Match OCD- /tmp/tmp8imczwuu/Asia/Irkutsk
28178  Open MIN  -     OCD- /tmp/tmp8imczwuu/Asia/Bangkok
28178  Crea MIN  -     OCD- /tmp/tmp8imczwuu/Asia/Bangkok.aes
28178  Del  MAJ  Match OCD- /tmp/tmp8imczwuu/Asia/Bangkok
28178  Open MIN  -     OCD- /tmp/tmp8imczwuu/Asia/Sakhalin
28178  Crea MIN  -     OCD- /tmp/tmp8imczwuu/Asia/Sakhalin.aes
28178  Del  MAJ  Match OCD- /tmp/tmp8imczwuu/Asia/Sakhalin
28178  Open MIN  -     OCD- /tmp/tmp8imczwuu/Asia/Ust-Nera
28178  Crea MIN  -     OCD- /tmp/tmp8imczwuu/Asia/Ust-Nera.aes
28178  Del  MAJ  Match OCD- /tmp/tmp8imczwuu/Asia/Ust-Nera
28178  Open MIN  -     OCD- /tmp/tmp8imczwuu/Asia/Macao
28178  Crea MIN  -     OCD- /tmp/tmp8imczwuu/Asia/Macao.aes
28178  Del  MAJ  Match OCD- /tmp/tmp8imczwuu/Asia/Macao
28178  Open MIN  -     OCD- /tmp/tmp8imczwuu/Asia/Magadan
28178  Crea MIN  -     OCD- /tmp/tmp8imczwuu/Asia/Magadan.aes
28178  Del  MAJ  Match OCD- /tmp/tmp8imczwuu/Asia/Magadan
868    Open OK   -     ---- /etc/fstab
868    Open OK   -     ---- /proc/self/mountinfo
868    Open OK   -     ---- /proc/self/mountinfo
221    Open OK   -     ---- /proc/525/comm
221    Open OK   -     ---- /proc/525/cmdline
221    Open OK   -     ---- /proc/525/status
221    Open OK   -     ---- /proc/525/attr/current
221    Open OK   -     ---- /proc/525/sessionid
```