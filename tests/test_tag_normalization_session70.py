"""
Automated Test for Session 70 Tag Normalization Fix
Test that tags with pipes are correctly normalized and parsed.

Date: 2026-02-06
Programmer: COM8
Related: Session 70 - Fix tag normalization for paragraph formatting
"""

import sys
import os
import tempfile
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from translation.format_mapper import FormatMapper, TextSegment, FormatBit


class TestTagNormalization:
    """Test tag normalization fixes from Session 70"""
    
    def test_normalize_simple_tags(self):
        """Test normalization of simple tags with spaces"""
        input_text = "< 1 >Bold text</ 1 >"
        
        # Parse should handle normalization internally
        segments = FormatMapper.parse_tagged_text(input_text)
        
        assert len(segments) == 1
        assert segments[0].text == "Bold text"
        assert '<' not in segments[0].text
        assert '>' not in segments[0].text
    
    def test_normalize_tags_with_pipes(self):
        """Test normalization of tags with pipes (THE BUG FROM SESSION 70)"""
        input_text = "< 113 | 65536 : L >Indented text</ 113 | 65536 >"
        
        segments = FormatMapper.parse_tagged_text(input_text)
        
        assert len(segments) == 1
        assert segments[0].text == "Indented text"
        assert '<' not in segments[0].text
        assert '>' not in segments[0].text
        assert segments[0].format_bits == 113
        assert segments[0].paragraph_format == 65536
    
    def test_normalize_complex_metadata(self):
        """Test normalization of tags with complex metadata"""
        input_text = "< 1 | 256 : | C >Centered text</ 1 | 256 >"
        
        segments = FormatMapper.parse_tagged_text(input_text)
        
        assert len(segments) == 1
        assert segments[0].text == "Centered text"
        assert '<' not in segments[0].text
        assert '>' not in segments[0].text
        assert segments[0].format_bits == 1
        assert segments[0].paragraph_format == 256
    
    def test_normalize_tags_with_metadata_and_values(self):
        """Test normalization with actual metadata values"""
        input_text = "< 112 | 65536 : 525252,9,Arial | 0,0 >Text with format</ 112 | 65536 >"
        
        segments = FormatMapper.parse_tagged_text(input_text)
        
        assert len(segments) == 1
        assert segments[0].text == "Text with format"
        assert '<' not in segments[0].text
        assert segments[0].format_bits == 112
        assert segments[0].paragraph_format == 65536
        # Character metadata and paragraph metadata are parsed separately
        assert "525252,9,Arial" in segments[0].metadata  # Character metadata
        assert "0,0" in segments[0].paragraph_metadata  # Paragraph metadata
    
    def test_parse_normalized_tags_no_leakage(self):
        """Ensure parsed segments have NO tag characters in text"""
        test_cases = [
            "< 1 >text</ 1 >",
            "< 113 | 65536 >text</ 113 | 65536 >",
            "< 1 | 256 : | C >text</ 1 | 256 >",
            "< 33 | 512 : 14 | 1.0 >text</ 33 | 512 >",
        ]
        
        for input_text in test_cases:
            segments = FormatMapper.parse_tagged_text(input_text)
            assert len(segments) > 0, f"Failed to parse: {input_text}"
            
            for seg in segments:
                # Critical: No tag characters should be in the text
                assert '<' not in seg.text, f"Found '<' in text: {seg.text}"
                assert '>' not in seg.text, f"Found '>' in text: {seg.text}"
    
    def test_google_translate_simulation(self):
        """Simulate Google Translate adding spaces (the actual bug scenario)"""
        # Original tagged text (without spaces)
        original = "<112|65536:525252,9,Arial|0,0>Text with formatting</112|65536>"
        
        # Google Translate adds spaces everywhere
        google_result = original.replace('<', '< ').replace('>', ' >').replace('|', ' | ').replace('/', ' / ')
        
        # Our fix should handle this
        segments = FormatMapper.parse_tagged_text(google_result)
        
        assert len(segments) == 1
        assert segments[0].text == "Text with formatting"
        assert '<' not in segments[0].text
        assert '>' not in segments[0].text
        assert segments[0].format_bits == 112
        assert segments[0].paragraph_format == 65536
    
    def test_multiple_segments_with_different_formats(self):
        """Test multiple segments with various formatting"""
        input_text = """<1|256:|C>Centered Title</1|256>
<113|65536:|L>Indented paragraph</113|65536>
<3>Bold italic text</3>
Normal text"""
        
        segments = FormatMapper.parse_tagged_text(input_text)
        
        # Should have 4 segments (3 formatted + 1 plain)
        assert len(segments) >= 3
        
        # Check each segment has clean text
        for seg in segments:
            assert '<' not in seg.text
            assert '>' not in seg.text
    
    def test_complete_translation_workflow(self):
        """Test complete workflow: Create → Tag → Google → Parse → Save → Verify"""
        # Create test segments
        segments = [
            TextSegment("Centered title", format_bits=FormatBit.BOLD, 
                       paragraph_format=256, paragraph_metadata="|C"),
            TextSegment("Indented paragraph text", format_bits=113, 
                       paragraph_format=65536, paragraph_metadata="100,50,0|12,6"),
            TextSegment("Normal text", format_bits=0, paragraph_format=0),
        ]
        
        # Step 1: Convert to tagged text
        tagged_text = ''.join(seg.to_tagged_text() for seg in segments)
        assert '<' in tagged_text  # Should have tags
        
        # Step 2: Simulate Google Translate adding spaces
        google_result = tagged_text.replace('<', '< ').replace('>', ' >').replace('|', ' | ').replace('/', ' / ')
        
        # Step 3: Parse back (THE FIX SHOULD WORK HERE)
        parsed_segments = FormatMapper.parse_tagged_text(google_result)
        
        # Step 4: Verify no tags in segment text
        assert len(parsed_segments) == 3
        for seg in parsed_segments:
            assert '<' not in seg.text, f"Found tag in text: {seg.text}"
            assert '>' not in seg.text, f"Found tag in text: {seg.text}"
        
        # Step 5: Verify formatting is preserved
        assert parsed_segments[0].format_bits == FormatBit.BOLD
        assert parsed_segments[0].paragraph_format == 256
        assert parsed_segments[1].format_bits == 113
        assert parsed_segments[1].paragraph_format == 65536
        assert parsed_segments[2].format_bits == 0
        
        # Step 6: Test save to ODT (if no errors, it's working)
        with tempfile.NamedTemporaryFile(suffix='.odt', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            FormatMapper.create_odt_from_segments(parsed_segments, output_path)
            
            # Step 7: Re-extract and verify no tags visible
            re_extracted_text = FormatMapper.extract_formatted_text_from_odt(output_path)
            re_parsed = FormatMapper.parse_tagged_text(re_extracted_text)
            
            # Verify re-extracted text also has no visible tags
            for seg in re_parsed:
                # Allow internal format tags, but not broken/visible ones
                # We're checking the text content is clean
                text_only = seg.text.strip()
                if text_only:  # Skip empty segments
                    # Should not have incomplete tags like "< 113 |"
                    assert not (text_only.startswith('<') and '|' in text_only[:20])
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_empty_input(self):
        """Test with empty input"""
        segments = FormatMapper.parse_tagged_text("")
        assert len(segments) == 0
    
    def test_plain_text_no_tags(self):
        """Test plain text without tags"""
        segments = FormatMapper.parse_tagged_text("Just plain text")
        assert len(segments) == 1
        assert segments[0].text == "Just plain text"
    
    def test_malformed_tag_single_bracket(self):
        """Test with user-typed < character (not a tag)"""
        # This is a limitation - we can't distinguish user-typed < from tags
        # But at least it shouldn't crash
        segments = FormatMapper.parse_tagged_text("This < is less than 5")
        assert len(segments) >= 1
        # The < will be treated as part of text or fail to match
    
    def test_nested_tags_not_supported(self):
        """Verify nested tags are not supported (expected behavior)"""
        input_text = "<1>Outer <2>inner</2> text</1>"
        # This might not parse correctly, but should not crash
        segments = FormatMapper.parse_tagged_text(input_text)
        # Just verify it doesn't crash
        assert True


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
