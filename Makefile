SIZE = B
CLASS = B
OMP_NUM_THREADS = 1

build_profiling_all: pre BT/profiling/bt_profiling CG/profiling/cg_profiling DC/profiling/dc_profiling EP/profiling/ep_profiling FT/profiling/ft_profiling IS/profiling/is_profiling LU/profiling/lu_profiling MG/profiling/mg_profiling SP/profiling/sp_profiling

run_profiling_all: build_profiling_all
	cd BT/profiling && ./bt_profiling
	cd CG/profiling && ./cg_profiling
	# cd DC/profiling && ./dc_profiling
	cd EP/profiling && ./ep_profiling
	cd FT/profiling && ./ft_profiling
	cd IS/profiling && ./is_profiling
	cd LU/profiling && ./lu_profiling
	cd MG/profiling && ./mg_profiling
	cd SP/profiling && ./sp_profiling

pre: 
	cd common; ${MAKE}

BT/bt.bc:
	cd BT; ${MAKE} CLASS=${CLASS} SIZE=${SIZE}

BT/profiling/bt_profiling: BT/bt.bc
	cd BT; ${MAKE} profiling

CG/cg.bc:
	cd CG; ${MAKE} CLASS=${CLASS} SIZE=${SIZE}

CG/profiling/cg_profiling: CG/cg.bc
	cd CG; ${MAKE} profiling

DC/dc.bc:
	cd DC; ${MAKE} CLASS=${CLASS} SIZE=${SIZE}

DC/profiling/dc_profiling: DC/dc.bc
	cd DC; ${MAKE} profiling

EP/ep.bc:
	cd EP; ${MAKE} CLASS=${CLASS} SIZE=${SIZE}

EP/profiling/ep_profiling: EP/ep.bc
	cd EP; ${MAKE} profiling

FT/ft.bc:
	cd FT; ${MAKE} CLASS=${CLASS} SIZE=${SIZE}

FT/profiling/ft_profiling: FT/ft.bc
	cd FT; ${MAKE} profiling

IS/is.bc:
	cd IS; ${MAKE} CLASS=${CLASS} SIZE=${SIZE}

IS/profiling/is_profiling: IS/is.bc
	cd IS; ${MAKE} profiling

LU/lu.bc:
	cd LU; ${MAKE} CLASS=${CLASS} SIZE=${SIZE}

LU/profiling/lu_profiling: LU/lu.bc
	cd LU; ${MAKE} profiling

MG/mg.bc:
	cd MG; ${MAKE} CLASS=${CLASS} SIZE=${SIZE}

MG/profiling/mg_profiling: MG/mg.bc
	cd MG; ${MAKE} profiling

SP/sp.bc:
	cd SP; ${MAKE} CLASS=${CLASS} SIZE=${SIZE}

SP/profiling/sp_profiling: SP/sp.bc
	cd SP; ${MAKE} profiling

clean:
	cd BT; ${MAKE} clean
	cd CG; ${MAKE} clean
	cd DC; ${MAKE} clean
	cd EP; ${MAKE} clean
	cd FT; ${MAKE} clean
	cd IS; ${MAKE} clean
	cd LU; ${MAKE} clean
	cd MG; ${MAKE} clean
	cd SP; ${MAKE} clean
	cd common; ${MAKE} clean


clean_all:
	cd BT; ${MAKE} clean_all
	cd CG; ${MAKE} clean_all
	cd DC; ${MAKE} clean_all
	cd EP; ${MAKE} clean_all
	cd FT; ${MAKE} clean_all
	cd IS; ${MAKE} clean_all
	cd LU; ${MAKE} clean_all
	cd MG; ${MAKE} clean_all
	cd SP; ${MAKE} clean_all
	cd common; ${MAKE} clean
