PROGRAM = lu

BENCHMARK=lu
BENCHMARKU=LU
SVER=

FLAGS=${BASIC_FLAGS}

CURRENT_DATE=$(shell date +"%Y-%m-%d-%H-%M-%S")

all: pre lu.bc lu_O3.bc

pre: ${SYS_DIR}/setparams.c
	${CC} -o setparams ${SYS_DIR}/setparams.c
	./setparams ${PROGRAM} ${SIZE}

lu.bc: lu.ll lu_data.ll read_input.ll \
	domain.ll setcoeff.ll setbv.ll exact.ll setiv.ll \
	erhs.ll ssor${SVER}.ll rhs.ll l2norm.ll \
	jacld.ll blts.ll jacu.ll buts.ll error.ll \
	pintgr.ll verify.ll ${COMMON}/print_results.ll \
	${COMMON}/timers.ll ${COMMON}/wtime.ll syncs.ll
	${LLVM_LINK} -o lu.bc lu.ll lu_data.ll read_input.ll \
	domain.ll setcoeff.ll setbv.ll exact.ll setiv.ll \
	erhs.ll ssor${SVER}.ll rhs.ll l2norm.ll \
	jacld.ll blts.ll jacu.ll buts.ll error.ll \
	pintgr.ll verify.ll ${COMMON}/print_results.ll \
	${COMMON}/timers.ll ${COMMON}/wtime.ll syncs.ll

lu_O3.bc: lu.bc
	${OPT} ${OPT_FLAGS} lu.bc -o lu_O3_${CURRENT_DATE}.bc

lu.ll: lu.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm lu.f90 -o lu.ll

lu_data.ll: lu_data.f90 npbparams.h
	${FC} ${FLAGS} -S -emit-llvm lu_data.f90 -o lu_data.ll

blts.ll: blts.f90
	${FC} ${FLAGS} -S -emit-llvm blts.f90 -o blts.ll

buts.ll: buts.f90
	${FC} ${FLAGS} -S -emit-llvm buts.f90 -o buts.ll

erhs.ll: erhs.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm erhs.f90 -o erhs.ll

error.ll: error.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm error.f90 -o error.ll

exact.ll: exact.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm exact.f90 -o exact.ll

jacld.ll: jacld.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm jacld.f90 -o jacld.ll

jacu.ll: jacu.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm jacu.f90 -o jacu.ll

l2norm.ll: l2norm.f90
	${FC} ${FLAGS} -S -emit-llvm l2norm.f90 -o l2norm.ll

pintgr.ll: pintgr.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm pintgr.f90 -o pintgr.ll

read_input.ll: read_input.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm read_input.f90 -o read_input.ll

rhs.ll: rhs.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm rhs.f90 -o rhs.ll

setbv.ll: setbv.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm setbv.f90 -o setbv.ll

setiv.ll: setiv.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm setiv.f90 -o setiv.ll

setcoeff.ll: setcoeff.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm setcoeff.f90 -o setcoeff.ll

ssor${SVER}.ll: ssor${SVER}.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm ssor${SVER}.f90 -o ssor${SVER}.ll

domain.ll: domain.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm domain.f90 -o domain.ll

verify.ll: verify.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm verify.f90 -o verify.ll

syncs.ll: syncs.f90 lu_data.ll
	${FC} ${FLAGS} -S -emit-llvm syncs.f90 -o syncs.ll

clean:
	- rm -f *.o *~ *.mod npbparams.h
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
	- rm -f *.o *~ *.mod npbparams.h
	- if [ -d rii_files ]; then rm -r rii_files; fi
	- rm -f *.ll *.bc
	- rm -rf naive profiling m5_fs papi_naive papi
