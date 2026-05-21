module hex_sb_ctrl(
    input  logic        clk_i,
    input  logic        rst_i,
    input  logic [31:0] addr_i,
    input  logic        req_i,
    input  logic [31:0] write_data_i,
    input  logic        write_enable_i,
    output logic [31:0] read_data_o,

    output logic [6:0]  hex_led,
    output logic [7:0]  hex_sel
);

logic [3:0] hex0, hex1, hex2, hex3, hex4, hex5, hex6, hex7;
logic [7:0] bitmask;

logic read_req;
logic write_req;
logic reset_req;
logic ctrl_rst;

assign read_req  = req_i && !write_enable_i;
assign write_req = req_i &&  write_enable_i;
assign reset_req = write_req && (addr_i == 32'h0000_0024) && write_data_i[0];
assign ctrl_rst  = rst_i || reset_req;

hex_digits hex_digits_unit (
    .clk_i     (clk_i),
    .rst_i     (ctrl_rst),
    .hex0_i    (hex0),
    .hex1_i    (hex1),
    .hex2_i    (hex2),
    .hex3_i    (hex3),
    .hex4_i    (hex4),
    .hex5_i    (hex5),
    .hex6_i    (hex6),
    .hex7_i    (hex7),
    .bitmask_i (bitmask),
    .hex_led_o (hex_led),
    .hex_sel_o (hex_sel)
);

always_ff @(posedge clk_i) begin
    if (ctrl_rst) begin
        hex0      <= 4'h0;
        hex1      <= 4'h0;
        hex2      <= 4'h0;
        hex3      <= 4'h0;
        hex4      <= 4'h0;
        hex5      <= 4'h0;
        hex6      <= 4'h0;
        hex7      <= 4'h0;
        bitmask   <= 8'hFF;
        read_data_o <= 32'h0000_0000;
    end
    else begin
        if (write_req) begin
            unique case (addr_i)
                32'h0000_0000: hex0    <= write_data_i[3:0];
                32'h0000_0004: hex1    <= write_data_i[3:0];
                32'h0000_0008: hex2    <= write_data_i[3:0];
                32'h0000_000C: hex3    <= write_data_i[3:0];
                32'h0000_0010: hex4    <= write_data_i[3:0];
                32'h0000_0014: hex5    <= write_data_i[3:0];
                32'h0000_0018: hex6    <= write_data_i[3:0];
                32'h0000_001C: hex7    <= write_data_i[3:0];
                32'h0000_0020: bitmask <= write_data_i[7:0];
                default: ; // Unsupported writes are ignored.
            endcase
        end

        if (read_req) begin
            unique case (addr_i)
                32'h0000_0000: read_data_o <= {28'h0000000, hex0};
                32'h0000_0004: read_data_o <= {28'h0000000, hex1};
                32'h0000_0008: read_data_o <= {28'h0000000, hex2};
                32'h0000_000C: read_data_o <= {28'h0000000, hex3};
                32'h0000_0010: read_data_o <= {28'h0000000, hex4};
                32'h0000_0014: read_data_o <= {28'h0000000, hex5};
                32'h0000_0018: read_data_o <= {28'h0000000, hex6};
                32'h0000_001C: read_data_o <= {28'h0000000, hex7};
                32'h0000_0020: read_data_o <= {24'h000000, bitmask};
                default: ; // Unsupported reads keep previous read_data_o value.
            endcase
        end
    end
end

endmodule
