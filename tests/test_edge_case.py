"""Edge case tests for nested objects within arrays.

Regression tests for GitHub issue #33.
Issue: Decoder fails to parse nested objects within arrays (returns empty objects)
URL: https://github.com/toon-format/toon-python/issues/33
"""

from toon_format import decode, encode


class TestNestedObjectsInArrays:
    """Test cases for issue #33: nested objects within arrays."""

    def test_simple_nested(self):
        """Test decoding array with single nested object."""
        test_data = [{"a": {"b": "123"}}]

        encoded = encode(test_data, {"lengthMarker": "#"})
        decoded = decode(encoded)

        assert decoded == test_data

    def test_multiple_nested(self):
        """Test decoding array with multiple nested objects."""
        test_data = [{"a": {"b": "1"}}, {"c": {"d": "2"}}]

        encoded = encode(test_data)
        decoded = decode(encoded)

        assert decoded == test_data

    def test_deeply_nested(self):
        """Test decoding array with deeply nested objects."""
        test_data = [{"a": {"b": {"c": {"d": "value"}}}}]

        encoded = encode(test_data)
        decoded = decode(encoded)

        assert decoded == test_data

    def test_nested_with_multiple_fields(self):
        """Test decoding array with nested object containing multiple fields."""
        test_data = [{"outer": {"inner1": "value1", "inner2": "value2"}}]

        encoded = encode(test_data)
        decoded = decode(encoded)

        assert decoded == test_data

    def test_mixed_nested_and_flat(self):
        """Test decoding array with mix of nested and flat fields."""
        test_data = [{"flat": "value", "nested": {"inner": "data"}}]

        encoded = encode(test_data)
        decoded = decode(encoded)

        assert decoded == test_data

    def test_empty_nested(self):
        """Test decoding array with empty nested object."""
        test_data = [{"outer": {}}]

        encoded = encode(test_data)
        decoded = decode(encoded)

        assert decoded == test_data

    def test_nested_with_primitives(self):
        """Test decoding array with nested object containing primitive values."""
        test_data = [
            {
                "user": {
                    "name": "Alice",
                    "age": 30,
                    "active": True,
                    "score": None,
                }
            }
        ]

        encoded = encode(test_data)
        decoded = decode(encoded)

        assert decoded == test_data

    def test_roundtrip(self):
        """Test encode-decode roundtrip preserves nested structure."""
        test_data = [
            {"data": {"nested": {"deep": "value"}}},
            {"data": {"nested": {"deep": "other"}}},
        ]

        encoded = encode(test_data)
        decoded = decode(encoded)

        assert decoded == test_data

    def test_original_reported_case(self):
        """Test the exact example from issue #33."""
        test_data = [{"a": {"b": "123"}}]

        encoded = encode(test_data, {"lengthMarker": "#"})

        # Verify encoded format matches expected
        expected_toon = '[#1]:\n  -\n    a:\n      b: "123"'
        assert encoded == expected_toon

        # Verify decode works correctly
        decoded = decode(encoded)
        assert decoded == test_data
        assert decoded != [{}]  # Should NOT be an empty object
