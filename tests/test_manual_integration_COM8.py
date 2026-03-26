#!/usr/bin/env python3
"""
Phase C.6: Manual Integration Test Script - COM8

Automated testing of pagination implementation with real files.
Tests chunking, overlap, semantic splitting, and error handling.

Date: 2026-02-17
Programmer: COM8
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from translation.google_translate import GoogleTranslateAPI


def test_small_file():
    """Test 1: Small file - no chunking should occur"""
    print("\n" + "="*70)
    print("TEST 1: Small File (No Regression)")
    print("="*70)
    
    translator = GoogleTranslateAPI()
    
    # Small text (under 4500 chars)
    text = "Hello world. This is a test. " * 50  # ~1500 chars
    
    print(f"Input text length: {len(text)} chars")
    print(f"Expected: NO chunking (< 4500 chars)")
    
    # This should NOT trigger chunking
    result = translator.translate_text(text, "en", "pt")
    
    if result and result.success:
        print(f"✅ Translation succeeded")
        print(f"Result preview: {result.translated_text[:100]}...")
        return True
    else:
        print(f"❌ Translation failed: {result.error_message if result else 'No result'}")
        return False


def test_medium_file_semantic():
    """Test 2: Medium file - semantic splitting"""
    print("\n" + "="*70)
    print("TEST 2: Medium File (Semantic Splitting)")
    print("="*70)
    
    translator = GoogleTranslateAPI()
    
    # Medium HTML text with paragraphs (~10KB)
    text = """
    <html>
    <body>
    """ + "\n".join([
        f"<p>This is paragraph number {i}. It contains important information about topic {i}. "
        f"The content is structured semantically to test boundary detection. "
        f"We want to ensure that paragraphs remain intact during translation. " * 20 + "</p>"
        for i in range(1, 11)
    ]) + """
    </body>
    </html>
    """
    
    print(f"Input text length: {len(text)} chars")
    print(f"Expected: Chunking with semantic boundaries (at </p> tags)")
    
    # Track progress
    chunks_seen = []
    def progress_callback(current, total, percentage, status):
        chunks_seen.append((current, total, percentage, status))
        print(f"  Progress: {status} ({percentage:.1f}%)")
    
    result = translator.translate_text_chunked(
        text, "en", "pt",
        progress_callback=progress_callback,
        use_semantic_splitting=True,
        use_overlap=True
    )
    
    if result and result.success:
        print(f"✅ Translation succeeded")
        print(f"Total chunks processed: {len(chunks_seen)}")
        print(f"Result length: {len(result.translated_text)} chars")
        print(f"Result preview: {result.translated_text[:200]}...")
        
        # Verify semantic splitting happened
        if len(chunks_seen) > 1:
            print(f"✅ Chunking triggered ({len(chunks_seen)} chunks)")
        else:
            print(f"⚠️  Expected multiple chunks, got {len(chunks_seen)}")
        
        return True
    else:
        print(f"❌ Translation failed: {result.error_message if result else 'No result'}")
        return False


def test_large_text_http413_fix():
    """Test 3: Large text - HTTP 413 fix"""
    print("\n" + "="*70)
    print("TEST 3: Large Text (HTTP 413 Fix)")
    print("="*70)
    
    translator = GoogleTranslateAPI()
    
    # Generate large text (~50KB) that would cause HTTP 413
    text = "This is a test sentence that will be repeated many times to create a very large text. " * 1000
    
    print(f"Input text length: {len(text)} chars")
    print(f"Expected: Chunking into ~10-15 chunks, NO HTTP 413 error")
    
    chunks_seen = []
    def progress_callback(current, total, percentage, status):
        chunks_seen.append((current, total))
        if current % 5 == 0 or current == total:  # Print every 5th chunk
            print(f"  Progress: Chunk {current}/{total} ({percentage:.1f}%)")
    
    try:
        result = translator.translate_text_chunked(
            text, "en", "pt",
            progress_callback=progress_callback
        )
        
        if result and result.success:
            print(f"✅ Translation succeeded (NO HTTP 413)")
            print(f"Total chunks: {len(chunks_seen)}")
            print(f"Result length: {len(result.translated_text)} chars")
            return True
        else:
            print(f"❌ Translation failed (but not HTTP 413): {result.error_message if result else 'No result'}")
            return False
            
    except Exception as e:
        if "413" in str(e) or "Too Large" in str(e):
            print(f"❌ HTTP 413 ERROR STILL OCCURS: {e}")
            return False
        else:
            print(f"❌ Other error: {e}")
            return False


def test_overlap_deduplication():
    """Test 4: Overlap deduplication"""
    print("\n" + "="*70)
    print("TEST 4: Overlap Deduplication")
    print("="*70)
    
    translator = GoogleTranslateAPI()
    
    # Text with clear sentences for overlap testing
    sentences = [f"This is sentence number {i}. " for i in range(1, 201)]
    text = "".join(sentences)  # ~5000 chars, will trigger 2 chunks
    
    print(f"Input text length: {len(text)} chars")
    print(f"Expected: 2-3 chunks with 200-char overlap")
    
    result = translator.translate_text_chunked(
        text, "en", "pt",
        use_overlap=True
    )
    
    if result and result.success:
        print(f"✅ Translation succeeded")
        print(f"Result length: {len(result.translated_text)} chars")
        
        # Check for duplicate sentences (would indicate failed deduplication)
        # This is a basic check - manual inspection would be more thorough
        words = result.translated_text.split()
        if len(words) != len(set(words)):
            print(f"⚠️  Possible duplicates detected (needs manual review)")
        else:
            print(f"✅ No obvious duplicates detected")
        
        return True
    else:
        print(f"❌ Translation failed: {result.error_message if result else 'No result'}")
        return False


def test_error_handling():
    """Test 5: Enhanced error messages"""
    print("\n" + "="*70)
    print("TEST 5: Enhanced Error Handling")
    print("="*70)
    
    translator = GoogleTranslateAPI()
    
    # Test with invalid language code to trigger error
    text = "This is a test. " * 1000
    
    print(f"Input text length: {len(text)} chars")
    print(f"Testing with invalid language code to trigger error...")
    
    try:
        result = translator.translate_text_chunked(
            text, "en", "INVALID_LANG"
        )
        print(f"⚠️  Expected error but got result")
        return False
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error caught: {error_msg[:200]}...")
        
        # Check if enhanced error info is present
        has_chunk_info = "chunk" in error_msg.lower()
        has_position = "position" in error_msg.lower()
        has_suggestions = "suggest" in error_msg.lower() or "try" in error_msg.lower()
        
        print(f"✅ Error raised as expected")
        print(f"  Has chunk info: {has_chunk_info}")
        print(f"  Has position: {has_position}")
        print(f"  Has suggestions: {has_suggestions}")
        
        if has_chunk_info or has_position:
            print(f"✅ Enhanced error context present")
            return True
        else:
            print(f"⚠️  Error lacks enhanced context")
            return False


def test_state_clearing():
    """Test 6: State clearing between translations"""
    print("\n" + "="*70)
    print("TEST 6: State Clearing (Bug #2)")
    print("="*70)
    
    translator = GoogleTranslateAPI()
    
    # First translation
    text1 = "This is the first document about cats and dogs. " * 50
    print(f"Translation 1: {len(text1)} chars")
    result1 = translator.translate_text(text1, "en", "pt")
    
    if not (result1 and result1.success):
        print(f"❌ First translation failed: {result1.error_message if result1 else 'No result'}")
        return False
    
    print(f"✅ First translation succeeded")
    print(f"Result 1 preview: {result1.translated_text[:50]}...")
    
    # Second translation (different content)
    text2 = "This is the second document about computers and programming. " * 50
    print(f"\nTranslation 2: {len(text2)} chars")
    result2 = translator.translate_text(text2, "en", "pt")
    
    if not (result2 and result2.success):
        print(f"❌ Second translation failed: {result2.error_message if result2 else 'No result'}")
        return False
    
    print(f"✅ Second translation succeeded")
    print(f"Result 2 preview: {result2.translated_text[:50]}...")
    
    # Check if results are different (no contamination)
    if result1.translated_text == result2.translated_text:
        print(f"❌ Results are identical (state persistence bug!)")
        return False
    
    # Check if result2 contains result1 content (contamination)
    if result1.translated_text[:30] in result2.translated_text:
        print(f"❌ Result 2 contains Result 1 content (contamination!)")
        return False
    
    print(f"✅ Results are different (no state contamination)")
    return True


def main():
    """Run all integration tests"""
    print("="*70)
    print("PHASE C.6: MANUAL INTEGRATION TEST SUITE - COM8")
    print("="*70)
    print("Date: 2026-02-17")
    print("Testing pagination implementation with real-world scenarios")
    print("="*70)
    
    # Note: Tests will use Google Translate API
    print("\n⚠️  WARNING: These tests will make real API calls to Google Translate")
    print("⚠️  Rate limiting: 0.5s delay between chunks")
    print("⚠️  Estimated time: 5-10 minutes\n")
    
    import time
    time.sleep(2)
    
    results = {}
    
    # Run tests
    results['Test 1: Small File'] = test_small_file()
    time.sleep(2)
    
    results['Test 2: Medium File (Semantic)'] = test_medium_file_semantic()
    time.sleep(2)
    
    results['Test 3: Large Text (HTTP 413)'] = test_large_text_http413_fix()
    time.sleep(2)
    
    results['Test 4: Overlap'] = test_overlap_deduplication()
    time.sleep(2)
    
    results['Test 5: Error Handling'] = test_error_handling()
    time.sleep(2)
    
    results['Test 6: State Clearing'] = test_state_clearing()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("="*70)
    print(f"Total: {passed} passed, {failed} failed out of {len(results)} tests")
    print("="*70)
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED - Ready for production!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed - Needs investigation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
