#!/usr/bin/env python3
"""
Test script for ProbePilot AI Service
Tests the OpenAI integration and error handling
"""

import os
import sys
import asyncio
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.services.ai_service import ProbePilotAI, get_ai_response, get_quick_analysis
from frontend.components.copilot import get_current_system_data

async def test_ai_service():
    """Test the AI service functionality"""
    
    print("🧪 Testing ProbePilot AI Service")
    print("=" * 50)
    
    # Test 1: Initialize AI service
    print("\n1. Testing AI Service Initialization...")
    ai = ProbePilotAI()
    
    if ai.client:
        print("✅ AI service initialized successfully")
        print(f"   API Key configured: {'Yes' if ai.api_key else 'No'}")
    else:
        print("❌ AI service not configured (no API key)")
        return
    
    # Test 2: Test system data format
    print("\n2. Testing System Data Format...")
    system_data = get_current_system_data()
    print(f"✅ System data generated: {type(system_data)}")
    print(f"   Keys: {list(system_data.keys())}")
    
    # Test 3: Test AI response
    print("\n3. Testing AI Response...")
    try:
        response = await get_ai_response(
            "What's the current system status?", 
            system_data, 
            []  # Empty chat history
        )
        print(f"✅ AI Response received ({len(response)} characters)")
        print(f"   First 100 chars: {response[:100]}...")
        
    except Exception as e:
        print(f"❌ AI Response failed: {e}")
    
    # Test 4: Test quick analysis
    print("\n4. Testing Quick Analysis...")
    try:
        analysis = await get_quick_analysis("performance", system_data)
        print(f"✅ Quick Analysis received ({len(analysis)} characters)")
        print(f"   First 100 chars: {analysis[:100]}...")
        
    except Exception as e:
        print(f"❌ Quick Analysis failed: {e}")
        
    # Test 5: Test chat history processing
    print("\n5. Testing Chat History Processing...")
    try:
        chat_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        response = await get_ai_response(
            "How are you?",
            system_data,
            chat_history
        )
        print(f"✅ Chat History processed successfully")
        
    except Exception as e:
        print(f"❌ Chat History processing failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 AI Service test completed!")

if __name__ == "__main__":
    asyncio.run(test_ai_service())