#include <cstdlib>
#include <iostream>
#include <fstream>
#include <string>
#include <omp.h>

#include <atomic>
std::atomic<uint64_t> counter(0);

omp_lock_t lock;
bool wait = false;
bool ifStart = false;
uint64_t region = 0;
uint64_t totalIRInst = 0;

uint64_t total_num_bbs = 0;
uint64_t num_threads = 0;
uint64_t* bbv;
uint64_t* timestamp;

std::string outputfile = "all_output.txt";
FILE *fptr = NULL;

__attribute__((no_profile_instrument_function, noinline))
void process_data() {
    fprintf(fptr, "Region: %lu\n", region);
    fprintf(fptr, "Total IR instructions: %lu\n", totalIRInst);
    fprintf(fptr, "Total IR instructions in region: %lu\n", counter.load());
    for (uint64_t i = 0; i < num_threads; i += 1) {
        fprintf(fptr, "Thread %lu BBV: [", i);
        for (uint64_t j = 0; j < total_num_bbs; j += 1) {
            uint64_t index = i * (total_num_bbs + 64) + j;
            fprintf(fptr, "%lu,", bbv[index]);
        }
        fprintf(fptr, "]\n");
    }
    fprintf(fptr, "Timestamp: [");
    for (uint64_t i = 0; i < total_num_bbs; i += 1) {
        fprintf(fptr, "%lu,", timestamp[i]);
    }
    fprintf(fptr, "]\n");
}

__attribute__((no_profile_instrument_function, noinline))
void bb_hook(uint64_t bb_inst, uint64_t bb_id, uint64_t threshold) {
    if (ifStart) {
        if (wait) {
            omp_set_lock(&lock);
            omp_unset_lock(&lock);
        }
        uint64_t thread_id = omp_get_thread_num();
        uint64_t index = thread_id * (total_num_bbs + 64) + bb_id;
        
        counter += bb_inst;

        bbv[index] += 1;

        if (omp_get_thread_num() == 0) {
            uint64_t cur_counter = counter.load();
            timestamp[bb_id] = cur_counter;
            if (cur_counter >= threshold) {
                omp_set_lock(&lock);
                wait = true;
                region ++;
                totalIRInst += counter.load();
                process_data();
                counter = 0;
                wait = false;
                omp_unset_lock(&lock);
            }
        }
    }
}

__attribute__((no_profile_instrument_function, noinline))
void init_arrays(uint64_t num_bbs) {
    total_num_bbs = num_bbs;
    num_threads = omp_get_max_threads();
    bbv = (uint64_t*)malloc(((num_bbs + 64) * num_threads) * sizeof(uint64_t));
    timestamp = (uint64_t*)malloc((num_bbs * num_threads) * sizeof(uint64_t));
    if (bbv == NULL || timestamp == NULL) {
        std::cerr << "Failed to allocate memory for bbv and timestamp arrays" << std::endl;
        exit(1);
    }
    memset(bbv, 0, ((num_bbs + 64) * num_threads) * sizeof(uint64_t));
    memset(timestamp, 0, (num_bbs * num_threads) * sizeof(uint64_t));
}

__attribute__((no_profile_instrument_function))
void delete_arrays() {
    free(bbv);
    free(timestamp);
}

__attribute__((no_profile_instrument_function))
extern "C" void roi_begin_() {
    counter = 0;
    omp_init_lock(&lock);
    ifStart = true;

    fptr = fopen(outputfile.c_str(), "w");
    if (fptr == NULL) {
        std::cerr << "Failed to open file " << outputfile << std::endl;
        exit(1);
    }

    printf("ROI begin\n");
}

__attribute__((no_profile_instrument_function))
extern "C" void roi_end_() {
    ifStart = false;
    omp_destroy_lock(&lock);

    fclose(fptr);

    printf("ROI end\n");
    printf("Region: %lu\n", region);
    printf("Total IR instructions: %lu\n", totalIRInst);
}

