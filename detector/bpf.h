/*  DISCLAIMER
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE. */

#pragma once

// type of event that occured
typedef enum event_type {
    T_OPEN = 0,
    T_CREATE = 1,
    T_DELETE = 2,
    T_ENCRYPT = 3,
    EVENT_TYPES,        // counts the number of event types
} event_type_t;

// flag suspicious events
typedef u8 severity_t;

typedef struct event_flags {
    severity_t severity;    // event severity
    u8 pattern_id;          // id of the pattern matched
    u8 thresholds_crossed;   // bitmap of event_type
} event_flags_t;

// severity levels
#define S_NORMAL    0
#define S_MINOR     1
#define S_MAJOR     2

#define FILENAME_SIZE    64

// an event to be reported
typedef u64 time_t;

typedef struct event {
    time_t ts;
    u32 pid;
    event_type_t type;
    event_flags_t flags;
    char filename[FILENAME_SIZE];
} event_t;

// file stats per pid
typedef u32 bitmap_t;
typedef u16 counts_t;

typedef struct pidstat {
    time_t last_reset_ts;               // timestamp of last counter reset (in nanosec)
    bitmap_t event_bitmap;              // see below
    counts_t event_counts[EVENT_TYPES]; // counts number of events per type
    counts_t pattern_counts;            // counts number of pattern matches
} pidstat_t;

/* The event_bitmap is a simple ring buffer filled from right (LSB) to left (MSB)
   It can store at most the last 8 event_types
   Each event_type is encoded using 4 bits
   Events are pushed from the right and shifted left
   Example: 0xFFFFF012 (then 0xFFFF0120 -> 0xFFF01201 ...)
   Corresponds to: T_OPEN (0), T_CREATE (1), T_UNLINK (2)
   Default: 0xFFFFFFFF means "no event" */

#define BITMAP_INIT     0xFFFFFFFF // initial value = no event
#define BITS_PER_EVENT  4  // number of bits per event
#define BITMAP_EVENTS   8  // max number of events in bitmap

// event patterns (event sequences)
// loaded from userspace into a BPF_ARRAY(MAX_PATTERNS)
typedef struct event_pattern {
    bitmap_t bitmap;
    bitmap_t bitmask;
} event_pattern_t;

#define MAX_PATTERNS    8

// configuration data, loaded from userspace into a BPF_ARRAY(1)
typedef struct config {
    counts_t thresholds[EVENT_TYPES];   // counter thresholds for each event type
    time_t reset_period_ns;             // nanoseconds btw counter reset
    severity_t min_severity;            // minimum severity to report events
} config_t;