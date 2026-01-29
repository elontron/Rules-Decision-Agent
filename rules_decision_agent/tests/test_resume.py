
import pytest
import os
import json
from pathlib import Path
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.resume_agent import ResumeParser, ResumeAnalysisLogic


class TestResumeParser:
    """Test suite for ResumeParser class."""
    
    def test_parse_txt_file(self):
        """Test parsing of plain text resume."""
        test_file = "examples/sample_resume.txt"
        if not os.path.exists(test_file):
            pytest.skip(f"Sample file not found: {test_file}")
        
        text = ResumeParser.parse_file(test_file)
        
        assert text is not None
        assert len(text) > 0
        assert "John Doe" in text or "Software Engineer" in text
    
    def test_unsupported_format(self):
        """Test that unsupported file formats raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported file format"):
            ResumeParser.parse_file("test.xyz")
    
    def test_file_not_found(self):
        """Test that missing files raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            ResumeParser.parse_file("nonexistent_file.txt")


class TestResumeAnalysisLogic:
    """Test suite for ResumeAnalysisLogic class."""
    
    @pytest.mark.asyncio
    async def test_extract_resume_data(self):
        """Test extraction of structured data from resume text."""
        sample_text = """
        John Doe
        Software Engineer
        Email: john@example.com
        
        Skills: Python, JavaScript, React
        
        Experience:
        - Senior Developer at TechCorp (2020-2023)
        - Built scalable web applications
        """
        
        logic = ResumeAnalysisLogic()
        result = await logic.extract_resume_data(sample_text)
        
        assert "extractedData" in result
        assert "logs" in result
        assert isinstance(result["logs"], list)
    
    @pytest.mark.asyncio
    async def test_process_resume_integration(self):
        """Integration test for complete resume processing."""
        test_file = "examples/sample_resume.txt"
        if not os.path.exists(test_file):
            pytest.skip(f"Sample file not found: {test_file}")
        
        logic = ResumeAnalysisLogic()
        result = await logic.process_resume(test_file)
        
        # Check result structure
        assert "success" in result
        assert result["success"] is True
        assert "extractedData" in result
        assert "questionsAndAnswers" in result
        assert "logs" in result
        
        # Validate Q&A structure
        qa_list = result.get("questionsAndAnswers", [])
        if qa_list:
            for category in qa_list:
                assert "category" in category
                assert "questions" in category
                for question in category["questions"]:
                    assert "question" in question
                    assert "suggestedAnswer" in question


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
