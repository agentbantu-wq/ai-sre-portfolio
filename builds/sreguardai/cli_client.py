#!/usr/bin/env python3
"""
SREGuardAI CLI Client
"""

import requests
import json
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="SREGuardAI CLI Client")
    parser.add_argument("prompt", help="SRE prompt to send to the gateway")
    parser.add_argument("--url", default="http://localhost:8000", help="Gateway URL")
    parser.add_argument("--model", default="llama3.1", help="Model to use")

    args = parser.parse_args()

    # Prepare request
    payload = {
        "prompt": args.prompt,
        "model": args.model
    }

    try:
        response = requests.post(
            f"{args.url}/generate",
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            print("Response:")
            print(result["response"])
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()