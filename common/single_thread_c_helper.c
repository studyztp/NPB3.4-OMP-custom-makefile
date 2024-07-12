#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>

#define BOOL uint8_t
#define TRUE 1
#define FALSE 0

#ifdef PROFILING
unsigned long long counter = 0;
#define ARRAY_SIZE 1000

unsigned long long region = 0;
unsigned long long total_num_bbs = 0;

unsigned long long *bbv;
unsigned long long *timestamp;
unsigned long long **bbv_array;
unsigned long long **timestamp_array;
unsigned long long *counter_array;
unsigned long long current_array_size = ARRAY_SIZE;

BOOL ifStart = FALSE;

FILE *fptr = NULL;

__attribute__((no_profile_instrument_function, noinline))
void increaseArray() {
    current_array_size += ARRAY_SIZE;
    bbv_array = (unsigned long long**)realloc(bbv_array, current_array_size * sizeof(unsigned long long*));
    timestamp_array = (unsigned long long**)realloc(timestamp_array, current_array_size * sizeof(unsigned long long*));
    if (bbv_array == NULL || timestamp_array == NULL) {
        printf("Failed to allocate memory for bbv_array and timestamp_array arrays\n");
        exit(1);
    }
    for (unsigned i = current_array_size - ARRAY_SIZE; i < current_array_size; i ++) 
    {
        bbv_array[i] = (unsigned long long*)malloc((total_num_bbs) * sizeof(unsigned long long));
        timestamp_array[i] = (unsigned long long*)malloc((total_num_bbs) * sizeof(unsigned long long));
        if (bbv_array[i] == NULL || timestamp_array[i] == NULL) {
            printf("Failed to allocate memory for bbv and timestamp arrays\n");
            exit(1);
        }
        memset(bbv_array[i], 0, ((total_num_bbs) * sizeof(unsigned long long)));
        memset(timestamp_array[i], 0, ((total_num_bbs) * sizeof(unsigned long long)));
    }
    counter_array = (unsigned long long*)realloc(counter_array, current_array_size * sizeof(unsigned long long));
    if (counter_array == NULL) {
        printf("Failed to allocate memory for counter_array\n");
        exit(1);
    }
}

__attribute__((no_profile_instrument_function, noinline))
void processData() {
    counter_array[region] = counter;
    region ++;
    bbv = bbv_array[region];
    timestamp = timestamp_array[region];
    if (region + 10 >= current_array_size) {
        increaseArray();
    }
    counter = 0;
}

__attribute__((no_profile_instrument_function, noinline))
void bbHook(unsigned long long bb_inst, unsigned long long bb_id, unsigned long long threshold) {
    if (ifStart) {
        counter += bb_inst;
        bbv[bb_id] += 1;
        timestamp[bb_id] = counter;
        if (counter >= threshold) {
            processData();
        }
    }
}

__attribute__((no_profile_instrument_function, noinline))
void initArrays(unsigned long long num_bbs) {
    total_num_bbs = num_bbs;
    bbv_array = (unsigned long long**)malloc(current_array_size * sizeof(unsigned long long*));
    timestamp_array = (unsigned long long**)malloc(current_array_size * sizeof(unsigned long long*));
    counter_array = (unsigned long long*)malloc(current_array_size * sizeof(unsigned long long));
    if (bbv_array == NULL || timestamp_array == NULL || counter_array == NULL) {
        printf("Failed to allocate memory for bbv_array, timestamp_array and counter_array arrays\n");
        exit(1);
    }
    for (unsigned i = 0; i < current_array_size; i ++) 
    {
        bbv_array[i] = (unsigned long long*)malloc((total_num_bbs) * sizeof(unsigned long long));
        timestamp_array[i] = (unsigned long long*)malloc((total_num_bbs) * sizeof(unsigned long long));
        if (bbv_array[i] == NULL || timestamp_array[i] == NULL) {
            printf("Failed to allocate memory for bbv and timestamp arrays\n");
            exit(1);
        }
        memset(bbv_array[i], 0, ((total_num_bbs) * sizeof(unsigned long long)));
        memset(timestamp_array[i], 0, ((total_num_bbs) * sizeof(unsigned long long)));
    }
    bbv = bbv_array[region];
    timestamp = timestamp_array[region];
}

__attribute__((no_profile_instrument_function, noinline))
void deleteArrays() {
    for (unsigned i = 0; i < current_array_size; i ++) 
    {
        free(bbv_array[i]);
        free(timestamp_array[i]);
    }
    free(bbv_array);
    free(timestamp_array);
    free(counter_array);
}

__attribute__((no_profile_instrument_function, noinline))
void roi_begin_() {
    ifStart = TRUE;

    printf("ROI begin\n");
}

__attribute__((no_profile_instrument_function, noinline))
void roi_end_() {
    ifStart = FALSE;

    processData();

    char outputfile[256];
    sprintf(outputfile, "all_output_1_threads.txt");

    fptr = fopen(outputfile, "w");
    if (fptr == NULL) {
        printf("Failed to open file\n");
        exit(1);
    }

    unsigned long long totalIRInst = 0;

    for (unsigned long long i = 0; i < region; i ++) {
        fprintf(fptr, "Region: %llu\n", i);
        totalIRInst += counter_array[i];
        fprintf(fptr, "Total IR instructions: %llu\n", totalIRInst);
        fprintf(fptr, "Total IR instructions in region: %llu\n", counter_array[i]);
        fprintf(fptr, "Thread 0 BBV and Timestamp: [");
        unsigned long long index = 0;
        for (unsigned long long  k = 0; k < total_num_bbs; k ++) {
            fprintf(fptr, "%llu:%llu,", bbv_array[i][index], timestamp_array[i][index]);
            index ++;
        }
        fprintf(fptr, "]\n");
    }

    fclose(fptr);

    deleteArrays();

    printf("ROI end\n");
    printf("Region: %llu\n", region);
    printf("Total IR instructions: %llu\n", totalIRInst);
}

#endif

#ifdef USING_PAPI_PROFILING
#include <papi.h>

unsigned long long counter = 0;

BOOL ifStart = FALSE;

unsigned long long region = 0;
unsigned long long totalIRInst = 0;

__attribute__((no_profile_instrument_function, noinline))
void startPapiRegion() {
    char str[64];
    sprintf(str, "%llu", region);
    int retval = PAPI_hl_region_begin(str);
    if (retval != PAPI_OK) {
        printf("PAPI_hl_region_begin failed due to %d.\n", retval);
    }
}

__attribute__((no_profile_instrument_function, noinline))
void endPapiRegion() {
    char str[64];
    sprintf(str, "%llu", region);
    int retval = PAPI_hl_region_end(str);
    if (retval != PAPI_OK) {
        printf("PAPI_hl_region_end failed due to %d.\n", retval);
    }
}

__attribute__((no_profile_instrument_function, noinline))
void bbHook(unsigned long long bb_inst, unsigned long long threshold) {
    if (ifStart) { 
        counter += bb_inst;
        if (counter >= threshold) {
            endPapiRegion();
            totalIRInst += counter;
            counter = 0;
            region ++;
            startPapiRegion();
        }
    }
}

__attribute__((no_profile_instrument_function, noinline))
void roi_begin_() {
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

    startPapiRegion();
}

__attribute__((no_profile_instrument_function, noinline))
void roi_end_() {
    ifStart = FALSE;

    endPapiRegion();

    printf("ROI end\n");
    printf("Region: %llu\n", region);
    printf("Total IR instructions: %llu\n", totalIRInst);
}

#endif

#ifdef MEASURING

unsigned long long counter = 0;

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
    printf("Papi Warmup marker\n");
}

__attribute__((no_profile_instrument_function, noinline))
void startEvent() {
    printf("Papi Start marker\n");
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
    printf("Papi End marker\n");
    printf("Now exiting the program\n");
    exit(0);
}

__attribute__((no_profile_instrument_function, noinline))
void roi_begin_() {
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
#include <papi.h>

__attribute__((no_profile_instrument_function, noinline))
void warmUpEvent() {
    printf("Warm up event reached\n");
    printf("PAPI region begin\n");

    int retval = PAPI_hl_region_begin("0");
    if (retval != PAPI_OK) {
        printf("PAPI_hl_region_begin failed due to %d.\n", retval);
    }
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

void roi_end_() {
    int retval = PAPI_hl_region_end("0");
    if (retval != PAPI_OK) {
        printf("PAPI_hl_region_end failed due to %d.\n", retval);
    }
    printf("PAPI region end\n");
    printf("Now exiting the program\n");
    exit(0);
}

#endif

__attribute__((no_profile_instrument_function, noinline))
void setupThresholds(unsigned long long warmUp, unsigned long long start, unsigned long long end) {
    warmUpThreshold = warmUp;
    if (warmUpThreshold == 0) {
        warmUpThreshold = 1;
    }
    startThreshold = start;

    if (startThreshold == 0) {
        startThreshold = 1;
    }
    endThreshold = end;
    if (endThreshold == 0) {
        endThreshold = 1;
    }
    printf("Warm up threshold: %llu\n", warmUpThreshold);
    printf("Start threshold: %llu\n", startThreshold);
    printf("End threshold: %llu\n", endThreshold);
}

__attribute__((no_profile_instrument_function, noinline))
void warmUpHook() {
    if (ifWarmUpNotMet) {
        counter ++;
        if (counter == warmUpThreshold) {
            ifWarmUpNotMet = FALSE;
            printf("Warm up marker met\n");
            warmUpEvent();
            counter = 0;
            ifStartNotMet = TRUE;
        }
    }
}

__attribute__((no_profile_instrument_function, noinline))
void startHook() {
    if (ifStartNotMet) {
        counter ++;
        if (counter == startThreshold) {
            ifStartNotMet = FALSE;
            printf("Start marker met\n");
            startEvent();
            counter = 0;
            ifEndNotMet = TRUE;
        }
    }
}

__attribute__((no_profile_instrument_function, noinline))
void endHook() {
    if (ifEndNotMet) {
        counter ++;
        if (counter == endThreshold) {
            ifEndNotMet = FALSE;
            printf("End marker met\n");
            endEvent();
            counter = 0;
        }
    }
}

#endif

