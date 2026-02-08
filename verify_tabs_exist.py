"""
Let me prove the tabs are really there
"""
import zipfile
import xml.etree.ElementTree as ET

print("=== VERIFYING TABS IN OUTPUT ===")
print()

with zipfile.ZipFile('CAIT_WITH_WHITESPACE_PROTECTION_COM8.odt', 'r') as z:
    with z.open('content.xml') as f:
        content = f.read().decode('utf-8')
        
        # Count tab elements
        tab_count = content.count('<text:tab/>')
        
        print(f"Found {tab_count} <text:tab/> elements in content.xml")
        print()
        
        # Show first occurrence
        if tab_count > 0:
            idx = content.find('<text:tab/>')
            context = content[max(0, idx-50):idx+100]
            print("Sample context:")
            print(context)
            print()
        
        # Parse and analyze
        root = ET.fromstring(content)
        ns = {'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'}
        
        tabs = root.findall('.//text:tab', ns)
        line_breaks = root.findall('.//text:line-break', ns)
        paragraphs = root.findall('.//text:p', ns)
        
        print(f"XML Parse Results:")
        print(f"  Tabs: {len(tabs)}")
        print(f"  Line breaks: {len(line_breaks)}")
        print(f"  Paragraphs: {len(paragraphs)}")
        print()
        
        if len(tabs) >= 10:
            print("✅ YES! Tabs are really preserved in the output!")
        else:
            print("⚠️  Fewer tabs than expected")
        
        # Show translated text sample
        first_p = paragraphs[0] if paragraphs else None
        if first_p is not None:
            text_content = ''.join(first_p.itertext())
            print()
            print(f"First paragraph text: {text_content[:200]}")

