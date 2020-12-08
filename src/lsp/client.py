import requests
import json


def main():
    url = "http://localhost:1234/jsonrpc"

    # Example echo method
    payload = {
        "method": "initialize",
        "jsonrpc": "2.0",
        "id": 0,
        "params": {
            "processId": "null",
            "rootUri": "null",
            "capabilities": {}
        }
    }
    response = requests.post(url, json=payload)

if __name__ == "__main__":
    main()
