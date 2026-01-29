
import asyncio
import os
import uuid
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from a2a.server.apps import A2AFastAPIApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor
from a2a.types import AgentCard, AgentInterface, Message, Role, TaskStatus, TaskState, TextPart, ContentTypeNotSupportedError
from src.agent import RulesDecisionLogic

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RulesAgentExecutor(AgentExecutor):
    async def cancel(self, context, event_queue):
        logger.info(f"Cancel requested for task {context.task_id}")
        # Logic to cancel running agent if possible
        # For now, just accept it.
        pass

    async def execute(self, context, event_queue):
        logger.info(f"Execute called with context: {vars(context)}")
        
        # Extract prompt
        # Context structure depends on request type (Task or Message)
        prompt = ""
        
        # Try to find message in context
        # Try to find message in context
        input_msg = getattr(context, 'message', None)
        if input_msg and hasattr(input_msg, 'parts') and input_msg.parts:
            for part in input_msg.parts:
                # Part might be a RootModel or Union
                actual_part = part.root if hasattr(part, 'root') else part
                
                if isinstance(actual_part, TextPart):
                    prompt += actual_part.text
                elif hasattr(actual_part, 'text') and getattr(actual_part, 'kind', '') == 'text':
                     prompt += actual_part.text
        
        # If no message, maybe it's a new task with description?
        if not prompt and getattr(context, 'task', None):
             prompt = context.task.description or ""
             
        if not prompt:
             logger.warning("No prompt found in context")
             prompt = "Hello based on no input?"

        logger.info(f"Running Logic with prompt: {prompt}")
        
        # Run Logic
        logic = RulesDecisionLogic()
        try:
            result = await logic.execute(prompt)
            
            # Format response
            response_text = json.dumps(result, indent=2)
            
            # Ensure we have a task_id to group events
            # If context.task_id is None (implicit creation), we should ideally generate one 
            # or rely on framework. But to keep events together, let's generate if missing.
            current_task_id = context.task_id or str(uuid.uuid4())

            # Construct message with results
            response_msg = Message(
                message_id=f"msg-{uuid.uuid4()}",
                task_id=current_task_id,
                role=Role.agent,
                parts=[TextPart(text=response_text)]
            )
            
            await event_queue.enqueue_event(response_msg)
            
            # Also publish TaskStatus COMPLETE if it was a task
            from a2a.types import TaskStatusUpdateEvent
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=current_task_id,
                    context_id=context.context_id,
                    status=TaskStatus(state=TaskState.completed),
                    final=True
                )
            )
            
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            from a2a.types import TaskStatusUpdateEvent
            # Use context.task_id if available, otherwise we might create a new one for error
            # If we generated current_task_id inside try, we lost it?
            # Let's rely on context.task_id or None for error (framework handles it)
            # Or better, move current_task_id definition up.
            t_id = context.task_id or str(uuid.uuid4())
            
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=t_id,
                    context_id=context.context_id,
                    status=TaskStatus(
                        state=TaskState.failed,
                        reason=str(e)
                    ),
                    final=True
                )
            )
        finally:
            await logic.close()

import json

# Define Agent Card
# Based on validation errors: AgentCard needs defaults, description, name etc. top level or in specific nested structure.
# Let's inspect signature or try to fill based on error.
# Error says AgentCard needs: capabilities, defaultInputModes, defaultOutputModes, description, name, skills, url.
# It seems "interface" might not be the only field or I am using strict SDK version.

from a2a.types import AgentCapabilities

agent_card = AgentCard(
    name="rules_decision_agent",
    description="Agent that decides on business rules based on input.",
    version="0.1.0",
    url="http://localhost:8001",
    capabilities=AgentCapabilities(
        input_types=["text"],
        output_types=["text"],
        supports_streaming=False
    ),
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
    skills=[],
    interface=AgentInterface(
        name="rules_decision_agent",
        description="Agent that decides on business rules based on input.",
        input_schema={"type": "object", "properties": {"text": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"result": {"type": "string"}}},
        transport="http",
        url="http://localhost:8001/a2a"
    )
)

# Setup Components
task_store = InMemoryTaskStore()
executor = RulesAgentExecutor()
request_handler = DefaultRequestHandler(
    agent_executor=executor,
    task_store=task_store
)

# FastAPI App
app = FastAPI()

# Initialize A2A App
a2a_app = A2AFastAPIApplication(
    agent_card=agent_card,
    http_handler=request_handler
)

# Mount Routes
a2a_app.add_routes_to_app(app)

# Add Resume Processing Endpoints
from fastapi import UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import shutil

@app.post("/resume/extract")
async def extract_resume_qa(file: UploadFile = File(...)):
    """
    Extract questions and answers from uploaded resume.
    
    Accepts: PDF, DOCX, TXT files
    Returns: JSON with candidate info, extracted data, and Q&A
    """
    # Validate file extension
    allowed_extensions = {'.pdf', '.docx', '.txt'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_ext}. Supported: {', '.join(allowed_extensions)}"
        )
    
    # Save uploaded file to temporary location
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            temp_file = tmp.name
            shutil.copyfileobj(file.file, tmp)
        
        # Process resume
        from src.resume_agent import ResumeAnalysisLogic
        logic = ResumeAnalysisLogic()
        result = await logic.process_resume(temp_file)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Resume processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)

@app.get("/resume/formats")
async def get_supported_formats():
    """Get list of supported resume file formats."""
    return {
        "supportedFormats": [
            {"extension": ".pdf", "description": "PDF documents"},
            {"extension": ".docx", "description": "Microsoft Word documents"},
            {"extension": ".txt", "description": "Plain text files"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
