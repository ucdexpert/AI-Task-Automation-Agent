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
        
        # 3. Execution Loop (Max 10 steps)
        step_number = 0
        final_result = None
        
        while step_number < 10:
            step_number += 1
            step_start = time.time()
            
            llm_response = llm_service.chat_completion(
                messages=messages,
                tools=tool_registry.get_tools_schema()
            )
            
            if hasattr(llm_response, 'tool_calls') and llm_response.tool_calls:
                for tool_call in llm_response.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    # Logic to ensure correct phone number for WhatsApp
                    if tool_name == "whatsapp":
                        # If Agent sends a placeholder like 'wa_XXXX' or 'user_phone_number'
                        current_to = tool_args.get("to_number", "")
                        if not current_to or "XXXX" in current_to or "phone" in current_to:
                            if is_whatsapp:
                                tool_args["to_number"] = session_id.replace("wa_", "")
                            else:
                                tool_args["to_number"] = settings.WHATSAPP_RECIPIENT_NUMBER
                        
                        # Ensure no 'wa_' prefix in the final number sent to Meta
                        if isinstance(tool_args["to_number"], str):
                            tool_args["to_number"] = tool_args["to_number"].replace("wa_", "")

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
                    
                    tools_used.append(tool_name)
                    logs.append({"step": step_number, "tool": tool_name, "result": result})
                    
                    # Feed tool output back to LLM
                    messages.append({"role": "assistant", "content": None, "tool_calls": [tool_call]})
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})
            else:
                final_result = llm_response.content
                break
        
        # 4. Save Final Memory
        self.memory.add_message(session_id=session_id, role="assistant", message=final_result)
        
        return {
            "success": True,
            "result": final_result,
            "tools_used": list(set(tools_used)),
            "steps": step_number,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            "logs": logs
        }
