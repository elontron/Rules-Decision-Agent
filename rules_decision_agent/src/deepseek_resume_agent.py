"""
DeepSeek Resume Analysis Agent
Uses DeepSeek API (OpenAI-compatible) for resume processing
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeepSeekResumeAnalyzer:
    """Resume analysis using DeepSeek API."""
    
    def __init__(self):
        """Initialize DeepSeek client."""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
        
        # DeepSeek uses OpenAI-compatible API
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.model_name = "deepseek-chat"
        logger.info(f"Initialized DeepSeek client with model: {self.model_name}")
    
    def extract_resume_data(self, resume_text: str, log_callback=None) -> Dict[str, Any]:
        """
        Extract structured data from resume text using DeepSeek.
        
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
        
        log("[DeepSeek Extraction] Starting resume data extraction...")
        
        prompt = f"""You are a Resume Analysis Expert.
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

Resume text:
{resume_text}

Return ONLY a valid JSON object with the following structure (no markdown, no explanations):
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
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a professional resume analyzer. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            response_text = response.choices[0].message.content
            
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
                
                log(f"[DeepSeek Extraction] Successfully extracted data with {len(extracted_data.get('skills', []))} skills")
            except json.JSONDecodeError as e:
                log(f"[DeepSeek Extraction] Failed to parse JSON: {e}")
                log(f"[DeepSeek Extraction] Response: {response_text[:200]}...")
            
            return {
                "extractedData": extracted_data,
                "logs": logs
            }
            
        except Exception as e:
            log(f"[DeepSeek Extraction] Error: {e}")
            logger.exception("DeepSeek extraction error")
            return {
                "extractedData": {},
                "logs": logs,
                "error": str(e)
            }
    
    def generate_questions_and_answers(self, extracted_data: Dict[str, Any], log_callback=None) -> Dict[str, Any]:
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
        
        log("[DeepSeek Q&A Generation] Starting question and answer generation...")
        
        prompt = f"""You are an Expert Interview Question Generator.
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

IMPORTANT: Base answers ONLY on information present in the resume. Do not hallucinate or invent experiences.

Resume data:
{json.dumps(extracted_data, indent=2)}

Return ONLY a valid JSON object (no markdown, no explanations):
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
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a professional interview question generator. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=6000
            )
            
            response_text = response.choices[0].message.content
            
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
                log(f"[DeepSeek Q&A Generation] Generated {total_questions} questions across {len(qa_data.get('questionsAndAnswers', []))} categories")
            except json.JSONDecodeError as e:
                log(f"[DeepSeek Q&A Generation] Failed to parse JSON: {e}")
                log(f"[DeepSeek Q&A Generation] Response: {response_text[:200]}...")
            
            return {
                "qaData": qa_data,
                "logs": logs
            }
            
        except Exception as e:
            log(f"[DeepSeek Q&A Generation] Error: {e}")
            logger.exception("DeepSeek Q&A generation error")
            return {
                "qaData": {},
                "logs": logs,
                "error": str(e)
            }
    
    def process_resume(self, resume_text: str, log_callback=None) -> Dict[str, Any]:
        """
        Complete resume processing pipeline using DeepSeek.
        
        Args:
            resume_text: Raw text extracted from resume
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
            # Step 1: Extract structured data
            extraction_result = self.extract_resume_data(resume_text, log_callback=log)
            extracted_data = extraction_result.get("extractedData", {})
            all_logs.extend(extraction_result.get("logs", []))
            
            if "error" in extraction_result:
                raise Exception(extraction_result["error"])
            
            # Step 2: Generate Q&A
            qa_result = self.generate_questions_and_answers(extracted_data, log_callback=log)
            qa_data = qa_result.get("qaData", {})
            all_logs.extend(qa_result.get("logs", []))
            
            if "error" in qa_result:
                raise Exception(qa_result["error"])
            
            # Combine results
            result = {
                "success": True,
                "provider": "deepseek",
                "model": self.model_name,
                "candidateInfo": extracted_data.get("personalInfo", {}),
                "summary": extracted_data.get("summary", ""),
                "extractedData": extracted_data,
                "questionsAndAnswers": qa_data.get("questionsAndAnswers", []),
                "logs": all_logs
            }
            
            log("[DeepSeek Complete] Resume processing completed successfully")
            return result
            
        except Exception as e:
            log(f"[DeepSeek Error] Resume processing failed: {e}")
            logger.exception("DeepSeek resume processing error")
            return {
                "success": False,
                "provider": "deepseek",
                "error": str(e),
                "logs": all_logs
            }
