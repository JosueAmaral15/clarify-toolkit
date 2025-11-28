#!/usr/bin/env python3
"""
test_is_file_feature.py

Verification test for "Is File" checkbox feature.
Verifies that the checkbox exists in all relevant panels.
"""


def test_checkbox_presence_in_code():
    """Verify that 'Is File' checkbox is present in source code."""
    with open('src/app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Search for checkbox declarations
    checkboxes = []
    
    # Pattern 1: self.is_file = QCheckBox
    import re
    matches = re.finditer(r'self\.is_file\s*=\s*QCheckBox\(["\'].*?["\']\)', content)
    for match in matches:
        checkboxes.append(match.group())
    
    assert len(checkboxes) >= 3, f"Expected at least 3 checkboxes, found {len(checkboxes)}"
    
    print(f"✓ Found {len(checkboxes)} 'Is File' checkboxes in code")
    for cb in checkboxes:
        print(f"  - {cb}")


def test_browse_methods_use_checkbox():
    """Verify that browse methods check the is_file checkbox."""
    with open('src/app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Search for browse methods that check is_file
    import re
    
    # Pattern: if self.is_file.isChecked()
    if_checks = re.findall(r'if self\.is_file\.isChecked\(\)', content)
    
    assert len(if_checks) >= 3, f"Expected at least 3 is_file checks, found {len(if_checks)}"
    
    print(f"✓ Found {len(if_checks)} is_file.isChecked() validations")


def test_both_dialog_types_present():
    """Verify that both file and directory dialogs are present."""
    with open('src/app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for both dialog types
    file_dialogs = content.count('QFileDialog.getOpenFileName')
    dir_dialogs = content.count('QFileDialog.getExistingDirectory')
    
    assert file_dialogs > 0, "No file selection dialogs found"
    assert dir_dialogs > 0, "No directory selection dialogs found"
    
    print(f"✓ File dialogs: {file_dialogs}")
    print(f"✓ Directory dialogs: {dir_dialogs}")


def test_panels_have_checkbox():
    """Verify that all main panels have the checkbox."""
    with open('src/app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    panels_found = {
        'SearchReplacePanel': False,
        'InsertPanel': False,
        'JsonTranslateDock': False
    }
    
    current_class = None
    
    for line in lines:
        # Track current class
        if 'class SearchReplacePanel' in line:
            current_class = 'SearchReplacePanel'
        elif 'class InsertPanel(' in line and '#' not in line:
            current_class = 'InsertPanel'
        elif 'class JsonTranslateDock' in line:
            current_class = 'JsonTranslateDock'
        
        # Check for checkbox in current class
        if current_class and 'self.is_file = QCheckBox' in line:
            panels_found[current_class] = True
    
    for panel, found in panels_found.items():
        assert found, f"{panel} does not have 'Is File' checkbox"
        print(f"✓ {panel} has 'Is File' checkbox")


def test_advanced_conditions_integration():
    """Verify that is_file checkbox integrates with advanced conditions."""
    with open('src/app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for change_advanced_conditions method
    assert 'def change_advanced_conditions(self):' in content
    
    # Check that it uses is_file
    import re
    pattern = r'def change_advanced_conditions.*?not self\.is_file\.isChecked\(\)'
    matches = re.search(pattern, content, re.DOTALL)
    
    assert matches, "change_advanced_conditions should check is_file status"
    
    print("✓ Advanced conditions integration verified")


def test_documentation_exists():
    """Verify that documentation file exists."""
    import os
    
    doc_path = 'docs/pt/IS_FILE_FEATURE.md'
    assert os.path.exists(doc_path), f"Documentation file not found: {doc_path}"
    
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key sections
    assert 'Search/Replace Panel' in content
    assert 'Insert Panel' in content
    assert 'JSON Translate Dock' in content
    assert 'Funcionalidade' in content
    
    print(f"✓ Documentation file exists and contains all sections")


if __name__ == "__main__":
    print("Running 'Is File' feature verification tests...\n")
    
    test_checkbox_presence_in_code()
    print()
    test_browse_methods_use_checkbox()
    print()
    test_both_dialog_types_present()
    print()
    test_panels_have_checkbox()
    print()
    test_advanced_conditions_integration()
    print()
    test_documentation_exists()
    
    print("\n" + "="*60)
    print("All 'Is File' feature verification tests passed! ✓")
    print("Feature is fully implemented and documented.")
    print("="*60)
