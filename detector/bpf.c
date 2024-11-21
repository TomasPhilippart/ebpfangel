/*  DISCLAIMER
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE. */

// SPDX-License-Identifier: GPL-2.0+
#define BPF_LICENSE GPL

#include "bpf.h"
#include <uapi/asm/fcntl.h>
#include <uapi/linux/ptrace.h>

// config data from userspace
BPF_ARRAY(config, config_t, 1);

// event patterns from userspace
BPF_ARRAY(patterns, event_pattern_t, MAX_PATTERNS);

// hash map (pid -> pidstat) to analyze file access pattern per pid and flag suspicious pid
BPF_HASH(pidstats, u32 /* pid */, pidstat_t, 1024);

// ring buffer to report events (16 pages x 4096 bytes shared across all CPUs)
// getconf PAGESIZE returns the page size in bytes (4096)
BPF_RINGBUF_OUTPUT(events, 1 << 4);


// get config from BPF_ARRAY
static __always_inline config_t *get_config() {
    int zero = 0;
    return config.lookup(&zero);
}

// get pid stats from BPF_HASH
static __always_inline pidstat_t *get_stats(u32 *pid) {
    pidstat_t zero;
    __builtin_memset(&zero, 0, sizeof(zero));
    zero.event_bitmap = BITMAP_INIT;
    return pidstats.lookup_or_try_init(pid, &zero);
}

// update pid stats (but does not save)
static __always_inline void update_stats(config_t *conf, event_type_t type, const pidstat_t *curr, pidstat_t *updated) {
   __builtin_memcpy(updated, curr, sizeof(*updated));

    time_t now = bpf_ktime_get_ns();
    time_t time_since_reset = now - curr->last_reset_ts;
    if (conf && curr->last_reset_ts && (time_since_reset > conf->reset_period_ns)) {
        // reset counters
        __builtin_memset(updated->event_counts, 0, sizeof(counts_t) * EVENT_TYPES);
        updated->last_reset_ts = now;
    }
    // this doesnt work: updated->event_counts[type]++; - maybe try with bpf_probe_kernel_read?
    switch (type) {
        case T_OPEN:
            updated->event_counts[0]++;
            break;
        case T_CREATE:
            updated->event_counts[1]++;
            break;
        case T_DELETE:
            updated->event_counts[2]++;
            break;
        case T_ENCRYPT:
            updated->event_counts[3]++;
            break;
        default:
            break;
    }
    // shift and add the event_type
    updated->event_bitmap = (curr->event_bitmap << BITS_PER_EVENT) | (bitmap_t)type;
}

// analyse pid stats and compute flags
static __always_inline void analyze_stats(config_t *conf, pidstat_t* stats, event_flags_t *flags) {
    __builtin_memset(flags, 0, sizeof(event_flags_t));

    // check counters
    // TODO: consider counts per unit of time & reset counts after some delay    
    #pragma clang loop unroll(full)
    for (u8 i=0; i < EVENT_TYPES; i++) {
        if (conf && stats->event_counts[i] > conf->thresholds[i]) {
            // set the i-th bit to 1
            flags->thresholds_crossed |= (1 << i); 
            flags->severity = S_MINOR;
        }
    }

    // check pattern matches
    #pragma clang loop unroll(full)
    for (u8 i=0; i < MAX_PATTERNS; i++) {
        int k = i;
        event_pattern_t *pat = patterns.lookup(&k);
        if (pat && pat->bitmask) {
            // 0xABCDE012 & 0x00000FFF == 0x00000012
            if ((stats->event_bitmap & pat->bitmask) == pat->bitmap) {
                flags->pattern_id = i + 1;
                flags->severity = S_MAJOR;
                stats->pattern_counts++;
                // reset the bitmap
                stats->event_bitmap = BITMAP_INIT;
                break;
            }
        }
    }
}

// submit event for userspace via ring buffer
static __always_inline int submit_event(u32 pid, event_type_t type, event_flags_t flags, const char *filename) {
    event_t *event = events.ringbuf_reserve(sizeof(event_t));
    if (!event) {
        return 1;
    }
    event->ts = bpf_ktime_get_ns();
    event->pid = pid;
    event->type = type;
    event->flags = flags;

    bpf_get_current_comm(&event->comm, TASK_COMM_LEN);

    int ret = bpf_probe_read_user_str(event->filename, FILENAME_SIZE, filename);
    if (ret < 0) {
        bpf_probe_read_kernel_str(event->filename, FILENAME_SIZE, filename);
    }

    events.ringbuf_submit(event, 0 /* flags */);
    return 0;
}

// update stats, analyse and submit event
static __always_inline int update_and_submit(event_type_t type, const char* filename) {
    u32 pid = bpf_get_current_pid_tgid();

    // get config
    config_t *conf = get_config();

    // get stats from BPF_HASH
    pidstat_t *curr = get_stats(&pid);
    if (!curr) {
        // cleanup old pid entries in pidstats?
        return 0;
    }

    // update stats
    pidstat_t updated;
    update_stats(conf, type, curr, &updated);

    // analyse stats
    event_flags_t flags;
    analyze_stats(conf, &updated, &flags);

   // save stats in BPF_HASH
    pidstats.update(&pid, &updated);

    // could be filtered based on event_flag
    if (conf && flags.severity >= conf->min_severity) {
        return submit_event(pid, type, flags, filename);
    }
    return 0;
}

// sys_open and sys_openat both have args->filename
TRACEPOINT_PROBE(syscalls, sys_enter_open) {
    // args from /sys/kernel/debug/tracing/events/syscalls/sys_enter_openat/format
    event_type_t type = T_OPEN;
    if (args->flags & O_CREAT) {
        type = T_CREATE;
    }
    return update_and_submit(type, args->filename);
}

// sys_open and sys_openat both have args->filename
TRACEPOINT_PROBE(syscalls, sys_enter_openat) {
    // args from /sys/kernel/debug/tracing/events/syscalls/sys_enter_openat/format
    event_type_t type = T_OPEN;
    if (args->flags & O_CREAT) {
        type = T_CREATE;
    }
    return update_and_submit(type, args->filename);
}

// sys_unlink and sys_unlinkat both have args->pathname
TRACEPOINT_PROBE(syscalls, sys_enter_unlink) {
    // args from /sys/kernel/debug/tracing/events/syscalls/sys_enter_unlink/format
    return update_and_submit(T_DELETE, args->pathname);
}

// sys_unlink and sys_unlinkat both have args->pathname
TRACEPOINT_PROBE(syscalls, sys_enter_unlinkat) {
    // args from /sys/kernel/debug/tracing/events/syscalls/sys_enter_unlink/format
    return update_and_submit(T_DELETE, args->pathname);
}

// uprobe on openssl
// int EVP_EncryptInit_ex(EVP_CIPHER_CTX *ctx, const EVP_CIPHER *type,
//                        ENGINE *impl, const unsigned char *key, const unsigned char *iv);
// int EVP_CipherInit_ex(EVP_CIPHER_CTX *ctx, const EVP_CIPHER *type,
//                       ENGINE *impl, const unsigned char *key, const unsigned char *iv, int enc);
int trace_encrypt1(struct pt_regs *ctx) {
    const char func[FILENAME_SIZE] = "EVP_EncryptInit_ex";
    return update_and_submit(T_ENCRYPT, func);
}
// int EVP_SealInit(EVP_CIPHER_CTX *ctx, const EVP_CIPHER *type,
//                  unsigned char **ek, int *ekl, unsigned char *iv,
//                  EVP_PKEY **pubk, int npubk);
int trace_encrypt2(struct pt_regs *ctx) {
    const char func[FILENAME_SIZE] = "EVP_CipherInit_ex";
    return update_and_submit(T_ENCRYPT, func);
}
