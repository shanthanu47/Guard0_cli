import subprocess
import json
import sys
import os
import time

def send_json(process, data):
    try:
        json_str = json.dumps(data)
        process.stdin.write(json_str + "\n")
        process.stdin.flush()
    except Exception as e:
        print(f"❌ Error sending data: {e}")

def read_json(process):
    try:
        line = process.stdout.readline()
        if not line:
            return None
        return json.loads(line)
    except Exception as e:
        print(f"❌ Error reading data: {e}")
        return None

def run_interaction():
    print("🚀 Starting MCP Server (src.server)...")
    process = subprocess.Popen(
        [sys.executable, "-m", "src.server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0 
    )

    try:
        print("\n[Init] Sending Initialize Request...")
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05", 
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0"}
            },
            "id": 1
        }
        send_json(process, init_request)
        read_json(process) # Ack

        notify_init = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        send_json(process, notify_init)
        print("[Init] Server Initialized.")

        print("\n\n--- TEST 1: NVD CVE Lookup (Log4Shell) ---")
        cve_req = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_cve",
                "arguments": {"cve_id": "CVE-2021-44228"}
            },
            "id": 2
        }
        send_json(process, cve_req)
        resp_cve = read_json(process)
        
        if resp_cve and "result" in resp_cve:
             content_str = resp_cve["result"]["content"][0]["text"]
             cve_data = json.loads(content_str)
             print(f"✅ Success! Found CVE: {cve_data['id']}")
             print(f"   Description: {cve_data['descriptions'][0]['value'][:100]}...")
        else:
             print("❌ Failed to fetch CVE.")
             print(resp_cve)

        print("\n\n--- TEST 2: MITRE Search ('Phishing') ---")
        mitre_req = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "search_mitre_techniques",
                "arguments": {"query": "phishing"}
            },
            "id": 3
        }
        send_json(process, mitre_req)
        resp_search = read_json(process)
        
        if resp_search and "result" in resp_search:
             results = []
             for item in resp_search["result"]["content"]:
                 if item["type"] == "text":
                     data = json.loads(item["text"])
                     if isinstance(data, list):
                         results.extend(data)
                     else:
                         results.append(data)
             print(f"✅ Success! Found {len(results)} techniques.")
             for t in results:
                 print(f"   - {t['id']}: {t['name']}")
        else:
             print("❌ Failed to search MITRE.")
             print(resp_search)

        print("\n\n--- TEST 3: MITRE Technique Details (T1566) ---")
        detail_req = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_mitre_technique",
                "arguments": {"mitre_id": "T1566"}
            },
            "id": 4
        }
        send_json(process, detail_req)
        resp_detail = read_json(process)
        
        if resp_detail and "result" in resp_detail:
             content_str = resp_detail["result"]["content"][0]["text"]
             tech_data = json.loads(content_str)
             print(f"✅ Success! Got details for {tech_data.get('mitre_id')}")
             print(f"   URL: {tech_data.get('url')}")
             print(f"   Platforms: {tech_data.get('platforms')}")
        else:
             print("❌ Failed to get technique details.")
             print(resp_detail)

    except Exception as e:
        print(f"❌ Verification Error: {e}")
        print("Stderr:", process.stderr.read())
    finally:
        process.terminate()

if __name__ == "__main__":
    run_interaction()
