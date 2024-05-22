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

PROGRAM = ft

BLKFAC=32

RAND = randi8

PAPI_PATH = ${COMMON}/papi/install
PAPI_INCLUDE = ${PAPI_PATH}/include
PAPI_LIB = ${PAPI_PATH}/lib
PAPI_LINE = -I${PAPI_INCLUDE} -L${PAPI_LIB} -lpapi -lpthread

M5_PATH = ${COMMON}/gem5
M5_LINE = -I${M5_PATH} -L${M5_PATH}/out -lm5

all: pre ft

pre: ${SYS_DIR}/setparams.c
	${CC} -o setparams ${SYS_DIR}/setparams.c
	./setparams ${PROGRAM} ${SIZE}

ft: ${COMMON}/${RAND}.ll ${COMMON}/print_results.ll ${COMMON}/timers.ll ${COMMON}/wtime.ll ft.ll ft_data.ll
	${LLVM_LINK} -o ft.bc ${COMMON}/${RAND}.ll ${COMMON}/print_results.ll ${COMMON}/timers.ll ${COMMON}/wtime.ll ft.ll ft_data.ll

naive: ft.bc ${COMMON}/profile_helper_naive.ll
	mkdir -p naive
	${LLVM_LINK} -o naive/ft_naive.bc ft.bc ${COMMON}/profile_helper_naive.ll
	${LLC} ${LLC_FLAGS} naive/ft_naive.bc -o naive/ft_naive.o
	${FC} ${COMPILER_FLAGS} -fopenmp -o naive/ft_naive naive/ft_naive.o

papi_naive: ft.bc ${COMMON}/profile_helper_papi_naive.ll
	mkdir -p naive
	${LLVM_LINK} -o papi_naive/ft_papi_naive.bc ft.bc ${COMMON}/profile_helper_papi_naive.ll
	${LLC} ${LLC_FLAGS} papi_naive/ft_papi_naive.bc -o papi_naive/ft_papi_naive.o
	${FC} ${COMPILER_FLAGS} ${PAPI_LINE} -fopenmp -o papi_naive/ft_papi_naive papi_naive/ft_papi_naive.o


profiling: ft.bc ${COMMON}/profile_helper_profiling.ll
	mkdir -p profiling
	${LLVM_LINK} -o profiling/ft_profiling.bc ft.bc ${COMMON}/profile_helper_profiling.ll
	cd profiling && ${OPT} -passes=phase-analysis ft_profiling.bc -o ft_profiling_opt.bc 2>> ft_profiling_opt.log
	${LLC} ${LLC_FLAGS} profiling/ft_profiling_opt.bc -o profiling/ft_profiling_opt.o
	${FC} ${COMPILER_FLAGS} -fopenmp -o profiling/ft_profiling profiling/ft_profiling_opt.o

m5_fs: m5_fs_${REGION}
m5_fs_${REGION}: ft.bc ${COMMON}/profile_helper_m5_fs.ll
	mkdir -p m5_fs
	mkdir -p m5_fs/${REGION}
	${LLVM_LINK} -o m5_fs/${REGION}/ft_m5_fs_${REGION}.bc ft.bc ${COMMON}/profile_helper_m5_fs.ll
	cd m5_fs/${REGION} && ${OPT} -passes=phase-bound ft_m5_fs_${REGION}.bc -o ft_m5_fs_${REGION}_opt.bc 2>> ft_m5_fs_${REGION}_opt.log
	${LLC} ${LLC_FLAGS} m5_fs/${REGION}/ft_m5_fs_${REGION}_opt.bc -o m5_fs/${REGION}/ft_m5_fs_${REGION}_opt.o
	${FC} ${COMPILER_FLAGS} -fopenmp -o m5_fs/${REGION}/ft_m5_fs_${REGION} m5_fs/${REGION}/ft_m5_fs_${REGION}_opt.o ${M5_LINE} 

papi: papi_${REGION}
papi_${REGION}: ft.bc ${COMMON}/profile_helper_papi.ll
	mkdir -p papi
	mkdir -p papi/${REGION}
	${LLVM_LINK} -o papi/${REGION}/ft_papi_${REGION}.bc ft.bc ${COMMON}/profile_helper_papi.ll
	cd papi/${REGION} && ${OPT} -passes=phase-bound ft_papi_${REGION}.bc -o ft_papi_${REGION}_opt.bc 2>> ft_papi_${REGION}_opt.log
	${LLC} ${LLC_FLAGS} papi/${REGION}/ft_papi_${REGION}_opt.bc -o papi/${REGION}/ft_papi_${REGION}_opt.o
	${FC} ${COMPILER_FLAGS} ${PAPI_LINE} -fopenmp -o papi/${REGION}/ft_papi_${REGION} papi/${REGION}/ft_papi_${REGION}_opt.o

${COMMON}/${RAND}.ll: ${COMMON}/${RAND}.f90
	${FC} ${FLAGS} -S -emit-llvm ${COMMON}/${RAND}.f90 -o ${COMMON}/${RAND}.ll

${COMMON}/print_results.ll: ${COMMON}/print_results.f90
	${FC} ${FLAGS} -S -emit-llvm ${COMMON}/print_results.f90 -o ${COMMON}/print_results.ll

${COMMON}/timers.ll: ${COMMON}/timers.f90
	${FC} ${FLAGS} -S -emit-llvm ${COMMON}/timers.f90 -o ${COMMON}/timers.ll

${COMMON}/wtime.ll: ${COMMON}/wtime.c
	${CC} ${FLAGS} -S -emit-llvm ${COMMON}/wtime.c -o ${COMMON}/wtime.ll

blk_par.h: FORCE
	sed -e 's/=0/=$(BLKFAC)/' blk_par0.h > blk_par.h_wk
	@ if ! `diff blk_par.h_wk blk_par.h > /dev/null 2>&1`; then \
	mv -f blk_par.h_wk blk_par.h; else rm -f blk_par.h_wk; fi
FORCE:

ft_data.ll: ft_data.f90 npbparams.h blk_par.h
	${FC} ${FLAGS} -S -emit-llvm ft_data.f90 -o ft_data.ll

ft.ll: ft.f90 ft_data.ll
	${FC} ${FLAGS} -S -emit-llvm ft.f90 -o ft.ll

clean:
	- rm -f *.o *~ mputil* *.mod
	- rm -f ft npbparams.h core blk_par.h
	- if [ -d rii_files ]; then rm -r rii_files; fi
	- rm -f *.ll *.bc

clean_all:
	- rm -f *.o *~ mputil* *.mod
	- rm -f ft npbparams.h core blk_par.h
	- if [ -d rii_files ]; then rm -r rii_files; fi
	- rm -f *.ll *.bc
	- rm -rf naive profiling m5_fs papi papi_naive
	