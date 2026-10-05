"""Collection policy for automated tests.

The ignored files are historical executable diagnostics: they run work at
import time, use local user documents or live translation services, and are not
pytest test modules. They remain available for explicit manual execution.
"""

IGNORED_TEST_MODULES = [
    "com3/test_all_formats_detailed.py",
    "com3/test_actual_extraction.py",
    "com3/test_camelcase_fix.py",
    "com3/test_camelcase_issue.py",
    "com3/test_case_conversion_complete.py",
    "com3/test_case_preservation.py",
    "com3/test_edge_cases.py",
    "com3/test_format_conversion.py",
    "com3/test_html_div_format.py",
    "com3/test_limit_parent_keys_with_real_jsx.py",
    "com3/test_toon_comprehensive.py",
    "com3/test_toon_format_check.py",
    "com8/test_adjacent_tags_fix_COM8.py",
    "com8/test_cli_direct_COM8.py",
    "com8/test_complete_workflow_COM8.py",
    "com8/test_complete_workflow_placeholder.py",
    "com8/test_end_to_end_translation_COM8.py",
    "com8/test_full_doc_placeholder.py",
    "com8/test_actual_translation_flow_COM8.py",
    "com8/test_generate_output_files_COM8.py",
    "com8/test_placeholder_system.py",
    "com8/test_pure_numbers.py",
    "com8/test_real_biology_text.py",
    "com8/test_regex_fix.py",
    "com8/test_tag_cleanup_simple.py",
    "com8/test_whitespace_protection.py",
    "com8/test_with_format_mapper_COM8.py",
    "extractor_comparison/test_extractor_equivalence.py",
    "test_ad1_siso_COM8.py",
    "test_apply_limit_restoration.py",
    "test_classname_restoration.py",
    "test_classname_with_limit_verification.py",
    "test_format_verification_user.py",
    "test_max_depth_js_literal_fix_3.py",
    "test_runner_monitored.py",
    "test_tag_workflow.py",
    "test_translate_pt_en_COM8.py",
]

collect_ignore = IGNORED_TEST_MODULES
