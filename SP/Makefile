PROGRAM = sp

BENCHMARK=sp
BENCHMARKU=SP
BLK=
BLKFAC=0

FLAGS=${BASIC_FLAGS}

CURRENT_DATE=$(shell date +"%Y-%m-%d-%H-%M-%S")
CURRENT_PATH = $(shell pwd)

ALL_SIZE = A B C D E 

all: pre 
	make clean_all_sizes;
	for size in ${ALL_SIZE}; do \
		make clean; \
		./setparams ${PROGRAM} $$size; \
		mkdir -p $$size; \
		make sp.bc SIZE=$$size; \
		cp ${CURRENT_PATH}/*.ll ${CURRENT_PATH}/$$size/; \
		cp ${CURRENT_PATH}/*.bc ${CURRENT_PATH}/$$size/; \
		cp npbparams.h ${CURRENT_PATH}/$$size/; \
		${OPT} ${OPT_FLAGS} ${CURRENT_PATH}/$$size/sp.bc -o  ${CURRENT_PATH}/$$size/sp_O3_${CURRENT_DATE}.bc; \
	done
	make clean;

pre: ${SYS_DIR}/setparams.c
	${CC} -o setparams ${SYS_DIR}/setparams.c --target=${HOST_ARCH}

sp.bc: sp.ll sp_data.ll initialize.ll exact_solution.ll exact_rhs.ll \
	set_constants.ll adi.ll rhs.ll work_lhs${BLK}.ll \
	x_solve${BLK}.ll ninvr.ll y_solve${BLK}.ll pinvr.ll \
	z_solve${BLK}.ll tzetar.ll add.ll txinvr.ll error.ll verify.ll \
	${COMMON}/print_results.ll ${COMMON}/timers.ll ${COMMON}/wtime.ll
	${LLVM_LINK} -o sp.bc sp.ll sp_data.ll initialize.ll exact_solution.ll \
	exact_rhs.ll set_constants.ll adi.ll rhs.ll work_lhs${BLK}.ll \
	x_solve${BLK}.ll ninvr.ll y_solve${BLK}.ll pinvr.ll \
	z_solve${BLK}.ll tzetar.ll add.ll txinvr.ll error.ll verify.ll \
	${COMMON}/print_results.ll ${COMMON}/timers.ll ${COMMON}/wtime.ll

sp_O3.bc: sp.bc
	${OPT} ${OPT_FLAGS} sp.bc -o sp_O3_${CURRENT_DATE}.bc

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

clean_all_sizes:
	for size in ${ALL_SIZE}; do \
		rm -f ${CURRENT_PATH}/$$size/*.ll; \
		rm -f ${CURRENT_PATH}/$$size/*.bc; \
		rm -f ${CURRENT_PATH}/$$size/npbparams.h; \
	done

clean_naive:
	- rm -rf naive

clean_profiling:
	- rm -rf profiling

clean_m5_fs:
	- rm -rf m5_fs

clean_papi:
	- rm -rf papi

clean_all:
	- rm -f *.o *~ *.mod mputil*
	- rm -f npbparams.h core blk_par.h
	- if [ -d rii_files ]; then rm -r rii_files; fi
	- rm -f *.ll *.bc
	for size in ${ALL_SIZE}; do \
		rm -rf ${CURRENT_PATH}/$$size; \
	done
