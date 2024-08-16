# compiler related paths
LLVM_BIN = /scr/studyztp/compiler/llvm-dir/bin
FC = ${LLVM_BIN}/flang-new
CC = ${LLVM_BIN}/clang
CPP = ${LLVM_BIN}/clang++
OPT = ${LLVM_BIN}/opt
LLC = ${LLVM_BIN}/llc
LLVM_LINK = ${LLVM_BIN}/llvm-link

# compiler related flags
DEBUG_FLAGS =
HW_FLAGS =
LIB_FLAGS = -fopenmp -lm 
OPT_FLAGS = -O3 
LLC_FLAGS = -relocation-model=pic -filetype=obj
BASIC_FLAGS = ${HW_FLAGS} ${LIB_FLAGS} ${OPT_FLAGS} ${DEBUG_FLAGS} 

# helper library paths
COMMON = ${PWD}/common
SYS_DIR = ${PWD}/sys

# target architecture
ifeq ($(TARGET_ARCH),)
TARGET_ARCH = $(shell uname -m)
endif

# defualt benchmark input size is B
ifeq ($(SIZE),)
SIZE = B
endif

# default thread size is 1
ifeq ($(THREAD_SIZE),)
THREAD_SIZE = 1
endif

PAPI_PATH = ${COMMON}/all_papi/${TARGET_ARCH}
PAPI_INCLUDE = ${PAPI_PATH}/include
PAPI_LIB = ${PAPI_PATH}/lib
PAPI_LINE = -I${PAPI_INCLUDE} -L${PAPI_LIB} -lpapi -lpthread

M5_PATH = ${COMMON}/gem5
M5_LIB = -L${M5_PATH}/all_outs/${TARGET_ARCH} -lm5
M5_INCLUDE = -I${M5_PATH}
M5_LINE = -no-pie ${M5_INCLUDE} ${M5_LIB}

HOST_ARCH = $(shell uname -m)-unknown-linux-gnu

# program related paths
PROGRAM_UPPER = $(shell echo ${PROGRAM} | tr '[:lower:]' '[:upper:]')
PROGRAM_PATH = ${PWD}/${PROGRAM_UPPER}

# compiler frontend selection
F_PROGRAMS = bt cg ep ft lu mg sp

ifeq ($(filter $(PROGRAM),$(F_PROGRAMS)), $(PROGRAM))
COMPILER = ${FC}
else
COMPILER = ${CC}
endif

ifeq ($(REGION_LENGTH),)
REGION_LENGTH = 100000000
endif

VERSION_STAMP= 

# environment variables for sub-makefiles
ENV_VARS = FC='${FC}' CC='${CC}' CPP='${CPP}' OPT='${OPT}' \
	LLVM_LINK='${LLVM_LINK}' HW_FLAGS='${HW_FLAGS}' LIB_FLAGS='${LIB_FLAGS}' \
	OPT_FLAGS='${OPT_FLAGS}' LLC='${LLC}' LLC_FLAGS='${LLC_FLAGS}' \
	BASIC_FLAGS='${BASIC_FLAGS}' COMMON='${COMMON}' SYS_DIR='${SYS_DIR}' \
	PAPI_LINE='${PAPI_LINE}' M5_LINE='${M5_LINE}' M5_INCLUDE='${M5_INCLUDE}' \
	M5_LIB='${M5_LIB}' HOST_ARCH='${HOST_ARCH}' TARGET_ARCH='${TARGET_ARCH}' \
	SIZE='${SIZE}'

all: pre ${PROGRAM}

pre:
	cd ${COMMON} && make all ${ENV_VARS}

$(PROGRAM): pre ${PROGRAM_PATH}/${SIZE}/${PROGRAM}.bc
${PROGRAM_PATH}/${SIZE}/${PROGRAM}.bc:
	cd ${PROGRAM_PATH} && make all ${ENV_VARS}

# get version stamp
get_version:
	$(eval FILE := $(wildcard ${PROGRAM_PATH}/${SIZE}/*${PROGRAM}_O3_*.bc))
	$(eval VERSION_STAMP := $(subst ${PROGRAM_PATH}/${SIZE}/$(PROGRAM)_O3_,,$(basename $(FILE))))
	@echo PROGRAM_PATH=${PROGRAM_PATH}/${SIZE}
	@echo PROGRAM=${PROGRAM}
	@echo FILE=${FILE}	
	@echo ${VERSION_STAMP}

single_thread_c_profiling: get_version single_thread_c_profiling_${PROGRAM}_${SIZE}
single_thread_c_profiling_${PROGRAM}_${SIZE}: ${COMMON}/single_thread_c_profiling.ll
	cd ${PROGRAM_PATH}/${SIZE} && mkdir -p single_thread_c_profiling
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_profiling && mkdir -p ${REGION_LENGTH}
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_profiling/${REGION_LENGTH} && ${LLVM_LINK} -o ${PROGRAM}_profiling.bc ${PROGRAM_PATH}/${SIZE}/${PROGRAM}_O3_${VERSION_STAMP}.bc ${COMMON}/single_thread_c_profiling.ll
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_profiling/${REGION_LENGTH} && ${OPT} -passes=phase-analysis -phase-analysis-output-file=basic_block_info_output_${VERSION_STAMP}.txt ${PROGRAM}_profiling.bc -o ${PROGRAM}_profiling_opt.bc \
		-phase-analysis-using-papi=false -phase-analysis-region-length=${REGION_LENGTH} \
		2>> phase_analysis_log_${VERSION_STAMP}.log

single_thread_c_papi_profiling: get_version single_thread_c_papi_profiling_${PROGRAM}_${SIZE}
single_thread_c_papi_profiling_${PROGRAM}_${SIZE}: ${COMMON}/single_thread_c_papi_profiling.ll
	cd ${PROGRAM_PATH}/${SIZE} && mkdir -p single_thread_c_papi_profiling
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_papi_profiling && mkdir -p ${REGION_LENGTH}
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_papi_profiling/${REGION_LENGTH} && ${LLVM_LINK} -o ${PROGRAM}_papi_profiling.bc ${PROGRAM_PATH}/${SIZE}/${PROGRAM}_O3_${VERSION_STAMP}.bc ${COMMON}/single_thread_c_papi_profiling.ll
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_papi_profiling/${REGION_LENGTH} && ${OPT} -passes=phase-analysis -phase-analysis-output-file=basic_block_info_output_${VERSION_STAMP}.txt ${PROGRAM}_papi_profiling.bc -o ${PROGRAM}_papi_profiling_opt.bc \
		-phase-analysis-using-papi=true -phase-analysis-region-length=${REGION_LENGTH} \
		2>> phase_analysis_log_${VERSION_STAMP}.log

single_thread_c_papi_measuring: get_version single_thread_c_papi_measuring_${PROGRAM}_${SIZE}_${REGION_LENGTH}_${REGION_ID}
single_thread_c_papi_measuring_${PROGRAM}_${SIZE}_${REGION_LENGTH}_${REGION_ID}: ${COMMON}/single_thread_c_papi_measuring.ll
	cd ${PROGRAM_PATH}/${SIZE} && mkdir -p single_thread_c_papi_measuring
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_papi_measuring && mkdir -p ${THREAD_SIZE}
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_papi_measuring/${THREAD_SIZE} && mkdir -p ${REGION_LENGTH}
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_papi_measuring/${THREAD_SIZE}/${REGION_LENGTH} && mkdir -p ${REGION_ID}
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_papi_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && ${LLVM_LINK} -o ${PROGRAM}_papi_measuring.bc ${PROGRAM_PATH}/${SIZE}/${PROGRAM}_O3_${VERSION_STAMP}.bc ${COMMON}/single_thread_c_papi_measuring.ll
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_papi_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && ${OPT} -passes=phase-bound \
	-phase-bound-bb-order-file=${PROGRAM_PATH}/${SIZE}/region_info/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/basic_block_info_output_${VERSION_STAMP}.txt \
	-phase-bound-input-file=${PROGRAM_PATH}/${SIZE}/region_info/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${REGION_ID}_marker_info.txt \
	-phase-bound-output-file=basic_block_info_output_${VERSION_STAMP}.txt ${PROGRAM}_papi_measuring.bc -o ${PROGRAM}_papi_measuring_opt.bc \
	2>> phase_bound_log_${VERSION_STAMP}.log

single_thread_c_m5_fs_measuring: get_version single_thread_c_m5_fs_measuring_${PROGRAM}_${SIZE}_${REGION_LENGTH}_${REGION_ID}
single_thread_c_m5_fs_measuring_${PROGRAM}_${SIZE}_${REGION_LENGTH}_${REGION_ID}: ${COMMON}/single_thread_c_m5_fs_measuring.ll
	cd ${PROGRAM_PATH}/${SIZE} && mkdir -p single_thread_c_m5_fs_measuring
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_m5_fs_measuring && mkdir -p ${THREAD_SIZE}
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_m5_fs_measuring/${THREAD_SIZE} && mkdir -p ${REGION_LENGTH}
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_m5_fs_measuring/${THREAD_SIZE}/${REGION_LENGTH} && mkdir -p ${REGION_ID}
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_m5_fs_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && ${LLVM_LINK} -o ${PROGRAM}_m5_fs_measuring.bc ${PROGRAM_PATH}/${SIZE}/${PROGRAM}_O3_${VERSION_STAMP}.bc ${COMMON}/single_thread_c_m5_fs_measuring.ll
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_m5_fs_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && ${OPT} -passes=phase-bound \
	-phase-bound-bb-order-file=${PROGRAM_PATH}/${SIZE}/region_info/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/basic_block_info_output_${VERSION_STAMP}.txt \
	-phase-bound-input-file=${PROGRAM_PATH}/${SIZE}/region_info/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${REGION_ID}_marker_info.txt \
	-phase-bound-output-file=basic_block_info_output_${VERSION_STAMP}.txt ${PROGRAM}_m5_fs_measuring.bc -o ${PROGRAM}_m5_fs_measuring_opt.bc \
	2>> phase_bound_log_${VERSION_STAMP}.log

single_thread_c_marker_overhead_measuring: get_version single_thread_c_marker_overhead_measuring_${PROGRAM}_${SIZE}_${REGION_LENGTH}_${REGION_ID}
single_thread_c_marker_overhead_measuring_${PROGRAM}_${SIZE}_${REGION_LENGTH}_${REGION_ID}: ${COMMON}/single_thread_c_marker_overhead_measuring_start.ll ${COMMON}/single_thread_c_marker_overhead_measuring_end.ll
	cd ${PROGRAM_PATH}/${SIZE} && mkdir -p single_thread_c_marker_overhead_measuring
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_marker_overhead_measuring && mkdir -p ${THREAD_SIZE}
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_marker_overhead_measuring/${THREAD_SIZE} && mkdir -p ${REGION_LENGTH}
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH} && mkdir -p ${REGION_ID}
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && ${LLVM_LINK} -o ${PROGRAM}_single_thread_c_marker_overhead_measuring_start.bc ${PROGRAM_PATH}/${SIZE}/${PROGRAM}_O3_${VERSION_STAMP}.bc ${COMMON}/single_thread_c_marker_overhead_measuring_start.ll
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && ${OPT} -passes=phase-bound \
	-phase-bound-bb-order-file=${PROGRAM_PATH}/${SIZE}/region_info/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/basic_block_info_output_${VERSION_STAMP}.txt \
	-phase-bound-input-file=${PROGRAM_PATH}/${SIZE}/region_info/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${REGION_ID}_marker_info.txt \
	-phase-bound-output-file=basic_block_info_output_${VERSION_STAMP}.txt ${PROGRAM}_single_thread_c_marker_overhead_measuring_start.bc -o ${PROGRAM}_single_thread_c_marker_overhead_measuring_start_opt.bc \
	2>> phase_bound_log_start_${VERSION_STAMP}.log
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && ${LLVM_LINK} -o ${PROGRAM}_single_thread_c_marker_overhead_measuring_end.bc ${PROGRAM_PATH}/${SIZE}/${PROGRAM}_O3_${VERSION_STAMP}.bc ${COMMON}/single_thread_c_marker_overhead_measuring_end.ll
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && ${OPT} -passes=phase-bound \
	-phase-bound-bb-order-file=${PROGRAM_PATH}/${SIZE}/region_info/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/basic_block_info_output_${VERSION_STAMP}.txt \
	-phase-bound-input-file=${PROGRAM_PATH}/${SIZE}/region_info/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${REGION_ID}_marker_info.txt \
	-phase-bound-output-file=basic_block_info_output_${VERSION_STAMP}.txt ${PROGRAM}_single_thread_c_marker_overhead_measuring_end.bc -o ${PROGRAM}single_thread_c_marker_overhead_measuring_end_opt.bc \
	2>> phase_bound_log_end_${VERSION_STAMP}.log

final_compile_single_thread_c_profiling: get_version final_compile_single_thread_c_profiling_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}
final_compile_single_thread_c_profiling_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}:
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_profiling/${REGION_LENGTH} && mkdir -p ${TARGET_ARCH}
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_profiling/${REGION_LENGTH}/${TARGET_ARCH} && ${LLC} ${LLC_FLAGS} ../${PROGRAM}_profiling_opt.bc -o ${PROGRAM}_${TARGET_ARCH}_profiling.o --march=$(subst _,-,$(TARGET_ARCH))
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_profiling/${REGION_LENGTH}/${TARGET_ARCH} && ${COMPILER} ${LIB_FLAGS} ${PROGRAM}_${TARGET_ARCH}_profiling.o -o ${PROGRAM}_${TARGET_ARCH}_${VERSION_STAMP}.single_thread_c_profiling --target=${TARGET_ARCH}-unknown-linux-gnu

final_compile_single_thread_c_papi_profiling: get_version final_compile_single_thread_c_papi_profiling_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}
final_compile_single_thread_c_papi_profiling_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}:
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_papi_profiling/${REGION_LENGTH} && mkdir -p ${TARGET_ARCH}
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_papi_profiling/${REGION_LENGTH}/${TARGET_ARCH} && ${LLC} ${LLC_FLAGS} ../${PROGRAM}_papi_profiling_opt.bc -o ${PROGRAM}_${TARGET_ARCH}_papi_profiling.o --march=$(subst _,-,$(TARGET_ARCH))
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_papi_profiling/${REGION_LENGTH}/${TARGET_ARCH} && ${COMPILER} ${LIB_FLAGS} ${PAPI_LINE} ${PROGRAM}_${TARGET_ARCH}_papi_profiling.o -o ${PROGRAM}_${TARGET_ARCH}_${VERSION_STAMP}.single_thread_c_papi_profiling --target=${TARGET_ARCH}-unknown-linux-gnu

final_compile_single_thread_c_papi_measuring: get_version final_compile_single_thread_c_papi_measuring_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}_${REGION_ID}
final_compile_single_thread_c_papi_measuring_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}_${REGION_ID}:
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_papi_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && mkdir -p ${TARGET_ARCH}
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_papi_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${TARGET_ARCH} && ${LLC} ${LLC_FLAGS} ../${PROGRAM}_papi_measuring_opt.bc -o ${PROGRAM}_${TARGET_ARCH}_papi_measuring.o --march=$(subst _,-,$(TARGET_ARCH))
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_papi_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${TARGET_ARCH} && ${COMPILER} ${LIB_FLAGS} ${PAPI_LINE} ${PROGRAM}_${TARGET_ARCH}_papi_measuring.o -o ${PROGRAM}_${TARGET_ARCH}_${VERSION_STAMP}.single_thread_c_papi_measuring --target=${TARGET_ARCH}-unknown-linux-gnu

final_compile_single_thread_c_m5_fs_measuring: get_version final_compile_single_thread_c_m5_fs_measuring_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}_${REGION_ID}
final_compile_single_thread_c_m5_fs_measuring_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}_${REGION_ID}:
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_m5_fs_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && mkdir -p ${TARGET_ARCH}
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_m5_fs_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${TARGET_ARCH} && ${LLC} ${LLC_FLAGS} ../${PROGRAM}_m5_fs_measuring_opt.bc -o ${PROGRAM}_${TARGET_ARCH}_m5_fs_measuring.o --march=$(subst _,-,$(TARGET_ARCH))
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_m5_fs_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${TARGET_ARCH} && ${COMPILER} ${LIB_FLAGS} ${PROGRAM}_${TARGET_ARCH}_m5_fs_measuring.o -o ${PROGRAM}_${TARGET_ARCH}_${VERSION_STAMP}.single_thread_c_m5_fs_measuring --target=${TARGET_ARCH}-unknown-linux-gnu ${M5_LINE}

final_compile_single_thread_c_marker_overhead_measuring: get_version final_compile_single_thread_c_marker_overhead_measuring${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}_${REGION_ID}
final_compile_single_thread_c_marker_overhead_measuring${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}_${REGION_ID}:
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && mkdir -p ${TARGET_ARCH}
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${TARGET_ARCH} && ${LLC} ${LLC_FLAGS} ../${PROGRAM}_single_thread_c_marker_overhead_measuring_end_opt.bc -o ${PROGRAM}_${TARGET_ARCH}_single_thread_c_marker_overhead_measuring_end.o --march=$(subst _,-,$(TARGET_ARCH))
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${TARGET_ARCH} && ${LLC} ${LLC_FLAGS} ../${PROGRAM}_single_thread_c_marker_overhead_measuring_start_opt.bc -o ${PROGRAM}_${TARGET_ARCH}_single_thread_c_marker_overhead_measuring_start.o --march=$(subst _,-,$(TARGET_ARCH))
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${TARGET_ARCH} && ${COMPILER} ${LIB_FLAGS} ${PAPI_LINE} ${PROGRAM}_${TARGET_ARCH}_single_thread_c_marker_overhead_measuring_end.o -o ${PROGRAM}_${TARGET_ARCH}_${VERSION_STAMP}.single_thread_c_marker_overhead_measuring_end --target=${TARGET_ARCH}-unknown-linux-gnu
	cd ${PROGRAM_PATH}/${SIZE}/single_thread_c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${TARGET_ARCH} && ${COMPILER} ${LIB_FLAGS} ${PAPI_LINE} ${PROGRAM}_${TARGET_ARCH}_single_thread_c_marker_overhead_measuring_start.o -o ${PROGRAM}_${TARGET_ARCH}_${VERSION_STAMP}.single_thread_c_marker_overhead_measuring_start --target=${TARGET_ARCH}-unknown-linux-gnu

c_profiling: get_version c_profiling_${PROGRAM}_${SIZE}
c_profiling_${PROGRAM}_${SIZE}: ${COMMON}/c_profiling.ll
	cd ${PROGRAM_PATH}/${SIZE} && mkdir -p c_profiling
	cd ${PROGRAM_PATH}/${SIZE}/c_profiling && mkdir -p ${REGION_LENGTH}
	cd ${PROGRAM_PATH}/${SIZE}/c_profiling/${REGION_LENGTH} && ${LLVM_LINK} -o ${PROGRAM}_profiling.bc ${PROGRAM_PATH}/${SIZE}/${PROGRAM}_O3_${VERSION_STAMP}.bc ${COMMON}/c_profiling.ll
	cd ${PROGRAM_PATH}/${SIZE}/c_profiling/${REGION_LENGTH} && ${OPT} -passes=phase-analysis -phase-analysis-output-file=basic_block_info_output_${VERSION_STAMP}.txt ${PROGRAM}_profiling.bc -o ${PROGRAM}_profiling_opt.bc \
		-phase-analysis-using-papi=false -phase-analysis-region-length=${REGION_LENGTH} \
		2>> phase_analysis_log_${VERSION_STAMP}.log

cpp_profiling: get_version cpp_profiling_${PROGRAM}_${SIZE}
cpp_profiling_${PROGRAM}_${SIZE}: ${COMMON}/cpp_profiling.ll
	cd ${PROGRAM_PATH}/${SIZE} && mkdir -p cpp_profiling
	cd ${PROGRAM_PATH}/${SIZE}/cpp_profiling && mkdir -p ${REGION_LENGTH}
	cd ${PROGRAM_PATH}/${SIZE}/cpp_profiling/${REGION_LENGTH} && ${LLVM_LINK} -o ${PROGRAM}_profiling.bc ${PROGRAM_PATH}/${SIZE}/${PROGRAM}_O3_${VERSION_STAMP}.bc ${COMMON}/cpp_profiling.ll
	cd ${PROGRAM_PATH}/${SIZE}/cpp_profiling/${REGION_LENGTH} && ${OPT} -passes=phase-analysis -phase-analysis-output-file=basic_block_info_output_${VERSION_STAMP}.txt ${PROGRAM}_profiling.bc -o ${PROGRAM}_profiling_opt.bc \
		-phase-analysis-using-papi=false -phase-analysis-region-length=${REGION_LENGTH} \
		2>> phase_analysis_log_${VERSION_STAMP}.log

c_papi_profiling: get_version c_papi_profiling_${PROGRAM}_${SIZE}
c_papi_profiling_${PROGRAM}_${SIZE}: ${COMMON}/c_papi_profiling.ll
	cd ${PROGRAM_PATH}/${SIZE} && mkdir -p c_papi_profiling
	cd ${PROGRAM_PATH}/${SIZE}/c_papi_profiling && mkdir -p ${REGION_LENGTH}
	cd ${PROGRAM_PATH}/${SIZE}/c_papi_profiling/${REGION_LENGTH} && ${LLVM_LINK} -o ${PROGRAM}_papi_profiling.bc ${PROGRAM_PATH}/${SIZE}/${PROGRAM}_O3_${VERSION_STAMP}.bc ${COMMON}/c_papi_profiling.ll
	cd ${PROGRAM_PATH}/${SIZE}/c_papi_profiling/${REGION_LENGTH} && ${OPT} -passes=phase-analysis -phase-analysis-output-file=basic_block_info_output_${VERSION_STAMP}.txt ${PROGRAM}_papi_profiling.bc -o ${PROGRAM}_papi_profiling_opt.bc \
		-phase-analysis-using-papi=true -phase-analysis-region-length=${REGION_LENGTH} \
		2>> phase_analysis_log_${VERSION_STAMP}.log

c_papi_measuring: get_version c_papi_measuring_${PROGRAM}_${SIZE}_${REGION_LENGTH}_${REGION_ID}
c_papi_measuring_${PROGRAM}_${SIZE}_${REGION_LENGTH}_${REGION_ID}: ${COMMON}/c_papi_measuring.ll
	cd ${PROGRAM_PATH}/${SIZE} && mkdir -p c_papi_measuring
	cd ${PROGRAM_PATH}/${SIZE}/c_papi_measuring && mkdir -p ${THREAD_SIZE}
	cd ${PROGRAM_PATH}/${SIZE}/c_papi_measuring/${THREAD_SIZE} && mkdir -p ${REGION_LENGTH}
	cd ${PROGRAM_PATH}/${SIZE}/c_papi_measuring/${THREAD_SIZE}/${REGION_LENGTH} && mkdir -p ${REGION_ID}
	cd ${PROGRAM_PATH}/${SIZE}/c_papi_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && ${LLVM_LINK} -o ${PROGRAM}_papi_measuring.bc ${PROGRAM_PATH}/${SIZE}/${PROGRAM}_O3_${VERSION_STAMP}.bc ${COMMON}/c_papi_measuring.ll
	cd ${PROGRAM_PATH}/${SIZE}/c_papi_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && ${OPT} -passes=phase-bound \
	-phase-bound-bb-order-file=${PROGRAM_PATH}/${SIZE}/region_info/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/basic_block_info_output_${VERSION_STAMP}.txt \
	-phase-bound-input-file=${PROGRAM_PATH}/${SIZE}/region_info/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${REGION_ID}_marker_info.txt \
	-phase-bound-output-file=basic_block_info_output_${VERSION_STAMP}.txt ${PROGRAM}_papi_measuring.bc -o ${PROGRAM}_papi_measuring_opt.bc \
	2>> phase_bound_log_${VERSION_STAMP}.log

c_m5_fs_measuring: get_version c_m5_fs_measuring_${PROGRAM}_${SIZE}_${REGION_LENGTH}_${REGION_ID}
c_m5_fs_measuring_${PROGRAM}_${SIZE}_${REGION_LENGTH}_${REGION_ID}: ${COMMON}/c_m5_fs_measuring.ll
	cd ${PROGRAM_PATH}/${SIZE} && mkdir -p c_m5_fs_measuring
	cd ${PROGRAM_PATH}/${SIZE}/c_m5_fs_measuring && mkdir -p ${THREAD_SIZE}
	cd ${PROGRAM_PATH}/${SIZE}/c_m5_fs_measuring/${THREAD_SIZE} && mkdir -p ${REGION_LENGTH}
	cd ${PROGRAM_PATH}/${SIZE}/c_m5_fs_measuring/${THREAD_SIZE}/${REGION_LENGTH} && mkdir -p ${REGION_ID}
	cd ${PROGRAM_PATH}/${SIZE}/c_m5_fs_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && ${LLVM_LINK} -o ${PROGRAM}_m5_fs_measuring.bc ${PROGRAM_PATH}/${SIZE}/${PROGRAM}_O3_${VERSION_STAMP}.bc ${COMMON}/c_m5_fs_measuring.ll
	cd ${PROGRAM_PATH}/${SIZE}/c_m5_fs_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && ${OPT} -passes=phase-bound \
	-phase-bound-bb-order-file=${PROGRAM_PATH}/${SIZE}/region_info/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/basic_block_info_output_${VERSION_STAMP}.txt \
	-phase-bound-input-file=${PROGRAM_PATH}/${SIZE}/region_info/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${REGION_ID}_marker_info.txt \
	-phase-bound-output-file=basic_block_info_output_${VERSION_STAMP}.txt ${PROGRAM}_m5_fs_measuring.bc -o ${PROGRAM}_m5_fs_measuring_opt.bc \
	2>> phase_bound_log_${VERSION_STAMP}.log

c_marker_overhead_measuring: get_version c_marker_overhead_measuring_${PROGRAM}_${SIZE}_${REGION_LENGTH}_${REGION_ID}
c_marker_overhead_measuring_${PROGRAM}_${SIZE}_${REGION_LENGTH}_${REGION_ID}: ${COMMON}/c_marker_overhead_measuring_start.ll ${COMMON}/c_marker_overhead_measuring_end.ll
	cd ${PROGRAM_PATH}/${SIZE} && mkdir -p c_papi_measuring
	cd ${PROGRAM_PATH}/${SIZE}/c_marker_overhead_measuring && mkdir -p ${THREAD_SIZE}
	cd ${PROGRAM_PATH}/${SIZE}/c_marker_overhead_measuring/${THREAD_SIZE} && mkdir -p ${REGION_LENGTH}
	cd ${PROGRAM_PATH}/${SIZE}/c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH} && mkdir -p ${REGION_ID}
	cd ${PROGRAM_PATH}/${SIZE}/c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && ${LLVM_LINK} -o ${PROGRAM}_c_marker_overhead_measuring_start.bc ${PROGRAM_PATH}/${SIZE}/${PROGRAM}_O3_${VERSION_STAMP}.bc ${COMMON}/c_marker_overhead_measuring_start.ll
	cd ${PROGRAM_PATH}/${SIZE}/c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && ${OPT} -passes=phase-bound \
	-phase-bound-bb-order-file=${PROGRAM_PATH}/${SIZE}/region_info/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/basic_block_info_output_${VERSION_STAMP}.txt \
	-phase-bound-input-file=${PROGRAM_PATH}/${SIZE}/region_info/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${REGION_ID}_marker_info.txt \
	-phase-bound-output-file=basic_block_info_output_${VERSION_STAMP}.txt ${PROGRAM}_c_marker_overhead_measuring_start.bc -o ${PROGRAM}_c_marker_overhead_measuring_start_opt.bc \
	2>> phase_bound_log_start_${VERSION_STAMP}.log
	cd ${PROGRAM_PATH}/${SIZE}/c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && ${LLVM_LINK} -o ${PROGRAM}_c_marker_overhead_measuring_end.bc ${PROGRAM_PATH}/${SIZE}/${PROGRAM}_O3_${VERSION_STAMP}.bc ${COMMON}/c_marker_overhead_measuring_end.ll
	cd ${PROGRAM_PATH}/${SIZE}/c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && ${OPT} -passes=phase-bound \
	-phase-bound-bb-order-file=${PROGRAM_PATH}/${SIZE}/region_info/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/basic_block_info_output_${VERSION_STAMP}.txt \
	-phase-bound-input-file=${PROGRAM_PATH}/${SIZE}/region_info/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${REGION_ID}_marker_info.txt \
	-phase-bound-output-file=basic_block_info_output_${VERSION_STAMP}.txt ${PROGRAM}_c_marker_overhead_measuring_end.bc -o ${PROGRAM}_c_marker_overhead_measuring_end_opt.bc \
	2>> phase_bound_log_end_${VERSION_STAMP}.log

final_compile_c_profiling: get_version final_compile_c_profiling_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}
final_compile_c_profiling_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}:
	cd ${PROGRAM_PATH}/${SIZE}/c_profiling/${REGION_LENGTH} && mkdir -p ${TARGET_ARCH}
	cd ${PROGRAM_PATH}/${SIZE}/c_profiling/${REGION_LENGTH}/${TARGET_ARCH} && ${LLC} ${LLC_FLAGS} ../${PROGRAM}_profiling_opt.bc -o ${PROGRAM}_${TARGET_ARCH}_profiling.o --march=$(subst _,-,$(TARGET_ARCH))
	cd ${PROGRAM_PATH}/${SIZE}/c_profiling/${REGION_LENGTH}/${TARGET_ARCH} && ${COMPILER} ${LIB_FLAGS} ${PROGRAM}_${TARGET_ARCH}_profiling.o -o ${PROGRAM}_${TARGET_ARCH}_${VERSION_STAMP}.c_profiling --target=${TARGET_ARCH}-unknown-linux-gnu

final_compile_cpp_profiling: get_version final_compile_cpp_profiling_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}
final_compile_cpp_profiling_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}:
	cd ${PROGRAM_PATH}/${SIZE}/cpp_profiling/${REGION_LENGTH} && mkdir -p ${TARGET_ARCH}
	cd ${PROGRAM_PATH}/${SIZE}/cpp_profiling/${REGION_LENGTH}/${TARGET_ARCH} && ${LLC} ${LLC_FLAGS} ../${PROGRAM}_profiling_opt.bc -o ${PROGRAM}_${TARGET_ARCH}_profiling.o --march=$(subst _,-,$(TARGET_ARCH))
	cd ${PROGRAM_PATH}/${SIZE}/cpp_profiling/${REGION_LENGTH}/${TARGET_ARCH} && ${COMPILER} ${LIB_FLAGS} -lstdc++ ${PROGRAM}_${TARGET_ARCH}_profiling.o -o ${PROGRAM}_${TARGET_ARCH}_${VERSION_STAMP}.cpp_profiling --target=${TARGET_ARCH}-unknown-linux-gnu

final_compile_c_papi_profiling: get_version final_compile_c_papi_profiling_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}
final_compile_c_papi_profiling_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}:
	cd ${PROGRAM_PATH}/${SIZE}/c_papi_profiling/${REGION_LENGTH} && mkdir -p ${TARGET_ARCH}
	cd ${PROGRAM_PATH}/${SIZE}/c_papi_profiling/${REGION_LENGTH}/${TARGET_ARCH} && ${LLC} ${LLC_FLAGS} ../${PROGRAM}_papi_profiling_opt.bc -o ${PROGRAM}_${TARGET_ARCH}_papi_profiling.o --march=$(subst _,-,$(TARGET_ARCH))
	cd ${PROGRAM_PATH}/${SIZE}/c_papi_profiling/${REGION_LENGTH}/${TARGET_ARCH} && ${COMPILER} ${LIB_FLAGS} ${PAPI_LINE} ${PROGRAM}_${TARGET_ARCH}_papi_profiling.o -o ${PROGRAM}_${TARGET_ARCH}_${VERSION_STAMP}.c_papi_profiling --target=${TARGET_ARCH}-unknown-linux-gnu

final_compile_c_papi_measuring: get_version final_compile_c_papi_measuring_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}_${REGION_ID}
final_compile_c_papi_measuring_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}_${REGION_ID}:
	cd ${PROGRAM_PATH}/${SIZE}/c_papi_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && mkdir -p ${TARGET_ARCH}
	cd ${PROGRAM_PATH}/${SIZE}/c_papi_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${TARGET_ARCH} && ${LLC} ${LLC_FLAGS} ../${PROGRAM}_papi_measuring_opt.bc -o ${PROGRAM}_${TARGET_ARCH}_papi_measuring.o --march=$(subst _,-,$(TARGET_ARCH))
	cd ${PROGRAM_PATH}/${SIZE}/c_papi_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${TARGET_ARCH} && ${COMPILER} ${LIB_FLAGS} ${PAPI_LINE} ${PROGRAM}_${TARGET_ARCH}_papi_measuring.o -o ${PROGRAM}_${TARGET_ARCH}_${VERSION_STAMP}.c_papi_measuring --target=${TARGET_ARCH}-unknown-linux-gnu

final_compile_c_m5_fs_measuring: get_version final_compile_c_m5_fs_measuring_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}_${REGION_ID}
final_compile_c_m5_fs_measuring_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}_${REGION_ID}:
	cd ${PROGRAM_PATH}/${SIZE}/c_m5_fs_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && mkdir -p ${TARGET_ARCH}
	cd ${PROGRAM_PATH}/${SIZE}/c_m5_fs_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${TARGET_ARCH} && ${LLC} ${LLC_FLAGS} ../${PROGRAM}_m5_fs_measuring_opt.bc -o ${PROGRAM}_${TARGET_ARCH}_m5_fs_measuring.o --march=$(subst _,-,$(TARGET_ARCH))
	cd ${PROGRAM_PATH}/${SIZE}/c_m5_fs_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${TARGET_ARCH} && ${COMPILER} ${LIB_FLAGS} ${PROGRAM}_${TARGET_ARCH}_m5_fs_measuring.o -o ${PROGRAM}_${TARGET_ARCH}_${VERSION_STAMP}.c_m5_fs_measuring --target=${TARGET_ARCH}-unknown-linux-gnu ${M5_LINE}

final_compile_c_marker_overhead_measuring: get_version final_compile_c_marker_overhead_measuring_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}_${REGION_ID}
final_compile_c_marker_overhead_measuring_${PROGRAM}_${SIZE}_${TARGET_ARCH}_${REGION_LENGTH}_${REGION_ID}:
	cd ${PROGRAM_PATH}/${SIZE}/c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID} && mkdir -p ${TARGET_ARCH}
	cd ${PROGRAM_PATH}/${SIZE}/c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${TARGET_ARCH} && ${LLC} ${LLC_FLAGS} ../${PROGRAM}c_marker_overhead_measuring_start_opt.bc -o ${PROGRAM}_${TARGET_ARCH}_c_marker_overhead_measuring_start.o --march=$(subst _,-,$(TARGET_ARCH))
	cd ${PROGRAM_PATH}/${SIZE}/c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${TARGET_ARCH} && ${COMPILER} ${LIB_FLAGS} ${PAPI_LINE} ${PROGRAM}_${TARGET_ARCH}_c_marker_overhead_measuring_start.o -o ${PROGRAM}_${TARGET_ARCH}_${VERSION_STAMP}.c_marker_overhead_measuring_start --target=${TARGET_ARCH}-unknown-linux-gnu
	cd ${PROGRAM_PATH}/${SIZE}/c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${TARGET_ARCH} && ${LLC} ${LLC_FLAGS} ../${PROGRAM}_c_marker_overhead_measuring_end_opt.bc -o ${PROGRAM}_${TARGET_ARCH}_c_marker_overhead_measuring_end.o --march=$(subst _,-,$(TARGET_ARCH))
	cd ${PROGRAM_PATH}/${SIZE}/c_marker_overhead_measuring/${THREAD_SIZE}/${REGION_LENGTH}/${REGION_ID}/${TARGET_ARCH} && ${COMPILER} ${LIB_FLAGS} ${PAPI_LINE} ${PROGRAM}_${TARGET_ARCH}_c_marker_overhead_measuring_end.o -o ${PROGRAM}_${TARGET_ARCH}_${VERSION_STAMP}.c_marker_overhead_measuring_end --target=${TARGET_ARCH}-unknown-linux-gnu

naive: get_version naive_${PROGRAM}_${SIZE}
naive_${PROGRAM}_${SIZE}: ${COMMON}/c_naive.ll
	cd ${PROGRAM_PATH}/${SIZE} && mkdir -p naive
	cd ${PROGRAM_PATH}/${SIZE}/naive && ${LLVM_LINK} -o ${PROGRAM}_naive.bc "${PROGRAM_PATH}/${SIZE}/${PROGRAM}_O3_${VERSION_STAMP}.bc" ${COMMON}/c_naive.ll

c_papi_naive: get_version c_papi_naive_${PROGRAM}_${SIZE}
c_papi_naive_${PROGRAM}_${SIZE}: ${COMMON}/c_papi_naive.ll
	cd ${PROGRAM_PATH}/${SIZE} && mkdir -p c_papi_naive
	cd ${PROGRAM_PATH}/${SIZE}/c_papi_naive && ${LLVM_LINK} -o ${PROGRAM}_papi_naive.bc ${PROGRAM_PATH}/${SIZE}/${PROGRAM}_O3_${VERSION_STAMP}.bc ${COMMON}/c_papi_naive.ll

c_marker_looppoint_m5_fs: get_version c_marker_looppoint_m5_fs_${PROGRAM}_${SIZE}
c_marker_looppoint_m5_fs_${PROGRAM}_${SIZE}: ${COMMON}/c_marker_looppoint_m5_fs.ll
	cd ${PROGRAM_PATH}/${SIZE} && mkdir -p c_marker_looppoint_m5_fs
	cd ${PROGRAM_PATH}/${SIZE}/c_marker_looppoint_m5_fs && ${LLVM_LINK} -o ${PROGRAM}_marker_looppoint_m5_fs.bc ${PROGRAM_PATH}/${SIZE}/${PROGRAM}_O3_${VERSION_STAMP}.bc ${COMMON}/c_marker_looppoint_m5_fs.ll

final_compile_naive: get_version final_compile_naive_${PROGRAM}_${SIZE}_${TARGET_ARCH}
final_compile_naive_${PROGRAM}_${SIZE}_${TARGET_ARCH}:
	cd ${PROGRAM_PATH}/${SIZE}/naive && mkdir -p ${TARGET_ARCH} 
	cd ${PROGRAM_PATH}/${SIZE}/naive/${TARGET_ARCH} && ${LLC} ${LLC_FLAGS} ../${PROGRAM}_naive.bc -o ${PROGRAM}_${TARGET_ARCH}_naive.o --march=$(subst _,-,$(TARGET_ARCH))
	cd ${PROGRAM_PATH}/${SIZE}/naive/${TARGET_ARCH} && ${COMPILER} ${LIB_FLAGS} ${PROGRAM}_${TARGET_ARCH}_naive.o -o ${PROGRAM}_${TARGET_ARCH}_${VERSION_STAMP}.naive --target=${TARGET_ARCH}-unknown-linux-gnu

final_compile_c_papi_naive: get_version final_compile_c_papi_naive_${PROGRAM}_${SIZE}_${TARGET_ARCH}
final_compile_c_papi_naive_${PROGRAM}_${SIZE}_${TARGET_ARCH}:
	cd ${PROGRAM_PATH}/${SIZE}/c_papi_naive && mkdir -p ${TARGET_ARCH}
	cd ${PROGRAM_PATH}/${SIZE}/c_papi_naive/${TARGET_ARCH} && ${LLC} ${LLC_FLAGS} ../${PROGRAM}_papi_naive.bc -o ${PROGRAM}_${TARGET_ARCH}_papi_naive.o --march=$(subst _,-,$(TARGET_ARCH))
	cd ${PROGRAM_PATH}/${SIZE}/c_papi_naive/${TARGET_ARCH} && ${COMPILER} ${LIB_FLAGS} ${PAPI_LINE} ${PROGRAM}_${TARGET_ARCH}_papi_naive.o -o ${PROGRAM}_${TARGET_ARCH}_${VERSION_STAMP}.c_papi_naive --target=${TARGET_ARCH}-unknown-linux-gnu

final_compile_c_marker_looppoint_m5_fs: get_version final_compile_c_marker_looppoint_m5_fs_${PROGRAM}_${SIZE}_${TARGET_ARCH}
final_compile_c_marker_looppoint_m5_fs_${PROGRAM}_${SIZE}_${TARGET_ARCH}:
	cd ${PROGRAM_PATH}/${SIZE}/c_marker_looppoint_m5_fs && mkdir -p ${TARGET_ARCH}
	cd ${PROGRAM_PATH}/${SIZE}/c_marker_looppoint_m5_fs/${TARGET_ARCH} && ${LLC} ${LLC_FLAGS} ../${PROGRAM}_marker_looppoint_m5_fs.bc -o ${PROGRAM}_${TARGET_ARCH}_marker_looppoint_m5_fs.o --march=$(subst _,-,$(TARGET_ARCH))
	cd ${PROGRAM_PATH}/${SIZE}/c_marker_looppoint_m5_fs/${TARGET_ARCH} && ${COMPILER} ${LIB_FLAGS} ${PROGRAM}_${TARGET_ARCH}_marker_looppoint_m5_fs.o -o ${PROGRAM}_${TARGET_ARCH}_${VERSION_STAMP}.c_marker_looppoint_m5_fs --target=${TARGET_ARCH}-unknown-linux-gnu ${M5_LINE}

clean:
	cd ${COMMON} && make clean
	cd ${PROGRAM_PATH} && make clean

clean_all:
	cd ${COMMON} && make clean
	cd ${PROGRAM_PATH} && make clean_all

