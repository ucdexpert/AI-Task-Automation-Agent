import json
import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.services.llm_service import llm_service
from app.tools.registry import tool_registry
from app.agents.prompts import SYSTEM_PROMPT
from app.agents.memory import AgentMemory
from app.models.task import Task, AgentLog
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
        
        # 1. Add user message to memory
        self.memory.add_message(session_id=session_id, role="user", message=task.user_input)
        context_messages = self.memory.get_context_messages(session_id)
        
        # 2. Build Agent System Prompt based on context
        is_whatsapp = session_id.startswith("wa_")
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *context_messages,
            {"role": "user", "content": task.user_input}
        ]
        
        # 3. Execution Loop (Limit to 3 turns for free-tier safety)
        step_number = 0
        final_result = None
        executed_tool_signatures = set()
        
        while step_number < 2:
            step_number += 1
            step_start = time.time()
            
            llm_response = llm_service.chat_completion(
                messages=messages,
                tools=tool_registry.get_tools_schema()
            )
            
            if hasattr(llm_response, 'tool_calls') and llm_response.tool_calls:
                tool_error_occurred = False
                for tool_call in llm_response.tool_calls[:2]:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    # STRICT: Handle duplicate tool calls
                    tool_signature = f"{tool_name}_{json.dumps(tool_args, sort_keys=True)}"
                    if tool_signature in executed_tool_signatures:
                        logger.warning(f"Blocking duplicate tool call: {tool_signature}")
                        # Tell the LLM this is already done so it doesn't get stuck
                        messages.append({"role": "assistant", "content": None, "tool_calls": [tool_call]})
                        messages.append({
                            "role": "tool", 
                            "tool_call_id": tool_call.id, 
                            "content": json.dumps({"success": True, "message": "This action was already performed successfully. Do not repeat it."})
                        })
                        continue
                    
                    executed_tool_signatures.add(tool_signature)
                    
                    # Logic to ensure correct phone number for WhatsApp
                    if tool_name == "whatsapp":
                        current_to = str(tool_args.get("to_number", ""))
                        # If number is fake, missing, or a placeholder
                        if not current_to or len(current_to) < 10 or "XXXX" in current_to or "12345" in current_to:
                            if is_whatsapp:
                                tool_args["to_number"] = session_id.replace("wa_", "")
                            else:
                                tool_args["to_number"] = settings.WHATSAPP_RECIPIENT_NUMBER
                        
                        # Strip any 'wa_' if still present
                        tool_args["to_number"] = str(tool_args["to_number"]).replace("wa_", "")

                    # Send real-time update via WebSocket
                    await manager.send_personal_message({
                        "type": "log",
                        "task_id": task.id,
                        "step": step_number,
                        "action": tool_name,
                        "status": "processing",
                        "message": f"Executing tool: {tool_name}..."
                    }, session_id)

                    # Tool Execution
                    result = await tool_registry.execute_tool(tool_name, **tool_args)
                    
                    # Log to DB
                    execution_time = int((time.time() - step_start) * 1000)
                    log_entry = AgentLog(
                        task_id=task.id,
                        step_number=step_number,
                        action=tool_name,
                        input_data=tool_args,
                        output_data=result,
                        status="success" if result.get("success", False) else "failed",
                        execution_time_ms=execution_time
                    )
                    self.db.add(log_entry)
                    self.db.commit()
                    
                    # Send update after execution
                    await manager.send_personal_message({
                        "type": "log_result",
                        "task_id": task.id,
                        "step": step_number,
                        "action": tool_name,
                        "status": log_entry.status,
                        "result": result
                    }, session_id)

                    # CRITICAL: If tool failed, STOP everything
                    if not result.get("success", False):
                        final_result = f"Task stopped due to error in {tool_name}: {result.get('message', 'Unknown error')}"
                        tool_error_occurred = True
                        break
                    
                    tools_used.append(tool_name)
                    logs.append({"step": step_number, "tool": tool_name, "result": result})
                    
                    # Feed tool output back to LLM
                    messages.append({"role": "assistant", "content": None, "tool_calls": [tool_call]})
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})
                
                # Break the outer while loop if a tool failed
                if tool_error_occurred:
                    break
            else:
                final_result = llm_response.content
                break
        
        # 4. Save Final Memory (Only if message is not None)
        if final_result:
            self.memory.add_message(session_id=session_id, role="assistant", message=final_result)
        else:
            logger.warning(f"Assistant generated an empty response for session {session_id}")
            final_result = "Task completed via tools, but no final summary was generated."
        
        return {
            "success": True,
            "result": final_result,
            "tools_used": list(set(tools_used)),
            "steps": step_number,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            "logs": logs
        }
