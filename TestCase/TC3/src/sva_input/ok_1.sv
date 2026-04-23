assert property (@(posedge pclk) disable iff (!nrst) psel |-> penable);
