module ps2_sb_ctrl(
    input  logic        clk_i,
    input  logic        rst_i,
    input  logic [31:0] addr_i,
    input  logic        req_i,
    input  logic [31:0] write_data_i,
    input  logic        write_enable_i,
    output logic [31:0] read_data_o,

    output logic        interrupt_request_o,
    input  logic        interrupt_return_i,

    input  logic        kclk_i,
    input  logic        kdata_i
);

logic [7:0] scan_code;
logic       scan_code_is_unread;

logic [7:0] keycode;
logic       keycode_valid;

logic read_req;
logic write_req;
logic reset_req;

assign read_req  = req_i && !write_enable_i;
assign write_req = req_i &&  write_enable_i;
assign reset_req = write_req && (addr_i == 32'h0000_0024) && write_data_i[0];

PS2Receiver ps2_receiver (
    .clk_i           (clk_i),
    .rst_i           (rst_i || reset_req),
    .kclk_i          (kclk_i),
    .kdata_i         (kdata_i),
    .keycodeout_o    (keycode),
    .keycode_valid_o (keycode_valid)
);

always_ff @(posedge clk_i) begin
    if (rst_i || reset_req) begin
        scan_code           <= 8'h00;
        scan_code_is_unread <= 1'b0;
        read_data_o         <= 32'h0000_0000;
    end
    else begin
        if (read_req) begin
            unique case (addr_i)
                32'h0000_0000: read_data_o <= {24'h000000, scan_code};
                32'h0000_0004: read_data_o <= {31'h00000000, scan_code_is_unread};
                default: ; // Unsupported reads keep previous read_data_o value.
            endcase
        end

        if (keycode_valid) begin
            scan_code           <= keycode;
            scan_code_is_unread <= 1'b1;
        end
        else if ((read_req && (addr_i == 32'h0000_0000)) || interrupt_return_i) begin
            scan_code_is_unread <= 1'b0;
        end
    end
end

assign interrupt_request_o = scan_code_is_unread;

endmodule
