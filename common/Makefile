FC = /scr/studyztp/compiler/llvm-dir/bin/flang-new
CC = /scr/studyztp/compiler/llvm-dir/bin/clang
OPT = /scr/studyztp/compiler/llvm-dir/bin/opt
LLVM_LINK = /scr/studyztp/compiler/llvm-dir/bin/llvm-link
COMPILER_FLAGS = --target=aarch64-unknown-linux-gnu -mcpu=neoverse-n1
FLAGS = -O3 -fopenmp -lm ${COMPILER_FLAGS}
LLC = /scr/studyztp/compiler/llvm-dir/bin/llc
LLC_FLAGS = -relocation-model=pic -filetype=obj

PAPI_PATH = ./papi/install
PAPI_INCLUDE = ${PAPI_PATH}/include
PAPI_LIB = ${PAPI_PATH}/lib
PAPI_LINE = -I${PAPI_INCLUDE} -L${PAPI_LIB} -lpapi -lpthread

M5_PATH = ./gem5
M5_LINE = -I${M5_PATH} -L${M5_PATH} -lm5


all: c_print_results.ll c_timers.ll print_results.ll randdp.ll randdpvec.ll \
	randi8_safe.ll randi8.ll timers.ll wtime.ll \
	profile_helper_naive.ll profile_helper_profiling.ll \
	profile_helper_m5_fs.ll profile_helper_papi.ll

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

profile_helper_naive.ll: profile_helper.c
	${CC} ${FLAGS} ${PAPI_LINE} -S -DPAPI_NAIVE -emit-llvm \
							profile_helper.c -o profile_helper_naive.ll

profile_helper_profiling.ll: profile_helper.c
	${CC} ${FLAGS} -S -DPROFILING -emit-llvm \
					profile_helper.c -o profile_helper_profiling.ll

profile_helper_m5_fs.ll: profile_helper.c
	${CC} ${FLAGS} ${M5_LINE} -S -DM5_FS -emit-llvm \
							profile_helper.c -o profile_helper_m5_fs.ll

profile_helper_papi.ll: profile_helper.c
	${CC} ${FLAGS} ${PAPI_LINE} -S -DPAPI -emit-llvm \
							profile_helper.c -o profile_helper_papi.ll

clean:
	rm -f *.ll
