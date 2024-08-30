BLK=
BLKFAC=0

PROGRAM=bt

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
		make bt.bc SIZE=$$size; \
		cp ${CURRENT_PATH}/*.ll ${CURRENT_PATH}/$$size/; \
		cp ${CURRENT_PATH}/*.bc ${CURRENT_PATH}/$$size/; \
		cp npbparams.h ${CURRENT_PATH}/$$size/; \
		${OPT} ${OPT_FLAGS}  ${CURRENT_PATH}/$$size/bt.bc -o  ${CURRENT_PATH}/$$size/bt_O3_${CURRENT_DATE}.bc; \
	done
	make clean;

pre: ${SYS_DIR}/setparams.c
	${CC} -o setparams ${SYS_DIR}/setparams.c --target=${HOST_ARCH}

bt.bc: bt.ll bt_data.ll initialize.ll exact_solution.ll \
	exact_rhs.ll set_constants.ll adi.ll rhs.ll \
	x_solve$(BLK).ll y_solve$(BLK).ll solve_subs$(BLK).ll \
	z_solve$(BLK).ll add.ll error.ll verify.ll work_lhs$(BLK).ll \
	${COMMON}/print_results.ll
	${LLVM_LINK} -o bt.bc bt.ll bt_data.ll initialize.ll exact_solution.ll \
	exact_rhs.ll set_constants.ll adi.ll rhs.ll \
	x_solve$(BLK).ll y_solve$(BLK).ll solve_subs$(BLK).ll \
	z_solve$(BLK).ll add.ll error.ll verify.ll work_lhs$(BLK).ll \
	${COMMON}/print_results.ll

bt_O3.bc: bt.bc
	${OPT} ${OPT_FLAGS} bt.bc -o bt_O3_${CURRENT_DATE}.bc

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
