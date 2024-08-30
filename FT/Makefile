PROGRAM = ft

BLKFAC=32

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
		make ft.bc SIZE=$$size; \
		cp ${CURRENT_PATH}/*.ll ${CURRENT_PATH}/$$size/; \
		cp ${CURRENT_PATH}/*.bc ${CURRENT_PATH}/$$size/; \
		cp npbparams.h ${CURRENT_PATH}/$$size/; \
		${OPT} ${OPT_FLAGS} ${CURRENT_PATH}/$$size/ft.bc -o ${CURRENT_PATH}/$$size/ft_O3_${CURRENT_DATE}.bc; \
	done
	make clean;

pre: ${SYS_DIR}/setparams.c
	${CC} -o setparams ${SYS_DIR}/setparams.c --target=${HOST_ARCH}

ft.bc: ${COMMON}/${RAND}.ll ${COMMON}/print_results.ll ft.ll ft_data.ll
	${LLVM_LINK} -o ft.bc ${COMMON}/${RAND}.ll ${COMMON}/print_results.ll ft.ll ft_data.ll

ft_O3.bc: ft.bc
	${OPT} ${OPT_FLAGS} ft.bc -o ft_O3_${CURRENT_DATE}.bc

${COMMON}/${RAND}.ll: ${COMMON}/${RAND}.f90
	${FC} ${FLAGS} -S -emit-llvm ${COMMON}/${RAND}.f90 -o ${COMMON}/${RAND}.ll

${COMMON}/print_results.ll: ${COMMON}/print_results.f90
	${FC} ${FLAGS} -S -emit-llvm ${COMMON}/print_results.f90 -o ${COMMON}/print_results.ll

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
	- rm -f *.o *~ mputil* *.mod
	- rm -f ft npbparams.h core blk_par.h
	- if [ -d rii_files ]; then rm -r rii_files; fi
	- rm -f *.ll *.bc
	for size in ${ALL_SIZE}; do \
		rm -rf ${CURRENT_PATH}/$$size; \
	done
	
