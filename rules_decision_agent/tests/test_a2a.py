
import asyncio
import sys
import uuid
import httpx
import json

async def main():
    if len(sys.argv) < 2:
        prompt = "Process a new sales order, SO-123, for CMP_SLURRY. This is a Strategic Material. The order has a Net Value of $55,000 and a Gross Margin of 10%"
    else:
        prompt = " ".join(sys.argv[1:])

    print(f"Test Prompt: {prompt}")

    async with httpx.AsyncClient() as client:
        # Step 1: Send Message WITHOUT task_id
        # We assume this triggers implicit task creation
        print("\n--- Step 1: Sending Message (New Task) ---")
        msg_req_id = str(uuid.uuid4())
        msg_payload = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {
                    "message_id": f"msg-{uuid.uuid4()}",
                    "role": "user",
                    "kind": "message",
                    "parts": [
                        {
                            "text": prompt,
                            "kind": "text"
                        }
                    ],
                    # "task_id": ... OMITTED
                    "context_id": str(uuid.uuid4())
                },
                "configuration": {
                    "blocking": True
                }
            },
            "id": msg_req_id
        }
        
        resp2 = await client.post("http://localhost:8001/", json=msg_payload, timeout=120.0)
        if resp2.status_code == 200:
            print("\nResponse Received:")
            print(json.dumps(resp2.json(), indent=2))
        else:
            print(f"Error: {resp2.status_code} - {resp2.text}")

if __name__ == "__main__":
    asyncio.run(main())
