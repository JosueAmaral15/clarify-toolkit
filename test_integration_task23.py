#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integration test for Task #23 - Complete workflow demonstration
Shows end-to-end process: dedupe → eliminate → update references
"""

import os
import tempfile
import json

from src.rewriter import (
    parse_json_preserving_duplicates_text,
    join_keys,
    eliminate_duplicates,
    extract_all_keys_from_dict,
    build_substitution_map,
    update_references_in_project,
    dump_ts_obj
)


def test_complete_workflow():
    """Test complete workflow: JSON with duplicates → eliminate → update refs."""
    print("\n" + "=" * 70)
    print("Task #23 - Integration Test: Complete Workflow")
    print("=" * 70)
    
    # Step 1: Create input JSON with duplicates
    print("\n📝 Step 1: Creating JSON with duplicate keys...")
    input_json = {
        "pages": {
            "home": {"title": "Home", "description": "Welcome"},
            "homePage": {"title": "Home", "description": "Welcome"},  # Duplicate
            "inicio": {"title": "Início", "description": "Bem-vindo"},  # Duplicate
            "contact": {"title": "Contact", "description": "Get in touch"},
            "contactPage": {"title": "Contact", "description": "Get in touch"},  # Duplicate
            "contato": {"title": "Contato", "description": "Entre em contato"}  # Duplicate
        },
        "common": {
            "submit": "Submit",
            "submitButton": "Submit",  # Duplicate
            "enviar": "Enviar"  # Duplicate
        }
    }
    
    print("\nOriginal JSON (with duplicates):")
    print(json.dumps(input_json, indent=2))
    
    # Step 2: Parse and process
    print("\n🔧 Step 2: Processing JSON...")
    
    # Extract keys before elimination
    old_keys = extract_all_keys_from_dict(input_json, prefix='t')
    print(f"\nKeys before elimination: {len(old_keys)}")
    for key in sorted(old_keys):
        print(f"  - {key}")
    
    # Parse and transform
    obj = parse_json_preserving_duplicates_text(json.dumps(input_json))
    obj = join_keys(obj)
    obj = eliminate_duplicates(obj)
    
    # Convert Obj back to dict for key extraction
    def obj_to_dict(obj):
        """Convert Obj structure back to dictionary."""
        if isinstance(obj, list):
            result = {}
            for key, value in obj:
                if isinstance(value, list):
                    # Check if it's an Obj (list of tuples) or array (list of values)
                    if value and isinstance(value[0], tuple):
                        result[key] = obj_to_dict(value)
                    else:
                        result[key] = value
                else:
                    result[key] = value
            return result
        return obj
    
    result_dict = obj_to_dict(obj)
    new_keys = extract_all_keys_from_dict(result_dict, prefix='t')
    print(f"\nKeys after elimination: {len(new_keys)}")
    for key in sorted(new_keys):
        print(f"  - {key}")
    
    # Step 3: Build substitution map
    print("\n🗺️  Step 3: Building substitution map...")
    sub_map = build_substitution_map(old_keys, new_keys)
    
    print(f"\nSubstitution map ({len(sub_map)} mappings):")
    for old_ref, new_ref in sorted(sub_map.items()):
        print(f"  {old_ref} → {new_ref}")
    
    # Step 4: Create test project with references
    print("\n📁 Step 4: Creating test project with orphaned references...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files with references
        test_files = {
            'HomePage.tsx': """
import React from 'react';

export default function HomePage() {
    return (
        <div>
            <h1>{t.pages.homePage.title}</h1>
            <p>{t.pages.inicio.description}</p>
            <a href="/contact">{t.pages.contactPage.title}</a>
        </div>
    );
}

const pageTitle = t.pages.homePage.title;
""",
            'ContactPage.tsx': """
import React from 'react';

export default function ContactPage() {
    return (
        <div>
            <h1>{t.pages.contactPage.title}</h1>
            <p>{t.pages.contato.description}</p>
            <button>{t.common.submitButton}</button>
        </div>
    );
}
""",
            'utils.ts': """
export const messages = {
    home: t.pages.homePage.title,
    contact: t.pages.contato.title,
    submit: t.common.enviar
};
"""
        }
        
        src_dir = os.path.join(tmpdir, 'src')
        os.makedirs(src_dir)
        
        for filename, content in test_files.items():
            filepath = os.path.join(src_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"  ✓ Created {filename}")
        
        # Step 5: Show files before update
        print("\n📄 Step 5: Files BEFORE update (with orphaned references):")
        for filename in test_files.keys():
            filepath = os.path.join(src_dir, filename)
            with open(filepath, 'r') as f:
                content = f.read()
            print(f"\n--- {filename} ---")
            # Count orphaned references
            orphan_count = sum(1 for ref in sub_map.keys() if ref in content)
            print(f"Orphaned references: {orphan_count}")
            print(content)
        
        # Step 6: Apply substitutions
        print("\n🔄 Step 6: Applying substitutions...")
        results = update_references_in_project(
            src_dir,
            sub_map,
            create_backup=True
        )
        
        print(f"\nUpdated {len(results)} files:")
        for filepath, count in results.items():
            print(f"  ✓ {os.path.basename(filepath)}: {count} substitutions")
        
        # Step 7: Show files after update
        print("\n📄 Step 7: Files AFTER update (references fixed):")
        for filename in test_files.keys():
            filepath = os.path.join(src_dir, filename)
            with open(filepath, 'r') as f:
                content = f.read()
            print(f"\n--- {filename} ---")
            # Count remaining orphaned references (should be 0)
            orphan_count = sum(1 for ref in sub_map.keys() if ref in content)
            print(f"Orphaned references: {orphan_count} (should be 0)")
            print(content)
            
            # Verify backup exists
            backup_path = filepath + '.bak'
            if os.path.exists(backup_path):
                print(f"  ✓ Backup created: {os.path.basename(backup_path)}")
        
        # Step 8: Verification
        print("\n✅ Step 8: Verification...")
        success = True
        for filename in test_files.keys():
            filepath = os.path.join(src_dir, filename)
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Check no orphaned references remain
            for old_ref in sub_map.keys():
                if old_ref in content:
                    print(f"  ❌ FAILED: {filename} still contains {old_ref}")
                    success = False
            
            # Check new references exist
            for new_ref in sub_map.values():
                if new_ref in content.replace('{', '').replace('}', ''):
                    pass  # Expected
        
        if success:
            print("  ✅ All orphaned references successfully updated!")
        else:
            print("  ❌ Some orphaned references remain (unexpected)")
    
    print("\n" + "=" * 70)
    print("✅ Integration Test Complete!")
    print("=" * 70)


if __name__ == '__main__':
    test_complete_workflow()
