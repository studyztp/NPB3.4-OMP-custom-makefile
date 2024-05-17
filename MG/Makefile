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

PROGRAM = mg

BENCHMARK=mg
BENCHMARKU=MG

PAPI_PATH = ${COMMON}/papi/install
PAPI_INCLUDE = ${PAPI_PATH}/include
PAPI_LIB = ${PAPI_PATH}/lib
PAPI_LINE = -I${PAPI_INCLUDE} -L${PAPI_LIB} -lpapi -lpthread

M5_PATH = ${COMMON}/gem5
M5_LINE = -I${M5_PATH} -L${M5_PATH} -lm5

RAND = randi8

all: pre mg

pre: ${SYS_DIR}/setparams.c
	${CC} -o setparams ${SYS_DIR}/setparams.c
	./setparams ${PROGRAM} ${SIZE}

mg: mg.ll mg_data.ll ${COMMON}/print_results.ll ${COMMON}/${RAND}.ll \
	${COMMON}/timers.ll ${COMMON}/wtime.ll
	${LLVM_LINK} -o mg.bc mg.ll mg_data.ll ${COMMON}/print_results.ll \
	${COMMON}/${RAND}.ll ${COMMON}/timers.ll ${COMMON}/wtime.ll

naive: mg.bc ${COMMON}/profile_helper_naive.ll
	mkdir -p naive
	${LLVM_LINK} -o naive/mg_naive.bc mg.bc ${COMMON}/profile_helper_naive.ll
	${LLC} ${LLC_FLAGS} naive/mg_naive.bc -o naive/mg_naive.o
	${FC} ${COMPILER_FLAGS} -fopenmp -o naive/mg_naive naive/mg_naive.o

papi_naive: mg.bc ${COMMON}/profile_helper_papi_naive.ll
	mkdir -p naive
	${LLVM_LINK} -o naive/mg_papi_naive.bc mg.bc ${COMMON}/profile_helper_papi_naive.ll
	${LLC} ${LLC_FLAGS} naive/mg_papi_naive.bc -o naive/mg_papi_naive.o
	${FC} ${COMPILER_FLAGS} ${PAPI_LINE} -fopenmp -o naive/mg_papi_naive naive/mg_papi_naive.o


profiling: mg.bc ${COMMON}/profile_helper_profiling.ll
	mkdir -p profiling
	${LLVM_LINK} -o profiling/mg_profiling.bc mg.bc ${COMMON}/profile_helper_profiling.ll
	cd profiling && ${OPT} -passes=phase-analysis mg_profiling.bc -o mg_profiling_opt.bc 2>> mg_profiling_opt.log
	${LLC} ${LLC_FLAGS} profiling/mg_profiling_opt.bc -o profiling/mg_profiling_opt.o
	${FC} ${COMPILER_FLAGS} -fopenmp -o profiling/mg_profiling profiling/mg_profiling_opt.o

m5_fs: mg.bc ${COMMON}/profile_helper_m5_fs.ll
	mkdir -p m5_fs
	mkdir -p m5_fs/${REGION}
	${LLVM_LINK} -o m5_fs/${REGION}/mg_m5_fs_${REGION}.bc mg.bc ${COMMON}/profile_helper_m5_fs.ll
	cd m5_fs/${REGION} && ${OPT} -passes=phase-bound mg_m5_fs_${REGION}.bc -o mg_m5_fs_${REGION}_opt.bc 2>> mg_m5_fs_${REGION}_opt.log
	${LLC} ${LLC_FLAGS} m5_fs/${REGION}/mg_m5_fs_${REGION}_opt.bc -o m5_fs/${REGION}/mg_m5_fs_${REGION}_opt.o
	${FC} ${COMPILER_FLAGS} ${M5_LINE} -fopenmp -o m5_fs/${REGION}/mg_m5_fs_${REGION} m5_fs/${REGION}/mg_m5_fs_${REGION}_opt.o

papi: mg.bc ${COMMON}/profile_helper_papi.ll
	mkdir -p papi
	mkdir -p papi/${REGION}
	${LLVM_LINK} -o papi/${REGION}/mg_papi_${REGION}.bc mg.bc ${COMMON}/profile_helper_papi.ll
	cd papi/${REGION} && ${OPT} -passes=phase-bound mg_papi_${REGION}.bc -o mg_papi_${REGION}_opt.bc 2>> mg_papi_${REGION}_opt.log
	${LLC} ${LLC_FLAGS} papi/${REGION}/mg_papi_${REGION}_opt.bc -o papi/${REGION}/mg_papi_${REGION}_opt.o
	${FC} ${COMPILER_FLAGS} ${PAPI_LINE} -fopenmp -o papi/${REGION}/mg_papi_${REGION} papi/${REGION}/mg_papi_${REGION}_opt.o

mg.ll: mg.f90 mg_data.ll
	${FC} ${FLAGS} -S -emit-llvm mg.f90 -o mg.ll

mg_data.ll: mg_data.f90 npbparams.h
	${FC} ${FLAGS} -S -emit-llvm mg_data.f90 -o mg_data.ll

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
	- rm -rf naive profiling m5_fs papi_naive papi

