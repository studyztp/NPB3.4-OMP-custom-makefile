#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>
#include <omp.h>
#ifdef PROFILING
#elif M5_SE
#include "gem5/m5ops.h"
#elif M5_FS
#include "gem5/m5ops.h"
#include "m5_mmap.h"
#include <errno.h>
#include <sys/utsname.h>
#elif PAPI_NAIVE
#include "papi.h"
#elif PAPI
#include "papi.h"
#elif USING_PAPI_PROFILING
#include "papi.h"
#endif

omp_lock_t writelock;
uint8_t lock_initialized = 0;

__attribute__((no_profile_instrument_function))
void get_lock() {
    if (!lock_initialized) {
        omp_init_lock(&writelock);
        lock_initialized = 1;
    }
    if (omp_in_parallel()) {
        omp_set_lock(&writelock);
    }
}

__attribute__((no_profile_instrument_function))
void release_lock() {
    if (omp_in_parallel()) {
        omp_unset_lock(&writelock);
     }
}

#ifdef PROFILING

char filename[] = "profiler_output.txt";
FILE *fptr = NULL;
uint64_t is_profiling = 0;

__attribute__((no_profile_instrument_function))
void write_single_data(char varName[], uint64_t var) {
    if(is_profiling != 0) {
        is_profiling++;
        fprintf(fptr, "Region%lu %s: %ld\n", is_profiling-1, varName, var);
    }
}

__attribute__((no_profile_instrument_function))
void write_array_data(char varName[], uint64_t* arr, uint32_t n) {
    if (is_profiling != 0) {
        fprintf(fptr, "Region%lu %s: \n", is_profiling-1, varName);
        for (uint32_t i = 0; i < n; i++) {
            fprintf(fptr, "%d:%ld ", i, arr[i]);
        }
        fprintf(fptr, "\n");
    }
}

__attribute__((no_profile_instrument_function))
void increment_array_element_at(uint64_t* arr, int index) {
    arr[index]++;
}

__attribute__((no_profile_instrument_function))
void set_array_element_at(uint64_t* arr, int index, uint64_t val) {
    arr[index] = val;
}

__attribute__((no_profile_instrument_function))
void increase_array_by(uint64_t* arr, int n, uint64_t inst) {
    for (int i = 0; i < n; i++) {
        arr[i] += inst;
    }
}

__attribute__((no_profile_instrument_function))
void reset_array(uint64_t* arr, int n) {
    for (int i = 0; i < n; i++) {
        arr[i] = 0;
    }
}
#elif USING_PAPI_PROFILING

uint64_t region_id = 0;
uint8_t start_profiling = 0;

__attribute__((no_profile_instrument_function))
void start_papi_region() {
    if(start_profiling) {
        char str[64];
        sprintf(str, "%lu", region_id);
        printf("Starting PAPI %s region\n", str);
        int retval = PAPI_hl_region_begin(str);
        if (retval != PAPI_OK) {
            printf("PAPI_hl_region_begin failed due to %d.\n", retval);
        }
    }
}

__attribute__((no_profile_instrument_function))
void end_papi_region() {
    if(start_profiling) {
        char str[64];
        sprintf(str, "%lu", region_id);
        printf("Ending PAPI %s region\n", str);
        int retval = PAPI_hl_region_end(str);
        if (retval != PAPI_OK) {
            printf("PAPI_hl_region_end failed due to %d.\n", retval);
        }
        region_id++;
    }
}

#endif

__attribute__((no_profile_instrument_function))
void roi_begin_() {
#ifdef PROFILING
    is_profiling = 1;
    fptr = fopen(filename, "a");
    printf("Profiling started\n");
#elif M5_SE
    printf("M5_SE ROI started\n");
#elif M5_FS

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
    printf("M5_FS ROI started\n");
#elif NAIVE
    printf("ROI started\n");
#elif PAPI_NAIVE
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
    printf("Starting PAPI roi region\n");
    PAPI_hl_region_begin("roi");
    if (retval != PAPI_OK) {
        printf("PAPI_hl_region_begin failed due to %d.\n", retval);
    }
#elif PAPI
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

#elif USING_PAPI_PROFILING
    start_profiling = 1;
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
    start_papi_region();
#endif
}

__attribute__((no_profile_instrument_function))
void roi_end_() {
    omp_destroy_lock(&writelock);
#ifdef PROFILING
    is_profiling = 0;
    fclose(fptr);
    printf("Profiling ended\n");
#elif M5_SE
    printf("M5_SE ROI ended\n");
#elif M5_FS
    unmap_m5_mem();
    printf("M5_FS ROI ended\n");
#elif NAIVE
    printf("ROI ended\n");
#elif PAPI_NAIVE
    int retval = PAPI_hl_region_end("roi");
    if (retval != PAPI_OK) {
        printf("PAPI_hl_region_end failed due to %d.\n", retval);
    }
    printf("Ending PAPI roi region\n");
#elif USING_PAPI_PROFILING
    end_papi_region();
    printf("ROI ended\n");
    start_profiling = 0;
#else
    printf("ROI ended\n");
#endif
}

#ifndef PROFILING

__attribute__((no_profile_instrument_function))
void warmup_marker() {
#ifdef M5_SE
    printf("M5_SE Warmup marker\n");
    m5_work_begin(0, 0);
#elif M5_FS
    printf("M5_FS Warmup marker\n");
    m5_work_begin_addr(0, 0);
#else
    printf("warmup marker\n");
#endif
}

__attribute__((no_profile_instrument_function))
void start_marker() {
#ifdef M5_SE
    printf("M5_SE Start marker\n");
    m5_work_begin(0, 0);
#elif M5_FS
    printf("M5_FS Start marker\n");
    m5_work_begin(0, 0);
#elif NAIVE
    printf("Start marker\n");
#elif PAPI
    printf("Start marker\n");
    char str[] = "0";
    int retval = PAPI_hl_region_begin(str);
    if (retval != PAPI_OK) {
        printf("PAPI_hl_region_begin failed due to %d.\n", retval);
    }
#endif
}

__attribute__((no_profile_instrument_function))
void end_marker() {
#ifdef M5_SE
    printf("M5_SE End marker\n");
    m5_work_end(0, 0);
#elif M5_FS
    printf("M5_FS End marker\n");
    m5_work_end(0,0);
#elif NAIVE
    printf("End marker\n");
#elif PAPI
    char str[] = "0";
    int retval = PAPI_hl_region_end(str);
    if (retval != PAPI_OK) {
        printf("PAPI_hl_region_end failed due to %d.\n", retval);
    }
    printf("End marker\n");
    printf("Exit now\n");
    exit(0);
#endif
}

#endif

