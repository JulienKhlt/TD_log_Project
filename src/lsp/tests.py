import requests
import json

def main():
    url = "http://localhost:1234/jsonrpc"

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "textDocument/didOpen",
        "params": {

        }
    }

    response = requests.post(url, json=payload).json()

    print(response)

if __name__ == '__main__':
    main()
