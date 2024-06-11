PROGRAM = cg

RAND = randi8

FLAGS=${BASIC_FLAGS}

CURRENT_DATE=$(shell date +"%Y-%m-%d-%H-%M-%S")

all: pre cg.bc cg_O3.bc

pre: ${SYS_DIR}/setparams.c
	${CC} -o setparams ${SYS_DIR}/setparams.c --target=${HOST_ARCH}
	./setparams ${PROGRAM} ${SIZE}

cg.bc: cg.ll cg_data.ll ${COMMON}/print_results.ll ${COMMON}/${RAND}.ll \
	${COMMON}/timers.ll ${COMMON}/wtime.ll
	${LLVM_LINK} -o cg.bc cg.ll cg_data.ll ${COMMON}/print_results.ll \
	${COMMON}/${RAND}.ll ${COMMON}/timers.ll ${COMMON}/wtime.ll

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
	- rm -rf naive profiling m5_fs papi papi_naive
