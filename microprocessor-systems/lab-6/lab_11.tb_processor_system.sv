/* -----------------------------------------------------------------------------
* Project Name   : Architectures of Processor Systems (APS) lab work
* Organization   : National Research University of Electronic Technology (MIET)
* Department     : Institute of Microdevices and Control Systems
* Author(s)      : Andrei Solodovnikov
* Email(s)       : hepoh@org.miet.ru
* ------------------------------------------------------------------------------
*/
module lab_11_tb_processor_system();

    reg clk;
    reg rst;
    reg irq_req;
    wire irq_ret;

    processor_system DUT(
    .clk_i(clk),
    .rst_i(rst),
    .irq_req_i(irq_req),
    .irq_ret_o(irq_ret)
    );

    initial begin
      repeat(5000) begin
        @(posedge clk);
      end
      $display("Test has been interrupted by watchdog timer");
      $finish;
    end

    initial clk = 0;
    always #10 clk = ~clk;

    // Мониторинг важных сигналов
    always @(posedge clk) begin
      if (!rst)
        $display("Time=%0t PC=%h Instr=%h MIE=%b MIE_REG=%h Trap=%b IRQ_RET=%b",
                 $time, DUT.core.instr_addr_o, DUT.core.instr_i, DUT.core.mstatus_mie, DUT.core.mie_reg, DUT.core.trap, irq_ret);
    end
    initial begin
        $dumpfile("wave.vcd");
        $dumpvars(0, lab_11_tb_processor_system);
        $display( "\nTest has been started");
        irq_req = 0;
        rst = 1;
        #40;
        rst = 0;

        // Даем программе время на инициализацию CSR (MTVEC, MIE)
        repeat(200)@(posedge clk);

        $display("Requesting interrupt...");
        irq_req = 1;

        // Ждем возврата из прерывания
        fork
          begin
            while(irq_ret !== 1) @(posedge clk);
            $display("Interrupt acknowledged (irq_ret observed)");
          end
          begin
            repeat(1000) @(posedge clk);
            if (irq_ret !== 1) $display("Timeout waiting for irq_ret!");
          end
        join_any

        irq_req = 0;
        repeat(100)@(posedge clk);
        $display("\n The test is over \n See the internal signals of the module on the waveform \n");
        $finish;
    end

endmodule
