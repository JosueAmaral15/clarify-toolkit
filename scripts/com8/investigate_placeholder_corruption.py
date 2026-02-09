"""
Investigating: Is Google Translate corrupting our placeholders?
"""
import zipfile

print("=== INVESTIGATING PLACEHOLDER CORRUPTION ===")
print()

with zipfile.ZipFile('CAIT_WITH_WHITESPACE_PROTECTION_COM8.odt', 'r') as z:
    with z.open('content.xml') as f:
        content = f.read().decode('utf-8')
        
        # Search for any remaining placeholders
        issues = []
        
        # Look for corrupted placeholders
        if '【TA B】' in content:
            issues.append("【TAB】 was corrupted to 【TA B】 (added space)")
            count = content.count('【TA B】')
            issues.append(f"  Found {count} instances of 【TA B】")
        
        if '【B R】' in content:
            issues.append("【BR】 was corrupted to 【B R】")
        
        if '【NB SP】' in content:
            issues.append("【NBSP】 was corrupted to 【NB SP】")
        
        # Look for any remaining uncorrupted placeholders
        remaining_tab = content.count('【TAB】')
        remaining_br = content.count('【BR】')
        remaining_nbsp = content.count('【NBSP】')
        
        print("Remaining Placeholders (should be 0 if all restored):")
        print(f"  【TAB】: {remaining_tab}")
        print(f"  【BR】: {remaining_br}")
        print(f"  【NBSP】: {remaining_nbsp}")
        print()
        
        print("Corrupted Placeholders:")
        if issues:
            for issue in issues:
                print(f"  ❌ {issue}")
        else:
            print("  ✅ No corrupted placeholders found")
        print()
        
        # This explains the mystery!
        if '【TA B】' in content:
            print("🔍 DISCOVERY:")
            print("   Google Translate is adding SPACES inside our placeholders!")
            print("   【TAB】 → 【TA B】")
            print()
            print("   This means:")
            print("   1. The placeholder SURVIVED translation (good!)")
            print("   2. But Google modified it slightly (bad!)")
            print("   3. Our restore_special_whitespace() didn't match it (missed it)")
            print()
            print("   Solution: Need to handle corrupted placeholders in restoration!")

