#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>
#include <omp.h>

#define BOOL uint8_t
#define TRUE 1
#define FALSE 0

#ifdef PROFILING
#include <stdatomic.h>
atomic_ullong counter;

omp_lock_t lock;
BOOL wait = FALSE;
BOOL ifStart = FALSE;
unsigned long long region = 0;
unsigned long long totalIRInst = 0;

unsigned long long total_num_bbs = 0;
unsigned long long num_threads = 0;
unsigned long long* bbv;
unsigned long long* timestamp;

FILE *fptr = NULL;

__attribute__((no_profile_instrument_function, noinline))
void process_data() {
    totalIRInst += atomic_load(&counter);
    fprintf(fptr, "Region: %llu\n", region);
    fprintf(fptr, "Total IR instructions: %llu\n", totalIRInst);
    fprintf(fptr, "Total IR instructions in region: %llu\n", atomic_load(&counter));
    for (unsigned long long i = 0; i < num_threads; i += 1) {
        fprintf(fptr, "Thread %llu BBV and Timestamp: [", i);
        for (unsigned long long j = 0; j < total_num_bbs; j += 1) {
            unsigned long long index = i * (total_num_bbs + 64) + j;
            fprintf(fptr, "%llu:%llu,", bbv[index], timestamp[index]);
            bbv[index] = 0;
            timestamp[index] = 0;
        }
        fprintf(fptr, "]\n");
    }
    region ++;
    atomic_store(&counter, 0);
}

__attribute__((no_profile_instrument_function, noinline))
void bb_hook(unsigned long long bb_inst, unsigned long long bb_id, unsigned long long threshold) {
    if (ifStart) {
        if (wait) {
            omp_set_lock(&lock);
            omp_unset_lock(&lock);
        }
        unsigned long long thread_id = omp_get_thread_num();
        unsigned long long index = thread_id * (total_num_bbs + 64) + bb_id;

        unsigned long long cur_counter = atomic_fetch_add(&counter, bb_inst) + bb_inst;

        bbv[index] += 1;
        timestamp[index] = cur_counter;

        if (omp_get_thread_num() == 0) {
            if (atomic_load(&counter) >= threshold) {
                omp_set_lock(&lock);
                wait = TRUE;
                process_data();
                wait = FALSE;
                omp_unset_lock(&lock);
            }
        }
    }
}

__attribute__((no_profile_instrument_function, noinline))
void init_arrays(unsigned long long num_bbs) {
    total_num_bbs = num_bbs;
    num_threads = omp_get_max_threads();
    bbv = (unsigned long long*)malloc(((num_bbs + 64) * num_threads) * sizeof(unsigned long long));
    timestamp = (unsigned long long*)malloc(((num_bbs + 64) * num_threads) * sizeof(unsigned long long));
    if (bbv == NULL || timestamp == NULL) {
        printf("Failed to allocate memory for bbv and timestamp arrays\n");
        exit(1);
    }
    memset(bbv, 0, ((num_bbs + 64) * num_threads) * sizeof(unsigned long long));
    memset(timestamp, 0, ((num_bbs + 64) * num_threads) * sizeof(unsigned long long));
}

__attribute__((no_profile_instrument_function))
void delete_arrays() {
    free(bbv);
    free(timestamp);
}

__attribute__((no_profile_instrument_function))
void roi_begin_(uint8_t num_threads_) {
    atomic_init(&counter, 0);
    omp_init_lock(&lock);
    ifStart = TRUE;
    char outputfile[256];
    sprintf(outputfile, "all_output_%d_threads.txt", omp_get_max_threads());

    fptr = fopen(outputfile, "w");
    if (fptr == NULL) {
        printf("Failed to open file\n");
        exit(1);
    }

    printf("ROI begin\n");
}

__attribute__((no_profile_instrument_function))
void roi_end_() {
    ifStart = FALSE;
    omp_destroy_lock(&lock);

    process_data();

    fclose(fptr);

    delete_arrays();

    printf("ROI end\n");
    printf("Region: %llu\n", region);
    printf("Total IR instructions: %llu\n", totalIRInst);
}

#endif

#ifdef NAIVE
__attribute__((no_profile_instrument_function, noinline))
void roi_begin_() {
    printf("ROI begin\n");
}

__attribute__((no_profile_instrument_function, noinline))
void roi_end_() {
    printf("ROI end\n");
}

#endif

#ifdef USING_PAPI_PROFILING
#include <papi.h>
#include <stdatomic.h>
atomic_ullong counter;

omp_lock_t lock;
BOOL wait = FALSE;
BOOL ifStart = FALSE;
unsigned long long region = 0;
unsigned long long totalIRInst = 0;

__attribute__((no_profile_instrument_function, noinline))
void start_papi_region() {
    char str[64];
    sprintf(str, "%llu", region);
    printf("Starting PAPI %s region\n", str);
    int retval = PAPI_hl_region_begin(str);
    if (retval != PAPI_OK) {
        printf("PAPI_hl_region_begin failed due to %d.\n", retval);
    }
}

__attribute__((no_profile_instrument_function, noinline))
void end_papi_region() {
    char str[64];
    sprintf(str, "%llu", region);
    printf("Ending PAPI %s region\n", str);
    int retval = PAPI_hl_region_end(str);
    if (retval != PAPI_OK) {
        printf("PAPI_hl_region_end failed due to %d.\n", retval);
    }
}

__attribute__((no_profile_instrument_function, noinline))
void bb_hook(unsigned long long bb_inst, unsigned long long threshold) {
    if (ifStart) {
        if (wait) {
            omp_set_lock(&lock);
            omp_unset_lock(&lock);
        }
        atomic_fetch_add(&counter, bb_inst);
        if (omp_get_thread_num() == 0) {
            if (atomic_load(&counter) >= threshold) {
                end_papi_region();
                omp_set_lock(&lock);
                wait = TRUE;
                printf("Region: %llu\n", region);
                totalIRInst += atomic_load(&counter);
                printf("Total IR instructions: %llu\n", totalIRInst);
                printf("Total IR instructions in region: %llu\n", atomic_load(&counter));
                atomic_store(&counter, 0);
                region ++;
                wait = FALSE;
                omp_unset_lock(&lock);
                start_papi_region();
            }
        }
    }
}

__attribute__((no_profile_instrument_function, noinline))
void roi_begin_() {
    atomic_init(&counter, 0);
    omp_init_lock(&lock);
    ifStart = TRUE;

    int retval = PAPI_library_init(PAPI_VER_CURRENT);
    if (retval != PAPI_VER_CURRENT) {
        printf("PAPI_library_init failed due to %d.\n", retval);
    }
    retval = PAPI_set_domain(PAPI_DOM_ALL);
    if (retval != PAPI_OK) {
        printf("PAPI_set_domain failed due to %d.\n", retval);
    }
    printf("ROI begin\n");
    start_papi_region();
}

__attribute__((no_profile_instrument_function, noinline))
void roi_end_() {
    end_papi_region();
    ifStart = FALSE;
    omp_destroy_lock(&lock);

    printf("ROI end\n");
    printf("Region: %llu\n", region);
    printf("Total IR instructions: %llu\n", totalIRInst);
}

#endif

#ifdef MEASURING
#include <stdatomic.h>
atomic_ullong warmUpCounter;
atomic_ullong startCounter;
atomic_ullong endCounter;

unsigned long long warmUpThreshold;
unsigned long long startThreshold;
unsigned long long endThreshold;

BOOL ifWarmUpNotMet = FALSE;
BOOL ifStartNotMet = FALSE;
BOOL ifEndNotMet = FALSE;

#ifdef PAPI_MEASURING
#include <papi.h>

__attribute__((no_profile_instrument_function, noinline))
void warmUpEvent() {
}

__attribute__((no_profile_instrument_function, noinline))
void startEvent() {
    int retval = PAPI_hl_region_begin("0");
    if (retval != PAPI_OK) {
        printf("PAPI_hl_region_begin failed due to %d.\n", retval);
    }
}

__attribute__((no_profile_instrument_function, noinline))
void endEvent() {
    int retval = PAPI_hl_region_end("0");
    if (retval != PAPI_OK) {
        printf("PAPI_hl_region_end failed due to %d.\n", retval);
    }
    printf("PAPI ended\nNow exiting the program\n");
    exit(0);
}

__attribute__((no_profile_instrument_function, noinline))
void roi_begin_() {
    atomic_init(&warmUpCounter, 0);
    atomic_init(&startCounter, 0);
    atomic_init(&endCounter, 0);
    
    ifWarmUpNotMet = TRUE;

    int retval = PAPI_library_init(PAPI_VER_CURRENT);
    if (retval != PAPI_VER_CURRENT) {
        printf("PAPI_library_init failed due to %d.\n", retval);
    }
    retval = PAPI_set_domain(PAPI_DOM_ALL);
    if (retval != PAPI_OK) {
        printf("PAPI_set_domain failed due to %d.\n", retval);
    }
    printf("ROI started\n");
    printf("PAPI initialized\n");
}

__attribute__((no_profile_instrument_function, noinline))
void roi_end_() {
    printf("ROI ended\n");
}

#elif defined(M5_FS_MEASURING)

#include "gem5/m5ops.h"
#include "m5_mmap.h"
#include <errno.h>
#include <sys/utsname.h>

__attribute__((no_profile_instrument_function, noinline))
void warmUpEvent() {
    printf("M5_FS Warmup marker\n");
    m5_work_begin_addr(0, 0);
}

__attribute__((no_profile_instrument_function, noinline))
void startEvent() {
    printf("M5_FS Start marker\n");
    m5_work_begin_addr(0, 0);
}

__attribute__((no_profile_instrument_function, noinline))
void endEvent() {
    printf("M5_FS End marker\n");
    m5_work_end_addr(0, 0);
}

__attribute__((no_profile_instrument_function, noinline))
void roi_begin_() {
    atomic_init(&warmUpCounter, 0);
    atomic_init(&startCounter, 0);
    atomic_init(&endCounter, 0);
    
    ifWarmUpNotMet = TRUE;

    struct utsname buffer;
    errno = 0;
    if (uname(&buffer) < 0) {
        perror("uname");
        exit(EXIT_FAILURE);
    }

    printf("arch     = %s\n", buffer.machine);

    if (strcmp(buffer.machine, "x86_64") == 0) {
        m5op_addr = 0xFFFF0000;
    } else if (strcmp(buffer.machine, "aarch64") == 0) {
        m5op_addr = 0x10010000;
    } else {
        m5op_addr = 0x0;
        printf("Unsupported architecture\n");
    }
    map_m5_mem();
    printf("M5_FS ADDR MOP initialized\n");
    printf("M5_FS ROI started\n");
}

__attribute__((no_profile_instrument_function, noinline))
void roi_end_() {
    unmap_m5_mem();
    printf("M5_FS ROI ended\n");
}

#elif defined(MARKER_OVERHEAD_MEASURING)

__attribute__((no_profile_instrument_function, noinline))
void warmUpEvent() {
    printf("Warm up event reached\n");
}

__attribute__((no_profile_instrument_function, noinline))
void startEvent() {
    printf("Start event reached\n");
}

__attribute__((no_profile_instrument_function, noinline))
void endEvent() {
    printf("End event reached\n");
}

__attribute__((no_profile_instrument_function, noinline))
void roi_begin_() {

    int retval = PAPI_library_init(PAPI_VER_CURRENT);
    if (retval != PAPI_VER_CURRENT) {
        printf("PAPI_library_init failed due to %d.\n", retval);
    }
    retval = PAPI_set_domain(PAPI_DOM_ALL);
    if (retval != PAPI_OK) {
        printf("PAPI_set_domain failed due to %d.\n", retval);
    }
    printf("ROI started\n");
    printf("PAPI initialized\n");

    printf("PAPI region begin\n");

    retval = PAPI_hl_region_begin("0");
    if (retval != PAPI_OK) {
        printf("PAPI_hl_region_begin failed due to %d.\n", retval);
    }
}

void roi_end_() {
    printf("PAPI region end\n");

    int retval = PAPI_hl_region_end("0");
    if (retval != PAPI_OK) {
        printf("PAPI_hl_region_end failed due to %d.\n", retval);
    }
    printf("PAPI ended\nNow exiting the program\n");
    exit(0);
}

#endif

__attribute__((no_profile_instrument_function, noinline))
void setupThresholds(unsigned long long warmUp, unsigned long long start, unsigned long long end) {
    warmUpThreshold = warmUp;
    startThreshold = start;
    endThreshold = end;
}

__attribute__((no_profile_instrument_function, noinline))
void warmUpHook() {
    if (ifWarmUpNotMet) {
        unsigned long long curr_count = atomic_fetch_add(&warmUpCounter, 1);
        if (curr_count + 1 == warmUpThreshold) {
            ifWarmUpNotMet = FALSE;
            printf("Warm up marker met\n");
            warmUpEvent();
            ifStartNotMet = TRUE;
        }
    }
}

__attribute__((no_profile_instrument_function, noinline))
void startHook() {
    if (ifStartNotMet) {
        unsigned long long curr_count = atomic_fetch_add(&startCounter, 1);
#ifdef PAPI_MEASURING
        if (omp_get_thread_num() == 0) {
            if (curr_count + 1 >= startThreshold) {
                ifStartNotMet = FALSE;
                printf("Start marker met\n");
                startEvent();
                ifEndNotMet = TRUE;
            }
        }
#else
        if (curr_count + 1 == startThreshold) {
            ifStartNotMet = FALSE;
            printf("Start marker met\n");
            startEvent();
            ifEndNotMet = TRUE;
        }
#endif
    }
}

__attribute__((no_profile_instrument_function, noinline))
void endHook() {
    if (ifEndNotMet) {
        unsigned long long curr_count =  atomic_fetch_add(&endCounter, 1);
#ifdef PAPI_MEASURING
        if (omp_get_thread_num() == 0) {
            if (curr_count + 1 >= endThreshold) {
                ifEndNotMet = FALSE;
                printf("End marker met\n");
                endEvent();
            }
        }
#else
        if (curr_count + 1 == endThreshold) {
            ifEndNotMet = FALSE;
            printf("End marker met\n");
            endEvent();
        }
#endif
    }
}

#endif

#ifdef PAPI_NAIVE
__attribute__((no_profile_instrument_function, noinline))
void roi_begin_() {

    int retval = PAPI_library_init(PAPI_VER_CURRENT);
    if (retval != PAPI_VER_CURRENT) {
        printf("PAPI_library_init failed due to %d.\n", retval);
    }
    retval = PAPI_set_domain(PAPI_DOM_ALL);
    if (retval != PAPI_OK) {
        printf("PAPI_set_domain failed due to %d.\n", retval);
    }
    printf("ROI started\n");
    printf("PAPI initialized\n");

    printf("PAPI region begin\n");

    retval = PAPI_hl_region_begin("0");
    if (retval != PAPI_OK) {
        printf("PAPI_hl_region_begin failed due to %d.\n", retval);
    }
}

void roi_end_() {
    printf("PAPI region end\n");

    int retval = PAPI_hl_region_end("0");
    if (retval != PAPI_OK) {
        printf("PAPI_hl_region_end failed due to %d.\n", retval);
    }
    printf("PAPI ended\nNow exiting the program\n");
    exit(0);
}

#endif

