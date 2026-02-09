"""
Check exact location and context of placeholder
"""
import zipfile

with zipfile.ZipFile('CAIT_WITH_WHITESPACE_PROTECTION_COM8.odt', 'r') as z:
    with z.open('content.xml') as f:
        content = f.read().decode('utf-8')
        
        # Find the exact location
        idx = content.find('【TA B】')
        
        if idx >= 0:
            context_start = max(0, idx - 150)
            context_end = min(len(content), idx + 150)
            context = content[context_start:context_end]
            
            print("Found 【TA B】 at position:", idx)
            print()
            print("Context:")
            print(context)
            print()
            
            # Is it inside a text span or outside?
            if '<text:span' in context[:150]:
                print("⚠️  It's inside a text:span element")
                print("   This means it's actual TEXT in the document")
                print("   User will see it!")
            
            # Show what's around it
            print()
            print("Characters around the placeholder:")
            for i in range(max(0, idx-10), min(len(content), idx+20)):
                char = content[i]
                if i == idx:
                    print(f"  >>> [{i}]: '{char}' (START OF 【TA B】)")
                else:
                    print(f"      [{i}]: '{char}'")
        else:
            print("✅ No 【TA B】 found!")

