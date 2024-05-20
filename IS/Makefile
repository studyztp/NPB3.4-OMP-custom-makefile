FC = /scr/studyztp/compiler/llvm-dir/bin/flang-new
CC = /scr/studyztp/compiler/llvm-dir/bin/clang
OPT = /scr/studyztp/compiler/llvm-dir/bin/opt
LLVM_LINK = /scr/studyztp/compiler/llvm-dir/bin/llvm-link
COMPILER_FLAGS = --target=aarch64-unknown-linux-gnu -mcpu=neoverse-n1
FLAGS = -O3 -fopenmp -lm ${COMPILER_FLAGS}
LLC = /scr/studyztp/compiler/llvm-dir/bin/llc
LLC_FLAGS = -relocation-model=pic -filetype=obj

COMMON = ../common
SYS_DIR =../sys/

PROGRAM = is

BENCHMARK=is
BENCHMARKU=IS

PAPI_PATH = ${COMMON}/papi/install
PAPI_INCLUDE = ${PAPI_PATH}/include
PAPI_LIB = ${PAPI_PATH}/lib
PAPI_LINE = -I${PAPI_INCLUDE} -L${PAPI_LIB} -lpapi -lpthread

M5_PATH = ${COMMON}/gem5
M5_LINE = -I${M5_PATH} -L${M5_PATH}/out -lm5

all: pre is

pre: ${SYS_DIR}/setparams.c
	${CC} -o setparams ${SYS_DIR}/setparams.c
	./setparams ${PROGRAM} ${SIZE}

is: is.ll \
	${COMMON}/c_print_results.ll ${COMMON}/c_timers.ll ${COMMON}/wtime.ll
	${LLVM_LINK} -o is.bc is.ll \
	${COMMON}/c_print_results.ll ${COMMON}/c_timers.ll ${COMMON}/wtime.ll

naive: is.bc ${COMMON}/profile_helper_naive.ll
	mkdir -p naive
	${LLVM_LINK} -o naive/is_naive.bc is.bc ${COMMON}/profile_helper_naive.ll
	${LLC} ${LLC_FLAGS} naive/is_naive.bc -o naive/is_naive.o
	${CC} ${COMPILER_FLAGS} -fopenmp -o naive/is_naive naive/is_naive.o

papi_naive: is.bc ${COMMON}/profile_helper_papi_naive.ll
	mkdir -p papi_naive
	${LLVM_LINK} -o papi_naive/is_papi_naive.bc is.bc ${COMMON}/profile_helper_papi_naive.ll
	${LLC} ${LLC_FLAGS} papi_naive/is_papi_naive.bc -o papi_naive/is_papi_naive.o
	${CC} ${COMPILER_FLAGS} ${PAPI_LINE} -fopenmp -o papi_naive/is_papi_naive papi_naive/is_papi_naive.o


profiling: is.bc ${COMMON}/profile_helper_profiling.ll
	mkdir -p profiling
	${LLVM_LINK} -o profiling/is_profiling.bc is.bc ${COMMON}/profile_helper_profiling.ll
	cd profiling && ${OPT} -passes=phase-analysis is_profiling.bc -o is_profiling_opt.bc 2>> is_profiling_opt.log
	${LLC} ${LLC_FLAGS} profiling/is_profiling_opt.bc -o profiling/is_profiling_opt.o
	${CC} ${COMPILER_FLAGS} -fopenmp -o profiling/is_profiling profiling/is_profiling_opt.o

m5_fs: m5_fs_${REGION}
m5_fs_${REGION}: is.bc ${COMMON}/profile_helper_m5_fs.ll
	mkdir -p m5_fs
	mkdir -p m5_fs/${REGION}
	${LLVM_LINK} -o m5_fs/${REGION}/is_m5_fs_${REGION}.bc is.bc ${COMMON}/profile_helper_m5_fs.ll
	cd m5_fs/${REGION} && ${OPT} -passes=phase-bound is_m5_fs_${REGION}.bc -o is_m5_fs_${REGION}_opt.bc 2>> is_m5_fs_${REGION}_opt.log
	${LLC} ${LLC_FLAGS} m5_fs/${REGION}/is_m5_fs_${REGION}_opt.bc -o m5_fs/${REGION}/is_m5_fs_${REGION}_opt.o
	${CC} ${COMPILER_FLAGS} -fopenmp -o m5_fs/${REGION}/is_m5_fs_${REGION} m5_fs/${REGION}/is_m5_fs_${REGION}_opt.o ${M5_LINE} 

papi: papi_${REGION}
papi_${REGION}: is.bc ${COMMON}/profile_helper_papi.ll
	mkdir -p papi
	mkdir -p papi/${REGION}
	${LLVM_LINK} -o papi/${REGION}/is_papi_${REGION}.bc is.bc ${COMMON}/profile_helper_papi.ll
	cd papi/${REGION} && ${OPT} -passes=phase-bound is_papi_${REGION}.bc -o is_papi_${REGION}_opt.bc 2>> is_papi_${REGION}_opt.log
	${LLC} ${LLC_FLAGS} papi/${REGION}/is_papi_${REGION}_opt.bc -o papi/${REGION}/is_papi_${REGION}_opt.o
	${CC} ${COMPILER_FLAGS} ${PAPI_LINE} -fopenmp -o papi/${REGION}/is_papi_${REGION} papi/${REGION}/is_papi_${REGION}_opt.o


is.ll: is.c npbparams.h
	${CC} -S -emit-llvm ${FLAGS} is.c -o is.ll

clean:
	- rm -f *.o *~ mputil*
	- rm -f npbparams.h core
	- if [ -d rii_files ]; then rm -r rii_files; fi
	- rm -f *.ll *.bc

clean_all:
	- rm -f *.o *~ mputil*
	- rm -f npbparams.h core
	- if [ -d rii_files ]; then rm -r rii_files; fi
	- rm -f *.ll *.bc
	- rm -rf naive profiling m5_fs papi_naive papi

