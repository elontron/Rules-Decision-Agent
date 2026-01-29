#!/usr/bin/env python3
"""
Quick test script to verify API configurations
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_google_api():
    """Test Google API key configuration."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print(f"✅ Google API Key found: {api_key[:20]}...")
        return True
    else:
        print("❌ Google API Key not found")
        return False

def test_deepseek_api():
    """Test DeepSeek API key configuration."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        print(f"✅ DeepSeek API Key found: {api_key[:20]}...")
        return True
    else:
        print("❌ DeepSeek API Key not found")
        return False

def test_deepseek_connection():
    """Test DeepSeek API connection."""
    try:
        from openai import OpenAI
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("❌ DeepSeek API Key not configured")
            return False
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        # Simple test call
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": "Say 'Hello' in one word."}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ DeepSeek API connection successful! Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ DeepSeek API connection failed: {e}")
        return False

def main():
    """Main test function."""
    print("=" * 60)
    print("API Configuration Test")
    print("=" * 60)
    print()
    
    # Test configurations
    google_ok = test_google_api()
    deepseek_ok = test_deepseek_api()
    
    print()
    print("=" * 60)
    print("Connection Test (DeepSeek)")
    print("=" * 60)
    print()
    
    if deepseek_ok:
        deepseek_conn_ok = test_deepseek_connection()
    else:
        deepseek_conn_ok = False
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    
    if google_ok:
        print("✅ Google Gemini: Configured")
        print("   ⚠️  Note: May have quota limitations on free tier")
    else:
        print("❌ Google Gemini: Not configured")
    
    print()
    
    if deepseek_ok and deepseek_conn_ok:
        print("✅ DeepSeek: Configured and working")
        print("   ✨ Recommended for resume analysis")
    elif deepseek_ok:
        print("⚠️  DeepSeek: Configured but connection failed")
    else:
        print("❌ DeepSeek: Not configured")
    
    print()
    print("=" * 60)
    print("Recommendations")
    print("=" * 60)
    print()
    
    if deepseek_ok and deepseek_conn_ok:
        print("🎉 You're all set! Use DeepSeek for resume analysis:")
        print("   python run_deepseek_resume.py examples/sample_resume.txt")
    elif google_ok:
        print("⚠️  Only Google API is configured.")
        print("   Consider adding DeepSeek API key to avoid quota issues.")
    else:
        print("❌ No working API configuration found.")
        print("   Please configure at least one API key in .env file")
    
    print()

if __name__ == "__main__":
    main()
