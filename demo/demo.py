"""Demo mode for DV Sentinel - runs without API keys."""

import os
import sys
from agent.handler import DVHandler


def run_demo():
    """Run interactive demo mode."""
    print("=" * 60)
    print("DV SENTINEL - DEMO MODE")
    print("=" * 60)
    print("No API keys required. Testing DV intelligence engine.")
    print("Type 'quit' to exit.\n")
    
    handler = DVHandler()
    
    demo_prompts = [
        "/start",
        "/assert FIFO should never read when empty",
        "/axi Why is my write transaction stuck?",
        "/coverage FIFO",
        "/testplan FIFO",
        "/bug My simulation failed with timeout",
        "/interview",
        "/daily",
        "/help"
    ]
    
    print("Sample commands to try:")
    for prompt in demo_prompts:
        print(f"  {prompt}")
    print()
    
    while True:
        try:
            user_input = input("DV> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Exiting demo mode.")
                break
            
            # Handle message
            response = handler.handle_message(
                text=user_input,
                user_id="demo_user",
                channel="demo"
            )
            
            print("\n" + response)
            print("\n" + "-" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\nExiting demo mode.")
            break
        except Exception as e:
            print(f"Error: {e}")


def run_scripted_demo():
    """Run scripted demo with predefined inputs."""
    print("=" * 60)
    print("DV SENTINEL - SCRIPTED DEMO")
    print("=" * 60)
    print()
    
    handler = DVHandler()
    
    demo_scenarios = [
        ("Start command", "/start"),
        ("FIFO assertion", "/assert FIFO should never read when empty"),
        ("AXI debugging", "/axi Why is my write transaction stuck?"),
        ("Coverage suggestions", "/coverage FIFO"),
        ("Test plan", "/testplan FIFO"),
        ("Bug report", "/bug My simulation failed with timeout"),
        ("Interview question", "/interview"),
        ("Daily challenge", "/daily"),
        ("Help", "/help"),
        ("Natural language", "Review this SystemVerilog FIFO"),
        ("Natural language", "Generate APB verification tests"),
    ]
    
    for title, input_text in demo_scenarios:
        print(f"\n{'=' * 60}")
        print(f"SCENARIO: {title}")
        print(f"INPUT: {input_text}")
        print(f"{'=' * 60}\n")
        
        response = handler.handle_message(
            text=input_text,
            user_id="demo_user",
            channel="demo"
        )
        
        print(response)
        print("\nPress Enter to continue...")
        input()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--scripted":
        run_scripted_demo()
    else:
        run_demo()
