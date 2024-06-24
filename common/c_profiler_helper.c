#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>
#include <omp.h>

#ifdef ATOMIC
#include <stdatomic.h>
atomic_ullong counter;
#else
unsigned long long** counters;
unsigned long long current_counter;
uint8_t num_threads;
#endif

#define BOOL uint8_t
#define TRUE 1
#define FALSE 0

omp_lock_t lock;
BOOL wait = FALSE;
BOOL ifStart = FALSE;
unsigned long long threshold = 100000000;
unsigned long long region = 0;

__attribute__((no_profile_instrument_function, noinline))
void bb_hook(unsigned long long inst) {
#ifdef ATOMIC
    if (ifStart) {
        if (wait) {
            omp_set_lock(&lock);
            omp_unset_lock(&lock);
        }
        atomic_fetch_add(&counter, inst);
        if (omp_get_thread_num() == 0) {
            if (atomic_load(&counter) >= threshold) {
                omp_set_lock(&lock);
                wait = TRUE;
                atomic_store(&counter, 0);
                region ++;
                wait = FALSE;
                omp_unset_lock(&lock);
            }
        }
    }
#else
    if (ifStart) {
        if (wait) {
            omp_set_lock(&lock);
            omp_unset_lock(&lock);
        }
        *counters[omp_get_thread_num()] += inst;
        if (omp_get_thread_num() == 0) {
            current_counter = *counters[0];
            for (uint8_t i = 1; i < num_threads; i++) {
                current_counter += *counters[i];
            }
            if (current_counter >= threshold) {
                omp_set_lock(&lock);
                wait = TRUE;
                for (uint8_t i = 0; i < num_threads; i ++) {
                    *counters[i] = 0;
                }
                region ++;
                wait = FALSE;
                omp_unset_lock(&lock);
            }
        }
    }
#endif
}

__attribute__((no_profile_instrument_function))
void roi_begin_(uint8_t num_threads_) {
#ifdef ATOMIC
    atomic_init(&counter, 0);
#else
    num_threads = omp_get_max_threads();
    counters = (unsigned long long**)malloc(num_threads * sizeof(unsigned long long*));
    for (uint8_t i = 0; i < num_threads; i++) {
        counters[i] = (unsigned long long*)malloc(sizeof(unsigned long long));
        *counters[i] = 0;
    }
#endif
    omp_init_lock(&lock);
    ifStart = TRUE;
    printf("ROI begin\n");
}

__attribute__((no_profile_instrument_function))
void roi_end_() {
    ifStart = FALSE;
    omp_destroy_lock(&lock);
#ifdef PARALLEL
    for (uint8_t i = 0; i < num_threads; i++) {
        free(counters[i]);
    }
    free(counters);
#endif
    printf("ROI end\n");
    printf("Region: %lu\n", region);

}
