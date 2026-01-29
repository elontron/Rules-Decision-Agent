
import os
import json
import logging
import re
import asyncio
from typing import Optional, Dict, Any, List
from types import SimpleNamespace
from uuid import uuid4
from dotenv import load_dotenv

from google.adk.agents import Agent, LlmAgent
from google.adk.runners import InMemoryRunner
try:
    from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
except ImportError as e:
    # Fallback or placeholder - will check exact import later
    MCPToolset = None
    StreamableHTTPConnectionParams = None

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
# Path to db.json relative to this file
# agent.py is in src/, so ../../rule-mngt-app/rules-data/db.json relative to src/
# Actually we are in a2a-adk-agents/rules_decision_agent/src
# db is in rule-mngt-app/rules-data/db.json
# Path from rules_decision_agent/src to root: ../../..
# Path from root to db: rule-mngt-app/rules-data/db.json
# Total relative: ../../../rule-mngt-app/rules-data/db.json
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../rule-mngt-app/rules-data/db.json"))

class RulesDecisionLogic:
    def __init__(self, mcp_url: str = "http://localhost:8080/mcp"):
        self.model_name = "gemini-2.5-flash"
        
        # Initialize MCP Toolset
        if MCPToolset and StreamableHTTPConnectionParams:
            self.mcp_toolset = MCPToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url=mcp_url
                )
            )
        else:
            logger.error("MCPToolset class not found or imported")
            self.mcp_toolset = None
            
        self.db = self._load_db()

    def _load_db(self):
        try:
            logger.info(f"Loading DB from {DB_PATH}")
            with open(DB_PATH, 'r') as f:
                data = json.load(f)
            logger.info(f"DB loaded. Rules: {len(data.get('rules', {}))}")
            return data
        except Exception as e:
            logger.error(f"Failed to load db.json: {e}")
            return {"rules": {}}

    async def close(self):
        if self.mcp_toolset and hasattr(self.mcp_toolset, 'close'):
            if asyncio.iscoroutinefunction(self.mcp_toolset.close):
                await self.mcp_toolset.close()
            else:
                self.mcp_toolset.close()
                

    def _create_discovery_agent(self):
        instruction = """
        You are the Discovery Agent.
        Your goal is to identify the best business rule for a given user prompt.

        Follow this process:
        1.  **Get Categories**: Call 'get_all_categories' to see what business categories are available.
        2.  **Infer Category**: Analyze the user prompt to infer the most likely business category from the available list.
        3.  **List Rules**: Use 'list_rules_by_category' to find rules for that category.
        4.  **Select Rule**: Identify the single best matching rule based on its name and description.
        
        OUTPUT:
        You must return the ID of the selected rule clearly in your final response.
        Format: "SELECTED_RULE_ID: <id>"
        """
        
        tools = [self.mcp_toolset] if self.mcp_toolset else []
        
        return LlmAgent(
            name="DiscoveryAgent",
            model=self.model_name,
            tools=tools,
            instruction=instruction
        )

    def _create_analysis_agent(self):
        instruction = """
        You are the Analysis Agent.
        Your goal is to extract data and evaluate a specific business rule.

        You will be given a Rule ID and a User Prompt.
        
        Follow this process:
        1.  **Get Requirements**: Call 'get_rule_requirements' with the provided Rule ID to understand what data is needed.
        2.  **Extract Data**: 
            - **CRITICAL**: Read the output of 'get_rule_requirements' carefully. It contains a list of fields required by the rule (e.g., fields involved in conditions).
            - Scan the User Prompt to find values for EACH of these required fields.
            - Construct a clean JSON object with the extracted data.
        3.  **Evaluate**: Use 'evaluate_rule_logic' with the extracted data and known Rule ID.
        4.  **Report**: Output the full evaluation result and recommended actions.
        """
        
        tools = [self.mcp_toolset] if self.mcp_toolset else []

        return LlmAgent(
            name="AnalysisAgent",
            model=self.model_name,
            tools=tools,
            instruction=instruction
        )

    async def execute(self, user_prompt: str, log_callback=None):
        logs = []
        def log(msg):
            logs.append(msg)
            logger.info(msg)
            if log_callback:
                log_callback(msg)

        selected_rule_id = None
        analysis_response = None
        actions = []
        
        try:
            # 1. Discovery Phase
            log('--- Phase 1: Discovery ---')
            discovery_agent = self._create_discovery_agent()
            # Explicit app_name to match create_session
            discovery_runner = InMemoryRunner(agent=discovery_agent, app_name="discovery-agent")
            
            discovery_session_id = f"session-{uuid4()}"
            await discovery_runner.session_service.create_session(
                app_name="discovery-agent",
                user_id="user",
                session_id=discovery_session_id
            )
            
            msg = SimpleNamespace(role="user", parts=[SimpleNamespace(text=user_prompt)])
            
            # Pass app_name to run_async just in case, though constructor should handle it
            discovery_iterator = discovery_runner.run_async(
                user_id="user",
                session_id=discovery_session_id,
                new_message=msg
            )
            
            full_discovery_text = ""
            
            async for event in discovery_iterator:
                text_chunk = ""
                # Handle delta if streaming (ADK often streams)
                if hasattr(event, "delta") and event.delta and hasattr(event.delta, "content"):
                     for part in event.delta.content.parts:
                         if hasattr(part, "text") and part.text:
                             text_chunk += part.text
                elif hasattr(event, "content") and event.content:
                     for part in event.content.parts:
                         if hasattr(part, "text") and part.text:
                             text_chunk += part.text
                             
                if text_chunk:
                    full_discovery_text += text_chunk
            
            # Post-loop check
            match = re.search(r"SELECTED_RULE_ID:\s*(\w+)", full_discovery_text)
            if match:
                selected_rule_id = match.group(1)
                log(f"[Discovery] Selected Rule: {selected_rule_id}")
            else:
                 log(f"[Discovery] Failed to find rule ID in: {full_discovery_text[:100]}...")

            if not selected_rule_id:
                log('Failed to select a rule.')
                return {
                    "selectedRuleId": selected_rule_id,
                    "analysisResponse": analysis_response,
                    "logs": logs,
                    "actions": actions
                }

            # 2. Analysis Phase
            log('\n--- Phase 2: Analysis ---')
            analysis_agent = self._create_analysis_agent()
            analysis_runner = InMemoryRunner(agent=analysis_agent, app_name="analysis-agent")
            
            analysis_session_id = f"session-analysis-{uuid4()}"
            await analysis_runner.session_service.create_session(
                app_name="analysis-agent",
                user_id="user",
                session_id=analysis_session_id
            )
            
            analysis_prompt_text = f"""
            Selected Rule ID: {selected_rule_id}
            Original User Prompt: "{user_prompt}"
            
            Task:
            1. Extract all parameter values required by this rule from the prompt.
            2. Specifically look for 'orderId', 'netValue', 'grossMargin', 'material' (or product), 'materialGroup'.
            3. Map 'CMP_SLURRY' to 'materialGroup' or 'material' if applicable.
            4. Return the data as a JSON object inside a JSON block.
            """
            
            msg = SimpleNamespace(role="user", parts=[SimpleNamespace(text=analysis_prompt_text)])
            
            analysis_iterator = analysis_runner.run_async(
                user_id="user",
                session_id=analysis_session_id,
                new_message=msg
            )
            
            analysis_response = ""
            async for event in analysis_iterator:
                 text_chunk = ""
                 if hasattr(event, "delta") and event.delta and hasattr(event.delta, "content"):
                     for part in event.delta.content.parts:
                         if hasattr(part, "text") and part.text:
                             text_chunk += part.text
                 elif hasattr(event, "content") and event.content:
                     for part in event.content.parts:
                         if hasattr(part, "text") and part.text:
                             text_chunk += part.text
                
                 if text_chunk:
                     log(f"[Analysis] Response Chunk: {text_chunk[:50]}...")
                     analysis_response += text_chunk

            # Parse extracted data
            extracted_data = {}
            if analysis_response:
                json_match = re.search(r"```json\n([\s\S]*?)\n```", analysis_response)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group(1))
                        extracted_data = parsed.get("extracted_data", parsed)
                        log(f"[Logic] Extracted Data: {json.dumps(extracted_data)}")
                    except Exception as e:
                        log(f"[Logic] Failed to parse analysis JSON: {e}")
            
            # Load Actions and Populate
            rules = self.db.get("rules", {})
            rule_def = rules.get(selected_rule_id)
            if rule_def and "actions" in rule_def:
                actions = json.loads(json.dumps(rule_def["actions"])) # Deep clone
                
                # Recursive replace
                self._populate_actions(actions, extracted_data)
                log(f"[Logic] Populated {len(actions)} actions.")
            else:
                log(f"[Logic] No rule definition found for {selected_rule_id}")

        except Exception as e:
            log(f"Error: {e}")
            logger.exception("Execution failed")

        return {
            "selectedRuleId": selected_rule_id,
            "analysisResponse": analysis_response,
            "logs": logs,
            "actions": actions
        }

    def _populate_actions(self, obj, extracted_data):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str):
                    # Replace <param> or {{param}}
                    # Match <param>
                    value = re.sub(r'<([\w.]+)>', lambda m: str(self._get_val(extracted_data, m.group(1)) or m.group(0)), value)
                    # Match {{param}}
                    value = re.sub(r'{{([\w.]+)}}', lambda m: str(self._get_val(extracted_data, m.group(1)) or m.group(0)), value)
                    obj[key] = value
                elif isinstance(value, (dict, list)):
                    self._populate_actions(value, extracted_data)
        elif isinstance(obj, list):
            for item in obj:
                self._populate_actions(item, extracted_data)
                
    def _get_val(self, data, key):
        # Handle nested keys if needed, or simple keys
        # logic.ts prototype assumed simple or flat matching for logic.ts keys
        # logic.ts: "extractedData[p1] || extractedData[p1.split('.').pop() || '']"
        val = data.get(key)
        if val is None:
             val = data.get(key.split('.')[-1])
        return val
