// -----------------------------------------------------------------------------
// Module: apb_slave
// Description: A fully functional APB4 Slave with memory-mapped registers.
//              Supports read/write operations, wait states (PREADY), and error response (PSLVERR).
// -----------------------------------------------------------------------------

module apb_slave #(
  parameter ADDR_WIDTH = 32,
  parameter DATA_WIDTH = 32
)(
  input  wire                    PCLK,    // Clock
  input  wire                    PRESETn, // Active-low Reset
  input  wire [ADDR_WIDTH-1:0]   PADDR,   // Address Bus
  input  wire                    PSEL,    // Select Signal
  input  wire                    PENABLE, // Enable Signal
  input  wire                    PWRITE,  // Write Control (1=Write, 0=Read)
  input  wire [DATA_WIDTH-1:0]   PWDATA,  // Write Data Bus
  output reg  [DATA_WIDTH-1:0]   PRDATA,  // Read Data Bus
  output reg                     PREADY,  // Ready Signal (Wait states)
  output reg                     PSLVERR  // Slave Error Signal
);

  // Internal memory (16 registers of 32-bits)
  reg [DATA_WIDTH-1:0] mem [0:15];
  
  // State machine for wait state injection (for demonstration)
  // STATE_IDLE: 0, STATE_ACCESS: 1
  reg state;
  localparam IDLE = 1'b0, ACCESS = 1'b1;

  // ---------------------------------------------------------------------------
  // APB Protocol Logic
  // ---------------------------------------------------------------------------
  always @(posedge PCLK or negedge PRESETn) begin
    if (!PRESETn) begin
      PREADY  <= 1'b0;
      PSLVERR <= 1'b0;
      PRDATA  <= {DATA_WIDTH{1'b0}};
      state   <= IDLE;
      // Reset memory initialization (optional)
      mem[0] <= 32'hDEADBEEF; 
      mem[1] <= 32'hCAFEBABE;
    end else begin
      
      // Default outputs
      PSLVERR <= 1'b0; 

      case (state)
        IDLE: begin
          if (PSEL && !PENABLE) begin
            // Setup Phase detected, move to Access Phase next cycle
            state   <= ACCESS;
            PREADY  <= 1'b0; // Inject 1 wait cycle for fun
          end else begin
            PREADY <= 1'b1;
          end
        end

        ACCESS: begin
           // Access Phase
           if (PSEL && PENABLE) begin
             PREADY <= 1'b1; // Ready to complete transfer
             
             // Check address range (simulation of error for out-of-bound access)
             if (PADDR[31:6] != 0) begin // Assuming base address 0 for simplicity
                PSLVERR <= 1'b1; 
             end else begin
                PSLVERR <= 1'b0;
                
                // Read/Write Logic
                if (PWRITE) begin
                   // Write operation
                   mem[PADDR[5:2]] <= PWDATA; // Word aligned access
                end else begin
                   // Read operation
                   PRDATA <= mem[PADDR[5:2]];
                end
             end
             
             // Transfer completes, go back to IDLE
             state <= IDLE;
           end
        end
      endcase
    end
  end

endmodule
