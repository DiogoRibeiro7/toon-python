# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.9.0-beta.2] - 2025-11-14

### Fixed
- **Issue #33**: Fixed decoder bug where nested objects within arrays were incorrectly returned as empty objects `[{}]` instead of the actual nested structure. The decoder now properly handles multi-line object format where the list item marker (`-`) appears on its own line with object fields on subsequent indented lines.
  - Added check for empty `item_content` in `decode_list_array` function
  - Now correctly calls `decode_object` to parse nested fields at appropriate depth
  - Removed incorrect fallback that created empty objects
  - Added comprehensive regression tests in `tests/test_edge_case.py`

- **Issue #30**: Fixed encoder bug where comma delimiter was incorrectly shown in array length brackets. Comma is the default delimiter and should not appear in brackets per TOON specification.
  - Tabular arrays now use `[N]{cols}:` format instead of `[N,]{cols}:`
  - Primitive arrays now use `[N]:` format instead of `[N,]:`
  - Non-default delimiters (pipe, tab) continue to show in brackets as expected
  - Added regression tests in `tests/test_encoder.py`

### Added
- New integration documentation file `docs/integration-examples.md` with comprehensive examples for:
  - Working with Pydantic models
  - Working with NumPy arrays
  - Working with Pandas DataFrames
  - Working with Python dataclasses
  - FastAPI integration patterns
  - Django integration patterns
  - LLM integration patterns
  - Data science workflows

- New edge case test suite `tests/test_edge_case.py` covering:
  - Simple nested objects in arrays
  - Multiple nested objects in arrays
  - Deeply nested objects (multi-level nesting)
  - Nested objects with multiple fields
  - Mixed nested and flat fields
  - Empty nested objects
  - Nested objects with primitive values
  - Roundtrip encoding/decoding preservation
  - Original issue #33 reported case

### Changed
- Test organization: Created dedicated `TestIssueRegressions` class in `tests/test_encoder.py` for tracking issue-specific regression tests

## [0.9.0-beta.1] - Previous Release

(Previous changelog entries would go here)
