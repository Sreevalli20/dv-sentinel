"""Interview mode for DV Sentinel."""

from typing import List, Dict, Any
import random


class InterviewGenerator:
    """Generates DV interview questions and answers."""
    
    QUESTIONS = {
        "systemverilog": [
            {
                "question": "What is the difference between blocking (=) and non-blocking (<=) assignments in SystemVerilog?",
                "answer": "Blocking (=) executes sequentially in the order they appear. Non-blocking (<=) executes in parallel, with all RHS evaluated before any LHS is updated. Use non-blocking for sequential logic (clocked), blocking for combinational logic."
            },
            {
                "question": "Explain the difference between logic and reg data types in SystemVerilog.",
                "answer": "In SystemVerilog, 'logic' is a more versatile type that can be used in places where 'reg' was required in Verilog. 'logic' can be driven by a single driver (continuous assignment, gate, or procedural assignment), while 'wire' requires multiple drivers. 'reg' is still supported but 'logic' is preferred for most signals."
            },
            {
                "question": "What are the different types of arrays in SystemVerilog?",
                "answer": "SystemVerilog has: 1) Fixed-size arrays (int arr[8]), 2) Dynamic arrays (int arr[]), 3) Associative arrays (int arr[string]), 4) Queues (int arr[$]). Each has different use cases - fixed for known size, dynamic for runtime sizing, associative for sparse data, queues for FIFO operations."
            },
            {
                "question": "What is the purpose of the 'interface' construct in SystemVerilog?",
                "answer": "Interfaces encapsulate connectivity and communication between modules. They reduce wiring errors, improve readability, and can contain tasks, functions, and assertions. Interfaces can also have modports to specify direction and access rights."
            }
        ],
        "uvm": [
            {
                "question": "What are the main phases in UVM?",
                "answer": "UVM phases: build_phase (construct testbench), connect_phase (connect components), end_of_elaboration_phase (resolve topology), start_of_simulation_phase (pre-sim checks), run_phase (main simulation), pre_reset/post_reset, pre_config/post_config, pre_main/post_main, pre_shutdown/post_shutdown, extract_phase, check_phase, report_phase."
            },
            {
                "question": "What is the difference between a UVM driver and a UVM sequencer?",
                "answer": "Driver converts sequence items into pin-level transactions and drives them to the DUT. Sequencer manages and arbitrates sequences, sending items to the driver. The sequencer handles flow control and randomization, while the driver handles timing and protocol."
            },
            {
                "question": "What is a UVM monitor and what is its role?",
                "answer": "A UVM monitor observes DUT signals and transactions, converting them into sequence items for analysis. It's passive - doesn't drive signals. Monitors feed scoreboards, coverage collectors, and checkers. They're essential for self-checking testbenches."
            },
            {
                "question": "Explain the UVM factory mechanism.",
                "answer": "The UVM factory enables object creation and type overriding at runtime. It supports registration with `uvm_object_utils` or `uvm_component_utils`, creation with `type_id::create()`, and overriding with `set_type_override()`. This allows test-level customization without modifying base classes."
            }
        ],
        "sva": [
            {
                "question": "What is the difference between immediate and concurrent assertions in SystemVerilog?",
                "answer": "Immediate assertions (assert) check conditions procedurally like if statements. Concurrent assertions (assert property) check over clocked time using temporal operators. Immediate are for procedural code, concurrent for protocol and timing checks across cycles."
            },
            {
                "question": "What are the temporal operators in SVA?",
                "answer": "Key SVA operators: |-> (implication), |=> (non-overlapping implication), ##n (delay n cycles), ##[1:n] (delay range), throughout, within, until, until_with, intersect, and, or. These enable sophisticated timing and sequence specifications."
            },
            {
                "question": "What is the difference between overlapping and non-overlapping implication?",
                "answer": "Overlapping implication (|->) checks the consequent in the same cycle as antecedent success. Non-overlapping (|=>) checks the consequent one cycle after antecedent success. Example: req |-> ack checks ack same cycle, req |=> ack checks ack next cycle."
            }
        ],
        "fifo": [
            {
                "question": "What is the difference between synchronous and asynchronous FIFO?",
                "answer": "Synchronous FIFO uses same clock for read and write. Asynchronous FIFO uses different clocks, requiring Gray code encoding for pointers to handle metastability. Async FIFO needs synchronization stages (usually 2-3 flip-flops) for clock domain crossing."
            },
            {
                "question": "How do you calculate FIFO depth?",
                "answer": "FIFO depth = (burst_write_rate - burst_read_rate) * burst_time. For worst case, consider maximum write burst when read is blocked, or vice versa. Add margin for uncertainty. Example: if write 100 beats/cycle for 100 cycles and read 50 beats/cycle, depth = (100-50)*100 = 5000."
            },
            {
                "question": "What are the common FIFO flags and how are they generated?",
                "answer": "Common flags: EMPTY (read pointer == write pointer), FULL (write pointer + 1 == read pointer), ALMOST_EMPTY, ALMOST_FULL. Generated by comparing read and write pointers. For async FIFO, compare synchronized Gray-coded pointers."
            }
        ],
        "axi": [
            {
                "question": "What are the five AXI channels?",
                "answer": "AXI has 5 channels: Write Address (AW), Write Data (W), Write Response (B), Read Address (AR), Read Data (R). Each is independent with VALID/READY handshake. This enables out-of-order completion and overlapping transactions."
            },
            {
                "question": "What is the difference between AXI4 and AXI-Lite?",
                "answer": "AXI4 supports bursts, outstanding transactions, and high performance. AXI-Lite is simpler, single-transfer only, no bursts, for register access. AXI-Lite has narrower address/data options and simpler protocol for low-bandwidth control interfaces."
            },
            {
                "question": "What are the AXI response codes?",
                "answer": "AXI response codes: OKAY (success), EXOKAY (exclusive access success), SLVERR (slave error), DECERR (decode error). OKAY indicates normal completion. EXOKAY for atomic operations. SLVERR for slave-specific errors. DECERR for invalid address."
            }
        ],
        "coverage": [
            {
                "question": "What is the difference between code coverage and functional coverage?",
                "answer": "Code coverage measures which lines/branches/paths of RTL are executed. Functional coverage measures design features and scenarios exercised. Code coverage is automatic, functional coverage requires explicit specification. Both needed - code ensures execution, functional ensures verification of intent."
            },
            {
                "question": "What are the different types of code coverage?",
                "answer": "Code coverage types: Line (statement), Branch (if/else), Toggle (bit toggles), FSM (state/transition), Condition (expression terms), Path (combinational paths). Line is basic, branch adds decision coverage, toggle checks signal activity, FSM verifies state machines."
            },
            {
                "question": "How do you define functional coverage in SystemVerilog?",
                "answer": "Use covergroup with coverpoints for variables and bins for value ranges. Example: covergroup cg; coverpoint addr { bins low = {[0:15]}; bins high = {[16:31]}; } endgroup. Instantiate and sample in testbench. Can use cross coverage for combinations."
            }
        ],
        "constrained_random": [
            {
                "question": "What is the difference between rand and randc in SystemVerilog?",
                "answer": "rand generates random values each time, can repeat. randc generates random cyclic values - each value in range appears once before repeating. Use rand for general randomization, randc when you need permutation without repetition."
            },
            {
                "question": "What are pre_randomize() and post_randomize() methods?",
                "answer": "pre_randomize() is called before randomization, useful for setup. post_randomize() is called after randomization, useful for post-processing or cleanup. They're part of the randomization callback mechanism in SystemVerilog."
            },
            {
                "question": "How do you solve randomization constraints?",
                "answer": "Use solve...before to guide solver: solve a before b makes solver prioritize 'a'. Use constraint_mode() to enable/disable constraints. Use randomize() with {} to add inline constraints. For complex cases, consider constraint ordering and avoid contradictions."
            }
        ]
    }
    
    @classmethod
    def get_random_question(cls, topic: str = None) -> Dict[str, str]:
        """Get a random interview question.
        
        Args:
            topic: Optional topic filter
            
        Returns:
            Dictionary with question and answer
        """
        if topic and topic.lower() in cls.QUESTIONS:
            questions = cls.QUESTIONS[topic.lower()]
        else:
            # Flatten all questions
            all_questions = []
            for topic_questions in cls.QUESTIONS.values():
                all_questions.extend(topic_questions)
            questions = all_questions
        
        if not questions:
            return {
                "question": "No questions available for this topic.",
                "answer": ""
            }
        
        return random.choice(questions)
    
    @classmethod
    def evaluate_answer(cls, question: str, user_answer: str) -> Dict[str, str]:
        """Evaluate user's interview answer.
        
        Args:
            question: The question asked
            user_answer: User's answer
            
        Returns:
            Dictionary with evaluation results
        """
        # Find the question in our database
        qa = None
        for topic_questions in cls.QUESTIONS.values():
            for q in topic_questions:
                if q["question"] == question:
                    qa = q
                    break
            if qa:
                break
        
        if not qa:
            return {
                "correctness": "unknown",
                "missing_points": "Question not found in database",
                "stronger_answer": "",
                "interviewer_feedback": "I don't have this question in my database.",
                "difficulty": "unknown"
            }
        
        # Simple keyword-based evaluation
        answer_lower = user_answer.lower()
        expected_lower = qa["answer"].lower()
        
        # Check for key concepts
        key_concepts = []
        if "blocking" in expected_lower and "non-blocking" in expected_lower:
            if "blocking" in answer_lower and "non-blocking" in answer_lower:
                key_concepts.append("blocking vs non-blocking")
            else:
                key_concepts.append("missing: blocking vs non-blocking distinction")
        
        if "sequential" in expected_lower and "combinational" in expected_lower:
            if "sequential" in answer_lower and "combinational" in answer_lower:
                key_concepts.append("sequential vs combinational")
            else:
                key_concepts.append("missing: sequential vs combinational use cases")
        
        # Determine correctness
        if len([c for c in key_concepts if "missing" not in c]) >= 2:
            correctness = "good"
            feedback = "Good answer covering key concepts."
        elif len([c for c in key_concepts if "missing" not in c]) >= 1:
            correctness = "acceptable"
            feedback = "Acceptable answer but could be more comprehensive."
        else:
            correctness = "needs_improvement"
            feedback = "Answer needs more technical depth."
        
        missing_points = [c for c in key_concepts if "missing" in c]
        
        return {
            "correctness": correctness,
            "missing_points": "; ".join(missing_points) if missing_points else "None",
            "stronger_answer": f"Consider adding: {'; '.join(missing_points)}" if missing_points else "Your answer is comprehensive.",
            "interviewer_feedback": feedback,
            "difficulty": cls._assess_difficulty(question)
        }
    
    @classmethod
    def _assess_difficulty(cls, question: str) -> str:
        """Assess question difficulty."""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["difference", "what is", "what are"]):
            return "junior"
        elif any(word in question_lower for word in ["explain", "how", "why"]):
            return "mid-level"
        else:
            return "senior"
    
    @classmethod
    def get_topics(cls) -> List[str]:
        """Get available interview topics."""
        return list(cls.QUESTIONS.keys())
    
    @classmethod
    def format_question(cls, qa: Dict[str, str]) -> str:
        """Format question for display.
        
        Args:
            qa: Question-answer dictionary
        """
        output = []
        output.append("DV INTERVIEW QUESTION")
        output.append("=" * 50)
        output.append(f"\nQuestion:\n{qa.get('question', 'N/A')}")
        output.append(f"\nAnswer:\n{qa.get('answer', 'N/A')}")
        return "\n".join(output)
