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

PROGRAM = sp

BENCHMARK=sp
BENCHMARKU=SP
BLK=
BLKFAC=0

PAPI_PATH = ${COMMON}/papi/install
PAPI_INCLUDE = ${PAPI_PATH}/include
PAPI_LIB = ${PAPI_PATH}/lib
PAPI_LINE = -I${PAPI_INCLUDE} -L${PAPI_LIB} -lpapi -lpthread

M5_PATH = ${COMMON}/gem5
M5_LINE = -I${M5_PATH} -L${M5_PATH}/out -lm5

all: pre sp

pre: ${SYS_DIR}/setparams.c
	${CC} -o setparams ${SYS_DIR}/setparams.c
	./setparams ${PROGRAM} ${SIZE}

sp: sp.ll sp_data.ll initialize.ll exact_solution.ll exact_rhs.ll \
	set_constants.ll adi.ll rhs.ll work_lhs${BLK}.ll \
	x_solve${BLK}.ll ninvr.ll y_solve${BLK}.ll pinvr.ll \
	z_solve${BLK}.ll tzetar.ll add.ll txinvr.ll error.ll verify.ll \
	${COMMON}/print_results.ll ${COMMON}/timers.ll ${COMMON}/wtime.ll
	${LLVM_LINK} -o sp.bc sp.ll sp_data.ll initialize.ll exact_solution.ll \
	exact_rhs.ll set_constants.ll adi.ll rhs.ll work_lhs${BLK}.ll \
	x_solve${BLK}.ll ninvr.ll y_solve${BLK}.ll pinvr.ll \
	z_solve${BLK}.ll tzetar.ll add.ll txinvr.ll error.ll verify.ll \
	${COMMON}/print_results.ll ${COMMON}/timers.ll ${COMMON}/wtime.ll

naive: sp.bc ${COMMON}/profile_helper_naive.ll
	mkdir -p naive
	${LLVM_LINK} -o naive/sp_naive.bc sp.bc ${COMMON}/profile_helper_naive.ll
	${LLC} ${LLC_FLAGS} naive/sp_naive.bc -o naive/sp_naive.o
	${FC} ${COMPILER_FLAGS} -fopenmp -o naive/sp_naive naive/sp_naive.o

papi_naive: sp.bc ${COMMON}/profile_helper_papi_naive.ll
	mkdir -p papi_naive
	${LLVM_LINK} -o papi_naive/sp_papi_naive.bc sp.bc ${COMMON}/profile_helper_papi_naive.ll
	${LLC} ${LLC_FLAGS} papi_naive/sp_papi_naive.bc -o papi_naive/sp_papi_naive.o
	${FC} ${COMPILER_FLAGS} ${PAPI_LINE} -fopenmp -o papi_naive/sp_papi_naive papi_naive/sp_papi_naive.o


profiling: sp.bc ${COMMON}/profile_helper_profiling.ll
	mkdir -p profiling
	${LLVM_LINK} -o profiling/sp_profiling.bc sp.bc ${COMMON}/profile_helper_profiling.ll
	cd profiling && ${OPT} -passes=phase-analysis sp_profiling.bc -o sp_profiling_opt.bc 2>> sp_profiling_opt.log
	${LLC} ${LLC_FLAGS} profiling/sp_profiling_opt.bc -o profiling/sp_profiling_opt.o
	${FC} ${COMPILER_FLAGS} -fopenmp -o profiling/sp_profiling profiling/sp_profiling_opt.o

m5_fs: m5_fs_${REGION}
m5_fs_${REGION}: sp.bc ${COMMON}/profile_helper_m5_fs.ll
	mkdir -p m5_fs
	mkdir -p m5_fs/${REGION}
	${LLVM_LINK} -o m5_fs/${REGION}/sp_m5_fs_${REGION}.bc sp.bc ${COMMON}/profile_helper_m5_fs.ll
	cd m5_fs/${REGION} && ${OPT} -passes=phase-bound sp_m5_fs_${REGION}.bc -o sp_m5_fs_${REGION}_opt.bc 2>> sp_m5_fs_${REGION}_opt.log
	${LLC} ${LLC_FLAGS} m5_fs/${REGION}/sp_m5_fs_${REGION}_opt.bc -o m5_fs/${REGION}/sp_m5_fs_${REGION}_opt.o
	${FC} ${COMPILER_FLAGS} -fopenmp -o m5_fs/${REGION}/sp_m5_fs_${REGION} m5_fs/${REGION}/sp_m5_fs_${REGION}_opt.o ${M5_LINE}

papi: papi_${REGION}
papi_${REGION}: sp.bc ${COMMON}/profile_helper_papi.ll
	mkdir -p papi
	mkdir -p papi/${REGION}
	${LLVM_LINK} -o papi/${REGION}/sp_papi_${REGION}.bc sp.bc ${COMMON}/profile_helper_papi.ll
	cd papi/${REGION} && ${OPT} -passes=phase-bound sp_papi_${REGION}.bc -o sp_papi_${REGION}_opt.bc 2>> sp_papi_${REGION}_opt.log
	${LLC} ${LLC_FLAGS} papi/${REGION}/sp_papi_${REGION}_opt.bc -o papi/${REGION}/sp_papi_${REGION}_opt.o
	${FC} ${COMPILER_FLAGS} ${PAPI_LINE} -fopenmp -o papi/${REGION}/sp_papi_${REGION} papi/${REGION}/sp_papi_${REGION}_opt.o

sp.ll: sp.f90 sp_data.ll blk_par.h
	${FC} ${FLAGS} -S -emit-llvm sp.f90 -o sp.ll

sp_data.ll: sp_data.f90 npbparams.h
	${FC} ${FLAGS} -S -emit-llvm sp_data.f90 -o sp_data.ll

initialize.ll: initialize.f90 sp_data.ll
	${FC} ${FLAGS} -S -emit-llvm initialize.f90 -o initialize.ll

exact_solution.ll: exact_solution.f90 sp_data.ll
	${FC} ${FLAGS} -S -emit-llvm exact_solution.f90 -o exact_solution.ll

exact_rhs.ll: exact_rhs.f90 sp_data.ll
	${FC} ${FLAGS} -S -emit-llvm exact_rhs.f90 -o exact_rhs.ll

set_constants.ll: set_constants.f90 sp_data.ll
	${FC} ${FLAGS} -S -emit-llvm set_constants.f90 -o set_constants.ll

adi.ll: adi.f90 sp_data.ll
	${FC} ${FLAGS} -S -emit-llvm adi.f90 -o adi.ll

rhs.ll: rhs.f90 sp_data.ll
	${FC} ${FLAGS} -S -emit-llvm rhs.f90 -o rhs.ll

x_solve${BLK}.ll: x_solve${BLK}.f90 sp_data.ll work_lhs$(BLK).ll
	${FC} ${FLAGS} -S -emit-llvm x_solve${BLK}.f90 -o x_solve${BLK}.ll

ninvr.ll: ninvr.f90 sp_data.ll
	${FC} ${FLAGS} -S -emit-llvm ninvr.f90 -o ninvr.ll

y_solve${BLK}.ll: y_solve${BLK}.f90 sp_data.ll work_lhs$(BLK).ll
	${FC} ${FLAGS} -S -emit-llvm y_solve${BLK}.f90 -o y_solve${BLK}.ll

pinvr.ll: pinvr.f90 sp_data.ll
	${FC} ${FLAGS} -S -emit-llvm pinvr.f90 -o pinvr.ll

z_solve${BLK}.ll: z_solve${BLK}.f90 sp_data.ll work_lhs$(BLK).ll
	${FC} ${FLAGS} -S -emit-llvm z_solve${BLK}.f90 -o z_solve${BLK}.ll

tzetar.ll: tzetar.f90 sp_data.ll
	${FC} ${FLAGS} -S -emit-llvm tzetar.f90 -o tzetar.ll

add.ll: add.f90 sp_data.ll
	${FC} ${FLAGS} -S -emit-llvm add.f90 -o add.ll

txinvr.ll: txinvr.f90 sp_data.ll
	${FC} ${FLAGS} -S -emit-llvm txinvr.f90 -o txinvr.ll

error.ll: error.f90 sp_data.ll
	${FC} ${FLAGS} -S -emit-llvm error.f90 -o error.ll

verify.ll: verify.f90 sp_data.ll
	${FC} ${FLAGS} -S -emit-llvm verify.f90 -o verify.ll

work_lhs${BLK}.ll: work_lhs${BLK}.f90 sp_data.ll blk_par.h
	${FC} ${FLAGS} -S -emit-llvm work_lhs${BLK}.f90 -o work_lhs${BLK}.ll

blk_par.h: FORCE
	sed -e 's/= 0/= $(BLKFAC)/' blk_par0.h > blk_par.h_wk
	@ if ! `diff blk_par.h_wk blk_par.h > /dev/null 2>&1`; then \
	mv -f blk_par.h_wk blk_par.h; else rm -f blk_par.h_wk; fi
FORCE:

clean:
	- rm -f *.o *~ *.mod mputil*
	- rm -f npbparams.h core blk_par.h
	- if [ -d rii_files ]; then rm -r rii_files; fi
	- rm -f *.ll *.bc

clean_all:
	- rm -f *.o *~ *.mod mputil*
	- rm -f npbparams.h core blk_par.h
	- if [ -d rii_files ]; then rm -r rii_files; fi
	- rm -f *.ll *.bc
	- rm -rf naive profiling m5_fs papi_naive papi
