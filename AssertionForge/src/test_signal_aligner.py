import json
import os
import sys

EXPECTED_MAPPINGS = {
    "write enable": ("WE_N", True),
    "system reset": ("nRST", True),
    "chip select": ("SS_N", True),
    "transmit acknowledge": ("tx_ack_flag", None),
    "FIFO empty status": ("TX_FIFO_MT", None),
    "data valid": ("dv_out", None),
    "slave address": ("SLV_ADDR_REG", None),
    "interrupt request": ("IRQ_OUT", None),
    "parity error": ("par_err_latch", None),
    "baud rate divisor": ("BAUD_DIV_REG", None),
    "transmission complete": ("tx_done_pulse", None),
    "flow control enable": ("fc_en", None),
    "receive buffer full": ("RX_BUF_FULL_N", True)
}

def main():
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = "output/toy_sdc_controller/toy_sdc_controller_signal_aliases.json"
        
    if not os.path.exists(json_file):
        print(f"File not found: {json_file}")
        return

    with open(json_file, 'r') as f:
        data = json.load(f)

    alignments = data.get("alignments", [])
    
    correct = 0
    wrong = []
    missing = []
    
    conf_sum = 0
    conf_count = 0
    
    rtl_to_align = {a["rtl_name"]: a for a in alignments}
    
    # Check expected
    for spec_mnt, (expected_rtl, exp_al) in EXPECTED_MAPPINGS.items():
        found = False
        for a in alignments:
            if spec_mnt.lower() in [m.lower() for m in a.get("spec_mentions", [])]:
                if a["rtl_name"] == expected_rtl:
                    correct += 1
                    if exp_al is not None and a.get("active_low") != exp_al:
                        wrong.append(f"{spec_mnt} mapped to {expected_rtl} but active_low={a.get('active_low')} instead of {exp_al}")
                    found = True
                else:
                    wrong.append(f"{spec_mnt} mapped to {a['rtl_name']}, expected {expected_rtl}")
                    found = True
                break
        if not found:
            # Maybe the spec mention is a bit modified
            missing.append(f"{spec_mnt} -> {expected_rtl}")
            
    for a in alignments:
        if a.get("confidence", 0) > 0:
            conf_sum += a.get("confidence", 0)
            conf_count += 1
            
    unresolved = [a for a in alignments if a.get("confidence", 0) < 0.7]
    
    print(f"Correct mappings: {correct}/{len(EXPECTED_MAPPINGS)}")
    if wrong:
        print("Wrong mappings:")
        for w in wrong:
            print("  -", w)
    if missing:
        print("Missing mappings:")
        for m in missing:
            print("  -", m)
            
    if conf_count > 0:
        print(f"Average confidence: {conf_sum/conf_count:.2f}")
        
    if unresolved:
        print("Unresolved signals:")
        for u in unresolved:
            print(f"  - {u['rtl_name']}")

if __name__ == "__main__":
    main()
