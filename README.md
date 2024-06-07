# ebpfangel - Ransomware Detection using Machine Learning with eBPF for Linux
## [Documentation 📖](https://tomasphilippart.github.io/ebpfangel/)

```
git clone https://github.com/TomasPhilippart/ebpfangel.git
```

> :warning: **Not a final product**: This is the final result of a research project. It is not intended to be a final product/solution to use in any productions environment whatsoever, it is simply the byproduct of research and therefore is intended to use as so.

### Overview

**ebpfangel** is an advanced ransomware detection system that leverages the power of eBPF and machine learning to provide real-time monitoring and protection against ransomware attacks on Linux-based systems. By integrating dynamic analysis techniques with the capabilities of eBPF, ebpfangel offers a flexible, low-overhead solution for identifying and mitigating ransomware threats.

### How it works

**ebpfangel** operates by attaching eBPF programs to key system calls and user-space functions. These programs are triggered by specific events, such as file operations and encryption activities, allowing for comprehensive monitoring of system behavior. The collected data is then processed and analyzed using machine learning algorithms to detect patterns indicative of ransomware activity.

#### Key Features
- **Real-Time Monitoring**: eBPF programs are attached to tracepoints, kprobes, and uprobes within the Linux kernel and user-space applications, enabling real-time detection of ransomware activities.
- **Low Overhead**: eBPF provides a lightweight mechanism for extending kernel capabilities without the need for additional kernel modules or modifications.
- **Machine Learning Integration:** The system uses supervised machine learning to classify events and detect ransomware based on patterns in the monitored data.
- **Open Source**: The codebase is open-source, promoting transparency, collaboration, and further development by the security community.

### License

The MIT License (MIT). Please see [License File](https://github.com/TomasPhilippart/ebpfangel/blob/main/LICENSE) for more information.
