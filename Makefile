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

BT/papi_naive/bt_papi_naive: BT/bt.bc
	cd BT; ${MAKE} papi_naive

CG/papi_naive/cg_papi_naive: CG/cg.bc
	cd CG; ${MAKE} papi_naive

DC/papi_naive/dc_papi_naive: DC/dc.bc
	cd DC; ${MAKE} papi_naive

EP/papi_naive/ep_papi_naive: EP/ep.bc
	cd EP; ${MAKE} papi_naive

FT/papi_naive/ft_papi_naive: FT/ft.bc
	cd FT; ${MAKE} papi_naive

IS/papi_naive/is_papi_naive: IS/is.bc
	cd IS; ${MAKE} papi_naive

LU/papi_naive/lu_papi_naive: LU/lu.bc
	cd LU; ${MAKE} papi_naive

MG/papi_naive/mg_papi_naive: MG/mg.bc
	cd MG; ${MAKE} papi_naive

SP/papi_naive/sp_papi_naive: SP/sp.bc
	cd SP; ${MAKE} papi_naive

build_papi_naive_all: pre BT/papi_naive/bt_papi_naive CG/papi_naive/cg_papi_naive DC/papi_naive/dc_papi_naive EP/papi_naive/ep_papi_naive FT/papi_naive/ft_papi_naive IS/papi_naive/is_papi_naive LU/papi_naive/lu_papi_naive MG/papi_naive/mg_papi_naive SP/papi_naive/sp_papi_naive

run_papi_naive_all: build_papi_naive_all
	cd BT/papi_naive && ./bt_papi_naive
	cd CG/papi_naive && ./cg_papi_naive
	cd DC/papi_naive && ./dc_papi_naive
	cd EP/papi_naive && ./ep_papi_naive
	cd FT/papi_naive && ./ft_papi_naive
	cd IS/papi_naive && ./is_papi_naive
	cd LU/papi_naive && ./lu_papi_naive
	cd MG/papi_naive && ./mg_papi_naive
	cd SP/papi_naive && ./sp_papi_naive

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
