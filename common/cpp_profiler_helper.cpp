#include <cstdlib>
#include <iostream>
#include <string>
#include <omp.h>

#include <atomic>
std::atomic<uint64_t> counter(0);

omp_lock_t lock;
bool wait = false;
bool ifStart = false;
uint64_t region = 0;
uint64_t totalIRInst = 0;

__attribute__((no_profile_instrument_function, noinline))
void bb_hook(uint64_t inst, uint64_t threshold) {
    if (ifStart) {
        if (wait) {
            omp_set_lock(&lock);
            omp_unset_lock(&lock);
        }
        counter += inst;
        if (omp_get_thread_num() == 0) {
            if (counter.load() >= threshold) {
                omp_set_lock(&lock);
                wait = true;
                region ++;
                totalIRInst += counter.load();
                counter = 0;
                wait = false;
                omp_unset_lock(&lock);
            }
        }
    }
}

__attribute__((no_profile_instrument_function))
extern "C" void roi_begin_() {
    counter = 0;
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
    printf("Total IR instructions: %lu\n", totalIRInst);
}

