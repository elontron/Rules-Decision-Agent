
import sys
import asyncio
import os
import json

# Add src to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

try:
    from resume_agent import ResumeAnalysisLogic
except ImportError:
    from src.resume_agent import ResumeAnalysisLogic


def print_formatted_output(result: dict):
    """Print formatted resume analysis results."""
    print("\n" + "="*80)
    print("RESUME ANALYSIS RESULTS")
    print("="*80)
    
    if not result.get("success"):
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        return
    
    # Candidate Info
    candidate_info = result.get("candidateInfo", {})
    if candidate_info:
        print("\n📋 CANDIDATE INFORMATION")
        print("-" * 80)
        if candidate_info.get("name"):
            print(f"Name: {candidate_info['name']}")
        if candidate_info.get("email"):
            print(f"Email: {candidate_info['email']}")
        if candidate_info.get("phone"):
            print(f"Phone: {candidate_info['phone']}")
        if candidate_info.get("location"):
            print(f"Location: {candidate_info['location']}")
    
    # Summary
    summary = result.get("summary", "")
    if summary:
        print(f"\n📝 PROFESSIONAL SUMMARY")
        print("-" * 80)
        print(summary)
    
    # Skills
    extracted_data = result.get("extractedData", {})
    skills = extracted_data.get("skills", [])
    if skills:
        print(f"\n💡 SKILLS ({len(skills)})")
        print("-" * 80)
        print(", ".join(skills))
    
    # Questions and Answers
    qa_list = result.get("questionsAndAnswers", [])
    if qa_list:
        print(f"\n❓ INTERVIEW QUESTIONS & ANSWERS")
        print("=" * 80)
        
        for category_data in qa_list:
            category = category_data.get("category", "Unknown")
            questions = category_data.get("questions", [])
            
            if questions:
                print(f"\n📌 {category.upper()} ({len(questions)} questions)")
                print("-" * 80)
                
                for idx, q in enumerate(questions, 1):
                    print(f"\nQ{idx}: {q.get('question', '')}")
                    
                    difficulty = q.get('difficulty', 'N/A')
                    print(f"   Difficulty: {difficulty}")
                    
                    related_skills = q.get('relatedSkills', [])
                    if related_skills:
                        print(f"   Related Skills: {', '.join(related_skills)}")
                    
                    answer = q.get('suggestedAnswer', '')
                    if answer:
                        print(f"\n   💬 Suggested Answer:")
                        # Indent the answer
                        for line in answer.split('\n'):
                            print(f"   {line}")
    
    print("\n" + "="*80)


async def main():
    if len(sys.argv) < 2:
        print("Usage: python run_resume.py <resume_file_path>")
        print("\nSupported formats: .pdf, .docx, .txt")
        print("\nExample:")
        print("  python run_resume.py examples/sample_resume.txt")
        print("  python run_resume.py /path/to/resume.pdf")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    
    print(f"📄 Processing resume: {file_path}")
    print("⏳ This may take a moment...\n")
    
    agent = ResumeAnalysisLogic()
    
    try:
        # Process resume with logging
        result = await agent.process_resume(
            file_path,
            log_callback=lambda msg: print(f"[LOG] {msg}")
        )
        
        # Print formatted output
        print_formatted_output(result)
        
        # Also save JSON output
        output_file = "resume_analysis_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Full JSON output saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error processing resume: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(0)
