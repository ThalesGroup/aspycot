// Author: Téo Biton, Thales
// Date: 29.10.2024
//
// Description: Toplevel of the jop_alarm detection unit
//              aimed at detecting jump-oriented programming
//              exploits. POC for aspycot.
//
// jop_alarm

module jop_alarm #(
  parameter int unsigned JopThreshold  = 100,
  parameter int unsigned StepUpValue   = 10,
  parameter int unsigned StepDownValue = 20
) (
  // Clock and Reset
  input  logic clk_i,
  input  logic rst_ni,

  // Execution stream data
  input  logic instr_valid_i,
  input  logic is_ind_jump_i,

  // Alarm sent on suspicious behavior
  output logic alarm_o
);

  localparam int unsigned CounterWidth = 32;

  logic [CounterWidth-1:0] cnt;
  logic [CounterWidth-1:0] cnt_step;

  logic cnt_inc, cnt_dec, cnt_en;

  // Counter is enabled for a valid instruction
  assign cnt_en = instr_valid_i;
  
  assign cnt_inc = cnt_en && is_ind_jump_i;
  assign cnt_dec = cnt_en && ~is_ind_jump_i;
  
  assign cnt_step = (cnt_inc) ? StepUpValue
                              : StepDownValue;

  // Control Flow Counter
  counter #(
    .Width      ( CounterWidth ),
    .ResetValue ( '0           )
  ) u_count (
    .clk_i,
    .rst_ni,
    .incr_en_i ( cnt_inc  ),
    .decr_en_i ( cnt_dec  ),
    .step_i    ( cnt_step ),
    .cnt_o     ( cnt      )
  );

  assign alarm_o = (cnt > JopThreshold);

endmodule
