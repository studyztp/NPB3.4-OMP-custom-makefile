PROGRAM = ft

BLKFAC=32

RAND = randi8

FLAGS=${BASIC_FLAGS}

CURRENT_DATE=$(shell date +"%Y-%m-%d-%H-%M-%S")


all: pre ft.bc ft_O3.bc

pre: ${SYS_DIR}/setparams.c
	${CC} -o setparams ${SYS_DIR}/setparams.c
	./setparams ${PROGRAM} ${SIZE}

ft.bc: ${COMMON}/${RAND}.ll ${COMMON}/print_results.ll ${COMMON}/timers.ll ${COMMON}/wtime.ll ft.ll ft_data.ll
	${LLVM_LINK} -o ft.bc ${COMMON}/${RAND}.ll ${COMMON}/print_results.ll ${COMMON}/timers.ll ${COMMON}/wtime.ll ft.ll ft_data.ll

ft_O3.bc: ft.bc
	${OPT} ${OPT_FLAGS} ft.bc -o ft_O3_${CURRENT_DATE}.bc

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
	- rm -rf naive profiling m5_fs papi papi_naive
	
