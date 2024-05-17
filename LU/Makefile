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

PROGRAM = lu

BENCHMARK=lu
BENCHMARKU=LU
SVER=

PAPI_PATH = ${COMMON}/papi/install
PAPI_INCLUDE = ${PAPI_PATH}/include
PAPI_LIB = ${PAPI_PATH}/lib
PAPI_LINE = -I${PAPI_INCLUDE} -L${PAPI_LIB} -lpapi -lpthread

M5_PATH = ${COMMON}/gem5
M5_LINE = -I${M5_PATH} -L${M5_PATH} -lm5

all: pre lu

pre: ${SYS_DIR}/setparams.c
	${CC} -o setparams ${SYS_DIR}/setparams.c
	./setparams ${PROGRAM} ${SIZE}

lu: lu.ll lu_data.ll read_input.ll \
	domain.ll setcoeff.ll setbv.ll exact.ll setiv.ll \
	erhs.ll ssor${SVER}.ll rhs.ll l2norm.ll \
	jacld.ll blts.ll jacu.ll buts.ll error.ll \
	pintgr.ll verify.ll ${COMMON}/print_results.ll \
	${COMMON}/timers.ll ${COMMON}/wtime.ll syncs.ll
	${LLVM_LINK} -o lu.bc lu.ll lu_data.ll read_input.ll \
	domain.ll setcoeff.ll setbv.ll exact.ll setiv.ll \
	erhs.ll ssor${SVER}.ll rhs.ll l2norm.ll \
	jacld.ll blts.ll jacu.ll buts.ll error.ll \
	pintgr.ll verify.ll ${COMMON}/print_results.ll \
	${COMMON}/timers.ll ${COMMON}/wtime.ll syncs.ll

naive: lu.bc ${COMMON}/profile_helper_naive.ll
	mkdir -p naive
	${LLVM_LINK} -o naive/lu_naive.bc lu.bc ${COMMON}/profile_helper_naive.ll
	${LLC} ${LLC_FLAGS} naive/lu_naive.bc -o naive/lu_naive.o
	${FC} ${COMPILER_FLAGS} -fopenmp -o naive/lu_naive naive/lu_naive.o

papi_naive: lu.bc ${COMMON}/profile_helper_papi_naive.ll
	mkdir -p naive
	${LLVM_LINK} -o naive/lu_papi_naive.bc lu.bc ${COMMON}/profile_helper_papi_naive.ll
	${LLC} ${LLC_FLAGS} naive/lu_papi_naive.bc -o naive/lu_papi_naive.o
	${FC} ${COMPILER_FLAGS} ${PAPI_LINE} -fopenmp -o naive/lu_papi_naive naive/lu_papi_naive.o


profiling: lu.bc ${COMMON}/profile_helper_profiling.ll
	mkdir -p profiling
	${LLVM_LINK} -o profiling/lu_profiling.bc lu.bc ${COMMON}/profile_helper_profiling.ll
	cd profiling && ${OPT} -passes=phase-analysis lu_profiling.bc -o lu_profiling_opt.bc 2>> lu_profiling_opt.log
	${LLC} ${LLC_FLAGS} profiling/lu_profiling_opt.bc -o profiling/lu_profiling_opt.o
	${FC} ${COMPILER_FLAGS} -fopenmp -o profiling/lu_profiling profiling/lu_profiling_opt.o

m5_fs: lu.bc ${COMMON}/profile_helper_m5_fs.ll
	mkdir -p m5_fs
	mkdir -p m5_fs/${REGION}
	${LLVM_LINK} -o m5_fs/${REGION}/lu_m5_fs_${REGION}.bc lu.bc ${COMMON}/profile_helper_m5_fs.ll
	cd m5_fs/${REGION} && ${OPT} -passes=phase-bound lu_m5_fs_${REGION}.bc -o lu_m5_fs_${REGION}_opt.bc 2>> lu_m5_fs_${REGION}_opt.log
	${LLC} ${LLC_FLAGS} m5_fs/${REGION}/lu_m5_fs_${REGION}_opt.bc -o m5_fs/${REGION}/lu_m5_fs_${REGION}_opt.o
	${FC} ${COMPILER_FLAGS} ${M5_LINE} -fopenmp -o m5_fs/${REGION}/lu_m5_fs_${REGION} m5_fs/${REGION}/lu_m5_fs_${REGION}_opt.o

papi: lu.bc ${COMMON}/profile_helper_papi.ll
	mkdir -p papi
	mkdir -p papi/${REGION}
	${LLVM_LINK} -o papi/${REGION}/lu_papi_${REGION}.bc lu.bc ${COMMON}/profile_helper_papi.ll
	cd papi/${REGION} && ${OPT} -passes=phase-bound lu_papi_${REGION}.bc -o lu_papi_${REGION}_opt.bc 2>> lu_papi_${REGION}_opt.log
	${LLC} ${LLC_FLAGS} papi/${REGION}/lu_papi_${REGION}_opt.bc -o papi/${REGION}/lu_papi_${REGION}_opt.o
	${FC} ${COMPILER_FLAGS} ${PAPI_LINE} -fopenmp -o papi/${REGION}/lu_papi_${REGION} papi/${REGION}/lu_papi_${REGION}_opt.o

lu.ll: lu.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm lu.f90 -o lu.ll

lu_data.ll: lu_data.f90 npbparams.h
	${FC} ${FLAGS} -S -emit-llvm lu_data.f90 -o lu_data.ll

blts.ll: blts.f90
	${FC} ${FLAGS} -S -emit-llvm blts.f90 -o blts.ll

buts.ll: buts.f90
	${FC} ${FLAGS} -S -emit-llvm buts.f90 -o buts.ll

erhs.ll: erhs.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm erhs.f90 -o erhs.ll

error.ll: error.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm error.f90 -o error.ll

exact.ll: exact.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm exact.f90 -o exact.ll

jacld.ll: jacld.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm jacld.f90 -o jacld.ll

jacu.ll: jacu.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm jacu.f90 -o jacu.ll

l2norm.ll: l2norm.f90
	${FC} ${FLAGS} -S -emit-llvm l2norm.f90 -o l2norm.ll

pintgr.ll: pintgr.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm pintgr.f90 -o pintgr.ll

read_input.ll: read_input.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm read_input.f90 -o read_input.ll

rhs.ll: rhs.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm rhs.f90 -o rhs.ll

setbv.ll: setbv.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm setbv.f90 -o setbv.ll

setiv.ll: setiv.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm setiv.f90 -o setiv.ll

setcoeff.ll: setcoeff.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm setcoeff.f90 -o setcoeff.ll

ssor${SVER}.ll: ssor${SVER}.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm ssor${SVER}.f90 -o ssor${SVER}.ll

domain.ll: domain.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm domain.f90 -o domain.ll

verify.ll: verify.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm verify.f90 -o verify.ll

syncs.ll: syncs.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm syncs.f90 -o syncs.ll

clean:
	- rm -f *.o *~ *.mod npbparams.h
	- if [ -d rii_files ]; then rm -r rii_files; fi
	- rm -f *.ll *.bc

clean_all:
	- rm -f *.o *~ *.mod npbparams.h
	- if [ -d rii_files ]; then rm -r rii_files; fi
	- rm -f *.ll *.bc
	- rm -rf naive profiling m5_fs papi_naive papi
