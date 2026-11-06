# ==============================================================
# Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2026.1 (64-bit)
# Tool Version Limit: 2026.06
# Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
# Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
# 
# ==============================================================
CSIM_DESIGN = 1

__SIM_FPO__ = 1

__SIM_MATHHLS__ = 1

__SIM_FFT__ = 1

__SIM_VRF_FFT__ = 1

__SIM_FIR__ = 1

__SIM_DDS__ = 1

__USE_CLANG__ = 1

ObjDir = obj

HLS_SOURCES = ../../../../../../../../../../../cholesky_hardware_64bits/tb_lu_decomposition.cpp ../../../../../../../../../../../cholesky_hardware_64bits/inversion.cpp ../../../../../../../../../../../cholesky_hardware_64bits/foward_substitution.cpp ../../../../../../../../../../../cholesky_hardware_64bits/g_step.cpp ../../../../../../../../../../../cholesky_hardware_64bits/s_step.cpp ../../../../../../../../../../../cholesky_hardware_64bits/dv_step.cpp ../../../../../../../../../../../cholesky_hardware_64bits/lu_decomposition.cpp ../../../../../../../../../../../cholesky_hardware_64bits/cholesky_decomposition.cpp

override TARGET := csim.exe

AUTOPILOT_ROOT := /home/juliana/2026.1/Vitis
AUTOPILOT_MACH := lnx64
ifdef AP_GCC_M32
  AUTOPILOT_MACH := Linux_x86
  IFLAG += -m32
endif
IFLAG += -fPIC
ifndef AP_GCC_PATH
  AP_GCC_PATH := /home/juliana/2026.1/Vitis/tps/lnx64/gcc-8.3.0/bin
endif
AUTOPILOT_TOOL := ${AUTOPILOT_ROOT}/${AUTOPILOT_MACH}/tools
AP_CLANG_PATH := ${AUTOPILOT_ROOT}/lnx64/tools/clang-16/bin
AUTOPILOT_TECH := ${AUTOPILOT_ROOT}/common/technology


IFLAG += -I "${AUTOPILOT_ROOT}/include"
IFLAG += -I "${AUTOPILOT_ROOT}/include/ap_sysc"
IFLAG += -I "${AUTOPILOT_TECH}/generic/SystemC"
IFLAG += -I "${AUTOPILOT_TECH}/generic/SystemC/AESL_FP_comp"
IFLAG += -I "${AUTOPILOT_TECH}/generic/SystemC/AESL_comp"
IFLAG += -I "${AUTOPILOT_TOOL}/auto_cc/include"
IFLAG += -I "/usr/include/x86_64-linux-gnu"
IFLAG += -D__HLS_COSIM__

IFLAG += -D__HLS_CSIM__

IFLAG += -D__VITIS_HLS__

IFLAG += -D__SIM_FPO__

IFLAG += -D__SIM_FFT__

IFLAG += -D__SIM_VRF_FFT__

IFLAG += -D__SIM_FIR__

IFLAG += -D__SIM_DDS__

IFLAG += -D__DSP48E2__
IFLAG += -g
DFLAG += -D__xilinx_ip_top= -DAESL_TB
CCFLAG += -Werror=return-type
CCFLAG += -Wno-abi
CCFLAG += -fdebug-default-version=4
CCFLAG += --gcc-toolchain=/home/juliana/2026.1/Vitis/tps/lnx64/gcc-8.3.0
CCFLAG += -Werror=uninitialized
CCFLAG += -Wno-c++11-narrowing
CCFLAG += -Wno-error=sometimes-uninitialized
LFLAG += --gcc-toolchain=/home/juliana/2026.1/Vitis/tps/lnx64/gcc-8.3.0
LFLAG += -lstdc++fs



include ./Makefile.rules

all: $(TARGET)



$(ObjDir)/tb_lu_decomposition.o: ../../../../../../../../../../../cholesky_hardware_64bits/tb_lu_decomposition.cpp $(ObjDir)/.dir csim.mk
	$(Echo) "   Compiling ../../../../../../../../../../../cholesky_hardware_64bits/tb_lu_decomposition.cpp in $(BuildMode) mode" $(AVE_DIR_DLOG)
	$(Verb)  $(CXX) -std=gnu++17 ${CCFLAG} -c -MMD -I/home/juliana/GitHub/TCC/hardware/cholesky_hardware_64bits -DCHOL_FRAC_BITS=32 -DCHOL_INT_BITS=32 -DCHOL_N=32 -DCHOL_QUANT=AP_TRN -DCHOL_OVERFLOW=AP_SAT -Wno-unknown-pragmas -Wno-unknown-pragmas  $(IFLAG) $(DFLAG) $< -o $@ ; \

-include $(ObjDir)/tb_lu_decomposition.d

$(ObjDir)/inversion.o: ../../../../../../../../../../../cholesky_hardware_64bits/inversion.cpp $(ObjDir)/.dir csim.mk
	$(Echo) "   Compiling ../../../../../../../../../../../cholesky_hardware_64bits/inversion.cpp in $(BuildMode) mode" $(AVE_DIR_DLOG)
	$(Verb)  $(CXX) -std=gnu++17 ${CCFLAG} -c -MMD -I/home/juliana/GitHub/TCC/hardware/cholesky_hardware_64bits -DCHOL_FRAC_BITS=32 -DCHOL_INT_BITS=32 -DCHOL_N=32 -DCHOL_QUANT=AP_TRN -DCHOL_OVERFLOW=AP_SAT  -fhls-csim -fhlstoplevel=cholesky_decomposition $(IFLAG) $(DFLAG) $< -o $@ ; \

-include $(ObjDir)/inversion.d

$(ObjDir)/foward_substitution.o: ../../../../../../../../../../../cholesky_hardware_64bits/foward_substitution.cpp $(ObjDir)/.dir csim.mk
	$(Echo) "   Compiling ../../../../../../../../../../../cholesky_hardware_64bits/foward_substitution.cpp in $(BuildMode) mode" $(AVE_DIR_DLOG)
	$(Verb)  $(CXX) -std=gnu++17 ${CCFLAG} -c -MMD -I/home/juliana/GitHub/TCC/hardware/cholesky_hardware_64bits -DCHOL_FRAC_BITS=32 -DCHOL_INT_BITS=32 -DCHOL_N=32 -DCHOL_QUANT=AP_TRN -DCHOL_OVERFLOW=AP_SAT  -fhls-csim -fhlstoplevel=cholesky_decomposition $(IFLAG) $(DFLAG) $< -o $@ ; \

-include $(ObjDir)/foward_substitution.d

$(ObjDir)/g_step.o: ../../../../../../../../../../../cholesky_hardware_64bits/g_step.cpp $(ObjDir)/.dir csim.mk
	$(Echo) "   Compiling ../../../../../../../../../../../cholesky_hardware_64bits/g_step.cpp in $(BuildMode) mode" $(AVE_DIR_DLOG)
	$(Verb)  $(CXX) -std=gnu++17 ${CCFLAG} -c -MMD -I/home/juliana/GitHub/TCC/hardware/cholesky_hardware_64bits -DCHOL_FRAC_BITS=32 -DCHOL_INT_BITS=32 -DCHOL_N=32 -DCHOL_QUANT=AP_TRN -DCHOL_OVERFLOW=AP_SAT  -fhls-csim -fhlstoplevel=cholesky_decomposition $(IFLAG) $(DFLAG) $< -o $@ ; \

-include $(ObjDir)/g_step.d

$(ObjDir)/s_step.o: ../../../../../../../../../../../cholesky_hardware_64bits/s_step.cpp $(ObjDir)/.dir csim.mk
	$(Echo) "   Compiling ../../../../../../../../../../../cholesky_hardware_64bits/s_step.cpp in $(BuildMode) mode" $(AVE_DIR_DLOG)
	$(Verb)  $(CXX) -std=gnu++17 ${CCFLAG} -c -MMD -I/home/juliana/GitHub/TCC/hardware/cholesky_hardware_64bits -DCHOL_FRAC_BITS=32 -DCHOL_INT_BITS=32 -DCHOL_N=32 -DCHOL_QUANT=AP_TRN -DCHOL_OVERFLOW=AP_SAT  -fhls-csim -fhlstoplevel=cholesky_decomposition $(IFLAG) $(DFLAG) $< -o $@ ; \

-include $(ObjDir)/s_step.d

$(ObjDir)/dv_step.o: ../../../../../../../../../../../cholesky_hardware_64bits/dv_step.cpp $(ObjDir)/.dir csim.mk
	$(Echo) "   Compiling ../../../../../../../../../../../cholesky_hardware_64bits/dv_step.cpp in $(BuildMode) mode" $(AVE_DIR_DLOG)
	$(Verb)  $(CXX) -std=gnu++17 ${CCFLAG} -c -MMD -I/home/juliana/GitHub/TCC/hardware/cholesky_hardware_64bits -DCHOL_FRAC_BITS=32 -DCHOL_INT_BITS=32 -DCHOL_N=32 -DCHOL_QUANT=AP_TRN -DCHOL_OVERFLOW=AP_SAT  -fhls-csim -fhlstoplevel=cholesky_decomposition $(IFLAG) $(DFLAG) $< -o $@ ; \

-include $(ObjDir)/dv_step.d

$(ObjDir)/lu_decomposition.o: ../../../../../../../../../../../cholesky_hardware_64bits/lu_decomposition.cpp $(ObjDir)/.dir csim.mk
	$(Echo) "   Compiling ../../../../../../../../../../../cholesky_hardware_64bits/lu_decomposition.cpp in $(BuildMode) mode" $(AVE_DIR_DLOG)
	$(Verb)  $(CXX) -std=gnu++17 ${CCFLAG} -c -MMD -I/home/juliana/GitHub/TCC/hardware/cholesky_hardware_64bits -DCHOL_FRAC_BITS=32 -DCHOL_INT_BITS=32 -DCHOL_N=32 -DCHOL_QUANT=AP_TRN -DCHOL_OVERFLOW=AP_SAT  -fhls-csim -fhlstoplevel=cholesky_decomposition $(IFLAG) $(DFLAG) $< -o $@ ; \

-include $(ObjDir)/lu_decomposition.d

$(ObjDir)/cholesky_decomposition.o: ../../../../../../../../../../../cholesky_hardware_64bits/cholesky_decomposition.cpp $(ObjDir)/.dir csim.mk
	$(Echo) "   Compiling ../../../../../../../../../../../cholesky_hardware_64bits/cholesky_decomposition.cpp in $(BuildMode) mode" $(AVE_DIR_DLOG)
	$(Verb)  $(CXX) -std=gnu++17 ${CCFLAG} -c -MMD -I/home/juliana/GitHub/TCC/hardware/cholesky_hardware_64bits -DCHOL_FRAC_BITS=32 -DCHOL_INT_BITS=32 -DCHOL_N=32 -DCHOL_QUANT=AP_TRN -DCHOL_OVERFLOW=AP_SAT  -fhls-csim -fhlstoplevel=cholesky_decomposition $(IFLAG) $(DFLAG) $< -o $@ ; \

-include $(ObjDir)/cholesky_decomposition.d
