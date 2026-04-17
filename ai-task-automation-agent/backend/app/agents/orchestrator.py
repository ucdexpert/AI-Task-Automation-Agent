import json
import time
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.services.llm_service import llm_service
from app.tools.registry import tool_registry
from app.agents.prompts import (
    SYSTEM_PROMPT, 
    ROUTER_PROMPT, 
    RESEARCHER_PROMPT, 
    EXECUTOR_PROMPT, 
    COMMUNICATOR_PROMPT
)
from app.agents.memory import AgentMemory
from app.models.task import Task, AgentLog
from app.models.user import User
from app.services.websocket_service import manager
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class MultiAgentOrchestrator:
    """
    Advanced Orchestrator that uses specialized agent personas
    and handles complex multi-step workflows.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.memory = AgentMemory(db)
    
    async def process_task(self, task: Task, session_id: str) -> Dict[str, Any]:
        """
        Process task using specialized agent logic
        """
        start_time = time.time()
        tools_used = []
        logs = []
        
        # 1. Fetch User details for dynamic notification
        user = self.db.query(User).filter(User.id == task.user_id).first()
        user_email = user.email if user else settings.EMAIL_ADDRESS
        user_name = user.full_name if user else "User"
        # Since phone_number is not in User model yet, we can check if it's in session_id or use default
        user_phone = settings.WHATSAPP_RECIPIENT_NUMBER
        if session_id.startswith("wa_"):
            user_phone = session_id.replace("wa_", "")

        # 1.5 Add user message to memory
        self.memory.add_message(session_id=session_id, role="user", message=task.user_input)
        context_messages = self.memory.get_context_messages(session_id)
        
        # 2. ROUTING PHASE: Decide which expert to use
        # Inject user info into system context
        user_info_context = f"\n\nCURRENT USER INFO:\n- Name: {user_name}\n- Email: {user_email}\n- WhatsApp: {user_phone}\nAlways use these details for notifications unless the user specifies otherwise."
        
        routing_messages = [
            {"role": "system", "content": ROUTER_PROMPT + user_info_context},
            {"role": "user", "content": f"Task: {task.user_input}\nContext: {json.dumps(context_messages)}"}
        ]
        
        route_response = llm_service.chat_completion(messages=routing_messages)
        route_content = route_response.content.upper()
        
        current_agent_prompt = SYSTEM_PROMPT # Default
        available_tools = tool_registry.get_tools_schema() # Default all
        
        if "RESEARCHER" in route_content:
            logger.info("Routing to RESEARCHER expert")
            current_agent_prompt = RESEARCHER_PROMPT
            # Optional: Filter tools for Researcher only
            # researcher_tools = ["web_search", "web_scraper"]
        elif "EXECUTOR" in route_content:
            logger.info("Routing to EXECUTOR expert")
            current_agent_prompt = EXECUTOR_PROMPT
        elif "COMMUNICATOR" in route_content:
            logger.info("Routing to COMMUNICATOR expert")
            current_agent_prompt = COMMUNICATOR_PROMPT
        
        messages = [
            {"role": "system", "content": current_agent_prompt},
            *context_messages,
            {"role": "user", "content": task.user_input}
        ]
        
        # 3. Execution Loop (Limit to 4 turns for complex tasks)
        step_number = 0
        final_result = None
        executed_tool_signatures = set()
        
        while step_number < 4:
            step_number += 1
            step_start = time.time()
            
            try:
                llm_response = llm_service.chat_completion(
                    messages=messages,
                    tools=tool_registry.get_tools_schema()
                )
            except Exception as e:
                error_msg = str(e)
                if "400" in error_msg or "tool_use_failed" in error_msg:
                    logger.warning(f"LLM tool call failed with 400 error. Attempting to fix via prompt correction. Error: {error_msg}")
                    # Extract tool name and args if possible from error message to manually fix
                    # Or just tell the model it messed up the format
                    messages.append({"role": "user", "content": f"ERROR: You used the wrong format for a tool call. NEVER use <function=...> or string-based tool calls. Please use the official tool-calling schema only. Retrying step {step_number}..."})
                    continue
                else:
                    logger.error(f"LLM call failed: {error_msg}")
                    break
            
            # PROTECT & RECOVER: Catch text-based tool calls (hallucinations)
            content = llm_response.content or ""
            # Improved regex to catch more variations of hallucinations
            text_tool_match = re.search(r'\{(\w+)\s*(\{.*?\})\}', content) or \
                             re.search(r'<function=(\w+)>(.*?)</function>', content) or \
                             re.search(r'<function=(\w+)=(.*?)></function>', content)
            
            if text_tool_match and not (hasattr(llm_response, 'tool_calls') and llm_response.tool_calls):
                tool_name = text_tool_match.group(1)
                args_str = text_tool_match.group(2)
                logger.warning(f"Detected text-based tool call: {tool_name}. Executing via recovery logic.")
                
                try:
                    # Clean up args_str if it contains the equals sign or is missing one
                    if args_str.startswith('='):
                        args_str = args_str[1:]
                    
                    tool_args = json.loads(args_str)
                    result = await tool_registry.execute_tool(tool_name, **tool_args)
                    
                    # LOG TO DB (Crucial for UI)
                    log_entry = AgentLog(
                        task_id=task.id,
                        step_number=step_number,
                        action=tool_name,
                        input_data=tool_args,
                        output_data=result,
                        status="success" if result.get("success", False) else "failed"
                    )
                    self.db.add(log_entry)
                    self.db.commit()
                    
                    # Feed it back as if it was a real tool call to keep the loop going
                    messages.append({"role": "assistant", "content": content})
                    messages.append({"role": "user", "content": f"Tool {tool_name} executed successfully. Result: {json.dumps(result)}. Continue to the next step or provide a final summary in Hinglish."})
                    tools_used.append(tool_name)
                    logs.append({"step": step_number, "tool": tool_name, "result": result})
                    continue
                except Exception as parse_error:
                    logger.error(f"Failed to parse text-based tool args: {parse_error}")
                    messages.append({"role": "assistant", "content": content})
                    messages.append({"role": "user", "content": f"Error: I couldn't parse your tool call for {tool_name}. Please use the ACTUAL tool calling feature, don't just write it as text."})
                    continue
            
            if hasattr(llm_response, 'tool_calls') and llm_response.tool_calls:
                tool_error_occurred = False
                for tool_call in llm_response.tool_calls[:2]:
                    # ... (rest of tool execution logic)
                    # Note: I'm keeping the logic here but ensuring it continues correctly
                    tool_name = tool_call.function.name
                    arguments_str = tool_call.function.arguments or "{}"
                    try:
                        tool_args = json.loads(arguments_str)
                        if not isinstance(tool_args, dict):
                            tool_args = {}
                    except json.JSONDecodeError:
                        tool_args = {}
                    
                    # Logic to ensure correct phone number for WhatsApp
                    if tool_name == "whatsapp":
                        current_to = str(tool_args.get("to_number", ""))
                        if not current_to or len(current_to) < 10 or "XXXX" in current_to:
                            tool_args["to_number"] = settings.WHATSAPP_RECIPIENT_NUMBER
                    
                    # Tool Execution
                    result = await tool_registry.execute_tool(tool_name, **tool_args)
                    
                    # Log to DB
                    log_entry = AgentLog(
                        task_id=task.id,
                        step_number=step_number,
                        action=tool_name,
                        input_data=tool_args,
                        output_data=result,
                        status="success" if result.get("success", False) else "failed"
                    )
                    self.db.add(log_entry)
                    self.db.commit()

                    # Feed tool output back to LLM
                    messages.append({"role": "assistant", "content": None, "tool_calls": [tool_call]})
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})
                    
                    if result.get("success", False):
                        tools_used.append(tool_name)
                        logs.append({"step": step_number, "tool": tool_name, "result": result})
                    else:
                        logger.warning(f"Tool {tool_name} failed: {result.get('message')}")
                        # Don't break, let the LLM see the error and retry in the next step
                        tool_error_occurred = True
                
                # If everything in this turn failed, we continue the while loop to give LLM another chance
                if tool_error_occurred:
                    continue
            else:
                final_result = llm_response.content
                break
        
        # 4. FINAL FALLBACK: If loop ended without a final_result, generate one!
        if not final_result or step_number >= 4:
            logger.info("Generating final summary fallback...")
            summary_prompt = messages + [{"role": "user", "content": "The execution loop has ended. Please provide a concise final summary of all the information gathered and actions taken above."}]
            summary_response = llm_service.chat_completion(messages=summary_prompt)
            final_result = summary_response.content
        
        # 5. Save Final Memory
        success_status = True
        if final_result and "stopped due to error" in str(final_result):
            success_status = False
        
        if final_result:
            self.memory.add_message(session_id=session_id, role="assistant", message=final_result)
        
        return {
            "success": success_status,
            "result": final_result,
            "tools_used": list(set(tools_used)),
            "steps": step_number,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            "logs": logs
        }
