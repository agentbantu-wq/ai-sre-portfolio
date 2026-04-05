"""
Test suite for AI-SRE-Readiness-Checker
"""

import pytest
from src.evaluator import Evaluator
from src.config import get_default_checklist


class TestEvaluator:
    """Tests for core evaluator"""
    
    def test_evaluator_init(self):
        """Test evaluator initialization"""
        checklist = get_default_checklist()
        evaluator = Evaluator("Test Tool", checklist)
        assert evaluator.tool_name == "Test Tool"
        assert evaluator.checklist is not None
    
    def test_default_checklist(self):
        """Test default checklist loads"""
        checklist = get_default_checklist()
        assert 'context' in checklist
        assert 'investigation' in checklist
        assert 'actionability' in checklist
        assert 'safety' in checklist
        assert 'efficiency' in checklist
    
    def test_pillars_exist(self):
        """Test all expected pillars exist"""
        expected = ['context', 'investigation', 'actionability', 'safety', 'efficiency']
        assert Evaluator.PILLARS == expected


if __name__ == '__main__':
    pytest.main([__file__])
