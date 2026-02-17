#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for TableManager and TableData classes.

Tests table preservation system for Google Translate tool.
Covers storage, retrieval, HTML conversion, and edge cases.

Author: Josué Amaral (COM8)
Date: February 17, 2026
Phase: 2.3 - TableManager Implementation
"""

import pytest
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).resolve().parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))

from translation.docx_html_mapper import TableData, TableManager


# ============================================================================
# TableData Tests
# ============================================================================

class TestTableData:
    """Test TableData dataclass functionality."""
    
    def test_create_simple_table(self):
        """Test creating a simple 2x2 table."""
        cells = [['A', 'B'], ['C', 'D']]
        table = TableData(
            table_id='TBL001',
            rows=2,
            cols=2,
            cells=cells
        )
        
        assert table.table_id == 'TBL001'
        assert table.rows == 2
        assert table.cols == 2
        assert table.cells == cells
        assert table.style is None
        assert table.document_index is None
    
    def test_create_table_with_style(self):
        """Test creating table with style."""
        cells = [['Header 1', 'Header 2'], ['Row 1', 'Row 2']]
        table = TableData(
            table_id='TBL002',
            rows=2,
            cols=2,
            cells=cells,
            style='Normal Table',
            document_index=5
        )
        
        assert table.style == 'Normal Table'
        assert table.document_index == 5
    
    def test_get_cell_valid_index(self):
        """Test getting cell content with valid indices."""
        cells = [['A', 'B', 'C'], ['D', 'E', 'F']]
        table = TableData(table_id='TBL001', rows=2, cols=3, cells=cells)
        
        assert table.get_cell(0, 0) == 'A'
        assert table.get_cell(0, 1) == 'B'
        assert table.get_cell(0, 2) == 'C'
        assert table.get_cell(1, 0) == 'D'
        assert table.get_cell(1, 1) == 'E'
        assert table.get_cell(1, 2) == 'F'
    
    def test_get_cell_out_of_bounds(self):
        """Test getting cell with out-of-bounds indices."""
        cells = [['A', 'B'], ['C', 'D']]
        table = TableData(table_id='TBL001', rows=2, cols=2, cells=cells)
        
        # Out of bounds should return empty string
        assert table.get_cell(-1, 0) == ''
        assert table.get_cell(0, -1) == ''
        assert table.get_cell(2, 0) == ''
        assert table.get_cell(0, 2) == ''
        assert table.get_cell(10, 10) == ''
    
    def test_set_cell_valid_index(self):
        """Test setting cell content with valid indices."""
        cells = [['A', 'B'], ['C', 'D']]
        table = TableData(table_id='TBL001', rows=2, cols=2, cells=cells)
        
        table.set_cell(0, 0, 'X')
        table.set_cell(1, 1, 'Y')
        
        assert table.get_cell(0, 0) == 'X'
        assert table.get_cell(1, 1) == 'Y'
        assert table.get_cell(0, 1) == 'B'  # Unchanged
        assert table.get_cell(1, 0) == 'C'  # Unchanged
    
    def test_set_cell_out_of_bounds(self):
        """Test setting cell with out-of-bounds indices (should be no-op)."""
        cells = [['A', 'B'], ['C', 'D']]
        table = TableData(table_id='TBL001', rows=2, cols=2, cells=cells)
        
        # These should not crash or modify anything
        table.set_cell(-1, 0, 'X')
        table.set_cell(0, -1, 'X')
        table.set_cell(2, 0, 'X')
        table.set_cell(0, 2, 'X')
        
        # Original data should be unchanged
        assert table.cells == [['A', 'B'], ['C', 'D']]
    
    def test_to_html_simple(self):
        """Test HTML conversion for simple table."""
        cells = [['A', 'B'], ['C', 'D']]
        table = TableData(table_id='TBL001', rows=2, cols=2, cells=cells)
        
        html = table.to_html()
        
        # Check structure
        assert '<table data-table="TBL001">' in html
        assert '<tr>' in html
        assert '<td>A</td>' in html
        assert '<td>B</td>' in html
        assert '<td>C</td>' in html
        assert '<td>D</td>' in html
        assert '</tr>' in html
        assert '</table>' in html
        
        # Check that rows are separate
        assert html.count('<tr>') == 2
        assert html.count('</tr>') == 2
    
    def test_to_html_with_special_characters(self):
        """Test HTML escaping for special characters."""
        cells = [['<script>', 'A & B'], ['"quote"', "It's"]]
        table = TableData(table_id='TBL002', rows=2, cols=2, cells=cells)
        
        html = table.to_html()
        
        # Check that special characters are escaped
        assert '&lt;script&gt;' in html
        assert 'A &amp; B' in html
        assert '&quot;quote&quot;' in html
        assert 'It&#x27;s' in html
        
        # Check that unescaped versions are NOT present
        assert '<script>' not in html.replace('<table', '').replace('</table', '')
        assert 'A & B' not in html.replace('&amp;', '')
    
    def test_to_html_empty_cells(self):
        """Test HTML conversion with empty cells."""
        cells = [['', 'B'], ['C', '']]
        table = TableData(table_id='TBL003', rows=2, cols=2, cells=cells)
        
        html = table.to_html()
        
        # Empty cells should still have <td></td> tags
        assert '<td></td>' in html
        assert html.count('<td>') == 4
        assert html.count('</td>') == 4
    
    def test_get_dimensions(self):
        """Test getting table dimensions."""
        cells = [['A', 'B', 'C'], ['D', 'E', 'F']]
        table = TableData(table_id='TBL001', rows=2, cols=3, cells=cells)
        
        dims = table.get_dimensions()
        assert dims == (2, 3)
    
    def test_single_cell_table(self):
        """Test 1x1 table (edge case)."""
        cells = [['Single Cell']]
        table = TableData(table_id='TBL999', rows=1, cols=1, cells=cells)
        
        assert table.rows == 1
        assert table.cols == 1
        assert table.get_cell(0, 0) == 'Single Cell'
        
        html = table.to_html()
        assert '<td>Single Cell</td>' in html
        assert html.count('<tr>') == 1


# ============================================================================
# TableManager Tests
# ============================================================================

class TestTableManager:
    """Test TableManager class functionality."""
    
    def test_create_empty_manager(self):
        """Test creating empty TableManager."""
        manager = TableManager()
        
        assert manager.get_table_count() == 0
        assert manager.get_all_tables() == []
    
    def test_add_single_table(self):
        """Test adding a single table."""
        manager = TableManager()
        cells = [['A', 'B'], ['C', 'D']]
        
        table_id = manager.add_table(rows=2, cols=2, cells=cells)
        
        assert table_id == 'TBL001'
        assert manager.get_table_count() == 1
        assert manager.has_table('TBL001')
    
    def test_add_multiple_tables(self):
        """Test adding multiple tables with sequential IDs."""
        manager = TableManager()
        
        id1 = manager.add_table(rows=2, cols=2, cells=[['A', 'B'], ['C', 'D']])
        id2 = manager.add_table(rows=1, cols=1, cells=[['X']])
        id3 = manager.add_table(rows=3, cols=2, cells=[['1', '2'], ['3', '4'], ['5', '6']])
        
        assert id1 == 'TBL001'
        assert id2 == 'TBL002'
        assert id3 == 'TBL003'
        assert manager.get_table_count() == 3
    
    def test_get_table_by_id(self):
        """Test retrieving table by ID."""
        manager = TableManager()
        cells = [['Header 1', 'Header 2'], ['Row 1', 'Row 2']]
        table_id = manager.add_table(rows=2, cols=2, cells=cells, style='Grid Table')
        
        table = manager.get_table(table_id)
        
        assert table is not None
        assert table.table_id == 'TBL001'
        assert table.rows == 2
        assert table.cols == 2
        assert table.cells == cells
        assert table.style == 'Grid Table'
    
    def test_get_nonexistent_table(self):
        """Test getting table that doesn't exist."""
        manager = TableManager()
        
        table = manager.get_table('TBL999')
        
        assert table is None
    
    def test_has_table(self):
        """Test has_table() method."""
        manager = TableManager()
        manager.add_table(rows=1, cols=1, cells=[['X']])
        
        assert manager.has_table('TBL001') is True
        assert manager.has_table('TBL002') is False
        assert manager.has_table('TBL999') is False
    
    def test_get_all_tables_order(self):
        """Test that get_all_tables() preserves document order."""
        manager = TableManager()
        
        manager.add_table(rows=1, cols=1, cells=[['First']])
        manager.add_table(rows=1, cols=1, cells=[['Second']])
        manager.add_table(rows=1, cols=1, cells=[['Third']])
        
        tables = manager.get_all_tables()
        
        assert len(tables) == 3
        assert tables[0].cells[0][0] == 'First'
        assert tables[1].cells[0][0] == 'Second'
        assert tables[2].cells[0][0] == 'Third'
    
    def test_generate_html_placeholder(self):
        """Test generating HTML placeholder for table."""
        manager = TableManager()
        cells = [['A', 'B'], ['C', 'D']]
        table_id = manager.add_table(rows=2, cols=2, cells=cells)
        
        html = manager.generate_html_placeholder(table_id)
        
        assert '<table data-table="TBL001">' in html
        assert '<td>A</td>' in html
        assert '<td>D</td>' in html
    
    def test_generate_html_placeholder_nonexistent(self):
        """Test generating placeholder for nonexistent table raises error."""
        manager = TableManager()
        
        with pytest.raises(ValueError, match='Table not found'):
            manager.generate_html_placeholder('TBL999')
    
    def test_get_statistics_empty(self):
        """Test statistics for empty manager."""
        manager = TableManager()
        
        stats = manager.get_statistics()
        
        assert stats['table_count'] == 0
        assert stats['total_cells'] == 0
        assert stats['largest_table'] == 0
        assert stats['table_ids'] == []
    
    def test_get_statistics_multiple_tables(self):
        """Test statistics with multiple tables."""
        manager = TableManager()
        
        manager.add_table(rows=2, cols=2, cells=[['A', 'B'], ['C', 'D']])  # 4 cells
        manager.add_table(rows=3, cols=3, cells=[['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']])  # 9 cells
        manager.add_table(rows=1, cols=1, cells=[['X']])  # 1 cell
        
        stats = manager.get_statistics()
        
        assert stats['table_count'] == 3
        assert stats['total_cells'] == 14  # 4 + 9 + 1
        assert stats['largest_table'] == 9
        assert stats['table_ids'] == ['TBL001', 'TBL002', 'TBL003']
    
    def test_clear(self):
        """Test clearing all tables."""
        manager = TableManager()
        
        manager.add_table(rows=1, cols=1, cells=[['A']])
        manager.add_table(rows=1, cols=1, cells=[['B']])
        
        assert manager.get_table_count() == 2
        
        manager.clear()
        
        assert manager.get_table_count() == 0
        assert manager.get_all_tables() == []
        
        # Next table should be TBL001 again
        new_id = manager.add_table(rows=1, cols=1, cells=[['C']])
        assert new_id == 'TBL001'
    
    def test_validation_wrong_row_count(self):
        """Test that wrong row count raises ValueError."""
        manager = TableManager()
        cells = [['A', 'B'], ['C', 'D'], ['E', 'F']]  # 3 rows
        
        with pytest.raises(ValueError, match='Expected 2 rows'):
            manager.add_table(rows=2, cols=2, cells=cells)  # Claims 2 rows
    
    def test_validation_wrong_col_count(self):
        """Test that wrong column count raises ValueError."""
        manager = TableManager()
        cells = [['A', 'B'], ['C', 'D', 'E']]  # Row 1 has 3 cols
        
        with pytest.raises(ValueError, match='Row 1 has 3 cells, expected 2'):
            manager.add_table(rows=2, cols=2, cells=cells)
    
    def test_validation_jagged_array(self):
        """Test that jagged array raises ValueError."""
        manager = TableManager()
        cells = [['A', 'B', 'C'], ['D', 'E'], ['F', 'G', 'H']]
        
        with pytest.raises(ValueError):
            manager.add_table(rows=3, cols=3, cells=cells)


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_large_table(self):
        """Test handling of large table (100x100)."""
        manager = TableManager()
        
        # Create 100x100 table
        cells = [[f'R{r}C{c}' for c in range(100)] for r in range(100)]
        table_id = manager.add_table(rows=100, cols=100, cells=cells)
        
        assert table_id == 'TBL001'
        assert manager.get_table_count() == 1
        
        table = manager.get_table(table_id)
        assert table.rows == 100
        assert table.cols == 100
        assert table.get_cell(50, 50) == 'R50C50'
        
        stats = manager.get_statistics()
        assert stats['total_cells'] == 10_000
        assert stats['largest_table'] == 10_000
    
    def test_table_with_multiline_cells(self):
        """Test table cells with newlines."""
        manager = TableManager()
        cells = [['Line 1\nLine 2', 'Single'], ['Multi\nLine\nCell', 'Normal']]
        table_id = manager.add_table(rows=2, cols=2, cells=cells)
        
        table = manager.get_table(table_id)
        assert '\n' in table.get_cell(0, 0)
        assert '\n' in table.get_cell(1, 0)
        
        html = table.to_html()
        # Newlines should be preserved in HTML
        assert 'Line 1\nLine 2' in html
    
    def test_table_with_unicode(self):
        """Test table with Unicode characters."""
        manager = TableManager()
        cells = [['你好', 'مرحبا'], ['Привет', '🎉']]
        table_id = manager.add_table(rows=2, cols=2, cells=cells)
        
        table = manager.get_table(table_id)
        assert table.get_cell(0, 0) == '你好'
        assert table.get_cell(1, 1) == '🎉'
        
        html = table.to_html()
        assert '你好' in html
        assert '🎉' in html
    
    def test_table_with_long_text(self):
        """Test table with very long cell content."""
        manager = TableManager()
        long_text = 'A' * 10_000  # 10K characters
        cells = [[long_text, 'Short']]
        table_id = manager.add_table(rows=1, cols=2, cells=cells)
        
        table = manager.get_table(table_id)
        assert len(table.get_cell(0, 0)) == 10_000
        
        html = table.to_html()
        assert long_text in html
    
    def test_rectangular_tables(self):
        """Test non-square tables (different rows/cols)."""
        manager = TableManager()
        
        # Wide table (1 row, 10 cols)
        wide_cells = [['C' + str(i) for i in range(10)]]
        id1 = manager.add_table(rows=1, cols=10, cells=wide_cells)
        
        # Tall table (10 rows, 1 col)
        tall_cells = [['R' + str(i)] for i in range(10)]
        id2 = manager.add_table(rows=10, cols=1, cells=tall_cells)
        
        wide_table = manager.get_table(id1)
        tall_table = manager.get_table(id2)
        
        assert wide_table.get_dimensions() == (1, 10)
        assert tall_table.get_dimensions() == (10, 1)


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
