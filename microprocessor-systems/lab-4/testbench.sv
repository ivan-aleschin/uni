`timescale 1ns/1ps

module testbench();

  logic        clk;
  logic        rstn;
  logic [15:0] sw_i;
  logic [31:0] out_o;

  // DUT
  CYBERcobra DUT (
    .clk_i(clk),
    .rst_i(rstn),
    .sw_i (sw_i),
    .out_o(out_o)
  );

  // Clock: 10 ns period
  initial clk = 1'b0;
  always #5 clk = ~clk;

  initial begin
    // Waveform dump
    $dumpfile("wave.vcd");
    $dumpvars(0, testbench);

    $display("Test has been started");
    rstn = 1'b1;
    sw_i = 16'b0;
    #10;

    rstn = 1'b0;
    sw_i = 16'b0000000000000010; // значение сдвига (k)

    #10000;
    $display("\n The test is over \n See the internal signals of the CYBERcobra on the waveform \n");
    $finish;
  end

endmodule
