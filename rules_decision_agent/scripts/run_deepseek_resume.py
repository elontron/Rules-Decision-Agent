#!/usr/bin/env python3
"""
Test script for DeepSeek Resume Analysis
Usage: python run_deepseek_resume.py <resume_file_path>
"""

import sys
import json
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from resume_agent import ResumeParser
from deepseek_resume_agent import DeepSeekResumeAnalyzer


def print_section(title: str, content: str = ""):
    """Print a formatted section."""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")
    if content:
        print(content)


def print_results(result: dict):
    """Print formatted results."""
    if not result.get("success"):
        print_section("RESUME ANALYSIS RESULTS")
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        return
    
    print_section("RESUME ANALYSIS RESULTS (DeepSeek)")
    
    # Candidate Info
    candidate_info = result.get("candidateInfo", {})
    if candidate_info:
        print("\n📋 Candidate Information:")
        for key, value in candidate_info.items():
            if value:
                print(f"  • {key.capitalize()}: {value}")
    
    # Summary
    summary = result.get("summary", "")
    if summary:
        print(f"\n📝 Professional Summary:")
        print(f"  {summary}")
    
    # Skills
    skills = result.get("extractedData", {}).get("skills", [])
    if skills:
        print(f"\n💡 Skills ({len(skills)}):")
        print(f"  {', '.join(skills[:15])}")
        if len(skills) > 15:
            print(f"  ... and {len(skills) - 15} more")
    
    # Questions and Answers
    qa_list = result.get("questionsAndAnswers", [])
    if qa_list:
        print(f"\n❓ Interview Questions & Answers:")
        for category_data in qa_list:
            category = category_data.get("category", "Unknown")
            questions = category_data.get("questions", [])
            print(f"\n  📌 {category} ({len(questions)} questions)")
            
            for i, q in enumerate(questions[:2], 1):  # Show first 2 questions per category
                print(f"\n    Q{i}: {q.get('question', '')}")
                print(f"    Difficulty: {q.get('difficulty', 'N/A')}")
                if q.get('relatedSkills'):
                    print(f"    Related Skills: {', '.join(q.get('relatedSkills', []))}")
                answer = q.get('suggestedAnswer', '')
                if answer:
                    # Truncate long answers
                    if len(answer) > 150:
                        answer = answer[:150] + "..."
                    print(f"    A: {answer}")
            
            if len(questions) > 2:
                print(f"\n    ... and {len(questions) - 2} more questions in this category")
    
    # Model info
    print(f"\n\n🤖 Powered by: {result.get('provider', 'unknown')} ({result.get('model', 'unknown')})")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python run_deepseek_resume.py <resume_file_path>")
        print("\nExample:")
        print("  python run_deepseek_resume.py examples/sample_resume.txt")
        print("  python run_deepseek_resume.py /path/to/resume.pdf")
        print("  python run_deepseek_resume.py /path/to/resume.docx")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    
    print(f"📄 Processing resume with DeepSeek: {file_path}")
    print("⏳ This may take a moment...")
    
    try:
        # Parse resume file
        print("\n[LOG] [Parser] Parsing resume file...")
        resume_text = ResumeParser.parse_file(file_path)
        print(f"[LOG] [Parser] Extracted {len(resume_text)} characters")
        
        # Initialize DeepSeek analyzer
        analyzer = DeepSeekResumeAnalyzer()
        
        # Process resume
        def log_callback(msg):
            print(f"[LOG] {msg}")
        
        result = analyzer.process_resume(resume_text, log_callback=log_callback)
        
        # Print results
        print_results(result)
        
        # Save to file
        output_dir = Path(__file__).parent.parent / "outputs"
        output_file = output_dir / "deepseek_resume_analysis_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Full JSON output saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
