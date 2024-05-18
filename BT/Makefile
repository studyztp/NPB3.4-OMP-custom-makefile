FC = /scr/studyztp/compiler/llvm-dir/bin/flang-new
CC = /scr/studyztp/compiler/llvm-dir/bin/clang
OPT = /scr/studyztp/compiler/llvm-dir/bin/opt
LLVM_LINK = /scr/studyztp/compiler/llvm-dir/bin/llvm-link
COMPILER_FLAGS = --target=aarch64-unknown-linux-gnu -mcpu=neoverse-n1
FLAGS = -O3 -fopenmp -lm ${COMPILER_FLAGS}
LLC = /scr/studyztp/compiler/llvm-dir/bin/llc
LLC_FLAGS = -relocation-model=pic -filetype=obj

COMMON = $(shell realpath ../common)
SYS_DIR = $(shell realpath ../sys)

PROGRAM = bt

BENCHMARK=bt
BENCHMARKU=BT
BLK=
BLKFAC=0

PAPI_PATH = ${COMMON}/papi/install
PAPI_INCLUDE = ${PAPI_PATH}/include
PAPI_LIB = ${PAPI_PATH}/lib
PAPI_LINE = -I${PAPI_INCLUDE} -L${PAPI_LIB} -lpapi -lpthread


M5_PATH = ${COMMON}/gem5
M5_LINE = -I${M5_PATH} -L${M5_PATH}/out -lm5

all: pre bt

pre: ${SYS_DIR}/setparams.c
	${CC} -o setparams ${SYS_DIR}/setparams.c
	./setparams ${PROGRAM} ${SIZE}

bt: bt.ll bt_data.ll initialize.ll exact_solution.ll \
	exact_rhs.ll set_constants.ll adi.ll rhs.ll \
	x_solve$(BLK).ll y_solve$(BLK).ll solve_subs$(BLK).ll \
	z_solve$(BLK).ll add.ll error.ll verify.ll work_lhs$(BLK).ll \
	${COMMON}/print_results.ll ${COMMON}/timers.ll ${COMMON}/wtime.ll
	${LLVM_LINK} -o bt.bc bt.ll bt_data.ll initialize.ll exact_solution.ll \
	exact_rhs.ll set_constants.ll adi.ll rhs.ll \
	x_solve$(BLK).ll y_solve$(BLK).ll solve_subs$(BLK).ll \
	z_solve$(BLK).ll add.ll error.ll verify.ll work_lhs$(BLK).ll \
	${COMMON}/print_results.ll ${COMMON}/timers.ll ${COMMON}/wtime.ll

naive: bt.bc ${COMMON}/profile_helper_naive.ll
	mkdir -p naive
	${LLVM_LINK} -o naive/bt_naive.bc bt.bc ${COMMON}/profile_helper_naive.ll
	${LLC} ${LLC_FLAGS} naive/bt_naive.bc -o naive/bt_naive.o
	${FC} ${COMPILER_FLAGS} ${PAPI_LINE} -fopenmp -o naive/bt_naive naive/bt_naive.o

papi_naive: bt.bc ${COMMON}/profile_helper_papi_naive.ll
	mkdir -p naive
	${LLVM_LINK} -o naive/bt_papi_naive.bc bt.bc ${COMMON}/profile_helper_papi_naive.ll
	${LLC} ${LLC_FLAGS} naive/bt_papi_naive.bc -o naive/bt_papi_naive.o
	${FC} ${COMPILER_FLAGS} ${PAPI_LINE} -fopenmp -o naive/bt_papi_naive naive/bt_papi_naive.o


profiling: bt.bc ${COMMON}/profile_helper_profiling.ll
	mkdir -p profiling
	${LLVM_LINK} -o profiling/bt_profiling.bc bt.bc ${COMMON}/profile_helper_profiling.ll
	cd profiling && ${OPT} -passes=phase-analysis bt_profiling.bc -o bt_profiling_opt.bc 2>> bt_profiling_opt.log
	${LLC} ${LLC_FLAGS} profiling/bt_profiling_opt.bc -o profiling/bt_profiling_opt.o
	${FC} ${COMPILER_FLAGS} -fopenmp -o profiling/bt_profiling profiling/bt_profiling_opt.o

m5_fs: m5_fs_${REGION}
m5_fs_${REGION}: bt.bc ${COMMON}/profile_helper_m5_fs.ll
	mkdir -p m5_fs
	mkdir -p m5_fs/${REGION}
	${LLVM_LINK} -o m5_fs/${REGION}/bt_m5_fs_${REGION}.bc bt.bc ${COMMON}/profile_helper_m5_fs.ll
	cd m5_fs/${REGION} && ${OPT} -passes=phase-bound bt_m5_fs_${REGION}.bc -o bt_m5_fs_${REGION}_opt.bc 2>> bt_m5_fs_${REGION}_opt.log
	${LLC} ${LLC_FLAGS} m5_fs/${REGION}/bt_m5_fs_${REGION}_opt.bc -o m5_fs/${REGION}/bt_m5_fs_${REGION}_opt.o
	${FC} ${COMPILER_FLAGS} -fopenmp -o m5_fs/${REGION}/bt_m5_fs_${REGION} m5_fs/${REGION}/bt_m5_fs_${REGION}_opt.o ${M5_LINE} 

papi: papi_${REGION}
papi_${REGION}: bt.bc ${COMMON}/profile_helper_papi.ll
	mkdir -p papi
	mkdir -p papi/${REGION}
	${LLVM_LINK} -o papi/${REGION}/bt_papi_${REGION}.bc bt.bc ${COMMON}/profile_helper_papi.ll
	cd papi/${REGION} && ${OPT} -passes=phase-bound bt_papi_${REGION}.bc -o bt_papi_${REGION}_opt.bc 2>> bt_papi_${REGION}_opt.log
	${LLC} ${LLC_FLAGS} papi/${REGION}/bt_papi_${REGION}_opt.bc -o papi/${REGION}/bt_papi_${REGION}_opt.o
	${FC} ${COMPILER_FLAGS} ${PAPI_LINE} -fopenmp -o papi/${REGION}/bt_papi_${REGION} papi/${REGION}/bt_papi_${REGION}_opt.o


bt.ll: bt.f90 bt_data.ll blk_par.h
	${FC} ${FLAGS} -S -emit-llvm bt.f90 -o bt.ll

bt_data.ll: bt_data.f90 npbparams.h
	${FC} ${FLAGS} -S -emit-llvm bt_data.f90 -o bt_data.ll

initialize.ll: initialize.f90 bt_data.ll
	${FC} ${FLAGS} -S -emit-llvm initialize.f90 -o initialize.ll

exact_solution.ll: exact_solution.f90 bt_data.ll
	${FC} ${FLAGS} -S -emit-llvm exact_solution.f90 -o exact_solution.ll

exact_rhs.ll: exact_rhs.f90 bt_data.ll
	${FC} ${FLAGS} -S -emit-llvm exact_rhs.f90 -o exact_rhs.ll

set_constants.ll: set_constants.f90 bt_data.ll
	${FC} ${FLAGS} -S -emit-llvm set_constants.f90 -o set_constants.ll

adi.ll: adi.f90 bt_data.ll
	${FC} ${FLAGS} -S -emit-llvm adi.f90 -o adi.ll

rhs.ll: rhs.f90 bt_data.ll
	${FC} ${FLAGS} -S -emit-llvm rhs.f90 -o rhs.ll

x_solve$(BLK).ll: x_solve$(BLK).f90 bt_data.ll work_lhs$(BLK).ll
	${FC} ${FLAGS} -S -emit-llvm x_solve$(BLK).f90 -o x_solve$(BLK).ll

y_solve$(BLK).ll: y_solve$(BLK).f90 bt_data.ll work_lhs$(BLK).ll	
	${FC} ${FLAGS} -S -emit-llvm y_solve$(BLK).f90 -o y_solve$(BLK).ll

z_solve$(BLK).ll: z_solve$(BLK).f90 bt_data.ll work_lhs$(BLK).ll
	${FC} ${FLAGS} -S -emit-llvm z_solve$(BLK).f90 -o z_solve$(BLK).ll

solve_subs$(BLK).ll: solve_subs$(BLK).f90 work_lhs$(BLK).ll
	${FC} ${FLAGS} -S -emit-llvm solve_subs$(BLK).f90 -o solve_subs$(BLK).ll

work_lhs$(BLK).ll: work_lhs$(BLK).f90 bt_data.ll blk_par.h
	${FC} ${FLAGS} -S -emit-llvm work_lhs$(BLK).f90 -o work_lhs$(BLK).ll

add.ll: add.f90 bt_data.ll
	${FC} ${FLAGS} -S -emit-llvm add.f90 -o add.ll

error.ll: error.f90 bt_data.ll
	${FC} ${FLAGS} -S -emit-llvm error.f90 -o error.ll

verify.ll: verify.f90 bt_data.ll
	${FC} ${FLAGS} -S -emit-llvm verify.f90 -o verify.ll

${COMMON}/print_results.ll: ${COMMON}/print_results.f90
	${FC} ${FLAGS} -S -emit-llvm ${COMMON}/print_results.f90 -o ${COMMON}/print_results.ll

${COMMON}/timers.ll: ${COMMON}/timers.f90
	${FC} ${FLAGS} -S -emit-llvm ${COMMON}/timers.f90 -o ${COMMON}/timers.ll

${COMMON}/wtime.ll: ${COMMON}/wtime.c
	${CC} ${FLAGS} -S -emit-llvm ${COMMON}/wtime.c -o ${COMMON}/wtime.ll

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
	- rm -rf naive profiling m5_fs papi papi_naive
