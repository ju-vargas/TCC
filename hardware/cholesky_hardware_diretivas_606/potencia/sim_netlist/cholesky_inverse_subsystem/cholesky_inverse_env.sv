//==============================================================
//Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2026.1 (64-bit)
//Tool Version Limit: 2026.06
//Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
//Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
//
//==============================================================
`ifndef CHOLESKY_INVERSE_ENV__SV                                                                                   
    `define CHOLESKY_INVERSE_ENV__SV                                                                               
                                                                                                                    
                                                                                                                    
    class cholesky_inverse_env extends uvm_env;                                                                          
                                                                                                                    
        cholesky_inverse_virtual_sequencer cholesky_inverse_virtual_sqr;                                                      
        cholesky_inverse_config cholesky_inverse_cfg;                                                                         
                                                                                                                    
                                                                                                                    
        cholesky_inverse_reference_model   refm;                                                                         
                                                                                                                    
        cholesky_inverse_subsystem_monitor subsys_mon;                                                                   
                                                                                                                    
        `uvm_component_utils_begin(cholesky_inverse_env)                                                                 
        `uvm_field_object (refm, UVM_DEFAULT | UVM_REFERENCE)                                                       
        `uvm_field_object (cholesky_inverse_virtual_sqr, UVM_DEFAULT | UVM_REFERENCE)                                    
        `uvm_field_object (cholesky_inverse_cfg        , UVM_DEFAULT)                                                    
        `uvm_component_utils_end                                                                                    
                                                                                                                    
        function new (string name = "cholesky_inverse_env", uvm_component parent = null);                              
            super.new(name, parent);                                                                                
        endfunction                                                                                                 
                                                                                                                    
        extern virtual function void build_phase(uvm_phase phase);                                                  
        extern virtual function void connect_phase(uvm_phase phase);                                                
        extern virtual task          run_phase(uvm_phase phase);                                                    
                                                                                                                    
    endclass                                                                                                        
                                                                                                                    
    function void cholesky_inverse_env::build_phase(uvm_phase phase);                                                    
        super.build_phase(phase);                                                                                   
        cholesky_inverse_cfg = cholesky_inverse_config::type_id::create("cholesky_inverse_cfg", this);                           
                                                                                                                    



        refm = cholesky_inverse_reference_model::type_id::create("refm", this);


        uvm_config_db#(cholesky_inverse_reference_model)::set(this, "*", "refm", refm);


        `uvm_info(this.get_full_name(), "set reference model by uvm_config_db", UVM_LOW)


        subsys_mon = cholesky_inverse_subsystem_monitor::type_id::create("subsys_mon", this);


        cholesky_inverse_virtual_sqr = cholesky_inverse_virtual_sequencer::type_id::create("cholesky_inverse_virtual_sqr", this);
        `uvm_info(this.get_full_name(), "build_phase done", UVM_LOW)
    endfunction


    function void cholesky_inverse_env::connect_phase(uvm_phase phase);
        super.connect_phase(phase);


        refm.cholesky_inverse_cfg = cholesky_inverse_cfg;
        `uvm_info(this.get_full_name(), "connect phase done", UVM_LOW)
    endfunction


    task cholesky_inverse_env::run_phase(uvm_phase phase);
        `uvm_info(this.get_full_name(), "cholesky_inverse_env is running", UVM_LOW)
    endtask


`endif
