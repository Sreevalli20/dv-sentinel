"""Intelligent response generator for DV Sentinel - Domain-specific technical responses."""

from typing import Dict, List, Optional
from .intent_engine import IntentEngine


class ResponseGenerator:
    """Generates technically accurate, domain-specific responses."""
    
    @staticmethod
    def generate_response(domain: str, sub_intent: str, metadata: Dict, text: str) -> str:
        """Generate a domain-specific response.
        
        Args:
            domain: Detected domain
            sub_intent: Detected sub-intent
            metadata: Extracted metadata
            text: Original user text
            
        Returns:
            Formatted response
        """
        if domain == "fifo":
            return ResponseGenerator._generate_fifo_response(sub_intent, metadata, text)
        elif domain == "axi":
            return ResponseGenerator._generate_axi_response(sub_intent, metadata, text)
        elif domain == "apb":
            return ResponseGenerator._generate_apb_response(sub_intent, metadata, text)
        elif domain == "sva":
            return ResponseGenerator._generate_sva_response(sub_intent, metadata, text)
        elif domain == "coverage":
            return ResponseGenerator._generate_coverage_response(sub_intent, metadata, text)
        elif domain == "debugging":
            return ResponseGenerator._generate_debugging_response(sub_intent, metadata, text)
        elif domain == "testplan":
            return ResponseGenerator._generate_testplan_response(sub_intent, metadata, text)
        elif domain == "reset":
            return ResponseGenerator._generate_reset_response(sub_intent, metadata, text)
        elif domain == "cdc":
            return ResponseGenerator._generate_cdc_response(sub_intent, metadata, text)
        elif domain == "uvm":
            return ResponseGenerator._generate_uvm_response(sub_intent, metadata, text)
        elif domain == "scoreboard":
            return ResponseGenerator._generate_scoreboard_response(sub_intent, metadata, text)
        elif domain == "constrained_random":
            return ResponseGenerator._generate_constrained_random_response(sub_intent, metadata, text)
        elif domain == "regression":
            return ResponseGenerator._generate_regression_response(sub_intent, metadata, text)
        
        return ResponseGenerator._generate_fallback_response(text)
    
    @staticmethod
    def _generate_fifo_response(sub_intent: str, metadata: Dict, text: str) -> str:
        """Generate FIFO-specific response."""
        
        if sub_intent == "pointer_wraparound":
            # Extract numbers if present
            import re
            depth_match = re.search(r'depth\s*(\d+)', text.lower())
            bits_match = re.search(r'(\d+)\s*bits?', text.lower())
            
            depth = int(depth_match.group(1)) if depth_match else 16
            bits = int(bits_match.group(1)) if bits_match else 4
            
            return ResponseGenerator._format_structured_response(
                direct_answer=f"""4 bits represent addresses 0..{depth-1}. The address wraps from {depth-1} back to 0. Equal 4-bit pointers are ambiguous - they can mean empty OR one complete FIFO-depth separation (full). Therefore 4-bit pointers alone cannot distinguish full from empty.""",
                why="""When write and read pointers are equal, it could mean the FIFO is empty (both at same address with no data) OR full (write pointer has wrapped around exactly once and caught up to read pointer). With only 4 bits, both conditions produce identical pointer values.""",
                verification_approach="""Use extended pointers with a phase/wrap bit. With a 5-bit pointer: lower 4 bits = memory address, upper bit = wrap/phase. Equal full pointers = empty. Same address + opposite phase = full. Alternatively, use an occupancy counter.""",
                example="""// SVA for full/empty distinction with phase bit
assert property (@(posedge clk)
    (wr_ptr[4] == rd_ptr[4]) |-> (wr_ptr[3:0] == rd_ptr[3:0]) ? empty : full);

// Coverage for wraparound
covergroup fifo_wraparound;
    coverpoint wr_ptr[3:0] {{
        bins wrap = (15, 0);
    }}
endgroup""",
                key_takeaway="Pointer wraparound ambiguity requires additional state (phase bit or occupancy counter) to distinguish full from empty."
            )
        
        elif sub_intent == "depth_width":
            return ResponseGenerator._format_structured_response(
                direct_answer="Pointer width = log2(FIFO depth). For depth 16, you need 4 bits (2^4 = 16). Address bits must match pointer width.",
                why="Each pointer value corresponds to a unique memory location. With N bits, you can address 2^N locations. The pointer width determines the maximum addressable depth.",
                verification_approach="Verify pointer width matches memory depth. Check that pointer overflow doesn't cause address aliasing. Add coverage for all pointer values.",
                example="// Pointer width assertion\nassert property (@(posedge clk)\n    wr_ptr < DEPTH);\n\n// Coverage for pointer values\ncovergroup ptr_values;\n    coverpoint wr_ptr {{\n        bins all_values = {{[0:DEPTH-1]}};\n    }}\nendgroup",
                key_takeaway="Pointer width must be log2(depth) to uniquely address all FIFO locations."
            )
        
        elif sub_intent == "full_empty_distinction":
            return ResponseGenerator._format_structured_response(
                direct_answer="Full and empty both have equal read/write pointers. Distinguish them using: (1) Phase/wrap bit on pointers, (2) Occupancy counter, or (3) Almost-full/almost-empty flags.",
                why="When pointers are equal, you need additional state to know if the FIFO is empty (no data) or full (wrapped around). The phase bit tracks whether the write pointer has wrapped more times than the read pointer.",
                verification_approach="Add assertions that full and empty are never true simultaneously. Verify occupancy counter matches pointer difference. Cover the transition from almost-full to full and almost-empty to empty.",
                example="// Phase bit approach\nassign empty = (wr_ptr == rd_ptr) && (wr_phase == rd_phase);\nassign full = (wr_ptr == rd_ptr) && (wr_phase != rd_phase);\n\n// Assertion\nassert property (@(posedge clk) !(empty && full));",
                key_takeaway="Equal pointers are ambiguous - use phase bit or occupancy counter to resolve full vs empty."
            )
        
        elif sub_intent == "overflow_underflow":
            return ResponseGenerator._format_structured_response(
                direct_answer="Overflow = writing when full. Underflow = reading when empty. Both are functional errors that corrupt data or return invalid data.",
                why="Overflow overwrites unread data, causing data loss. Underflow reads invalid data, potentially propagating errors downstream. Both violate FIFO contract.",
                verification_approach="Add assertions: full |-> !wr_en and empty |-> !rd_en. Inject negative tests attempting overflow/underflow. Verify error handling or flag generation.",
                example="// Overflow/underflow assertions\nassert property (@(posedge clk)\n    full |-> !wr_en) else $error(\"FIFO overflow\");\n\nassert property (@(posedge clk)\n    empty |-> !rd_en) else $error(\"FIFO underflow\");",
                key_takeaway="Overflow and underflow must be prevented by design and verified with assertions."
            )
        
        elif sub_intent == "async_fifo":
            return ResponseGenerator._format_structured_response(
                direct_answer="Asynchronous FIFO uses Gray code for pointers crossing clock domains. Gray code ensures only one bit changes per increment, minimizing metastability risk.",
                why="Binary pointers can have multiple bits change simultaneously (e.g., 7->8: 0111->1000). When crossing clock domains, this can cause metastable intermediate values. Gray code's single-bit change property makes synchronization safer.",
                verification_approach="Verify Gray encoding/decoding logic. Add CDC checks with synchronizer stages. Cover all Gray code transitions. Verify pointer synchronization depth (typically 2-3 flip-flops).",
                example="// Gray code conversion\nfunction [3:0] bin2gray(input [3:0] bin);\n    bin2gray = bin ^ (bin >> 1);\nendfunction\n\n// Synchronizer stages\nalways @(posedge rd_clk) begin\n    sync1 <= sync2;\n    sync2 <= wr_ptr_gray;\n    wr_ptr_gray_sync <= sync1;\nend",
                key_takeaway="Gray code is essential for async FIFO pointers to safely cross clock domains."
            )
        
        elif sub_intent == "gray_code":
            return ResponseGenerator._format_structured_response(
                direct_answer="Gray code is a binary encoding where only one bit changes between consecutive values. Used in CDC to minimize metastability risk.",
                why="When crossing clock domains, multiple simultaneous bit changes can cause metastable intermediate values. Gray code's single-bit change property ensures synchronized values are always valid (either old or new, never corrupted).",
                verification_approach="Verify Gray code conversion logic (bin ^ (bin >> 1)). Add coverage for all Gray code transitions. Check that synchronized pointers don't skip values.",
                example="// Gray code coverage\ncovergroup gray_transitions;\n    coverpoint gray_ptr {{\n        bins transitions[] = (0 => 1 => 3 => 2 => 6 => 7 => 5 => 4 => 12 => 13 => 15 => 14 => 10 => 11 => 9 => 8 => 0);\n    }}\nendgroup",
                key_takeaway="Gray code's single-bit change property makes it ideal for clock domain crossing."
            )
        
        # Generic FIFO response
        return ResponseGenerator._format_structured_response(
            direct_answer="I understand this as a FIFO question. Common FIFO concerns include: pointer management, full/empty detection, overflow/underflow prevention, reset behavior, and clock domain crossing.",
            why="FIFOs are fundamental buffering structures with specific verification challenges around pointer wraparound, flag generation, and data integrity.",
            verification_approach="Add assertions for: no read when empty, no write when full, data integrity, reset clears pointers. Cover: empty/full states, simultaneous read/write, pointer wraparound, reset scenarios.",
            example="// Key FIFO assertions\nassert property (@(posedge clk) empty |-> !rd_en);\nassert property (@(posedge clk) full |-> !wr_en);\nassert property (@(posedge clk) reset |-> ##1 (rd_ptr == 0 && wr_ptr == 0));",
            key_takeaway="FIFO verification requires comprehensive coverage of pointer behavior, flag accuracy, and boundary conditions."
        )
    
    @staticmethod
    def _generate_axi_response(sub_intent: str, metadata: Dict, text: str) -> str:
        """Generate AXI-specific response."""
        
        if sub_intent == "deadlock":
            return ResponseGenerator._format_structured_response(
                direct_answer="AWVALID asserted but AWREADY low is NOT a protocol violation. The master may keep AWVALID asserted until handshake. Deadlock occurs if AWREADY is never asserted or if VALID is dropped before READY.",
                why="AXI protocol allows VALID to wait indefinitely for READY. The master should keep VALID asserted until handshake completes. Deadlock happens when: (1) Slave never asserts READY, (2) Master drops VALID before READY, (3) Response channel blocked.",
                verification_approach="Check which handshake stopped. Verify AWVALID persistence. Check AWREADY assertion logic. Inspect outstanding transaction state. Verify IDs and ordering rules. Check reset.",
                example="// AWVALID persistence check\nassert property (@(posedge clk)\n    $rose(awvalid) |-> awvalid throughout !awready);\n\n// Eventual progress assumption\nassert property (@(posedge clk)\n    awvalid |-> ##[1:100] awready);",
                key_takeaway="VALID waiting for READY is normal - deadlock occurs when READY never comes or VALID is dropped prematurely."
            )
        
        elif sub_intent == "backpressure":
            return ResponseGenerator._format_structured_response(
                direct_answer="Backpressure is when READY is deasserted, causing the master to wait. This is normal AXI behavior for flow control. The master must keep VALID asserted until handshake.",
                why="Slaves use backpressure to manage internal resources (FIFO full, processing busy). The protocol requires VALID to remain stable while waiting for READY. Dropping VALID before READY violates the handshake protocol.",
                verification_approach="Verify payload stability while VALID && !READY. Check that VALID persists until handshake. Cover backpressure on all channels. Verify no deadlock from backpressure.",
                example="// Payload stability during backpressure\nassert property (@(posedge clk)\n    awvalid && !awready |-> $stable(awaddr));\n\n// Backpressure coverage\ncovergroup axi_backpressure;\n    coverpoint awready {{\n        bins backpressure = {{0}};\n    }}\nendgroup",
                key_takeaway="Backpressure is normal flow control - verify payload stability and VALID persistence."
            )
        
        elif sub_intent == "outstanding":
            return ResponseGenerator._format_structured_response(
                direct_answer="Outstanding transactions are transactions issued but not yet completed. AXI supports multiple outstanding transactions using IDs for reordering. Verification must track ID matching and ordering rules.",
                why="Outstanding transactions improve throughput by allowing pipelining. Each transaction has an ID for response matching. Write and read channels are independent. Ordering rules: same ID must maintain order, different IDs can complete out-of-order.",
                verification_approach="Track outstanding transaction count per ID. Verify response ID matches request ID. Check ordering rules for same ID. Cover maximum outstanding transactions. Verify no ID exhaustion.",
                example="// Outstanding transaction tracking\nint outstanding_count = 0;\nalways @(posedge clk) begin\n    if (awvalid && awready) outstanding_count <= outstanding_count + 1;\n    if (bvalid && bready) outstanding_count <= outstanding_count - 1;\nend\n\n// ID matching assertion\nassert property (@(posedge clk)\n    bvalid |-> $past(awid, outstanding_count) == bid);",
                key_takeaway="Track outstanding transactions by ID, verify response matching, and enforce ordering rules."
            )
        
        elif sub_intent == "burst":
            return ResponseGenerator._format_structured_response(
                direct_answer="AXI bursts transfer multiple data beats with a single address. Burst length (LEN) specifies beat count. Burst type (FIXED, INCR, WRAP) determines address calculation. 4KB boundary crossing may require special handling.",
                why="Bursts improve efficiency by reducing address overhead. The master provides start address + length + size. The slave calculates subsequent addresses. WRAP bursts wrap at address-aligned boundaries. INCR increments normally.",
                verification_approach="Verify burst length matches data beats. Check address calculation for each burst type. Cover 4KB boundary crossing. Verify burst size alignment. Check write strobes for partial beats.",
                example="// Burst address calculation\nalways @(posedge clk) begin\n    case (burst_type)\n        INCR: addr <= addr + size;\n        WRAP: addr <= (addr & ~((1<<size)-1)) | ((addr + size) & ((1<<size)-1));\n    endcase\nend\n\n// Boundary crossing coverage\ncovergroup burst_4kb;\n    coverpoint addr[11:0] {{\n        bins boundary = {{4095, 0}};\n    }}\nendgroup",
                key_takeaway="Verify burst length, address calculation, boundary crossing, and alignment for AXI burst transactions."
            )
        
        elif sub_intent == "valid_ready":
            return ResponseGenerator._format_structured_response(
                direct_answer="VALID/READY is a handshake protocol. Transaction occurs when both are asserted. VALID must remain stable until handshake. READY can be asserted/deasserted by slave. Master may keep VALID asserted until handshake.",
                why="The handshake ensures both sides are ready. VALID indicates data is valid. READY indicates receiver can accept. The protocol allows flexibility: VALID before READY, READY before VALID, or both same cycle. Payload must be stable once VALID is asserted.",
                verification_approach="Verify payload stability while VALID && !READY. Check handshake completion. Cover all timing combinations. Verify no deadlock. Check reset clears channels.",
                example="// Handshake assertion\nassert property (@(posedge clk)\n    awvalid |-> ##[0:$] awready);\n\n// Stability assertion\nassert property (@(posedge clk)\n    awvalid && !awready |-> $stable(awaddr));",
                key_takeaway="VALID/READY handshake requires payload stability and eventual completion - verify both."
            )
        
        # Generic AXI response
        return ResponseGenerator._format_structured_response(
            direct_answer="I understand this as an AXI protocol question. AXI has 5 channels (AW, W, B, AR, R) with VALID/READY handshakes. Key concerns: deadlock, backpressure, outstanding transactions, bursts, and ordering.",
            why="AXI is a high-performance protocol with independent channels, out-of-order completion, and complex ordering rules. Verification requires checking each channel's handshake protocol.",
            verification_approach="Add assertions for: VALID waits for READY, payload stability, response consumption, reset clears channels. Cover: backpressure, burst lengths, outstanding transactions, response types, reset scenarios.",
            example="// Key AXI assertions\nassert property (@(posedge clk) awvalid |-> ##[0:$] awready);\nassert property (@(posedge clk) awvalid && !awready |-> $stable(awaddr));\nassert property (@(posedge clk) !aresetn |-> ##1 (!awvalid && !wvalid && !arvalid));",
            key_takeaway="AXI verification requires comprehensive coverage of handshake protocol, payload stability, and ordering rules."
        )
    
    @staticmethod
    def _generate_apb_response(sub_intent: str, metadata: Dict, text: str) -> str:
        """Generate APB-specific response."""
        
        if sub_intent == "protocol_phases":
            return ResponseGenerator._format_structured_response(
                direct_answer="APB has three phases: IDLE (PSEL=0, PENABLE=0), SETUP (PSEL=1, PENABLE=0), and ACCESS (PSEL=1, PENABLE=1). PENABLE must NOT be high during SETUP phase. Transfer completes when PREADY is asserted.",
                why="The SETUP phase allows the slave to decode the address. The ACCESS phase performs the actual transfer. PENABLE timing is critical - it must only be asserted after one cycle of PSEL to distinguish the phases.",
                verification_approach="Add assertions for PENABLE timing (not asserted in SETUP). Verify address stability during ACCESS. Check PREADY completes transfer. Cover wait states and error responses.",
                example="// PENABLE timing assertion\nassert property (@(posedge clk)\n    psel && !penable |=> penable);\n\n// Address stability assertion\nassert property (@(posedge clk)\n    penable && !pready |-> $stable(paddr));",
                key_takeaway="PENABLE must follow PSEL with one cycle delay - never assert in SETUP phase."
            )
        
        elif sub_intent == "penable_timing":
            return ResponseGenerator._format_structured_response(
                direct_answer="PENABLE must be asserted one cycle after PSEL. In SETUP phase: PSEL=1, PENABLE=0. In ACCESS phase: PSEL=1, PENABLE=1. PENABLE must not be asserted without PSEL.",
                why="The two-cycle protocol (SETUP then ACCESS) gives the slave time to decode the address before the transfer begins. Asserting PENABLE too early violates the protocol and can cause transfer errors.",
                verification_approach="Assert PENABLE follows PSEL with one cycle delay. Verify PENABLE never asserted without PSEL. Check PENABLE deasserted after transfer. Cover all phase transitions.",
                example="// PENABLE timing assertion\nassert property (@(posedge clk)\n    psel && !penable |=> penable);\n\nassert property (@(posedge clk)\n    !psel |-> !penable);",
                key_takeaway="PENABLE timing is critical - must follow PSEL with exactly one cycle delay."
            )
        
        elif sub_intent == "wait_states":
            return ResponseGenerator._format_structured_response(
                direct_answer="Wait states occur when the slave keeps PREADY deasserted during ACCESS phase. The master must keep PSEL and PENABLE asserted until PREADY is asserted. Multiple wait states are allowed.",
                why="Slaves use wait states when they need more time to complete the transfer (e.g., slow peripheral, memory access). The protocol supports variable wait states by keeping PENABLE asserted until PREADY.",
                verification_approach="Verify PSEL and PENABLE remain asserted during wait states. Check PREADY eventually asserted. Cover various wait state counts. Verify address/data stability during wait states.",
                example="// Wait state assertion\nassert property (@(posedge clk)\n    penable |-> ##[0:$] pready);\n\n// Stability during wait states\nassert property (@(posedge clk)\n    penable && !pready |-> $stable(paddr));",
                key_takeaway="Wait states are normal - verify control signals remain stable until PREADY."
            )
        
        # Generic APB response
        return ResponseGenerator._format_structured_response(
            direct_answer="I understand this as an APB protocol question. APB is a simple peripheral bus with three phases: IDLE, SETUP, ACCESS. Key signals: PSEL, PENABLE, PREADY, PADDR, PWRITE, PWDATA, PRDATA, PSLVERR.",
            why="APB's simplicity makes it ideal for low-bandwidth peripherals. The two-phase protocol (SETUP then ACCESS) gives slaves time to decode addresses before transfers begin.",
            verification_approach="Add assertions for: PENABLE timing, address stability, PREADY completion. Cover: read/write, wait states, error responses, back-to-back transfers, reset scenarios.",
            example="// Key APB assertions\nassert property (@(posedge clk) psel && !penable |=> penable);\nassert property (@(posedge clk) penable |-> ##[0:$] pready);\nassert property (@(posedge clk) penable && !pready |-> $stable(paddr));",
            key_takeaway="APB verification focuses on PENABLE timing, address stability, and wait state handling."
        )
    
    @staticmethod
    def _generate_sva_response(sub_intent: str, metadata: Dict, text: str) -> str:
        """Generate SVA-specific response."""
        
        if sub_intent == "implication":
            return ResponseGenerator._format_structured_response(
                direct_answer="Overlapping implication (|->) checks consequent in the same cycle as antecedent success. Non-overlapping implication (|=>) checks consequent one cycle after antecedent success.",
                why="Overlapping is for same-cycle conditions (e.g., req |-> ack). Non-overlapping is for next-cycle conditions (e.g., req |=> ack). The choice depends on the protocol timing requirements.",
                verification_approach="Use |-> when consequent should be true immediately. Use |=> when there's a known cycle delay. Add coverage for both timing scenarios.",
                example="// Overlapping implication\nassert property (@(posedge clk)\n    req |-> ack);\n\n// Non-overlapping implication\nassert property (@(posedge clk)\n    req |=> ack);\n\n// Delayed implication\nassert property (@(posedge clk)\n    req |-> ##[1:10] ack);",
                key_takeaway="Use |-> for same-cycle, |=> for next-cycle, ##n for specific delay."
            )
        
        elif sub_intent == "write_assertion":
            # Check what kind of assertion is requested
            text_lower = text.lower()
            if "arvalid" in text_lower and "arready" in text_lower:
                return ResponseGenerator._format_structured_response(
                    direct_answer="Here's an SVA assertion that ARVALID remains asserted until ARREADY:",
                    why="The 'until_with' operator ensures ARVALID stays asserted from when it's asserted until ARREADY is asserted. This prevents the master from dropping ARVALID prematurely.",
                    verification_approach="Add this assertion to your testbench. Verify it passes during normal operation. Cover cases where ARREADY is delayed (backpressure).",
                    example="assert property (\n    @(posedge clk)\n    disable iff (!rst_n)\n    ARVALID |-> ARVALID until_with ARREADY\n);",
                    key_takeaway="Use 'until_with' to ensure VALID signals persist until handshake completion."
                )
            else:
                return ResponseGenerator._format_structured_response(
                    direct_answer="Please specify which signals you want to assert. For VALID/READY handshakes, use the pattern: VALID |-> VALID until_with READY",
                    why="The exact assertion depends on the specific signals and protocol. Provide the signal names for a precise assertion.",
                    verification_approach="Replace signal names in the template with your actual signals. Add disable iff for reset if needed.",
                    example="// Template\nassert property (\n    @(posedge clk)\n    disable iff (!rst_n)\n    VALID_SIGNAL |-> VALID_SIGNAL until_with READY_SIGNAL\n);",
                    key_takeaway="Specify signal names for precise SVA assertions."
                )
        
        elif sub_intent == "delay":
            return ResponseGenerator._format_structured_response(
                direct_answer="##n specifies a fixed delay of n cycles. ##[m:n] specifies a delay range from m to n cycles. ##[0:$] specifies zero or more cycles (eventually).",
                why="Fixed delay is for known timing. Range delay is for variable timing. Eventually (##[0:$]) is for protocols with no guaranteed maximum delay but requiring eventual completion.",
                verification_approach="Use ##n for cycle-accurate protocols. Use ##[m:n] for bounded variable delays. Use ##[0:$] with caution - add timeout assumptions to prevent infinite waits.",
                example="// Fixed delay\nassert property (@(posedge clk) req |-> ##3 ack);\n\n// Range delay\nassert property (@(posedge clk) req |-> ##[1:10] ack);\n\n// Eventually\nassert property (@(posedge clk) req |-> ##[0:$] ack);",
                    key_takeaway="Choose delay operator based on protocol timing requirements."
                )
        
        elif sub_intent == "stability":
            return ResponseGenerator._format_structured_response(
                direct_answer="$stable(signal) returns true if the signal has not changed value compared to the previous clock cycle. Used to verify signals remain stable during specific conditions.",
                why="Stability checks are critical for handshake protocols - payload must not change while VALID is asserted and waiting for READY. Also used for address stability in APB/AXI.",
                verification_approach="Add stability checks for payload signals during VALID && !READY. Verify address stability during access phases. Cover all signals that must be stable.",
                example="// Payload stability\nassert property (@(posedge clk)\n    valid && !ready |-> $stable(data));\n\n// Address stability\nassert property (@(posedge clk)\n    penable && !pready |-> $stable(paddr));",
                key_takeaway="Use $stable to verify signals don't change when they shouldn't."
            )
        
        # Generic SVA response
        return ResponseGenerator._format_structured_response(
            direct_answer="I understand this as an SVA assertion request. SVA provides temporal operators: |-> (overlapping implication), |=> (non-overlapping), ##n (delay), $stable, $rose, $fell, throughout, until.",
            why="SVA enables concise specification of complex timing behaviors. Key operators: implication for conditional checking, delay for timing, stability for signal invariance.",
            verification_approach="Use disable iff for reset conditions. Choose appropriate implication type. Use delay operators for timing. Add coverage for assertion success/failure.",
            example="// Basic assertion template\nassert property (\n    @(posedge clk)\n    disable iff (!rst_n)\n    antecedent |-> consequent\n);",
            key_takeaway="SVA assertions should include clocking, reset disable, and appropriate temporal operators."
        )
    
    @staticmethod
    def _generate_coverage_response(sub_intent: str, metadata: Dict, text: str) -> str:
        """Generate coverage-specific response."""
        
        if sub_intent == "code_vs_functional":
            return ResponseGenerator._format_structured_response(
                direct_answer="Code coverage measures which RTL lines/branches/paths are executed. Functional coverage measures whether design features and scenarios are exercised. 98% code coverage + 72% functional coverage means code is well-executed but verification intent is incomplete.",
                why="Code coverage is automatic but doesn't prove correct behavior. Functional coverage requires explicit specification and measures verification completeness. High code with low functional indicates missing tests for important scenarios.",
                verification_approach="Identify uncovered functional bins. Determine if bins are unreachable or missing tests. Add targeted stimulus for uncovered scenarios. Use coverage closure rather than blind randomization. Review test plan gaps.",
                example="// Functional coverage example\ncovergroup fifo_coverage;\n    coverpoint fifo_depth {{\n        bins empty = {{0}};\n        bins full = {{DEPTH}};\n        bins normal = {{[1:DEPTH-1]}};\n    }}\n    cross depth, read_enable, write_enable;\nendgroup",
                key_takeaway="Code coverage proves execution, functional coverage proves verification of design intent."
            )
        
        elif sub_intent == "coverage_holes":
            return ResponseGenerator._format_structured_response(
                direct_answer="Coverage holes are functional scenarios not yet exercised. Identify them by reviewing uncovered bins in functional coverage. Determine if holes are: (1) Unreachable (design limitation), (2) Missing tests (test gap), or (3) Incorrectly specified (coverage bug).",
                why="Coverage holes indicate incomplete verification. Some holes may be legitimate (unreachable features), but most indicate missing test scenarios. Systematic hole analysis improves verification quality.",
                verification_approach="Review uncovered bins. Analyze design to determine reachability. Add directed tests for reachable holes. Mark unreachable bins as ignore_bins. Use coverage closure to track progress.",
                example="// Handling unreachable bins\ncoverpoint addr {{\n    bins valid = {{[0:1023]}};\n    bins reserved = {{[1024:2047]}};\n    ignore_bins reserved;  // Design doesn't use these\n}}\n\n// Coverage closure\ncovergroup with_closure;\n    coverpoint feature;\n    option.goal = 100;  // Require 100% coverage\nendgroup",
                key_takeaway="Analyze coverage holes systematically - add tests for reachable holes, ignore unreachable ones."
            )
        
        elif sub_intent == "coverage_closure":
            return ResponseGenerator._format_structured_response(
                direct_answer="Coverage closure is the process of achieving 100% functional coverage by systematically filling coverage holes. Use directed tests for hard-to-hit scenarios, constrained random for common scenarios, and analyze unreachable bins.",
                why="Blind randomization rarely achieves complete coverage. Coverage closure requires: (1) Identifying holes, (2) Classifying holes (reachable vs unreachable), (3) Adding targeted tests, (4) Iterating until closure.",
                verification_approach="Set coverage goals per covergroup. Track hole closure progress. Use directed tests for corner cases. Use constrained random with biasing for common scenarios. Review and mark unreachable bins.",
                example="// Coverage closure strategy\n// 1. Set goals\ncovergroup cg;\n    coverpoint feature;\n    option.goal = 100;\nendgroup\n\n// 2. Add directed tests for holes\nfeature_x: begin\n    force specific_condition = 1;\n    // test\nend\n\n// 3. Use biasing in random\nclass Item;\n    rand feature_t feature;\n    constraint hit_holes {\n        feature dist {HOLE1:=10, HOLE2:=10, others:=1};\n    }\nendclass",
                key_takeaway="Coverage closure requires systematic hole analysis and targeted test addition, not just more randomization."
            )
        
        # Generic coverage response
        return ResponseGenerator._format_structured_response(
            direct_answer="I understand this as a coverage question. Functional coverage measures design features and scenarios. Key types: bins, cross coverage, coverage closure, coverage holes. Code coverage measures RTL execution.",
            why="Functional coverage requires explicit specification and measures verification completeness. Combined with code coverage, it provides comprehensive verification metrics.",
            verification_approach="Define covergroups for key features. Use bins for value ranges, cross for combinations. Set coverage goals. Track hole closure. Review unreachable bins.",
            example="// Functional coverage template\ncovergroup feature_cg;\n    coverpoint feature {\n        bins low = {[0:15]};\n        bins high = {[16:31]};\n    }\n    cross feature, mode;\nendgroup",
            key_takeaway="Functional coverage must be explicitly defined and systematically closed for complete verification."
        )
    
    @staticmethod
    def _generate_debugging_response(sub_intent: str, metadata: Dict, text: str) -> str:
        """Generate debugging-specific response."""
        
        if sub_intent == "timeout":
            return ResponseGenerator._format_structured_response(
                direct_answer="Timeout indicates the simulation hung without completing expected operations. Debug by: (1) Identifying which process/transaction timed out, (2) Checking for deadlock conditions, (3) Verifying handshake completion, (4) Inspecting waveform for stuck signals.",
                why="Timeouts occur when: handshakes never complete, reset is stuck, counters never reach target, or events never trigger. Systematic waveform analysis is required to identify the root cause.",
                verification_approach="Add timeout assertions with informative messages. Check all handshake channels. Verify reset deassertion. Inspect outstanding transaction counts. Reproduce with same seed for deterministic debugging.",
                example="// Timeout assertion\nassert property (@(posedge clk)\n    disable iff (!rst_n)\n    req |-> ##[1:1000] ack) else $error(\"Timeout: req not acknowledged within 1000 cycles\");\n\n// Debugging checklist\n// 1. Which signal is stuck?\n// 2. Which handshake didn't complete?\n// 3. Is reset properly deasserted?\n// 4. Are there outstanding transactions?",
                key_takeaway="Timeout debugging requires systematic waveform analysis and handshake verification."
            )
        
        elif sub_intent == "hang":
            return ResponseGenerator._format_structured_response(
                direct_answer="Hang indicates the simulation is stuck in a state with no progress. For AXI: check which handshake stopped (AW, W, B, AR, R). For FIFO: check pointer movement. General: check event triggers, counters, and state machines.",
                why="Hangs occur when: a handshake never completes (VALID/READY deadlock), a state machine never transitions, a counter never increments, or an event never triggers. Identify the stuck component first.",
                verification_approach="Identify stuck signals in waveform. Check handshake completion on all channels. Verify state machine transitions. Inspect counter increments. Check for X-state propagation. Reproduce with seed.",
                example="// Hang detection assertion\nassert property (@(posedge clk)\n    disable iff (!rst_n)\n    state == ACTIVE |-> ##[1:100] (state == DONE || state == IDLE))\n    else $error(\"State machine stuck in ACTIVE\");",
                key_takeaway="Identify the stuck component first, then trace why it's not progressing."
            )
        
        elif sub_intent == "mismatch":
            return ResponseGenerator._format_structured_response(
                direct_answer="Scoreboard mismatch indicates DUT output doesn't match reference model. Debug by: (1) Identifying which transaction mismatched, (2) Comparing DUT vs reference waveforms, (3) Checking scoreboard comparison logic, (4) Verifying reference model correctness.",
                why="Mismatches occur from: RTL bugs, reference model bugs, scoreboard comparison bugs, timing issues, or configuration errors. Systematic comparison of DUT and reference behavior is required.",
                verification_approach="Log mismatch details (transaction ID, expected, actual). Compare waveforms at mismatch point. Inspect reference model logic. Check scoreboard comparison code. Verify configuration and stimulus.",
                example="// Scoreboard comparison with logging\nif (dut_data != ref_data) begin\n    $error(\"Mismatch: ID=%0h, Expected=%0h, Actual=%0h\", \n           trans_id, ref_data, dut_data);\n    // Log waveform trigger\nend\n\n// Debugging checklist\n// 1. Is reference model correct?\n// 2. Is comparison logic correct?\n// 3. Is timing aligned?\n// 4. Is stimulus correct?",
                key_takeaway="Mismatch debugging requires comparing DUT and reference behavior at the failure point."
            )
        
        elif sub_intent == "intermittent":
            return ResponseGenerator._format_structured_response(
                direct_answer="Intermittent failures occur only with specific random seeds. Debug by: (1) Reproducing with the failing seed, (2) Freezing randomization at failure point, (3) Analyzing what makes this seed unique, (4) Adding targeted tests for the condition.",
                why="Intermittent failures indicate: rare corner cases, race conditions, constraint interactions, or timing-dependent bugs. The seed determines the random stimulus that triggers the condition.",
                verification_approach="Capture failing seed. Reproduce deterministically. Freeze randomization to identify trigger. Add coverage for the rare condition. Add directed test. Verify fix with multiple seeds.",
                example="// Seed reproduction\n// Run with specific seed\n+seed=12345\n\n// Freeze randomization at failure\nfunction void freeze_randomization();\n    // Save current random state\nendfunction\n\n// Add coverage for rare condition\ncovergroup rare_condition;\n    coverpoint rare_signal;\nendgroup",
                key_takeaway="Intermittent failures require seed reproduction and systematic analysis of the triggering condition."
            )
        
        elif sub_intent == "reset_issue":
            return ResponseGenerator._format_structured_response(
                direct_answer="Reset issues include: reset not clearing state, reset during active traffic, reset synchronization (async), or reset release timing. Debug by checking reset assertion/deassertion timing and state clearing.",
                why="Reset bugs occur when: reset doesn't clear all state, reset is asserted during critical operations, reset timing violates protocol, or async reset has metastability issues.",
                verification_approach="Verify reset clears all state (pointers, counters, flags). Check reset assertion/deassertion timing. Verify reset during traffic. Check async reset synchronization. Add reset coverage.",
                example="// Reset assertion\nassert property (@(posedge clk)\n    reset |-> ##1 (rd_ptr == 0 && wr_ptr == 0 && full == 0 && empty == 1));\n\n// Reset coverage\ncovergroup reset_coverage;\n    coverpoint reset_phase {{\n        bins idle = {{IDLE}};\n        bins active = {{ACTIVE}};\n    }}\nendgroup",
                key_takeaway="Verify reset clears all state and handles timing correctly."
            )
        
        # Generic debugging response
        return ResponseGenerator._format_structured_response(
            direct_answer="I understand this as a debugging question. Common DV issues: timeout, hang, mismatch, intermittent failures, reset issues, X propagation. Debug by systematic waveform analysis and failure reproduction.",
            why="Debugging requires: (1) Reproducing the failure, (2) Identifying the failure point, (3) Comparing expected vs actual, (4) Tracing root cause, (5) Adding regression test.",
            verification_approach="Capture failing seed. Inspect waveform at failure. Check assertions. Compare DUT vs reference. Add targeted tests. Verify fix with regression.",
            example="// Debugging checklist\n// 1. Can you reproduce with seed?\n// 2. What assertion failed?\n// 3. What's the waveform at failure?\n// 4. Expected vs actual?\n// 5. Is this a corner case?",
            key_takeaway="Systematic debugging: reproduce, identify, compare, trace, fix, verify."
        )
    
    @staticmethod
    def _generate_testplan_response(sub_intent: str, metadata: Dict, text: str) -> str:
        """Generate testplan-specific response."""
        
        component = metadata.get("component", "generic")
        
        return ResponseGenerator._format_structured_response(
            direct_answer=f"A verification plan for {component.upper()} should include: objective, features, scenarios, directed tests, constrained-random tests, negative tests, reset tests, corner cases, assertions, functional coverage, and regression strategy.",
            why="A comprehensive test plan ensures all functionality is verified, corner cases are covered, and verification is measurable through coverage and assertions.",
            verification_approach=f"Define test objectives for {component}. List features to verify. Specify directed tests for corner cases. Use constrained random for main scenarios. Add negative tests. Define assertions and coverage. Plan regression strategy.",
            example=f"""TEST PLAN: {component.upper()}
━━━━━━━━━━━━━━━━━━

Objective: Verify {component} functionality

Features:
- Basic operation
- Protocol compliance
- Error handling

Scenarios:
- Normal operation
- Corner cases
- Error conditions
- Reset scenarios

Directed Tests:
- Feature-specific tests
- Boundary conditions
- Error injection

Constrained-Random Tests:
- Random traffic
- Random delays
- Random error injection

Negative Tests:
- Protocol violations
- Invalid inputs

Assertions:
- Protocol compliance
- Data integrity
- Reset behavior

Functional Coverage:
- All features
- Corner cases
- Error conditions

Regression Strategy:
- Full regression nightly
- Smoke test per commit
- Coverage-driven closure""",
            key_takeaway="A good test plan balances directed and random testing, with clear coverage goals and regression strategy."
        )
    
    @staticmethod
    def _generate_reset_response(sub_intent: str, metadata: Dict, text: str) -> str:
        """Generate reset-specific response."""
        
        if sub_intent == "async_reset":
            return ResponseGenerator._format_structured_response(
                direct_answer="Asynchronous reset takes effect immediately when asserted, regardless of clock. Requires proper synchronization to avoid metastability when crossing clock domains. Reset assertion is immediate, deassertion should be synchronized.",
                why="Async reset provides immediate response but can cause metastability if not synchronized. The reset tree must be balanced to avoid skew. Reset deassertion should be synchronized to the clock domain.",
                verification_approach="Verify reset clears all state immediately. Check reset deassertion synchronization. Verify reset timing (recovery, removal). Cover reset during all operations. Check reset tree balance.",
                example="// Async reset assertion\nassert property (\n    @(posedge clk)\n    !rst_n |-> ##1 (state == IDLE && ptr == 0));\n\n// Synchronized reset deassertion\nalways @(posedge clk or negedge rst_n) begin\n    if (!rst_n) begin\n        sync1 <= 1'b0;\n        sync2 <= 1'b0;\n    end else begin\n        sync1 <= 1'b1;\n        sync2 <= sync1;\n    end\nend\nassign rst_n_sync = sync2;",
                key_takeaway="Async reset requires immediate assertion but synchronized deassertion to avoid metastability."
            )
        
        elif sub_intent == "sync_reset":
            return ResponseGenerator._format_structured_response(
                direct_answer="Synchronous reset takes effect only on a clock edge when asserted. Simpler than async reset but requires clock to be running. No metastability concerns but slower response.",
                why="Sync reset is simpler and avoids metastability but requires a running clock. Reset assertion is registered, so timing is predictable. Used when clock is always available and immediate reset isn't critical.",
                verification_approach="Verify reset clears state on clock edge after assertion. Check reset timing relative to clock. Cover reset during all operations. Verify reset release timing.",
                example="// Sync reset assertion\nassert property (\n    @(posedge clk)\n    rst |-> ##1 (state == IDLE && ptr == 0));\n\n// Sync reset in always block\nalways @(posedge clk) begin\n    if (rst) begin\n        state <= IDLE;\n        ptr <= 0;\n    end else begin\n        // normal logic\n    end\nend",
                key_takeaway="Sync reset is simpler but requires clock and has slower response than async reset."
            )
        
        # Generic reset response
        return ResponseGenerator._format_structured_response(
            direct_answer="I understand this as a reset verification question. Reset types: synchronous (clocked) and asynchronous (immediate). Key concerns: state clearing, timing, synchronization, and reset during traffic.",
            why="Reset verification ensures the design can recover from any state. Reset must clear all state, handle timing correctly, and not cause metastability or protocol violations.",
            verification_approach="Add assertions for reset clearing all state. Check reset assertion/deassertion timing. Verify reset during active operations. Cover reset scenarios. Check async reset synchronization.",
            example="// Reset assertion template\nassert property (@(posedge clk)\n    reset |-> ##1 (all_state_cleared));\n\n// Reset coverage\ncovergroup reset_coverage;\n    coverpoint reset_phase {{\n        bins idle = {{IDLE}};\n        bins active = {{ACTIVE}};\n        bins error = {{ERROR}};\n    }}\nendgroup",
            key_takeaway="Reset verification must ensure complete state clearing and proper timing."
        )
    
    @staticmethod
    def _generate_cdc_response(sub_intent: str, metadata: Dict, text: str) -> str:
        """Generate CDC-specific response."""
        
        if sub_intent == "gray_code":
            return ResponseGenerator._format_structured_response(
                direct_answer="Gray code is used in CDC because only one bit changes between consecutive values. This minimizes metastability risk when signals cross clock domains. Binary pointers can have multiple bits change simultaneously, causing corrupted synchronized values.",
                why="When crossing clock domains, signals are sampled by flip-flops in the receiving domain. If multiple bits change simultaneously (e.g., binary 7->8: 0111->1000), the receiving flip-flop may sample a metastable intermediate value. Gray code's single-bit change ensures sampled values are always valid.",
                verification_approach="Verify Gray encoding/decoding logic. Add CDC checks with synchronizer stages. Cover all Gray code transitions. Verify pointer synchronization depth (typically 2-3 flip-flops). Check for CDC violations using tools.",
                example="// Gray码 conversion\nfunction [3:0] bin2gray(input [3:0] bin);\n    bin2gray = bin ^ (bin >> 1);\nendfunction\n\n// Synchronizer stages\nalways @(posedge rd_clk) begin\n    sync1 <= sync2;\n    sync2 <= wr_ptr_gray;\n    wr_ptr_gray_sync <= sync1;\nend",
                key_takeaway="Gray code's single-bit change property makes it essential for safe clock domain crossing."
            )
        
        elif sub_intent == "synchronizer":
            return ResponseGenerator._format_structured_response(
                direct_answer="A synchronizer is a chain of flip-flops (typically 2-3) used to safely pass signals across clock domains. It reduces metastability probability by allowing time for metastable states to resolve.",
                why="When a signal changes near the receiving clock edge, the receiving flip-flop may enter a metastable state (neither 0 nor 1). A synchronizer chain gives the metastable state time to resolve before being used by downstream logic.",
                verification_approach="Verify synchronizer has at least 2 stages. Check that synchronized signals are only used after full synchronization. Add coverage for synchronizer timing. Use CDC analysis tools to verify proper synchronization.",
                example="// 2-stage synchronizer\nalways @(posedge clk_b) begin\n    sync1 <= async_signal;\n    sync2 <= sync1;\nend\nassign sync_signal = sync2;  // Use sync2, not sync1\n\n// CDC assertion\nassert property (@(posedge clk_b)\n    $stable(sync_signal) throughout !async_signal);",
                key_takeaway="Use 2-3 stage synchronizers for CDC, and only use the final synchronized output."
            )
        
        elif sub_intent == "metastability":
            return ResponseGenerator._format_structured_response(
                direct_answer="Metastability occurs when a signal changes near a clock edge, causing a flip-flop to settle to an undefined state. It can cause functional failures if the metastable signal is used. Mitigation: synchronizers, Gray code, proper timing constraints.",
                why="Flip-flops have setup and hold time requirements. If input changes near the clock edge, the output may oscillate or settle to an intermediate value. This metastable state can propagate through the design causing errors.",
                verification_approach="Add synchronizers for all CDC paths. Use Gray code for multi-bit signals. Apply proper timing constraints (set_multicycle_path if needed). Use CDC analysis tools. Verify MTBF (Mean Time Between Failures) is acceptable.",
                example="// Metastability mitigation\n// 1. Synchronizer for single-bit\nalways @(posedge clk_b) begin\n    sync1 <= async_signal;\n    sync2 <= sync1;\nend\n\n// 2. Gray code for multi-bit\ngray_ptr = bin2gray(binary_ptr);\n\n// 3. Timing constraints\nset_max_delay -from [get_clocks clk_a] -to [get_clocks clk_b] 3.0",
                key_takeaway="Metastability is mitigated by synchronizers, Gray code, and proper timing constraints."
            )
        
        # Generic CDC response
        return ResponseGenerator._format_structured_response(
            direct_answer="I understand this as a CDC question. Clock Domain Crossing (CDC) issues include metastability, data corruption, and protocol violations. Mitigation: synchronizers, Gray code, proper timing constraints.",
            why="Signals crossing clock domains can cause metastability if timing violates setup/hold requirements. Multi-bit signals can have bits change at different times, causing corrupted values.",
            verification_approach="Use synchronizers (2-3 stages) for single-bit signals. Use Gray code for multi-bit signals (e.g., FIFO pointers). Apply proper timing constraints. Use CDC analysis tools. Verify all CDC paths are properly handled.",
            example="// CDC checklist\n// 1. All async signals synchronized?\n// 2. Multi-bit signals use Gray code?\n// 3. Timing constraints applied?\n// 4. CDC tool clean?\n// 5. MTBF acceptable?",
            key_takeaway="CDC requires systematic handling: synchronizers, Gray code, timing constraints, and tool verification."
        )
    
    @staticmethod
    def _generate_uvm_response(sub_intent: str, metadata: Dict, text: str) -> str:
        """Generate UVM-specific response."""
        
        if sub_intent == "phases":
            return ResponseGenerator._format_structured_response(
                direct_answer="UVM phases: build_phase (construct testbench), connect_phase (connect components), end_of_elaboration_phase (resolve topology), start_of_simulation_phase (pre-sim checks), run_phase (main simulation), extract_phase, check_phase, report_phase. Sub-phases: pre_reset, post_reset, pre_config, post_config, pre_main, post_main, pre_shutdown, post_shutdown.",
                why="Phases provide structured testbench execution. Build/create hierarchy, connect components, run simulation, extract results, check correctness, report. Sub-phases allow fine-grained control during run_phase.",
                verification_approach="Implement all required phases. Use build_phase for construction. Use connect_phase for TLM connections. Use run_phase for stimulus. Use check_phase for result verification. Use report_phase for summary.",
                example="// Phase implementation\nfunction void build_phase(uvm_phase phase);\n    super.build_phase(phase);\n    driver = driver::type_id::create(\"driver\", this);\n    monitor = monitor::type_id::create(\"monitor\", this);\nendfunction\n\nfunction void connect_phase(uvm_phase phase);\n    super.connect_phase(phase);\n    driver.seq_item_port.connect(sequencer.seq_item_export);\nendfunction",
                key_takeaway="UVM phases provide structured execution - use appropriate phases for each activity."
            )
        
        elif sub_intent == "factory":
            return ResponseGenerator._format_structured_response(
                direct_answer="UVM factory enables object creation and type overriding at runtime. Register with `uvm_object_utils` or `uvm_component_utils`. Create with `type_id::create()`. Override with `set_type_override()`. This allows test-level customization without modifying base classes.",
                why="Factory pattern enables flexible testbench configuration. Tests can override component types without modifying the environment. Supports hierarchical overrides and instance-specific overrides.",
                verification_approach="Register all components with factory macros. Use factory for all object creation. Use type overrides for test-specific customization. Verify overrides are applied correctly.",
                example="// Factory registration\nclass my_driver extends uvm_driver;\n    `uvm_component_utils(my_driver)\nendclass\n\n// Factory creation\ndriver = my_driver::type_id::create(\"driver\", this);\n\n// Type override\nmy_driver::type_id::set_type_override(my_extended_driver::get_type());",
                key_takeaway="Use factory for all object creation to enable runtime type overriding."
            )
        
        elif sub_intent == "components":
            return ResponseGenerator._format_structured_response(
                direct_answer="UVM components: driver (drives DUT), monitor (observes DUT), sequencer (manages sequences), agent (contains driver+monitor+sequencer), env (contains agents), scoreboard (compares results), reference model (predicts expected behavior).",
                why="UVM provides reusable components with standard interfaces. Driver converts sequence items to pin-level. Monitor observes DUT and creates transactions. Sequencer manages sequence flow. Agent groups related components.",
                verification_approach="Use standard UVM components. Implement driver for DUT interface. Implement monitor for observation. Use sequencer for stimulus management. Use scoreboard for checking. Use reference model for prediction.",
                example="// Component instantiation\nfunction void build_phase(uvm_phase phase);\n    super.build_phase(phase);\n    agent = my_agent::type_id::create(\"agent\", this);\n    scoreboard = my_scoreboard::type_id::create(\"scoreboard\", this);\nendfunction\n\n// TLM connection\nfunction void connect_phase(uvm_phase phase);\n    monitor.analysis_port.connect(scoreboard.analysis_export);\nendfunction",
                key_takeaway="Use standard UVM components with TLM interfaces for modular, reusable testbenches."
            )
        
        # Generic UVM response
        return ResponseGenerator._format_structured_response(
            direct_answer="I understand this as a UVM question. UVM provides a methodology for reusable verification. Key concepts: phases, factory, components (driver, monitor, sequencer, agent, env, scoreboard), TLM, sequences, objections.",
            why="UVM standardizes verification methodology, enabling reuse across projects and teams. It provides building blocks and guidelines for creating scalable, maintainable testbenches.",
            verification_approach="Follow UVM methodology. Use standard components. Implement phases correctly. Use factory for creation. Use TLM for communication. Use sequences for stimulus. Use objections for phase control.",
            example="// Basic UVM test\nclass my_test extends uvm_test;\n    `uvm_component_utils(my_test)\n    \n    my_env env;\n    \n    function void build_phase(uvm_phase phase);\n        env = my_env::type_id::create(\"env\", this);\n    endfunction\n    \n    task run_phase(uvm_phase phase);\n        my_seq seq = my_seq::type_id::create(\"seq\");\n        seq.start(env.agent.sequencer);\n    endtask\nendclass",
            key_takeaway="UVM provides a structured methodology - follow the standard patterns for best results."
        )
    
    @staticmethod
    def _generate_scoreboard_response(sub_intent: str, metadata: Dict, text: str) -> str:
        """Generate scoreboard-specific response."""
        
        if sub_intent == "mismatch":
            return ResponseGenerator._format_structured_response(
                direct_answer="Scoreboard mismatch occurs when DUT output doesn't match reference model output. Debug by: (1) Identifying which transaction mismatched, (2) Comparing DUT vs reference waveforms, (3) Checking scoreboard comparison logic, (4) Verifying reference model correctness.",
                why="Mismatches indicate: RTL bugs, reference model bugs, scoreboard bugs, timing issues, or configuration errors. Systematic comparison of DUT and reference behavior at the failure point is required.",
                verification_approach="Log mismatch details (transaction ID, expected, actual). Compare waveforms at mismatch. Inspect reference model logic. Check scoreboard comparison code. Verify configuration and stimulus alignment.",
                example="// Scoreboard comparison with logging\nfunction void write(input trans t);\n    trans exp = ref_model.predict(t);\n    if (t.data != exp.data) begin\n        $error(\"Mismatch: ID=%0h, Exp=%0h, Act=%0h\", \n               t.id, exp.data, t.data);\n    end\nendfunction\n\n// Debugging checklist\n// 1. Is reference model correct?\n// 2. Is comparison logic correct?\n// 3. Is timing aligned?\n// 4. Is stimulus correct?",
                key_takeaway="Scoreboard debugging requires comparing DUT and reference behavior at the failure point."
            )
        
        elif sub_intent == "reference_model":
            return ResponseGenerator._format_structured_response(
                direct_answer="Reference model predicts expected DUT behavior. It should: (1) Match DUT functionality, (2) Use same inputs as DUT, (3) Produce expected outputs, (4) Handle timing correctly (cycle-accurate or transaction-level).",
                why="Reference model provides the golden reference for scoreboard comparison. It must accurately model DUT behavior to correctly identify bugs. Reference model bugs can cause false mismatches.",
                verification_approach="Verify reference model against specification. Test reference model independently. Check that reference model receives same inputs as DUT. Verify timing alignment. Add assertions to reference model.",
                example="// Reference model example\nclass ref_model extends uvm_component;\n    function trans predict(input trans t);\n        trans exp = trans::type_id::create(\"exp\");\n        exp.data = t.data + 1;  // Example logic\n        exp.addr = t.addr;\n        return exp;\n    endfunction\nendclass",
                key_takeaway="Reference model must accurately model DUT behavior and be verified independently."
            )
        
        # Generic scoreboard response
        return ResponseGenerator._format_structured_response(
            direct_answer="I understand this as a scoreboard question. Scoreboard compares DUT outputs against reference model predictions. Key concerns: comparison logic, reference model correctness, timing alignment, and mismatch debugging.",
            why="Scoreboard enables self-checking testbenches by automatically comparing DUT behavior against expected behavior. It's essential for regression testing and identifying functional bugs.",
            verification_approach="Implement comparison logic for all transactions. Add detailed mismatch logging. Verify reference model correctness. Check timing alignment. Use in-order comparison or out-of-order with transaction IDs.",
            example="// Basic scoreboard\nclass scoreboard extends uvm_scoreboard;\n    uvm_analysis_export #(trans) dut_export;\n    uvm_analysis_export #(trans) ref_export;\n    \n    function void write_trans(input trans t);\n        // Compare DUT vs reference\n        if (dut_trans.data != ref_trans.data) begin\n            $error(\"Mismatch detected\");\n        end\n    endfunction\nendclass",
            key_takeaway="Scoreboard requires accurate comparison logic and a verified reference model."
        )
    
    @staticmethod
    def _generate_constrained_random_response(sub_intent: str, metadata: Dict, text: str) -> str:
        """Generate constrained random response."""
        
        if sub_intent == "constraints":
            return ResponseGenerator._format_structured_response(
                direct_answer="Constraints control randomization to generate legal and interesting stimulus. Use constraint blocks to specify legal value ranges, relationships between variables, and distribution weights. Constraints must be solvable (no contradictions).",
                why="Pure random can generate illegal or uninteresting stimulus. Constraints guide randomization to legal ranges while maintaining randomness. This improves verification efficiency by focusing on valid scenarios.",
                verification_approach="Define constraints for all legal value ranges. Use distribution weights for interesting scenarios. Verify constraints are solvable. Use constraint_mode to enable/disable. Add coverage to verify constraint effectiveness.",
                example="// Constraint example\nclass item extends uvm_sequence_item;\n    rand bit [7:0] addr;\n    rand bit [7:0] data;\n    rand bit [3:0] len;\n    \n    constraint valid_addr {\n        addr inside {[0:127]};\n    }\n    \n    constraint reasonable_len {\n        len inside {[1:16]};\n        len dist {1:=40, [2:8]:=40, [9:16]:=20};\n    }\nendclass",
                key_takeaway="Constraints guide randomization to legal, interesting scenarios while maintaining randomness."
            )
        
        elif sub_intent == "randomization":
            return ResponseGenerator._format_structured_response(
                direct_answer="rand generates random values each time (can repeat). randc generates random cyclic values (each value appears once before repeating). Use randomize() to randomize objects. Use pre_randomize() and post_randomize() for setup/cleanup.",
                why="rand is for general randomization where repetition is allowed. randc is for permutation without repetition (useful for sequences). pre_randomize() allows setup before randomization. post_randomize() allows cleanup or post-processing.",
                verification_approach="Use rand for general randomization. Use randc when you need permutation. Implement pre_randomize for setup. Implement post_randomize for post-processing. Add coverage to verify randomization distribution.",
                example="// Randomization example\nclass item extends uvm_sequence_item;\n    rand bit [7:0] addr;\n    randc bit [3:0] id;\n    \n    function void pre_randomize();\n        addr = 0;  // Setup\n    endfunction\n    \n    function void post_randomize();\n        if (addr == 0) addr = 8'h80;  // Post-process\n    endfunction\nendclass",
                key_takeaway="Use rand for general randomization, randc for permutation, and callbacks for setup/cleanup."
            )
        
        # Generic constrained random response
        return ResponseGenerator._format_structured_response(
            direct_answer="I understand this as a constrained random question. Constrained random generates legal stimulus within specified constraints. Key concepts: rand/randc, constraint blocks, solve before, pre/post_randomize, constraint_mode.",
            why="Constrained random improves verification efficiency by focusing on legal, interesting scenarios while maintaining randomness. It's more efficient than pure random and more comprehensive than directed tests.",
            verification_approach="Define constraints for legal ranges. Use distribution weights for interesting scenarios. Use solve before to guide solver. Add coverage to verify distribution. Use constraint_mode for flexibility.",
            example="// Constrained random template\nclass item extends uvm_sequence_item;\n    rand bit [7:0] value;\n    \n    constraint valid {\n        value inside {[0:255]};\n    }\n    \n    constraint interesting {\n        value dist {0:=10, [1:254]:=80, 255:=10};\n    }\nendclass",
            key_takeaway="Constrained random balances randomness with legal, interesting scenario generation."
        )
    
    @staticmethod
    def _generate_regression_response(sub_intent: str, metadata: Dict, text: str) -> str:
        """Generate regression-specific response."""
        
        if sub_intent == "seed":
            return ResponseGenerator._format_structured_response(
                direct_answer="Random seed controls randomization in regression tests. Same seed produces same stimulus. Use seeds for: (1) Reproducing failures, (2) Regression stability, (3) Coverage analysis. Different seeds provide different stimulus for coverage.",
                why="Randomization is seed-dependent. Same seed = same random sequence. This enables reproducible debugging and stable regression. Different seeds provide stimulus diversity for coverage closure.",
                verification_approach="Log seeds for all tests. Use same seed to reproduce failures. Use different seeds for coverage closure. Track seed-to-coverage mapping. Use seed management for regression.",
                example="// Seed usage\n// Command line\n+seed=12345\n\n// In code\nfunction void randomize();\n    process proc;\n    proc = process::self();\n    proc.srandom(seed);\nendfunction\n\n// Seed logging\n$display(\"Test seed: %0d\", $urandom_range(0, 2**32-1));",
                key_takeaway="Seeds enable reproducible debugging and systematic coverage closure."
            )
        
        elif sub_intent == "failure":
            return ResponseGenerator._format_structured_response(
                direct_answer="Regression failure indicates a test that passed before now fails. Debug by: (1) Identifying what changed (RTL, testbench, environment), (2) Reproducing with same seed, (3) Analyzing failure type, (4) Determining if it's a real bug or test issue.",
                why="Regression failures can indicate: RTL regression (new bug), testbench issue (fragile test), environment change, or seed sensitivity. Systematic analysis is required to determine root cause.",
                verification_approach="Compare passing vs failing runs. Identify changes. Reproduce with seed. Analyze failure type (assertion, mismatch, timeout). Determine if RTL or testbench issue. Add regression test if RTL bug.",
                example="// Regression debugging checklist\n// 1. What changed?\n// 2. Can you reproduce with seed?\n// 3. Is it RTL or testbench?\n// 4. Is it seed-sensitive?\n// 5. Add regression test if RTL bug\n\n// Seed management\n+seed=<seed_from_failure>",
                key_takeaway="Regression failures require systematic analysis of changes and seed reproduction."
            )
        
        # Generic regression response
        return ResponseGenerator._format_structured_response(
            direct_answer="I understand this as a regression question. Regression testing runs test suites to verify no new bugs. Key concerns: seed management, failure analysis, coverage tracking, and test stability.",
            why="Regression ensures code changes don't introduce new bugs. Systematic regression with seed management enables reproducible debugging and coverage tracking.",
            verification_approach="Run full regression regularly. Log seeds for all tests. Track coverage over time. Analyze failures systematically. Add regression tests for found bugs.",
            example="// Regression strategy\n// Nightly: Full regression\n// Per-commit: Smoke test\n// Weekly: Coverage analysis\n// Per-release: Full regression + coverage closure",
            key_takeaway="Regression requires systematic execution, seed management, and failure analysis."
        )
    
    @staticmethod
    def _generate_fallback_response(text: str) -> str:
        """Generate fallback response when intent is unclear."""
        return f"""I understand you're asking about: "{text}"

I can help with technical DV questions in these domains:

• FIFO (depth, pointers, wraparound, full/empty, overflow/underflow)
• AXI (handshakes, backpressure, outstanding transactions, bursts)
• APB (protocol phases, PENABLE timing, wait states)
• SVA (assertions, temporal operators, implications)
• Coverage (functional vs code, coverage holes, closure)
• Debugging (timeout, hang, mismatch, intermittent failures)
• Test Plans (verification planning, scenarios, coverage)
• Reset (sync/async, timing, state clearing)
• CDC (metastability, synchronizers, Gray code)
• UVM (phases, factory, components)
• Scoreboard (comparison, reference models)
• Constrained Random (constraints, randomization)
• Regression (seeds, failure analysis)

Please be more specific about your DV question, or try commands like:
/axi, /apb, /fifo, /assert, /coverage, /testplan, /bug, /interview, /daily"""
    
    @staticmethod
    def _format_structured_response(

direct_answer: str, why: str, verification_approach: str, 
                              example: str, key_takeaway: str) -> str:
        """Format response in structured format."""
        return f"""**Direct Answer**

{direct_answer}

**Why**

{why}

**Verification Approach**

{verification_approach}

**Example**

{example}

**Key Takeaway**

{key_takeaway}"""
