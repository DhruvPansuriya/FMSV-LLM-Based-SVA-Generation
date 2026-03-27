// Dummy APB master/slave interface
module apb_slave (
    input  wire        pclk,
    input  wire        presetn,
    input  wire        psel,
    input  wire        penable,
    input  wire        pwrite,
    input  wire [31:0] paddr,
    input  wire [31:0] pwdata,
    output reg  [31:0] prdata,
    output wire        pready,
    output wire        pslverr
);

    // Simple register logic to make it valid Verilog
    reg [31:0] mem [0:31];
    
    always @(posedge pclk or negedge presetn) begin
        if (!presetn) begin
            prdata <= 32'h0;
        end else if (psel && penable && pwrite) begin
            mem[paddr[4:0]] <= pwdata;
        end else if (psel && !pwrite) begin
            prdata <= mem[paddr[4:0]];
        end
    end

    assign pready  = 1'b1; // Always ready
    assign pslverr = 1'b0; // No errors

endmodule
