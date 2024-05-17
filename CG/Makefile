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

PROGRAM = cg

BENCHMARK=cg
BENCHMARKU=CG

PAPI_PATH = ${COMMON}/papi/install
PAPI_INCLUDE = ${PAPI_PATH}/include
PAPI_LIB = ${PAPI_PATH}/lib
PAPI_LINE = -I${PAPI_INCLUDE} -L${PAPI_LIB} -lpapi -lpthread

M5_PATH = ${COMMON}/gem5
M5_LINE = -I${M5_PATH} -L${M5_PATH} -lm5

RAND = randi8

all: pre cg

pre: ${SYS_DIR}/setparams.c
	${CC} -o setparams ${SYS_DIR}/setparams.c
	./setparams ${PROGRAM} ${SIZE}

cg: cg.ll cg_data.ll ${COMMON}/print_results.ll ${COMMON}/${RAND}.ll \
	${COMMON}/timers.ll ${COMMON}/wtime.ll
	${LLVM_LINK} -o cg.bc cg.ll cg_data.ll ${COMMON}/print_results.ll \
	${COMMON}/${RAND}.ll ${COMMON}/timers.ll ${COMMON}/wtime.ll

naive: cg.bc ${COMMON}/profile_helper_naive.ll
	mkdir -p naive
	${LLVM_LINK} -o naive/cg_naive.bc cg.bc ${COMMON}/profile_helper_naive.ll
	${LLC} ${LLC_FLAGS} naive/cg_naive.bc -o naive/cg_naive.o
	${FC} ${COMPILER_FLAGS} -fopenmp -o naive/cg_naive naive/cg_naive.o

papi_naive: cg.bc ${COMMON}/profile_helper_papi_naive.ll
	mkdir -p naive
	${LLVM_LINK} -o naive/cg_papi_naive.bc cg.bc ${COMMON}/profile_helper_papi_naive.ll
	${LLC} ${LLC_FLAGS} naive/cg_papi_naive.bc -o naive/cg_papi_naive.o
	${FC} ${COMPILER_FLAGS} ${PAPI_LINE} -fopenmp -o naive/cg_papi_naive naive/cg_papi_naive.o


profiling: cg.bc ${COMMON}/profile_helper_profiling.ll
	mkdir -p profiling
	${LLVM_LINK} -o profiling/cg_profiling.bc cg.bc ${COMMON}/profile_helper_profiling.ll
	cd profiling && ${OPT} -passes=phase-analysis cg_profiling.bc -o cg_profiling_opt.bc 2>> cg_profiling_opt.log
	${LLC} ${LLC_FLAGS} profiling/cg_profiling_opt.bc -o profiling/cg_profiling_opt.o
	${FC} ${COMPILER_FLAGS} -fopenmp -o profiling/cg_profiling profiling/cg_profiling_opt.o

m5_fs: cg.bc ${COMMON}/profile_helper_m5_fs.ll
	mkdir -p m5_fs
	mkdir -p m5_fs/${REGION}
	${LLVM_LINK} -o m5_fs/${REGION}/cg_m5_fs_${REGION}.bc cg.bc ${COMMON}/profile_helper_m5_fs.ll
	cd m5_fs/${REGION} && ${OPT} -passes=phase-bound cg_m5_fs_${REGION}.bc -o cg_m5_fs_${REGION}_opt.bc 2>> cg_m5_fs_${REGION}_opt.log
	${LLC} ${LLC_FLAGS} m5_fs/${REGION}/cg_m5_fs_${REGION}_opt.bc -o m5_fs/${REGION}/cg_m5_fs_${REGION}_opt.o
	${FC} ${COMPILER_FLAGS} ${M5_LINE} -fopenmp -o m5_fs/${REGION}/cg_m5_fs_${REGION} m5_fs/${REGION}/cg_m5_fs_${REGION}_opt.o

papi: cg.bc ${COMMON}/profile_helper_papi.ll
	mkdir -p papi
	mkdir -p papi/${REGION}
	${LLVM_LINK} -o papi/${REGION}/cg_papi_${REGION}.bc cg.bc ${COMMON}/profile_helper_papi.ll
	cd papi/${REGION} && ${OPT} -passes=phase-bound cg_papi_${REGION}.bc -o cg_papi_${REGION}_opt.bc 2>> cg_papi_${REGION}_opt.log
	${LLC} ${LLC_FLAGS} papi/${REGION}/cg_papi_${REGION}_opt.bc -o papi/${REGION}/cg_papi_${REGION}_opt.o
	${FC} ${COMPILER_FLAGS} ${PAPI_LINE} -fopenmp -o papi/${REGION}/cg_papi_${REGION} papi/${REGION}/cg_papi_${REGION}_opt.o


cg.ll: cg.f90 cg_data.ll
	${FC} ${FLAGS} -S -emit-llvm cg.f90 -o cg.ll

cg_data.ll: cg_data.f90 npbparams.h
	${FC} ${FLAGS} -S -emit-llvm cg_data.f90 -o cg_data.ll

clean:
	- rm -f *.o *~ *.mod
	- rm -f npbparams.h core
	- if [ -d rii_files ]; then rm -r rii_files; fi
	- rm -f *.ll *.bc

clean_all:
	- rm -f *.o *~ *.mod
	- rm -f npbparams.h core
	- if [ -d rii_files ]; then rm -r rii_files; fi
	- rm -f *.ll *.bc
	- rm -rf naive profiling m5_fs papi papi_naive
