#!/usr/bin/env python3
"""
Test script to verify the refactored sentiment analysis service works correctly.

This script tests:
1. Service initialization
2. Basic sentiment analysis
3. Hybrid analysis
4. Detailed analysis with insights
5. Analyzer comparison
6. Test samples functionality

Run this script to ensure the refactoring was successful.
"""

import sys
import os

# Add the current directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from sentimentAnalysisService import sentiment_service
    print("✅ Successfully imported sentiment_service")
except ImportError as e:
    print(f"❌ Failed to import sentiment_service: {e}")
    sys.exit(1)

def test_basic_functionality():
    """Test basic sentiment analysis functionality"""
    print("\n🧪 Testing Basic Functionality...")
    
    test_texts = [
        "I love this movie! It's absolutely amazing!",
        "This is terrible. I hate it.",
        "The weather is okay today."
    ]
    
    for text in test_texts:
        try:
            result = sentiment_service.analyze_sentiment(text)
            print(f"✅ Text: '{text[:30]}...' -> {result['label']} ({result['emoji']})")
        except Exception as e:
            print(f"❌ Error analyzing '{text[:30]}...': {e}")
            return False
    
    return True

def test_hybrid_analysis():
    """Test hybrid sentiment analysis"""
    print("\n🔬 Testing Hybrid Analysis...")
    
    try:
        text = "This movie is not bad, but it's not great either."
        result = sentiment_service.analyze_sentiment_hybrid(text, show_details=True)
        
        print(f"✅ Hybrid analysis successful")
        print(f"   Label: {result['label']}")
        print(f"   Combined Score: {result['combined_score']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Models Agree: {result['models_agree']}")
        
        return True
    except Exception as e:
        print(f"❌ Hybrid analysis failed: {e}")
        return False

def test_detailed_analysis():
    """Test detailed analysis with insights"""
    print("\n📊 Testing Detailed Analysis...")
    
    try:
        text = "Wow! This is absolutely fantastic! Best experience ever!"
        result = sentiment_service.analyze_sentiment(text, show_details=True)
        insights = sentiment_service.generate_insights(result)
        
        print(f"✅ Detailed analysis successful")
        print(f"   Text Length: {result['details']['text_length']}")
        print(f"   Word Count: {result['details']['word_count']}")
        print(f"   Insights: {len(insights)} generated")
        
        for insight in insights:
            print(f"   - {insight}")
        
        return True
    except Exception as e:
        print(f"❌ Detailed analysis failed: {e}")
        return False

def test_analyzer_comparison():
    """Test analyzer comparison functionality"""
    print("\n⚖️ Testing Analyzer Comparison...")
    
    try:
        text = "The movie wasn't terrible, but I didn't love it either."
        comparison = sentiment_service.compare_analyzers(text)
        
        print(f"✅ Analyzer comparison successful")
        print(f"   VADER: {comparison['vader_only']['label']}")
        print(f"   Hybrid: {comparison['hybrid']['label']}")
        print(f"   Same Label: {comparison['comparison']['same_label']}")
        print(f"   Recommendation: {comparison['comparison']['recommendation']}")
        
        return True
    except Exception as e:
        print(f"❌ Analyzer comparison failed: {e}")
        return False


def test_llm_analysis():
    """Optionally test LLM sentiment if API key is configured"""
    print("\n🤖 Testing LLM Analysis (if configured)...")
    try:
        # skip if neither key is present
        if not (os.getenv('OPENAI_API_KEY') or os.getenv('OPENROUTER_API_KEY')):
            print("⚠️ No LLM API key set, skipping LLM test")
            return True
        text = "I really enjoyed this strong performance, excellent cinematography."
        result = sentiment_service.analyze_sentiment(text, use_llm=True)
        print(f"✅ LLM analysis returned: {result.get('label')} (confidence {result.get('confidence')})")
        return True
    except Exception as e:
        print(f"❌ LLM analysis failed: {e}")
        return False

def test_samples_functionality():
    """Test the test samples functionality"""
    print("\n🎯 Testing Sample Analysis...")
    
    try:
        results = sentiment_service.test_samples_analysis()
        
        print(f"✅ Test samples analysis successful")
        print(f"   Total Samples: {results['summary']['total']}")
        print(f"   Correct: {results['summary']['correct']}")
        print(f"   Accuracy: {results['summary']['accuracy']}")
        
        return True
    except Exception as e:
        print(f"❌ Test samples analysis failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Sentiment Analysis Service Tests...")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Hybrid Analysis", test_hybrid_analysis),
        ("Detailed Analysis", test_detailed_analysis),
        ("Analyzer Comparison", test_analyzer_comparison),
        ("LLM Analysis", test_llm_analysis),
        ("Test Samples", test_samples_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The refactored service is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
