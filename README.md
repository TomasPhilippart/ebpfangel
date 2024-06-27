<a href="https://ebpfangel.philippart.me/">
<picture aling="center">
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/ebpfangel-logo-white.png">
  <img alt="Logo" src="docs/assets/ebpfangel-logo-black.png">
</picture>
</a>

<h2 align="center">
Ransomware Detection using Machine Learning with eBPF for Linux
</h2>

<p align="center">
  <img alt="GitHub License" src="https://img.shields.io/github/license/TomasPhilippart/ebpfangel">
  <a href="https://ebpfangel.philippart.me/"><img alt="Website" src="https://img.shields.io/website?url=https%3A%2F%2Febpfangel.philippart.me"></a>
</p>



<p align="center">
  Authors: <br>
  <a href="https://www.linkedin.com/in/max-willers-53830b268">Max Willers</a> •
  <a href="https://www.linkedin.com/in/tomasphilippart/">Tomás Philippart</a>
</p>



<p align="center">
  <a href="https://github.com/TomasPhilippart/ebpfangel/blob/main/docs/Ransomware_Detection_using_Machine_Learning_with_eBPF.pdf">Paper</a> •
  <a href="https://github.com/TomasPhilippart/ebpfangel/blob/main/docs/ebpfangel-presentation.pdf">Presentation slides</a>
</p>

---


<p align="center">
  <a href="https://ebpfangel.philippart.me/">Overview</a> •
  <a href="https://ebpfangel.philippart.me/simulator/">Simulator</a> •
  <a href="https://ebpfangel.philippart.me/detector/">Detector</a> •
  <a href="https://ebpfangel.philippart.me/machinelearning/">Machine Learning</a>
</p>

---



```shell
$ git clone https://github.com/TomasPhilippart/ebpfangel.git
```

> :warning: **Not a final product**: This is the final result of a research project. It is not intended to be a final product/solution to use in any productions environment whatsoever, it is simply the byproduct of research and therefore is intended to use as so.

## Overview

**ebpfangel** is a ransomware detection system that leverages the power of eBPF and machine learning to provide real-time monitoring and protection against ransomware attacks on Linux-based systems. By integrating dynamic analysis techniques with the capabilities of eBPF, ebpfangel offers a flexible, low-overhead solution for identifying and mitigating ransomware threats.

## How it works

**ebpfangel** operates by attaching eBPF programs to key system calls and user-space functions. These programs are triggered by specific events, such as file operations and encryption activities, allowing for comprehensive monitoring of system behavior. The collected data is then processed and analyzed using machine learning algorithms to detect patterns indicative of ransomware activity.

### Key Features
- **Real-Time Monitoring**: eBPF programs are attached to tracepoints, kprobes, and uprobes within the Linux kernel and user-space applications, enabling real-time detection of ransomware activities.
- **Low Overhead**: eBPF provides a lightweight mechanism for extending kernel capabilities without the need for additional kernel modules or modifications.
- **Machine Learning Integration:** The system uses supervised machine learning to classify events and detect ransomware based on patterns in the monitored data.
- **Open Source**: The codebase is open-source, promoting transparency, collaboration, and further development by the security community.


## Contributing

To foster progress in the field of ransomware detection, collaboration and knowledge sharing within the research community are essential. Encouraging open collaboration, sharing of datasets, methodologies, and findings will enable researchers to collectively combat the growing threat of ransomware attacks. By fostering collaboration, we can pool resources and expertise to develop more advanced and robust ransomware detection techniques, ultimately enhancing the overall security posture against this persistent threat.

If you are forking this project for your own uses, please consider creating a Pull Request with your changes.

There are some [open (un-assigned) issues](https://github.com/TomasPhilippart/ebpfangel/issues) created that would be good for new comers and people who would like to contribute to the project.


## License

The MIT License (MIT). Please see [License File](https://github.com/TomasPhilippart/ebpfangel/blob/main/LICENSE) for more information.
