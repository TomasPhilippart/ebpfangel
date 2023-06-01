# ebpfangel - Ransomware Detection using Machine Learning with eBPF for Linux

## Overview

The aim of this project is to detect Linux malware, stegomalware, ransomware, cryptojacking, or cryptoworms using eBPF.

## Software architecture

```mermaid
flowchart LR
  subgraph sandbox_VM
    ransomware
  end
  ransomware --> network_hook & filesystem_hooks & crypto_hooks
  subgraph host_kernel
    network_hook & filesystem_hooks & crypto_hooks --> ebpf_c

  end
  subgraph host_userland
    ebpf_c -- events --> ebpf_python
    ebpf_python -- patterns + config --> ebpf_c
    ebpf_python --> machine_learning
  end
```

### eBPF C program

```mermaid
flowchart LR
  A(event) --> B(compute stats <br/>per pid)
  B --> C(detect event pattern <br/>and threshold counts)
  X(python) -. patterns + config .-> C
  C --> D{report event?}
  D -- yes --> E(submit event <br/>to ring buffer) -->F(end)
  D -- no --> F
```

## Learning resources and references

1. UNVEIL: A Large-Scale, Automated Approach to Detecting Ransomware
2. Toward A Network-Assisted Approach for Effective Ransomware Detection
3. Software-Defined Networking-based Crypto Ransomware Detection Using HTTP Traffic Characteristics
4. Ransomware Detection and Classification Strategies
5. Ransomware Detection techniques in the Dawn of Artificial Intelligence: A Survey
6. PayBreak: Defense Against Cryptographic Ransomware
7. Checking yourcryptography usage with eBPF (redhat, devconf 2020)
8. A Multi-Classifier Network-based Crypto Ransomware Detection System: A Casestudy of Locky Ransomware
9. A flow-based IDS using Machine Learning in eBPF
10. Kernel-level tracing for detecting stegomalware and covert channels in Linux environments
11. CryptoLock (and Drop It): Stopping Ransomware Attacks on User Data
12. https://www.bleepingcomputer.com/news/security/linux-version-of-rtm-locker-ransomware-targets-vmware-esxi-servers/ 
    https://blogs.vmware.com/security/2022/02/avoslocker-modern-linux-ransomware-threats.html
    https://www.uptycs.com/blog/rtm-locker-ransomware-as-a-service-raas-linux (see yara rule)
