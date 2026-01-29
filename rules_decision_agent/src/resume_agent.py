
import os
import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner

# Document parsing imports
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResumeParser:
    """Handles parsing of various resume file formats."""
    
    @staticmethod
    def parse_file(file_path: str) -> str:
        """
        Parse resume file and extract text content.
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Extracted text content
            
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file does not exist
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix == '.pdf':
            return ResumeParser._parse_pdf(file_path)
        elif suffix == '.docx':
            return ResumeParser._parse_docx(file_path)
        elif suffix == '.txt':
            return ResumeParser._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}. Supported formats: .pdf, .docx, .txt")
    
    @staticmethod
    def _parse_pdf(file_path: str) -> str:
        """Parse PDF file."""
        if PyPDF2 is None:
            raise ImportError("PyPDF2 is required for PDF parsing. Install with: pip install PyPDF2")
        
        text = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            return '\n'.join(text)
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise ValueError(f"Failed to parse PDF file: {e}")
    
    @staticmethod
    def _parse_docx(file_path: str) -> str:
        """Parse DOCX file."""
        if docx is None:
            raise ImportError("python-docx is required for DOCX parsing. Install with: pip install python-docx")
        
        try:
            doc = docx.Document(file_path)
            text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
            return '\n'.join(text)
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            raise ValueError(f"Failed to parse DOCX file: {e}")
    
    @staticmethod
    def _parse_txt(file_path: str) -> str:
        """Parse plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error parsing TXT: {e}")
            raise ValueError(f"Failed to parse TXT file: {e}")


class ResumeAnalysisLogic:
    """Main logic for resume analysis and Q&A generation."""
    
    def __init__(self):
        self.model_name = "gemini-2.0-flash-001"
    
    def _create_extraction_agent(self) -> LlmAgent:
        """Create agent for extracting structured information from resume."""
        instruction = """
        You are a Resume Analysis Expert.
        Your task is to extract structured information from a resume text.
        
        Extract the following information:
        1. **Personal Information**: Name, email, phone, location, LinkedIn, etc.
        2. **Professional Summary**: Brief overview of the candidate's profile
        3. **Skills**: Technical skills, tools, frameworks, languages, certifications
        4. **Work Experience**: Company, role, duration, responsibilities, achievements
        5. **Education**: Degree, institution, graduation year, relevant coursework
        6. **Projects**: Project name, description, technologies used, outcomes
        7. **Achievements**: Awards, publications, notable accomplishments
        
        Return the extracted information as a well-structured JSON object.
        Be thorough and accurate. If information is not available, use null or empty arrays.
        """
        
        return LlmAgent(
            name="ResumeExtractionAgent",
            model=self.model_name,
            instruction=instruction
        )
    
    def _create_qa_generation_agent(self) -> LlmAgent:
        """Create agent for generating questions and answers."""
        instruction = """
        You are an Expert Interview Question Generator.
        Your task is to generate relevant interview questions and suggested answers based on a candidate's resume.
        
        Generate questions in the following categories:
        1. **Technical Skills**: Questions about specific technologies, tools, and frameworks mentioned
        2. **Behavioral**: STAR-format questions based on work experience and achievements
        3. **Project Deep-Dive**: Detailed questions about specific projects
        4. **Problem-Solving**: Scenario-based questions related to their domain
        
        For each question:
        - Make it specific to the candidate's experience
        - Provide a suggested answer based on resume content
        - Indicate difficulty level (entry, intermediate, advanced)
        - List related skills/technologies
        
        Generate 3-5 questions per category.
        Return as a structured JSON object with categories and questions.
        
        IMPORTANT: Base answers ONLY on information present in the resume. Do not hallucinate or invent experiences.
        """
        
        return LlmAgent(
            name="QAGenerationAgent",
            model=self.model_name,
            instruction=instruction
        )
    
    async def extract_resume_data(self, resume_text: str, log_callback=None) -> Dict[str, Any]:
        """
        Extract structured data from resume text.
        
        Args:
            resume_text: Raw text extracted from resume
            log_callback: Optional callback for logging
            
        Returns:
            Dictionary containing extracted structured data
        """
        logs = []
        def log(msg):
            logs.append(msg)
            logger.info(msg)
            if log_callback:
                log_callback(msg)
        
        log("[Extraction] Starting resume data extraction...")
        
        extraction_agent = self._create_extraction_agent()
        runner = InMemoryRunner(agent=extraction_agent, app_name="resume-extraction")
        
        session_id = f"session-{uuid4()}"
        await runner.session_service.create_session(
            app_name="resume-extraction",
            user_id="user",
            session_id=session_id
        )
        
        prompt = f"""
        Please extract structured information from the following resume:
        
        {resume_text}
        
        Return the data as a JSON object with the following structure:
        {{
            "personalInfo": {{"name": "", "email": "", "phone": "", "location": "", "linkedin": ""}},
            "summary": "",
            "skills": [],
            "experience": [
                {{"company": "", "role": "", "duration": "", "responsibilities": [], "achievements": []}}
            ],
            "education": [
                {{"degree": "", "institution": "", "year": "", "details": ""}}
            ],
            "projects": [
                {{"name": "", "description": "", "technologies": [], "outcomes": ""}}
            ],
            "achievements": []
        }}
        """
        
        msg = SimpleNamespace(role="user", parts=[SimpleNamespace(text=prompt)])
        
        iterator = runner.run_async(
            user_id="user",
            session_id=session_id,
            new_message=msg
        )
        
        response_text = ""
        async for event in iterator:
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
                response_text += text_chunk
        
        # Parse JSON from response
        extracted_data = {}
        try:
            # Try to extract JSON from markdown code block
            import re
            json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', response_text)
            if json_match:
                extracted_data = json.loads(json_match.group(1))
            else:
                # Try to parse the entire response as JSON
                extracted_data = json.loads(response_text)
            
            log(f"[Extraction] Successfully extracted data with {len(extracted_data.get('skills', []))} skills")
        except json.JSONDecodeError as e:
            log(f"[Extraction] Failed to parse JSON: {e}")
            log(f"[Extraction] Response: {response_text[:200]}...")
        
        return {
            "extractedData": extracted_data,
            "logs": logs
        }
    
    async def generate_questions_and_answers(self, extracted_data: Dict[str, Any], log_callback=None) -> Dict[str, Any]:
        """
        Generate interview questions and answers based on extracted resume data.
        
        Args:
            extracted_data: Structured data extracted from resume
            log_callback: Optional callback for logging
            
        Returns:
            Dictionary containing categorized questions and answers
        """
        logs = []
        def log(msg):
            logs.append(msg)
            logger.info(msg)
            if log_callback:
                log_callback(msg)
        
        log("[Q&A Generation] Starting question and answer generation...")
        
        qa_agent = self._create_qa_generation_agent()
        runner = InMemoryRunner(agent=qa_agent, app_name="qa-generation")
        
        session_id = f"session-{uuid4()}"
        await runner.session_service.create_session(
            app_name="qa-generation",
            user_id="user",
            session_id=session_id
        )
        
        prompt = f"""
        Based on the following resume data, generate relevant interview questions and suggested answers:
        
        {json.dumps(extracted_data, indent=2)}
        
        Return the questions and answers in the following JSON structure:
        {{
            "questionsAndAnswers": [
                {{
                    "category": "Technical Skills",
                    "questions": [
                        {{
                            "question": "...",
                            "suggestedAnswer": "...",
                            "difficulty": "intermediate",
                            "relatedSkills": ["skill1", "skill2"]
                        }}
                    ]
                }},
                {{
                    "category": "Behavioral",
                    "questions": [...]
                }},
                {{
                    "category": "Project Deep-Dive",
                    "questions": [...]
                }},
                {{
                    "category": "Problem-Solving",
                    "questions": [...]
                }}
            ]
        }}
        """
        
        msg = SimpleNamespace(role="user", parts=[SimpleNamespace(text=prompt)])
        
        iterator = runner.run_async(
            user_id="user",
            session_id=session_id,
            new_message=msg
        )
        
        response_text = ""
        async for event in iterator:
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
                response_text += text_chunk
        
        # Parse JSON from response
        qa_data = {}
        try:
            import re
            json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', response_text)
            if json_match:
                qa_data = json.loads(json_match.group(1))
            else:
                qa_data = json.loads(response_text)
            
            total_questions = sum(len(cat.get('questions', [])) for cat in qa_data.get('questionsAndAnswers', []))
            log(f"[Q&A Generation] Generated {total_questions} questions across {len(qa_data.get('questionsAndAnswers', []))} categories")
        except json.JSONDecodeError as e:
            log(f"[Q&A Generation] Failed to parse JSON: {e}")
            log(f"[Q&A Generation] Response: {response_text[:200]}...")
        
        return {
            "qaData": qa_data,
            "logs": logs
        }
    
    async def process_resume(self, file_path: str, log_callback=None) -> Dict[str, Any]:
        """
        Complete resume processing pipeline: parse, extract, and generate Q&A.
        
        Args:
            file_path: Path to resume file
            log_callback: Optional callback for logging
            
        Returns:
            Complete result with extracted data and Q&A
        """
        all_logs = []
        def log(msg):
            all_logs.append(msg)
            logger.info(msg)
            if log_callback:
                log_callback(msg)
        
        try:
            # Step 1: Parse resume file
            log(f"[Parser] Parsing resume file: {file_path}")
            resume_text = ResumeParser.parse_file(file_path)
            log(f"[Parser] Extracted {len(resume_text)} characters")
            
            # Step 2: Extract structured data
            extraction_result = await self.extract_resume_data(resume_text, log_callback=log)
            extracted_data = extraction_result.get("extractedData", {})
            all_logs.extend(extraction_result.get("logs", []))
            
            # Step 3: Generate Q&A
            qa_result = await self.generate_questions_and_answers(extracted_data, log_callback=log)
            qa_data = qa_result.get("qaData", {})
            all_logs.extend(qa_result.get("logs", []))
            
            # Combine results
            result = {
                "success": True,
                "candidateInfo": extracted_data.get("personalInfo", {}),
                "summary": extracted_data.get("summary", ""),
                "extractedData": extracted_data,
                "questionsAndAnswers": qa_data.get("questionsAndAnswers", []),
                "logs": all_logs
            }
            
            log("[Complete] Resume processing completed successfully")
            return result
            
        except Exception as e:
            log(f"[Error] Resume processing failed: {e}")
            logger.exception("Resume processing error")
            return {
                "success": False,
                "error": str(e),
                "logs": all_logs
            }
