#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>
#include <atomic>
#include <omp.h>

// #include "gem5/m5ops.h"
// #include "m5_mmap.h"
 
// #include "papi.h"


std::atomic<uint64_t> counter(0);
omp_lock_t lock;
bool wait = false;
bool ifStart = false;
uint64_t threshold = 100000000;
uint64_t region = 0;

__attribute__((no_profile_instrument_function, noinline))
void bb_hook(uint64_t inst) {
    if (ifStart) {
        if (wait) {
            omp_set_lock(&lock);
            omp_unset_lock(&lock);
        }
        counter+=inst;
        if (counter.load(std::memory_order_relaxed) >= threshold) {
            omp_set_lock(&lock);
            if (counter.load() >= threshold) {
                wait = true;
                // printf("Inner current counter: %lu\n", counter.load());
                // printf("Inner urrent tid: %d\n", omp_get_thread_num());
                counter = 0;
                region ++;
                wait = false;
            }
            omp_unset_lock(&lock);
        }
    }
}

__attribute__((no_profile_instrument_function))
extern "C" void roi_begin_() {
    omp_init_lock(&lock);
    ifStart = true;
    printf("ROI begin\n");
}

__attribute__((no_profile_instrument_function))
extern "C" void roi_end_() {
    ifStart = false;
    omp_destroy_lock(&lock);
    printf("ROI end\n");
    printf("Region: %lu\n", region);
}

