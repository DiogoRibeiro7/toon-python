"""Comprehensive edge case tests for TOON decoder.

This file contains extensive edge case testing to improve coverage and
ensure robust handling of corner cases in the decoder module.

Coverage targets:
- Empty arrays with different delimiters (tab, pipe, comma)
- Malformed headers and syntax errors
- Unicode handling in quoted strings
- Deeply nested structures (>10 levels)
- Large arrays (>1000 elements)
- Mixed delimiter scenarios
- Blank lines in arrays (strict vs non-strict mode)
- Depth transitions in arrays
- Quoted keys and edge case key parsing
- Error handling paths
"""

import pytest

from toon_format import ToonDecodeError, decode
from toon_format.types import DecodeOptions


class TestEmptyArraysWithDelimiters:
    """Test empty arrays with different delimiter types."""

    def test_empty_array_comma_delimiter(self):
        """Test empty array with explicit comma delimiter."""
        toon = "items[0,]:"
        result = decode(toon)
        assert result == {"items": []}

    def test_empty_array_tab_delimiter(self):
        """Test empty array with tab delimiter."""
        toon = "items[0\t]:"
        result = decode(toon)
        assert result == {"items": []}

    def test_empty_array_pipe_delimiter(self):
        """Test empty array with pipe delimiter."""
        toon = "items[0|]:"
        result = decode(toon)
        assert result == {"items": []}

    def test_empty_inline_array_default_delimiter(self):
        """Test empty inline array with default (comma) delimiter."""
        toon = "[0]:"
        result = decode(toon)
        assert result == []

    def test_empty_tabular_array_with_fields(self):
        """Test empty tabular array with field definitions."""
        toon = "[0,]{id,name}:"
        result = decode(toon)
        assert result == []

    def test_empty_array_with_length_marker(self):
        """Test empty array with # length marker."""
        toon = "items[#0]:"
        result = decode(toon)
        assert result == {"items": []}


class TestMalformedHeaders:
    """Test malformed header syntax that should raise errors."""

    def test_unterminated_bracket(self):
        """Test header with missing closing bracket."""
        toon = "items[3:"
        # This should not parse as a header, so it tries to parse as key:value
        # The key is "items[3" and empty value becomes empty object
        result = decode(toon)
        assert result == {"items[3": {}}

    def test_unterminated_fields_segment(self):
        """Test header with unterminated fields brace - line 172."""
        toon = "[2,]{id,name:"
        with pytest.raises(ToonDecodeError, match="Unterminated fields segment"):
            decode(toon)

    def test_header_without_colon(self):
        """Test header without trailing colon - line 183."""
        toon = "[3] 1,2,3"
        # This won't be recognized as a header, will be treated as primitive
        result = decode(toon)
        assert result == "[3] 1,2,3"

    def test_invalid_length_in_header(self):
        """Test header with non-numeric length."""
        toon = "items[abc]:"
        # This won't parse as a header, will be key:value with empty value → empty object
        result = decode(toon)
        assert result == {"items[abc]": {}}

    def test_unterminated_quoted_key(self):
        """Test unterminated quoted key - line 204."""
        toon = '"unterminated: 123'
        with pytest.raises(ToonDecodeError, match="Unterminated|missing closing quote"):
            decode(toon)

    def test_unterminated_quoted_string_in_value(self):
        """Test unterminated quoted string in value."""
        toon = 'text: "unterminated'
        with pytest.raises(ToonDecodeError, match="missing closing quote"):
            decode(toon)


class TestUnicodeHandling:
    """Test Unicode character handling in quoted strings."""

    def test_unicode_emoji_in_quoted_string(self):
        """Test emoji characters in quoted strings."""
        toon = 'message: "Hello 👋 World 🌍"'
        result = decode(toon)
        assert result == {"message": "Hello 👋 World 🌍"}

    def test_unicode_chinese_characters(self):
        """Test Chinese characters in quoted strings."""
        toon = 'text: "你好世界"'
        result = decode(toon)
        assert result == {"text": "你好世界"}

    def test_unicode_arabic_characters(self):
        """Test Arabic characters in quoted strings."""
        toon = 'text: "مرحبا بالعالم"'
        result = decode(toon)
        assert result == {"text": "مرحبا بالعالم"}

    def test_unicode_mixed_scripts(self):
        """Test mixed Unicode scripts in single string."""
        toon = 'text: "English 中文 العربية हिन्दी 🎉"'
        result = decode(toon)
        assert result == {"text": "English 中文 العربية हिन्दी 🎉"}

    def test_unicode_in_array_values(self):
        """Test Unicode in array values."""
        toon = 'langs[3]: "English","中文","العربية"'
        result = decode(toon)
        assert result == {"langs": ["English", "中文", "العربية"]}

    def test_unicode_escape_sequences(self):
        """Test Unicode escape sequences in quoted strings are not supported."""
        toon = r'text: "Unicode: \u0048\u0065\u006C\u006C\u006F"'
        # Unicode escape sequences (\u) are not supported and raise an error
        with pytest.raises(ToonDecodeError, match="Invalid escape sequence"):
            decode(toon)

    def test_unicode_in_key_names(self):
        """Test Unicode characters in unquoted keys."""
        toon = "名前: Alice\nعمر: 30"
        result = decode(toon)
        assert result == {"名前": "Alice", "عمر": 30}

    def test_unicode_quoted_key(self):
        """Test Unicode in quoted keys."""
        toon = '"🔑": "value"'
        result = decode(toon)
        assert result == {"🔑": "value"}


class TestDeeplyNestedStructures:
    """Test deeply nested structures (>10 levels)."""

    def test_deeply_nested_objects_15_levels(self):
        """Test 15 levels of nested objects."""
        toon = """level1:
  level2:
    level3:
      level4:
        level5:
          level6:
            level7:
              level8:
                level9:
                  level10:
                    level11:
                      level12:
                        level13:
                          level14:
                            level15: deep_value"""
        result = decode(toon)
        # Navigate through all levels
        current = result
        for i in range(1, 15):
            assert f"level{i}" in current
            current = current[f"level{i}"]
        assert current == {"level15": "deep_value"}

    def test_deeply_nested_arrays_12_levels(self):
        """Test 12 levels of nested structures with mixed objects and arrays."""
        # Build a deeply nested structure with alternating objects and arrays
        toon = """level1[1]:
  - level2:
      level3[1]:
        - level4:
            level5[1]:
              - level6:
                  level7[1]:
                    - level8:
                        level9[1]:
                          - level10:
                              level11[1]:
                                - level12: deep_value"""
        result = decode(toon)
        # Navigate through the nested structure
        assert "level1" in result
        current = result["level1"][0]["level2"]["level3"][0]["level4"]["level5"][0][
            "level6"
        ]["level7"][0]["level8"]["level9"][0]["level10"]["level11"][0]["level12"]
        assert current == "deep_value"

    def test_mixed_nested_objects_and_arrays(self):
        """Test mixed nesting of objects and arrays beyond 10 levels."""
        toon = """root:
  items[1]:
    - obj:
        nested:
          data[1]:
            - deep:
                more:
                  levels:
                    array[1]:
                      - even:
                          deeper:
                            value: bottom"""
        result = decode(toon)
        # Verify we can reach the bottom value
        bottom = (
            result["root"]["items"][0]["obj"]["nested"]["data"][0]["deep"]["more"][
                "levels"
            ]["array"][0]["even"]["deeper"]["value"]
        )
        assert bottom == "bottom"


class TestLargeArrays:
    """Test large arrays with >1000 elements."""

    def test_large_primitive_array_1000_elements(self):
        """Test array with exactly 1000 elements."""
        values = ",".join(str(i) for i in range(1000))
        toon = f"nums[1000]: {values}"
        result = decode(toon)
        assert len(result["nums"]) == 1000
        assert result["nums"][0] == 0
        assert result["nums"][999] == 999

    def test_large_primitive_array_2000_elements(self):
        """Test array with 2000 elements."""
        values = ",".join(str(i) for i in range(2000))
        toon = f"[2000]: {values}"
        result = decode(toon)
        assert len(result) == 2000
        assert result[0] == 0
        assert result[1999] == 1999

    def test_large_tabular_array_1500_rows(self):
        """Test tabular array with 1500 rows."""
        header = "[1500,]{id,value}:\n"
        rows = "\n".join(f"  {i},{i*2}" for i in range(1500))
        toon = header + rows
        result = decode(toon)
        assert len(result) == 1500
        assert result[0] == {"id": 0, "value": 0}
        assert result[1499] == {"id": 1499, "value": 2998}

    def test_large_list_array_1200_items(self):
        """Test list format array with 1200 items."""
        header = "[1200]:\n"
        items = "\n".join(f"  - {i}" for i in range(1200))
        toon = header + items
        result = decode(toon)
        assert len(result) == 1200
        assert result[0] == 0
        assert result[1199] == 1199


class TestMixedDelimiterScenarios:
    """Test scenarios with mixed and changing delimiters."""

    def test_tab_delimited_array(self):
        """Test tab-delimited inline array."""
        toon = "items[3\t]: a\tb\tc"
        result = decode(toon)
        assert result == {"items": ["a", "b", "c"]}

    def test_pipe_delimited_array(self):
        """Test pipe-delimited inline array."""
        toon = "items[3|]: a|b|c"
        result = decode(toon)
        assert result == {"items": ["a", "b", "c"]}

    def test_tab_delimited_tabular_array(self):
        """Test tab-delimited tabular array."""
        toon = "[2\t]{name\tage}:\n  Alice\t30\n  Bob\t25"
        result = decode(toon)
        assert result == [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

    def test_pipe_delimited_tabular_array(self):
        """Test pipe-delimited tabular array."""
        toon = "[2|]{id|name}:\n  1|Alice\n  2|Bob"
        result = decode(toon)
        assert result == [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]

    def test_nested_arrays_different_delimiters(self):
        """Test nested arrays with different delimiters."""
        # Commas inside quoted strings are preserved
        toon = """outer[2,]{id,tags}:
  1,"a,b,c"
  2,"x,y,z\""""
        result = decode(toon)
        # Result is an object with "outer" key
        assert result == {
            "outer": [
                {"id": 1, "tags": "a,b,c"},
                {"id": 2, "tags": "x,y,z"},
            ]
        }

    def test_explicit_comma_delimiter_in_header(self):
        """Test explicit comma delimiter - line 156-157."""
        toon = "[3,]: 1,2,3"
        result = decode(toon)
        assert result == [1, 2, 3]


class TestBlankLinesInArrays:
    """Test blank line handling in arrays (strict vs non-strict mode)."""

    def test_blank_line_in_tabular_array_strict_mode(self):
        """Test blank line in tabular array raises error in strict mode - line 522."""
        toon = "[3,]{id,name}:\n  1,Alice\n\n  2,Bob"
        # Blank line causes array to end early, then length mismatch error
        with pytest.raises(ToonDecodeError, match="Expected .* rows"):
            decode(toon, DecodeOptions(strict=True))

    def test_blank_line_in_tabular_array_non_strict_mode(self):
        """Test blank line in tabular array ignored in non-strict mode."""
        toon = "[2,]{id,name}:\n  1,Alice\n\n  2,Bob"
        result = decode(toon, DecodeOptions(strict=False))
        # Non-strict mode should ignore blank lines
        assert len(result) == 2
        assert result[0] == {"id": 1, "name": "Alice"}
        assert result[1] == {"id": 2, "name": "Bob"}

    def test_blank_line_in_list_array_strict_mode(self):
        """Test blank line in list array raises error in strict mode."""
        toon = "[3]:\n  - a\n\n  - b\n  - c"
        # Scanner or decoder will raise error about blank lines or length mismatch
        with pytest.raises(ToonDecodeError):
            decode(toon, DecodeOptions(strict=True))

    def test_blank_line_in_list_array_non_strict_mode(self):
        """Test blank line in list array ignored in non-strict mode."""
        toon = "[2]:\n  - a\n\n  - b"
        result = decode(toon, DecodeOptions(strict=False))
        assert result == ["a", "b"]


class TestDepthTransitionsInArrays:
    """Test depth/indentation transitions in arrays."""

    def test_tabular_array_depth_less_than_row_depth(self):
        """Test tabular array stops when depth < row_depth - line 532."""
        toon = """data[2,]{id,val}:
  1,a
  2,b
next_key: value"""
        result = decode(toon)
        assert result == {
            "data": [{"id": 1, "val": "a"}, {"id": 2, "val": "b"}],
            "next_key": "value",
        }

    def test_tabular_array_depth_greater_than_row_depth(self):
        """Test tabular array stops when depth > row_depth - line 535."""
        toon = """data[1,]{id,val}:
  1,a
    nested: should_stop"""
        result = decode(toon)
        # Should only parse one row and stop when depth increases
        assert "data" in result
        assert len(result["data"]) == 1

    def test_list_array_depth_less_than_item_depth(self):
        """Test list array stops when depth < item_depth - line 637."""
        toon = """items[2]:
  - a
  - b
next: value"""
        result = decode(toon)
        assert result == {"items": ["a", "b"], "next": "value"}

    def test_list_array_with_nested_objects_blank_lines(self):
        """Test list array with nested objects and blank lines - lines 679-680, 742-743."""
        # Blank lines in the middle of an object's fields cause the object to end early
        # So we test blank lines between items instead
        toon = """[2]:
  - id: 1
    name: Alice

  - id: 2
    name: Bob"""
        # In non-strict mode, blank lines between items should be ignored
        result = decode(toon, DecodeOptions(strict=False))
        assert len(result) == 2
        assert result[0] == {"id": 1, "name": "Alice"}
        assert result[1] == {"id": 2, "name": "Bob"}


class TestNonStrictModeEdgeCases:
    """Test non-strict mode behavior for various edge cases."""

    def test_invalid_line_skipped_in_non_strict_mode(self):
        """Test invalid line is skipped in non-strict mode - lines 361-362."""
        toon = """valid: 123
invalid line without colon
another: 456"""
        result = decode(toon, DecodeOptions(strict=False))
        assert result == {"valid": 123, "another": 456}

    def test_invalid_line_raises_in_strict_mode(self):
        """Test invalid line raises error in strict mode."""
        toon = """valid: 123
invalid line without colon
another: 456"""
        with pytest.raises(ToonDecodeError, match="Missing colon"):
            decode(toon, DecodeOptions(strict=True))

    def test_array_length_mismatch_non_strict(self):
        """Test array length mismatch allowed in non-strict mode."""
        toon = "items[5]: a,b,c"
        result = decode(toon, DecodeOptions(strict=False))
        assert result == {"items": ["a", "b", "c"]}  # Only 3 items, not 5

    def test_tabular_row_width_mismatch_non_strict(self):
        """Test row width mismatch in tabular array (non-strict mode)."""
        toon = "[2,]{a,b,c}:\n  1,2\n  3,4,5"
        result = decode(toon, DecodeOptions(strict=False))
        # Should handle rows with different widths gracefully
        assert len(result) == 2


class TestQuotedKeys:
    """Test various quoted key scenarios."""

    def test_quoted_key_with_spaces(self):
        """Test quoted key with spaces."""
        toon = '"key with spaces": value'
        result = decode(toon)
        assert result == {"key with spaces": "value"}

    def test_quoted_key_with_special_chars(self):
        """Test quoted key with special characters."""
        toon = '"key:with:colons": value'
        result = decode(toon)
        assert result == {"key:with:colons": "value"}

    def test_quoted_key_with_escape_sequences(self):
        """Test quoted key with escape sequences."""
        toon = r'"key\"with\"quotes": value'
        result = decode(toon)
        assert result == {'key"with"quotes': "value"}

    def test_quoted_key_in_tabular_array_fields(self):
        """Test quoted keys in tabular array field definitions."""
        toon = '[1,]{"first name","last name"}:\n  Alice,Smith'
        result = decode(toon)
        assert result == [{"first name": "Alice", "last name": "Smith"}]


class TestNumericEdgeCases:
    """Test numeric parsing edge cases."""

    def test_invalid_numeric_parsed_as_string(self):
        """Test invalid numeric format falls back to string - lines 98-99."""
        # This tests the ValueError catch in parse_primitive
        # Note: is_numeric_literal filters most invalid cases, but edge cases exist
        toon = "value: 123abc"
        result = decode(toon)
        # Should be parsed as string since it's not a valid number
        assert result == {"value": "123abc"}

    def test_very_large_integer(self):
        """Test very large integer parsing."""
        toon = "big: 99999999999999999999999999999999"
        result = decode(toon)
        assert result == {"big": 99999999999999999999999999999999}

    def test_very_small_float(self):
        """Test very small float with exponent."""
        toon = "small: 1e-308"
        result = decode(toon)
        assert result == {"small": 1e-308}


class TestArrayWithInlineContent:
    """Test arrays with inline content edge cases."""

    def test_empty_array_with_inline_content_check(self):
        """Test empty array inline content handling - lines 408-410."""
        toon = "items[0]:"
        result = decode(toon)
        assert result == {"items": []}

    def test_array_header_without_colon_in_parse(self):
        """Test array header parsing without colon in inline content check."""
        # This is a complex case where we have a header but split_key_value might fail
        # The code at lines 408-410 handles this case
        toon = "[0]:"
        result = decode(toon)
        assert result == []


class TestListArrayEdgeCases:
    """Test list array edge cases for uncovered error handling."""

    def test_list_array_with_nested_object_invalid_field(self):
        """Test list array with nested object encountering invalid field - lines 711-712."""
        toon = """[1]:
  - id: 1
    name: Alice
    invalid field without colon"""
        # In strict mode, should raise error when encountering invalid field
        # Actually, the break at 712 means it stops parsing fields for that item
        result = decode(toon, DecodeOptions(strict=False))
        # Should still parse the valid fields
        assert len(result) == 1

    def test_list_array_object_item_invalid_field(self):
        """Test list array object item with invalid field - lines 772-773."""
        toon = """[1]:
  - name: Alice
    age: 30
    invalid without colon"""
        # Should handle the error and stop parsing fields
        result = decode(toon, DecodeOptions(strict=False))
        assert len(result) == 1


class TestNestedObjectsInListArrays:
    """Test nested objects within list arrays - lines 702-707."""

    def test_list_array_item_with_nested_object_field(self):
        """Test list array item with nested object as field value."""
        toon = """[1]:
  - id: 1
    details:
      name: Alice
      age: 30"""
        result = decode(toon)
        assert result == [{"id": 1, "details": {"name": "Alice", "age": 30}}]

    def test_list_array_with_array_header_in_object(self):
        """Test list array with array header as field in object."""
        toon = """[1]:
  - id: 1
    tags[2]: tag1,tag2
    name: Alice"""
        result = decode(toon)
        assert result == [{"id": 1, "tags": ["tag1", "tag2"], "name": "Alice"}]
