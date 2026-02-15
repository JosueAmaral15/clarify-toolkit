"""
Verify: How many tabs are actually in the final ODT?
"""
import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('CAIT_WITH_WHITESPACE_PROTECTION_COM8.odt', 'r') as z:
    with z.open('content.xml') as f:
        content = f.read().decode('utf-8')
        root = ET.fromstring(content)
        
        ns = {'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'}
        
        tabs = root.findall('.//text:tab', ns)
        
        print("Final ODT Analysis:")
        print(f"  <text:tab/> elements: {len(tabs)}")
        print()
        
        if len(tabs) == 14:
            print("✅ PERFECT! 14/14 tabs = 100% preservation!")
        elif len(tabs) == 13:
            print("⚠️  13/14 tabs = 93% preservation")
            print("   One tab was lost somewhere")
        else:
            print(f"Result: {len(tabs)}/14 tabs")
        
        # Where are the tabs?
        print()
        print("Tab locations:")
        for i, tab in enumerate(tabs[:5], 1):
            # Get parent paragraph
            para = tab
            while para is not None and para.tag != '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p':
                para = para.getparent() if hasattr(para, 'getparent') else None
            
            print(f"  Tab {i}: {tab.tag}")

