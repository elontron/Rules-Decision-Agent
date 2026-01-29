
import sys
import asyncio
import os
import json

# Add src to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from agent import RulesDecisionLogic

async def main():
    if len(sys.argv) < 2:
        print("Usage: python run_direct.py <prompt>")
        print("Example: python run_direct.py \"I need to return order 123 because it is defective\"")
        sys.exit(1)
        
    prompt = " ".join(sys.argv[1:])
    print(f"Running with prompt: {prompt}")
    
    agent = RulesDecisionLogic()
    try:
        result = await agent.execute(prompt, log_callback=lambda msg: print(f"[LOG] {msg}"))
        print("\n=== RESULT ===")
        print(json.dumps(result, indent=2))

        # Extract and print Recommended Action
        analysis_response = result.get("analysisResponse")
        if analysis_response:
            import re
            
            # Helper to print action
            def print_action(text):
                 print("\n=== RECOMMENDED ACTION ===")
                 print(text)

            # Try parsing as JSON first (if it's a JSON block or pure JSON)
            # Remove Markdown code blocks if present
            clean_json = re.sub(r'```json\s*|\s*```', '', analysis_response).strip()
            try:
                parsed = json.loads(clean_json)
                if isinstance(parsed, dict):
                    # Check for popular keys
                    action = parsed.get("recommendedActions") or parsed.get("recommendedAction")
                    if action:
                        print_action(action)
                        return
                    # If structured but no specific key, maybe fallback to text search in raw response?
                    # Or check for extracting from "extracted_data" if that's where it ended up (unlikely for action)
            except json.JSONDecodeError:
                pass
            
            # Fallback to regex pattern matching for text-based response
            # Handle "Recommended Action" or "Recommended Actions"
            match = re.search(r"\*\*Recommended Actions?:\*\*\s*(.*)", analysis_response, re.DOTALL | re.IGNORECASE)
            if match:
                print_action(match.group(1).strip())
    finally:
        await agent.close()

if __name__ == "__main__":
    # Ensure event loop behavior for library compatibility
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
