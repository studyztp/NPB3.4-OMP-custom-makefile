FLAGS=${BASIC_FLAGS}

all: c_print_results.ll c_timers.ll print_results.ll randdp.ll randdpvec.ll \
	randi8_safe.ll randi8.ll timers.ll wtime.ll \
	profile_helper_naive.ll profile_helper_profiling.ll \
	profile_helper_m5_fs.ll profile_helper_papi.ll \
	profile_helper_papi_profiling.ll \
	profile_helper_papi_naive.ll

c_print_results.ll: c_print_results.c
	${CC} ${FLAGS} -S -emit-llvm c_print_results.c -o c_print_results.ll

c_timers.ll: c_timers.c
	${CC} ${FLAGS} -S -emit-llvm c_timers.c -o c_timers.ll

print_results.ll: print_results.f90
	${FC} ${FLAGS} -S -emit-llvm print_results.f90 -o print_results.ll

randdp.ll: randdp.f90
	${FC} ${FLAGS} -S -emit-llvm randdp.f90 -o randdp.ll

randdpvec.ll: randdpvec.f90
	${FC} ${FLAGS} -S -emit-llvm randdpvec.f90 -o randdpvec.ll

randi8_safe.ll: randi8_safe.f90
	${FC} ${FLAGS} -S -emit-llvm randi8_safe.f90 -o randi8_safe.ll

randi8.ll: randi8.f90
	${FC} ${FLAGS} -S -emit-llvm randi8.f90 -o randi8.ll

timers.ll: timers.f90
	${FC} ${FLAGS} -S -emit-llvm timers.f90 -o timers.ll

wtime.ll: wtime.c
	${CC} ${FLAGS} -S -emit-llvm wtime.c -o wtime.ll

profile_helper_naive.ll: cpp_profiler_helper.cpp
	${CPP} ${FLAGS} -S -DNAIVE -emit-llvm \
							cpp_profiler_helper.cpp -o profile_helper_naive.ll

profile_helper_papi_naive.ll: profile_helper.c
	${CC} ${FLAGS} ${PAPI_LINE} -S -DPAPI_NAIVE -emit-llvm \
							profile_helper.c -o profile_helper_papi_naive.ll

profile_helper_profiling.ll: cpp_profiler_helper.cpp
	${CPP} ${FLAGS} -S -DPROFILING -emit-llvm \
					cpp_profiler_helper.cpp -o profile_helper_profiling.ll

profile_helper_m5_fs.ll: profile_helper.c
	${CC} ${FLAGS} -S -DM5_FS -emit-llvm \
							profile_helper.c -o profile_helper_m5_fs.ll ${M5_INCLUDE}

profile_helper_papi_profiling.ll: profile_helper.c
	${CC} ${FLAGS} ${PAPI_LINE} -S -DUSING_PAPI_PROFILING -emit-llvm \
							profile_helper.c -o profile_helper_papi_profiling.ll

profile_helper_papi.ll: profile_helper.c
	${CC} ${FLAGS} ${PAPI_LINE} -S -DPAPI -emit-llvm \
							profile_helper.c -o profile_helper_papi.ll

clean:
	rm -f *.ll
