// Author: Téo Biton, Thales
// Date: 08.12.2023
//
// Description: Basic counter that can be both incremented
//              and decremented.
//
// counter

module counter #(
  parameter int unsigned Width = 8,
  parameter logic [Width-1:0] ResetValue = {Width{1'b0}}
) (
  // Clock and Reset
  input  logic             clk_i,
  input  logic             rst_ni,

  // Control logic
  input  logic             incr_en_i,
  input  logic             decr_en_i,
  input  logic [Width-1:0] step_i,

  // Current counter state
  output logic [Width-1:0] cnt_o
);

  logic [Width-1:0] cnt_d, cnt_q;

  logic             incr_en, decr_en;
  logic [Width:0]   ext_cnt;
  logic             uflow, oflow;
  logic [Width-1:0] cnt_sat;
  logic             cnt_en;
  logic             cnt_min, cnt_max;

  assign incr_en = incr_en_i;
  assign decr_en = decr_en_i;

  // Main counter logic
  assign ext_cnt = (decr_en) ? {1'b0, cnt_q} - {1'b0, step_i} :
                   (incr_en) ? {1'b0, cnt_q} + {1'b0, step_i} :
                               {1'b0, cnt_q};

  // Saturation logic
  assign oflow = incr_en && ext_cnt[Width];
  assign uflow = decr_en && ext_cnt[Width];

  assign cnt_sat = (uflow) ? '0            :
                   (oflow) ? {Width{1'b1}} : ext_cnt[Width-1:0];

  assign cnt_max = incr_en && !(&cnt_q);
  assign cnt_min = decr_en && !(cnt_q == '0);

  // Clock gate flops when in saturation, and do not
  // count if both incr_en and decr_en are asserted.
  assign cnt_en = (incr_en ^ decr_en) && (cnt_max || cnt_min);

  assign cnt_d = (cnt_en) ? cnt_sat : cnt_q;

  always_ff @(posedge clk_i or negedge rst_ni) begin : cnt_reg
    if (!rst_ni) begin
      cnt_q <= ResetValue;
    end else begin
      cnt_q <= cnt_d;
    end
  end

  // Output count values
  assign cnt_o = cnt_q;

endmodule
