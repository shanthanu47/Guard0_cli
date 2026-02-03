import os
import json
import re
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
from src.tools.nvd import nvd_client
from src.tools.mitre import mitre_tool

load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1:free") # Fallback to free tier if env missing

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# --- Tool Definitions ---
TOOLS = [
    {
        "name": "get_cve_details",
        "description": "Fetch details for a specific CVE ID (e.g. CVE-2021-44228). Returns CVSS score, description, and affected configurations.",
        "parameters": {
            "type": "object",
            "properties": {
                "cve_id": {"type": "string", "description": "The CVE ID to lookup."}
            },
            "required": ["cve_id"]
        }
    },
    {
        "name": "search_mitre_knowledge",
        "description": "Search for MITRE ATT&CK Techniques/Tactics by keyword. Use this to find Technique IDs (Txxxx) or learn about specific attacks (e.g. 'Phishing').",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search keyword."}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_mitre_technique",
        "description": "Get detailed information for a specific MITRE Technique ID (e.g. T1059).",
        "parameters": {
            "type": "object",
            "properties": {
                "mitre_id": {"type": "string", "description": "The T-code (e.g. T1059)."}
            },
            "required": ["mitre_id"]
        }
    }
]

SYSTEM_PROMPT = f"""
You are a Cyber Security Analyst Assistant CLI.
You have access to the following tools:
{json.dumps(TOOLS, indent=2)}

## Instructions
1. You must answer the user's question accurately using the provided tools.
2. You operate in a **Reason + Act** loop.
3. For EVERY step, output your thought process, followed by one of two actions:
    a) **Execute Tool**: Output a JSON block to call a tool.
    b) **Final Answer**: Output the final response to the user.

## Format
To call a tool, use this EXACT format (markdown code block):
```json
{{
  "action": "execute_tool",
  "tool_name": "get_cve_details",
  "arguments": {{ "cve_id": "CVE-2021-44228" }}
}}
```

To provide the answer, use this format:
```json
{{
  "action": "final_answer",
  "content": "The Log4j vulnerability..."
}}
```

## Constraints
- **CRITICAL**: You MUST use the JSON format above. Do not output raw text outside the thought block.
- **CRITICAL**: Look up NVD data for CVEs and MITRE data for TTPs.
- If the user asks a general question, use "final_answer".
"""

class Agent:
    def __init__(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def chat(self, user_input: str):
        self.messages.append({"role": "user", "content": user_input})
        
        step_count = 0
        MAX_STEPS = 5
        
        while step_count < MAX_STEPS:
            # 1. Get LLM Response
            yield ("debug", f"Sending request to LLM (Step {step_count})...")
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=self.messages,
                    temperature=0.1,
                    extra_headers={
                        "HTTP-Referer": "https://github.com/vuln-bot",
                        "X-Title": "VulnBot CLI",
                    }
                )
                # DEBUG: Inspect the raw object
                yield ("debug", f"Raw Response Type: {type(response)}")
                # yield ("debug", f"Raw Response: {response}") 
                
                if not response or not response.choices:
                     yield ("error", "LLM returned empty response or no choices.")
                     return

            except Exception as e:
                error_msg = str(e)
                if "401" in error_msg:
                    yield ("error", "Authentication Failed (401). Please check your OPENROUTER_API_KEY in the .env file.")
                else:
                    yield ("error", f"LLM API Connection Error: {error_msg}")
                return # Stop generator

            content = response.choices[0].message.content
            yield ("debug", f"LLM Response: {content[:100]}...") # Log preview
            self.messages.append({"role": "assistant", "content": content})
            
            # 2. Parse Action
            action_data = self._parse_json_action(content)
            
            if not action_data:
                yield ("debug", "No JSON action found. Treating as final answer.")
                yield ("final", content)
                return 
            
            action_type = action_data.get("action")
            yield ("debug", f"Action Type: {action_type}")
            
            # 3. Handle Final Answer
            if action_type == "final_answer":
                yield ("final", action_data.get("content"))
                return
            
            # 4. Handle Tool Execution
            elif action_type == "execute_tool":
                tool_name = action_data.get("tool_name")
                args = action_data.get("arguments", {})
                
                yield ("log", f"🛠️ Executing {tool_name} with args {args}...")
                
                try:
                    result = self._execute_tool(tool_name, args)
                    yield ("data", result)
                    yield ("debug", f"Tool Result: {str(result)[:100]}...")
                except Exception as e:
                    yield ("error", f"Tool Execution Failed: {str(e)}")
                    result = {"error": str(e)}
                
                # Feed observation back
                observation = f"Observation: {json.dumps(result)}"
                self.messages.append({"role": "user", "content": observation})
                step_count += 1
            
            else:
                yield ("error", f"Unknown action type: {action_type}")
                return

        yield ("error", "Maximum recursion steps reached.")

    def _parse_json_action(self, text: str):
        """Extracts the JSON block from the LLM response."""
        try:
            # Look for ```json ... ```
            match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            
            # Fallback: look for raw JSON object at end
            match = re.search(r"(\{.*\})$", text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
                
        except json.JSONDecodeError:
            return None
        return None

    def _execute_tool(self, tool_name, args):
        try:
            if tool_name == "get_cve_details":
                return nvd_client.get_cve(args.get("cve_id"))
            elif tool_name == "search_mitre_knowledge":
                return mitre_tool.search_techniques(args.get("query"))
            elif tool_name == "get_mitre_technique":
                return mitre_tool.get_technique(args.get("mitre_id"))
            else:
                return {"error": "Tool not found"}
        except Exception as e:
            return {"error": str(e)}

# Singleton
agent = Agent()
