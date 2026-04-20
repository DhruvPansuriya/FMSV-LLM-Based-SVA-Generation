// Module: sdc_top (Serial Data Controller)
// Tests signal alignment: spec names vs RTL names differ deliberately.

module sdc_top (
    input  wire        nRST,     
    input  wire        PCLK,      
    input  wire        PSEL,      
    input  wire        PENABLE,  
    input  wire        PWRITE,   
    input  wire [7:0]  PADDR,    
    input  wire [31:0] PWDATA,    
    output reg  [31:0] PRDATA,   
    output wire        PREADY,    
    output wire        SCK,       
    output wire        MOSI,    
    input  wire        MISO,     
    output reg         SS_N,      
    output reg         IRQ_OUT,   
    output wire        WE_N       
);

    localparam ADDR_CTRL   = 8'h00;
    localparam ADDR_BAUD   = 8'h04;
    localparam ADDR_STATUS = 8'h08;

    reg [15:0] BAUD_DIV_REG;   
    reg [7:0]  CTRL_REG;
    reg        tx_ack_flag;    
    reg        par_err_latch;  

    wire       TX_FIFO_MT;     
    wire       dv_out;        
    wire       tx_done_pulse;  
    wire       RX_BUF_FULL_N;  
    wire       fc_en;         

    assign WE_N   = ~(PSEL & PENABLE & PWRITE);
    assign PREADY = 1'b1;
    assign fc_en  = CTRL_REG[3];

    sdc_tx u_tx (
        .clk(PCLK), .rst_n(nRST), .baud_div(BAUD_DIV_REG),
        .tx_data(PWDATA[7:0]), .tx_start(CTRL_REG[0]), .fc_en(fc_en),
        .sck_out(SCK), .mosi_out(MOSI),
        .tx_done(tx_done_pulse), .fifo_empty(TX_FIFO_MT), .ack_flag(tx_ack_flag)
    );

    sdc_rx u_rx (
        .clk(PCLK), .rst_n(nRST), .miso_in(MISO), .sck_in(SCK),
        .dv(dv_out), .par_err(par_err_latch),
        .buf_full_n(RX_BUF_FULL_N), .rx_data(PRDATA[7:0])
    );

    always @(posedge PCLK or negedge nRST) begin
        if (!nRST) begin
            BAUD_DIV_REG <= 16'h0; CTRL_REG <= 8'h0; SS_N <= 1'b1;
        end else if (!WE_N) begin
            case (PADDR)
                ADDR_CTRL: CTRL_REG     <= PWDATA[7:0];
                ADDR_BAUD: BAUD_DIV_REG <= PWDATA[15:0];
                default: ;
            endcase
            SS_N <= 1'b0;
        end
    end

    always @(*) begin
        case (PADDR)
            ADDR_CTRL:   PRDATA = {24'h0, CTRL_REG};
            ADDR_BAUD:   PRDATA = {16'h0, BAUD_DIV_REG};
            ADDR_STATUS: PRDATA = {24'h0, RX_BUF_FULL_N, TX_FIFO_MT,
                                   tx_ack_flag, par_err_latch,
                                   dv_out, tx_done_pulse, fc_en, 1'b0};
            default:     PRDATA = 32'h0;
        endcase
    end

    always @(posedge PCLK or negedge nRST) begin
        if (!nRST) IRQ_OUT <= 1'b0;
        else       IRQ_OUT <= tx_done_pulse | par_err_latch;
    end

endmodule


module sdc_tx (
    input  wire        clk, rst_n, tx_start, fc_en,
    input  wire [15:0] baud_div,
    input  wire [7:0]  tx_data,
    output wire        sck_out, mosi_out, tx_done, fifo_empty,
    output reg         ack_flag
);
    reg [15:0] baud_cnt;
    reg [3:0]  bit_cnt;
    reg [7:0]  shift_reg;
    reg        sck_r, active;

    assign fifo_empty = ~active & ~tx_start;
    assign sck_out    = sck_r & active;
    assign mosi_out   = shift_reg[7];
    assign tx_done    = (bit_cnt == 4'd8) & active;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            baud_cnt <= 0; bit_cnt <= 0; shift_reg <= 0;
            sck_r <= 0; active <= 0; ack_flag <= 0;
        end else if (!active && tx_start && !fc_en) begin
            active <= 1; shift_reg <= tx_data; bit_cnt <= 0; baud_cnt <= 0;
        end else if (active) begin
            if (baud_cnt == baud_div) begin
                baud_cnt <= 0; sck_r <= ~sck_r;
                if (sck_r) begin
                    shift_reg <= {shift_reg[6:0], 1'b0};
                    bit_cnt   <= bit_cnt + 1;
                end
                if (bit_cnt == 4'd8) begin active <= 0; ack_flag <= 1; end
            end else baud_cnt <= baud_cnt + 1;
        end else ack_flag <= 0;
    end
endmodule


module sdc_rx (
    input  wire       clk, rst_n, miso_in, sck_in,
    output reg        dv, par_err,
    output wire       buf_full_n,
    output reg [7:0]  rx_data
);
    reg [7:0] sr;
    reg [3:0] cnt;
    reg       full;

    assign buf_full_n = ~full;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sr <= 0; cnt <= 0; rx_data <= 0; dv <= 0; par_err <= 0; full <= 0;
        end else if (sck_in) begin
            sr  <= {sr[6:0], miso_in};
            cnt <= cnt + 1;
            if (cnt == 4'd7) begin
                rx_data <= {sr[6:0], miso_in};
                dv      <= 1; full <= 1;
                par_err <= ^{sr[6:0], miso_in};
                cnt     <= 0;
            end
        end else begin dv <= 0; full <= 0; end
    end
endmodule