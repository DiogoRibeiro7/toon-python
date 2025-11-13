"""Tests for Python-specific TOON encoder behavior.

This file contains ONLY Python-specific encoder tests that are not covered
by the official spec fixtures in test_spec_fixtures.py.

For spec compliance testing, see test_spec_fixtures.py (306 official tests).
For Python type normalization, see test_normalization.py.
For API testing, see test_api.py.
"""

import pytest

from toon_format import encode
from toon_format.types import EncodeOptions


class TestPythonEncoderAPI:
    """Test Python-specific encoder API behavior."""

    def test_encode_accepts_dict_options(self):
        """Test that encode accepts options as plain dict (Python convenience)."""
        result = encode([1, 2, 3], {"delimiter": "\t"})
        assert result == "[3\t]: 1\t2\t3"

    def test_encode_accepts_encode_options_object(self):
        """Test that encode accepts EncodeOptions typed object."""
        options = EncodeOptions(delimiter="|", indent=4)
        result = encode([1, 2, 3], options)
        assert result == "[3|]: 1|2|3"

    def test_encode_returns_python_str(self):
        """Ensure encode returns native Python str, not bytes or custom type."""
        result = encode({"id": 123})
        assert isinstance(result, str)
        assert type(result) is str  # Not a subclass

    def test_encode_handles_none_gracefully(self):
        """Test encoding None doesn't crash (Python-specific edge case)."""
        result = encode(None)
        assert result == "null"
        assert isinstance(result, str)


class TestPythonTypeHandling:
    """Test encoding of Python-specific types that require normalization."""

    def test_callable_becomes_null(self):
        """Callables (functions, methods) should normalize to null."""

        def func():
            pass

        result = encode(func)
        assert result == "null"

    def test_lambda_becomes_null(self):
        """Lambda functions should normalize to null."""
        result = encode(lambda x: x)
        assert result == "null"

    def test_class_instance_becomes_null(self):
        """Custom class instances should normalize to null."""

        class CustomClass:
            pass

        obj = CustomClass()
        result = encode(obj)
        assert result == "null"

    def test_builtin_function_becomes_null(self):
        """Built-in functions should normalize to null."""
        result = encode(len)
        assert result == "null"


class TestNonFiniteNumbers:
    """Test encoding of non-finite float values (Python-specific)."""

    def test_positive_infinity_becomes_null(self):
        """float('inf') should encode as null."""
        result = encode(float("inf"))
        assert result == "null"

    def test_negative_infinity_becomes_null(self):
        """float('-inf') should encode as null."""
        result = encode(float("-inf"))
        assert result == "null"

    def test_nan_becomes_null(self):
        """float('nan') should encode as null."""
        result = encode(float("nan"))
        assert result == "null"

    def test_infinity_in_object(self):
        """Infinity in object should encode field as null."""
        obj = {"value": float("inf")}
        result = encode(obj)
        assert "value: null" in result

    def test_nan_in_array(self):
        """NaN in array should encode as null."""
        arr = [1, float("nan"), 3]
        result = encode(arr)
        assert "[3]: 1,null,3" in result


class TestPythonOptionsHandling:
    """Test Python-specific options handling."""

    def test_invalid_option_type_handling(self):
        """Test that invalid options don't cause crashes."""
        # Should either accept or raise a clear error, not crash
        try:
            result = encode([1, 2, 3], EncodeOptions(delimiter=123))  # type: ignore[typeddict-item]
            # If accepted, verify output exists
            assert result is not None
        except (TypeError, ValueError, AttributeError):
            # Also acceptable to reject invalid types
            pass

    def test_options_with_none_values(self):
        """Test that None option values are handled gracefully."""
        # Should use defaults for None values or raise clear error
        try:
            result = encode([1, 2, 3], EncodeOptions(delimiter=None))  # type: ignore[typeddict-item]
            assert result is not None
        except (TypeError, ValueError, AttributeError):
            # Also acceptable to reject None
            pass

    def test_encode_with_extra_unknown_options(self):
        """Test that unknown options are ignored (forward compatibility)."""
        # Unknown options should be ignored, not cause errors
        result = encode([1, 2, 3], EncodeOptions(delimiter=",", unknown_option="value"))  # type: ignore[typeddict-unknown-key]
        assert result == "[3]: 1,2,3"


class TestNumberPrecisionSpec:
    """Tests for number precision requirements per Section 2 of spec."""

    def test_no_scientific_notation_in_output(self):
        """Encoders MUST NOT use scientific notation (Section 2)."""
        # Large numbers should be written in full decimal form
        data = {"big": 1000000}
        result = encode(data)
        assert "1000000" in result
        assert "1e6" not in result.lower()
        assert "1e+6" not in result.lower()

    def test_small_decimals_no_scientific_notation(self):
        """Small decimals should not use scientific notation."""
        data = {"small": 0.000001}
        result = encode(data)
        assert "0.000001" in result
        assert "1e-6" not in result.lower()

    def test_round_trip_precision_preserved(self):
        """Numbers must preserve round-trip fidelity (Section 2)."""
        original = {
            "float": 3.14159265358979,
            "small": 0.1 + 0.2,
            "large": 999999999999999,
        }
        toon = encode(original)
        from toon_format import decode

        decoded = decode(toon)
        assert isinstance(decoded, dict)

        # Should round-trip with fidelity
        assert decoded["float"] == original["float"]
        assert decoded["small"] == original["small"]
        assert decoded["large"] == original["large"]

    def test_negative_zero_normalized(self):
        """-0 MUST be normalized to 0 (Section 2)."""
        data = {"value": -0.0}
        result = encode(data)
        # Should not contain "-0"
        assert "-0" not in result
        # Should contain positive 0
        assert "value: 0" in result

    def test_negative_zero_in_array(self):
        """-0 in arrays should be normalized."""
        data = [-0.0, 0.0, 1.0]
        result = encode(data)
        # Should not have -0
        assert "-0" not in result

    def test_key_order_preserved(self):
        """Object key order MUST be preserved (Section 2)."""
        from collections import OrderedDict

        # Use OrderedDict to ensure specific order
        data = OrderedDict([("z", 1), ("a", 2), ("m", 3)])
        result = encode(data)
        lines = result.split("\n")
        # Verify order in output
        assert "z:" in lines[0]
        assert "a:" in lines[1]
        assert "m:" in lines[2]


class TestIssueRegressions:
    """Regression tests for reported GitHub issues.
    
    Each test is marked with @pytest.mark.issue_regression and references
    the specific GitHub issue number for traceability.
    """

    @pytest.mark.issue_regression
    def test_issue_30_comma_delimiter_not_shown_in_tabular_brackets(self) -> None:
        """Tabular arrays should use [N]{cols}: not [N,]{cols}: with comma delimiter.

        GitHub Issue #30: https://github.com/toon-format/toon-python/issues/30
        The comma delimiter is the default and should not appear in the length bracket.
        Non-comma delimiters (pipe, tab) should appear in the bracket.
        """
        # Test with default comma delimiter (should be implicit, not shown)
        data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        result = encode(data)

        # Verify correct format without delimiter in bracket
        assert "[2]{id,name}:" in result
        assert "[2,]{" not in result, "Comma should not appear in bracket"
        assert ",]{" not in result, "Comma should not appear before closing bracket"

        # Test with pipe delimiter - should be explicit
        result_pipe = encode(data, {"delimiter": "|"})
        assert "[2|]{id|name}:" in result_pipe, "Pipe delimiter should appear in bracket"
        assert "[2]{" not in result_pipe, "Bracket should include pipe delimiter"

        # Test with tab delimiter - should be explicit
        result_tab = encode(data, {"delimiter": "\t"})
        assert "[2\t]{" in result_tab, "Tab delimiter should appear in bracket"

    @pytest.mark.issue_regression
    def test_issue_30_comma_not_shown_in_primitive_array_brackets(self) -> None:
        """Primitive arrays should use [N]: not [N,]: with comma delimiter.

        Related to GitHub Issue #30.
        Comma is the default delimiter and should be implicit in array length brackets.
        """
        # Test inline primitive array with default comma delimiter
        data = [1, 2, 3]
        result = encode(data)

        # Verify correct format
        assert "[3]:" in result, "Should use [N]: format for default delimiter"
        assert "[3,]:" not in result, "Comma should not appear in bracket"

        # Test with pipe delimiter - should be explicit
        result_pipe = encode(data, {"delimiter": "|"})
        assert "[3|]:" in result_pipe, "Non-default delimiter should appear in bracket"
