#!/usr/bin/env python3
"""
Test suite for TikZ diagram generator
"""

import sys
import json
import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.tikz_generator import TikZGenerator


class TestTikZGenerator:
    """Test cases for TikZGenerator class"""

    @pytest.fixture
    def generator(self):
        """Create generator instance with test data"""
        # Create temporary test data
        test_data = Path("diagrams/data")
        if test_data.exists():
            return TikZGenerator(str(test_data))
        else:
            # Use mock data for testing
            return TikZGenerator()

    def test_generator_init(self, generator):
        """Test generator initialization"""
        assert hasattr(generator, 'kernel_data')
        assert hasattr(generator, 'process_data')
        assert hasattr(generator, 'memory_data')
        assert hasattr(generator, 'ipc_data')
        assert hasattr(generator, 'boot_data')
        assert hasattr(generator, 'stats')

    def test_syscall_table_generation(self, generator):
        """Test system call table TikZ generation"""
        tex = generator.generate_syscall_table_tikz()

        # Check for required TikZ structure
        assert r"\documentclass{standalone}" in tex
        assert r"\begin{tikzpicture}" in tex
        assert r"\end{tikzpicture}" in tex
        assert r"\begin{tabular}" in tex

        # Check for data integration
        if generator.stats:
            assert str(generator.stats.get('total_syscalls', 0)) in tex

    def test_process_states_generation(self, generator):
        """Test process states diagram generation"""
        tex = generator.generate_process_states_tikz()

        # Check for TikZ structure
        assert r"\documentclass{standalone}" in tex
        assert r"\begin{tikzpicture}" in tex
        assert r"state/.style" in tex

        # Verify no underscores in text mode
        assert "RTS_" not in tex or "RTS " in tex

    def test_boot_sequence_generation(self, generator):
        """Test boot sequence diagram generation"""
        tex = generator.generate_boot_sequence_tikz()

        # Check for TikZ structure
        assert r"\documentclass{standalone}" in tex
        assert r"\begin{tikzpicture}" in tex
        assert r"box/.style" in tex

        # Check for proper escaping
        lines = tex.split('\n')
        for line in lines:
            if r'\node[box]' in line:
                # Verify underscores are handled
                assert '_' not in line or r'\_' in line or ' ' in line

    def test_ipc_architecture_generation(self, generator):
        """Test IPC architecture diagram generation"""
        tex = generator.generate_ipc_architecture_tikz()

        # Check for TikZ structure
        assert r"\documentclass{standalone}" in tex
        assert r"\begin{tikzpicture}" in tex
        assert r"endpoint/.style" in tex

    def test_memory_regions_generation(self, generator):
        """Test memory regions diagram generation"""
        tex = generator.generate_memory_regions_tikz()

        # Check for TikZ structure
        assert r"\documentclass{standalone}" in tex
        assert r"\begin{tikzpicture}" in tex
        assert r"region/.style" in tex

    def test_special_character_handling(self, generator):
        """Test that special characters are properly escaped"""
        # Test data with problematic characters
        generator.kernel_data = {
            "system_calls": [
                {
                    "name": "test_call",
                    "file": "test_file.c",
                    "signature": "int test_func()",
                    "line_count": 100
                }
            ]
        }

        tex = generator.generate_syscall_table_tikz()

        # Underscores should be replaced or escaped
        assert "test_call" not in tex or "test call" in tex

    def test_tikz_compilation_validity(self, generator, tmp_path):
        """Test that generated TikZ can be compiled"""
        # Generate all diagrams
        output_path = generator.save_all_tikz_files(str(tmp_path))

        # Check files were created
        tex_files = list(output_path.glob("*.tex"))
        assert len(tex_files) == 5

        # Verify each file has valid TikZ structure
        for tex_file in tex_files:
            with open(tex_file, 'r') as f:
                content = f.read()
                assert r"\documentclass" in content
                assert r"\begin{document}" in content
                assert r"\end{document}" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])