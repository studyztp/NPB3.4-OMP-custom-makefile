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

PROGRAM = dc

BENCHMARK=dc
BENCHMARKU=DC

PAPI_PATH = ${COMMON}/papi/install
PAPI_INCLUDE = ${PAPI_PATH}/include
PAPI_LIB = ${PAPI_PATH}/lib
PAPI_LINE = -I${PAPI_INCLUDE} -L${PAPI_LIB} -lpapi -lpthread

M5_PATH = ${COMMON}/gem5
M5_LINE = -I${M5_PATH} -L${M5_PATH}/out -lm5

all: pre dc

pre: ${SYS_DIR}/setparams.c
	${CC} -o setparams ${SYS_DIR}/setparams.c
	./setparams ${PROGRAM} ${SIZE}

dc: adc.ll dc.ll extbuild.ll rbt.ll jobcntl.ll \
	${COMMON}/c_print_results.ll  \
	${COMMON}/c_timers.ll ${COMMON}/wtime.ll
	${LLVM_LINK} -o dc.bc adc.ll dc.ll extbuild.ll rbt.ll jobcntl.ll \
	${COMMON}/c_print_results.ll  \
	${COMMON}/c_timers.ll ${COMMON}/wtime.ll

naive: dc.bc ${COMMON}/profile_helper_naive.ll
	mkdir -p naive
	${LLVM_LINK} -o naive/dc_naive.bc dc.bc ${COMMON}/profile_helper_naive.ll
	${LLC} ${LLC_FLAGS} naive/dc_naive.bc -o naive/dc_naive.o
	${CC} ${COMPILER_FLAGS} -fopenmp -o naive/dc_naive naive/dc_naive.o

papi_naive: dc.bc ${COMMON}/profile_helper_papi_naive.ll
	mkdir -p papi_naive
	${LLVM_LINK} -o papi_naive/dc_papi_naive.bc dc.bc ${COMMON}/profile_helper_papi_naive.ll
	${LLC} ${LLC_FLAGS} papi_naive/dc_papi_naive.bc -o papi_naive/dc_papi_naive.o
	${CC} ${COMPILER_FLAGS} ${PAPI_LINE} -fopenmp -o papi_naive/dc_papi_naive papi_naive/dc_papi_naive.o


profiling: dc.bc ${COMMON}/profile_helper_profiling.ll
	mkdir -p profiling
	${LLVM_LINK} -o profiling/dc_profiling.bc dc.bc ${COMMON}/profile_helper_profiling.ll
	cd profiling && ${OPT} -passes=phase-analysis dc_profiling.bc -o dc_profiling_opt.bc 2>> dc_profiling_opt.log
	${LLC} ${LLC_FLAGS} profiling/dc_profiling_opt.bc -o profiling/dc_profiling_opt.o
	${CC} ${COMPILER_FLAGS} -fopenmp -o profiling/dc_profiling profiling/dc_profiling_opt.o

m5_fs: m5_fs_${REGION}
m5_fs_${REGION}: dc.bc ${COMMON}/profile_helper_m5_fs.ll
	mkdir -p m5_fs
	mkdir -p m5_fs/${REGION}
	${LLVM_LINK} -o m5_fs/${REGION}/dc_m5_fs_${REGION}.bc dc.bc ${COMMON}/profile_helper_m5_fs.ll
	cd m5_fs/${REGION} && ${OPT} -passes=phase-bound dc_m5_fs_${REGION}.bc -o dc_m5_fs_${REGION}_opt.bc 2>> dc_m5_fs_${REGION}_opt.log
	${LLC} ${LLC_FLAGS} m5_fs/${REGION}/dc_m5_fs_${REGION}_opt.bc -o m5_fs/${REGION}/dc_m5_fs_${REGION}_opt.o
	${CC} ${COMPILER_FLAGS} -fopenmp -o m5_fs/${REGION}/dc_m5_fs_${REGION} m5_fs/${REGION}/dc_m5_fs_${REGION}_opt.o ${M5_LINE}

papi: papi_${REGION}
papi_${REGION}: dc.bc ${COMMON}/profile_helper_papi.ll
	mkdir -p papi
	mkdir -p papi/${REGION}
	${LLVM_LINK} -o papi/${REGION}/dc_papi_${REGION}.bc dc.bc ${COMMON}/profile_helper_papi.ll
	cd papi/${REGION} && ${OPT} -passes=phase-bound dc_papi_${REGION}.bc -o dc_papi_${REGION}_opt.bc 2>> dc_papi_${REGION}_opt.log
	${LLC} ${LLC_FLAGS} papi/${REGION}/dc_papi_${REGION}_opt.bc -o papi/${REGION}/dc_papi_${REGION}_opt.o
	${CC} ${COMPILER_FLAGS} ${PAPI_LINE} -fopenmp -o papi/${REGION}/dc_papi_${REGION} papi/${REGION}/dc_papi_${REGION}_opt.o


adc.ll: adc.c npbparams.h
	${CC} -S -emit-llvm adc.c -o adc.ll

dc.ll: dc.c adcc.h adc.h macrodef.h npbparams.h
	${CC} -S -emit-llvm dc.c -o dc.ll

extbuild.ll: extbuild.c adcc.h adc.h macrodef.h npbparams.h
	${CC} -S -emit-llvm extbuild.c -o extbuild.ll

rbt.ll: rbt.c adcc.h adc.h rbt.h macrodef.h npbparams.h
	${CC} -S -emit-llvm rbt.c -o rbt.ll

jobcntl.ll: jobcntl.c adcc.h adc.h macrodef.h npbparams.h
	${CC} -S -emit-llvm jobcntl.c -o jobcntl.ll

clean:
	- rm -f *.o 
	- rm -f npbparams.h core
	- rm -f {../,}ADC.{logf,view,dat,viewsz,groupby,chunks}.* 
	- rm -f *.ll *.bc

clean_all:
	- rm -f *.o 
	- rm -f npbparams.h core
	- rm -f {../,}ADC.{logf,view,dat,viewsz,groupby,chunks}.* 
	- rm -f *.ll
	- rm -rf naive profiling m5_fs papi papi_naive

