PROGRAM = ep

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
		make ep.bc SIZE=$$size; \
		cp ${CURRENT_PATH}/*.ll ${CURRENT_PATH}/$$size/; \
		cp ${CURRENT_PATH}/*.bc ${CURRENT_PATH}/$$size/; \
		cp npbparams.h ${CURRENT_PATH}/$$size/; \
		${OPT} ${OPT_FLAGS} ${CURRENT_PATH}/$$size/ep.bc -o ${CURRENT_PATH}/$$size/ep_O3_${CURRENT_DATE}.bc; \
	done
	make clean;

pre: ${SYS_DIR}/setparams.c
	${CC} -o setparams ${SYS_DIR}/setparams.c --target=${HOST_ARCH}

ep.bc: ep.ll ep_data.ll verify.ll \
	${COMMON}/print_results.ll ${COMMON}/${RAND}.ll ${COMMON}/timers.ll \
	${COMMON}/wtime.ll
	${LLVM_LINK} -o ep.bc ep.ll ep_data.ll verify.ll \
	${COMMON}/print_results.ll ${COMMON}/${RAND}.ll ${COMMON}/timers.ll \
	${COMMON}/wtime.ll

ep_O3.bc: ep.bc
	${OPT} ${OPT_FLAGS} ep.bc -o ep_O3_${CURRENT_DATE}.bc

ep.ll: ep.f90 ep_data.ll
	${FC} ${FLAGS} -S -emit-llvm ep.f90 -o ep.ll

ep_data.ll: ep_data.f90 npbparams.h
	${FC} ${FLAGS} -S -emit-llvm ep_data.f90 -o ep_data.ll

verify.ll: verify.f90
	${FC} ${FLAGS} -S -emit-llvm verify.f90 -o verify.ll

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
