"""One-shot OpenRouter key tester. Reads files-practice/openrouter_key.txt (or OPENROUTER_API_KEY),
makes ONE cheap call, prints the reply, tokens and cost. Safe: costs a fraction of a cent."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "ds-copilot" / "ds-copilot" / "src"))
import llm
print("Status:", json.dumps(llm.status(), indent=1))
if not llm._key():
    print("\nNo key found. Paste your key into:  openrouter_key.txt  (this folder), then rerun.")
    sys.exit(1)
txt, meta = llm.complete("You are a test. Reply with exactly: LLM CONNECTED.",
                         "Say the test phrase.")
print("\nReply:", txt)
print("Meta :", meta)
print("\n=> " + ("SUCCESS - key works. Restart the servers (START_ALL) to see the AI layer light up."
                 if txt else "FAILED - check the key / your internet. The demos still work in rules mode."))
