import json
import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.services.llm_service import llm_service
from app.tools.registry import tool_registry
from app.agents.prompts import SYSTEM_PROMPT, TASK_ANALYSIS_PROMPT
from app.agents.memory import AgentMemory
from app.models.task import Task, AgentLog
from app.config import settings

class AgentOrchestrator:
    """
    Main agent orchestrator that processes tasks using LLM and tools
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.memory = AgentMemory(db)
    
    async def process_task(self, task: Task, session_id: str) -> Dict[str, Any]:
        """
        Process a user task using LLM and available tools
        """
        start_time = time.time()
        tools_used = []
        logs = []
        
        try:
            # Add user message to memory
            self.memory.add_message(
                session_id=session_id,
                role="user",
                message=task.user_input
            )
            
            # Get conversation context
            context_messages = self.memory.get_context_messages(session_id)
            
            # Build messages for LLM
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                *context_messages,
                {"role": "user", "content": task.user_input}
            ]
            
            # Get tools schema
            tools_schema = tool_registry.get_tools_schema()
            
            # Call LLM with tool support
            step_number = 0
            max_iterations = 10
            final_result = None
            
            while step_number < max_iterations:
                step_number += 1
                step_start = time.time()
                
                # Get LLM response with tool calling
                llm_response = llm_service.chat_completion(
                    messages=messages,
                    tools=tools_schema
                )
                
                # Check if LLM wants to use tools
                if hasattr(llm_response, 'tool_calls') and llm_response.tool_calls:
                    # Execute tool calls
                    for tool_call in llm_response.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        
                        # Log tool execution
                        log_entry = AgentLog(
                            task_id=task.id,
                            step_number=step_number,
                            action=tool_name,
                            input_data=tool_args,
                            status="processing"
                        )
                        self.db.add(log_entry)
                        self.db.commit()
                        
                        # Execute tool
                        result = await tool_registry.execute_tool(tool_name, **tool_args)
                        
                        # Update log
                        execution_time = int((time.time() - step_start) * 1000)
                        log_entry.output_data = result
                        log_entry.status = "success" if result.get("success", False) else "failed"
                        log_entry.execution_time_ms = execution_time
                        self.db.commit()
                        
                        tools_used.append(tool_name)
                        logs.append({
                            "step": step_number,
                            "tool": tool_name,
                            "result": result
                        })
                        
                        # Add tool response to messages
                        messages.append({
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [tool_call]
                        })
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result)
                        })
                        
                        # If tool failed, stop execution
                        if not result.get("success", False):
                            final_result = f"Task stopped due to tool error: {result.get('message', 'Unknown error')}"
                            break
                    
                    if final_result:
                        break
                else:
                    # LLM provided a final response
                    final_result = llm_response.content
                    messages.append({"role": "assistant", "content": final_result})
                    break
            
            if not final_result:
                final_result = "Task processing completed but no result generated"
            
            # Save assistant response to memory
            self.memory.add_message(
                session_id=session_id,
                role="assistant",
                message=final_result,
                extra_data={"tools_used": tools_used, "steps": step_number}
            )
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return {
                "success": True,
                "result": final_result,
                "tools_used": list(set(tools_used)),
                "steps": step_number,
                "execution_time_ms": execution_time,
                "logs": logs
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log error
            log_entry = AgentLog(
                task_id=task.id,
                step_number=step_number + 1,
                action="error",
                input_data={"error": str(e)},
                status="failed",
                execution_time_ms=execution_time
            )
            self.db.add(log_entry)
            self.db.commit()
            
            return {
                "success": False,
                "result": None,
                "error": str(e),
                "tools_used": list(set(tools_used)),
                "execution_time_ms": execution_time
            }
