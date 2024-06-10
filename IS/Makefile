PROGRAM = is

BENCHMARK=is
BENCHMARKU=IS

FLAGS=${BASIC_FLAGS}

CURRENT_DATE=$(shell date +"%Y-%m-%d-%H-%M-%S")

all: pre is.bc is_O3.bc

pre: ${SYS_DIR}/setparams.c
	${CC} -o setparams ${SYS_DIR}/setparams.c
	./setparams ${PROGRAM} ${SIZE}

is.bc: is.ll \
	${COMMON}/c_print_results.ll ${COMMON}/c_timers.ll ${COMMON}/wtime.ll
	${LLVM_LINK} -o is.bc is.ll \
	${COMMON}/c_print_results.ll ${COMMON}/c_timers.ll ${COMMON}/wtime.ll

is_O3.bc: is.bc
	${OPT} ${OPT_FLAGS} is.bc -o is_O3_${CURRENT_DATE}.bc

is.ll: is.c npbparams.h
	${CC} -S -emit-llvm ${FLAGS} is.c -o is.ll

clean:
	- rm -f *.o *~ mputil*
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
	- rm -f *.o *~ mputil*
	- rm -f npbparams.h core
	- if [ -d rii_files ]; then rm -r rii_files; fi
	- rm -f *.ll *.bc
	- rm -rf naive profiling m5_fs papi_naive papi
