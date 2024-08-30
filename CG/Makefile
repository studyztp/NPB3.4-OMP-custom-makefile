PROGRAM = cg

RAND = randi8

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
		make cg.bc SIZE=$$size; \
		cp ${CURRENT_PATH}/*.ll ${CURRENT_PATH}/$$size/; \
		cp ${CURRENT_PATH}/*.bc ${CURRENT_PATH}/$$size/; \
		cp npbparams.h ${CURRENT_PATH}/$$size/; \
		${OPT} ${OPT_FLAGS} ${CURRENT_PATH}/$$size/cg.bc -o ${CURRENT_PATH}/$$size/cg_O3_${CURRENT_DATE}.bc; \
	done
	make clean;

pre: ${SYS_DIR}/setparams.c
	${CC} -o setparams ${SYS_DIR}/setparams.c --target=${HOST_ARCH}

cg.bc: cg.ll cg_data.ll ${COMMON}/print_results.ll ${COMMON}/${RAND}.ll 
	${LLVM_LINK} -o cg.bc cg.ll cg_data.ll ${COMMON}/print_results.ll \
	${COMMON}/${RAND}.ll 

cg_O3.bc: cg.bc
	${OPT} ${OPT_FLAGS} cg.bc -o cg_O3_${CURRENT_DATE}.bc

cg.ll: cg.f90 cg_data.ll
	${FC} ${FLAGS} -S -emit-llvm cg.f90 -o cg.ll

cg_data.ll: cg_data.f90 npbparams.h
	${FC} ${FLAGS} -S -emit-llvm cg_data.f90 -o cg_data.ll

clean:
	- rm -f *.o *~ *.mod
	- rm -f npbparams.h core
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
	- rm -f *.o *~ *.mod
	- rm -f npbparams.h core
	- if [ -d rii_files ]; then rm -r rii_files; fi
	- rm -f *.ll *.bc
	for size in ${ALL_SIZE}; do \
		rm -rf ${CURRENT_PATH}/$$size; \
	done
