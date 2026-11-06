//==============================================================
//Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2026.1 (64-bit)
//Tool Version Limit: 2026.06
//Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
//Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
//
//==============================================================
`ifndef CHOLESKY_INVERSE_CONFIG__SV                        
    `define CHOLESKY_INVERSE_CONFIG__SV                    
                                                            
    class cholesky_inverse_config extends uvm_object;            
                                                            
        int check_ena;                                      
        int cover_ena;                                      

        `uvm_object_utils_begin(cholesky_inverse_config)         
        `uvm_field_int   (check_ena , UVM_DEFAULT)          
        `uvm_field_int   (cover_ena , UVM_DEFAULT)          
        `uvm_object_utils_end                               

        function new (string name = "cholesky_inverse_config");
            super.new(name);                                
        endfunction                                         
                                                            
    endclass                                                
                                                            
`endif                                                      
