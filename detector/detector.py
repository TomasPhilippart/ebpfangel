#!/usr/bin/python3

#   DISCLAIMER
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.

import os
import sys
import time
import ctypes
from bcc import BPF
import csv

# see <bpf.h>
EVENT_TYPES = 4
class Config(ctypes.Structure):
    _fields_ = [
        ('thresholds', ctypes.c_uint16 * EVENT_TYPES),
        ('reset_period_ns', ctypes.c_uint32),
        ('min_severity', ctypes.c_uint8),
    ]

def update_config(b: BPF):
    # 10 billion nanoseconds = 10 seconds
    thresholds = ctypes.c_uint16 * EVENT_TYPES
    b['config'][ctypes.c_int(0)] = Config(thresholds(50, 25, 25, 50), 10_000_000_000, 0)

# see <bpf.h>
class Pattern(ctypes.Structure):
    _fields_ = [
        ('bitmap', ctypes.c_uint32),
        ('bitmask', ctypes.c_uint32),
    ]

def update_patterns(b: BPF):
    values = [Pattern(0x0000_0012, 0x0000_0FFF), Pattern(0x0013_3332, 0x0FFF_FFFF)]
    patterns = b['patterns']
    for k,v in enumerate(values):
        patterns[ctypes.c_int(k)] = v

# see <bpf.h>
class Flags(ctypes.Structure):
    _fields_ = [
        ('severity', ctypes.c_uint8),
        ('pattern_id', ctypes.c_uint8),
        ('thresholds_crossed', ctypes.c_uint8),
    ]

# see <bpf.h> and <linux/sched.h>
FILENAME_SIZE = 64
TASK_COMM_LEN = 16
class Event(ctypes.Structure):
    _fields_ = [
        ('ts', ctypes.c_uint64),
        ('pid', ctypes.c_uint32),
        ('type', ctypes.c_uint),
        ('flags', Flags),
        ('filename', ctypes.c_char * FILENAME_SIZE),
        ('comm', ctypes.c_char * TASK_COMM_LEN),
    ]

def decode_type(t: ctypes.c_uint) -> str:
    name = {0: "Open", 1: "Crea", 2: "Del", 3: "Enc"}
    return name[t]

def decode_severity(s: ctypes.c_uint8) -> str:
    name = {0: "OK", 1: "MIN", 2: "MAJ"}
    return name[s]

def decode_pattern(p: ctypes.c_uint8) -> str:
    return "P%d" % p if p > 0 else "-"

def decode_thresholds(t: ctypes.c_uint8) -> str:
    output = []
    map = {1: "O", 2: "C", 4: "D", 8: "E"}
    for k,v in map.items():
        if t & k:
            output.append(v)
        else:
            output.append("-")
    return "".join(output)

def unpack_thresholds(t: ctypes.c_uint8):
    output = []
    for k in range(EVENT_TYPES):
        if t & k:
            output.append(1)
        else:
            output.append(0)
    return output

# find library pathname
def find_lib(lib: str) -> str:
    for path in ['/usr/lib/', '/opt']:
        for root, _, files in os.walk(path):
            if lib in files:
                return os.path.join(root, lib)
    return None

def save_data(event: Event):
    # write data to csv
    writer.writerow([event.ts,
                     event.pid, 
                     event.type, 
                     event.flags.severity, 
                     event.flags.pattern_id, 
                     *unpack_thresholds(event.flags.thresholds_crossed), # transforms to multiple args/colums
                     event.filename.decode('utf-8')])

def print_event(_ctx, data, _size):
    event = ctypes.cast(data, ctypes.POINTER(Event)).contents
    print("%-6d %-6d %-16s %-4s %-4s %-5s %-4s %-64s" % (
        int(event.ts / 1e6),
        event.pid,
        event.comm.decode('utf-8'),
        decode_type(event.type), 
        decode_severity(event.flags.severity), 
        decode_pattern(event.flags.pattern_id), 
        decode_thresholds(event.flags.thresholds_crossed), 
        event.filename.decode('utf-8')))
    save_data(event)

def runas_root() -> bool:
    return os.getuid() == 0

def main():
    b = BPF(src_file="bpf.c", cflags=["-Wno-macro-redefined"], debug=4)

    # send config + patterns to ebpf programs
    update_config(b)
    update_patterns(b)

    # the path to libcrypto may differ from OS to OS
    # check symbol address with nm -gD /path/to/lib.so or readelf -Ws --dyn-syms /path/to/lib.so
    for lib in ['libcrypto.so.1.1', 'libcrypto.so.3']:
        pathname = find_lib(lib)
        if pathname:
            b.attach_uprobe(name=pathname, sym="EVP_EncryptInit_ex", fn_name="trace_encrypt1")
            b.attach_uprobe(name=pathname, sym="EVP_CipherInit_ex", fn_name="trace_encrypt1")
            b.attach_uprobe(name=pathname, sym="EVP_SealInit", fn_name="trace_encrypt2")
 
    b['events'].open_ring_buffer(print_event)

    print("Printing file & crypto events, ctrl-c to exit.")
    print("%-6s %-16s %-6s %-4s %-4s %-5s %-4s %-64s" % 
          ("TS", "PID", "COMM", "TYPE", "FLAG", "PATT", "TRESH", "FILENAME"))
    # header
    writer.writerow(["TS", "PID", "TYPE", "FLAG", "PATTERN", "OPEN", "CREATE", "DELETE", "ENCRYPT", "FILENAME"])

    # loop with callback to print events
    try:
        while 1:
            b.ring_buffer_consume()
            time.sleep(0.5)
    except KeyboardInterrupt:
        f.close()
        sys.exit()
    
    f.close()

if __name__ == '__main__':
    if not runas_root():
        print("You must run this program as root or with sudo.")
        sys.exit()
    
    f = open('log.csv', 'w', encoding='UTF8', newline='') # deixa ^M no fim!
    writer = csv.writer(f)
    main()
