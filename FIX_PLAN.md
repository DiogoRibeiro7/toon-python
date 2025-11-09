# Python 3.8 Compatibility Fix Plan

## Branch
`fix/python-38-compatibility`

## Problem Summary

**Root Cause:** The codebase uses Python 3.9+ type annotation syntax (`dict[...]`, `list[...]`) which is incompatible with Python 3.8. This syntax was introduced in [PEP 585](https://peps.python.org/pep-0585/) and is only available in Python 3.9+.

**Why It Wasn't Caught Earlier:** 
- The bug was present since the initial commit (43fd07b)
- Tests passed on Python 3.8 until Nov 9, 2025
- The failure was triggered by upgrading `actions/setup-python` from v5 to v6 (PR #15)
- The new version installs a stricter Python 3.8 build that properly enforces PEP 585 restrictions

**Impact:**
- ❌ Python 3.8 tests fail with `TypeError: 'type' object is not subscriptable`
- ✅ Python 3.9+ tests pass (syntax is valid)
- Project claims Python 3.8+ support but doesn't deliver it

## Affected Files

Found **3 occurrences** of Python 3.9+ syntax:

1. **`src/toon_format/constants.py:48`**
   ```python
   DELIMITERS: dict[str, "Delimiter"] = {
   ```

2. **`src/toon_format/utils.py:94`**
   ```python
   def estimate_savings(data: Any, encoding: str = "o200k_base") -> dict[str, Any]:
   ```

3. **`src/toon_format/writer.py:27`**
   ```python
   self._indent_cache: dict[int, str] = {0: ""}
   ```

## Solution

Replace Python 3.9+ syntax with Python 3.8-compatible `typing` module imports:

| Python 3.9+ | Python 3.8 Compatible |
|-------------|----------------------|
| `dict[K, V]` | `Dict[K, V]` (from `typing`) |
| `list[T]` | `List[T]` (from `typing`) |
| `set[T]` | `Set[T]` (from `typing`) |
| `tuple[T, ...]` | `Tuple[T, ...]` (from `typing`) |

## Implementation Steps

### 1. Fix `src/toon_format/constants.py`
- [x] Identified issue at line 48
- [ ] Add `from typing import Dict` to imports
- [ ] Replace `dict[str, "Delimiter"]` with `Dict[str, "Delimiter"]`

### 2. Fix `src/toon_format/utils.py`
- [x] Identified issue at line 94
- [ ] Add `from typing import Dict` to imports (if not already present)
- [ ] Replace `dict[str, Any]` with `Dict[str, Any]`

### 3. Fix `src/toon_format/writer.py`
- [x] Identified issue at line 27
- [ ] Add `from typing import Dict` to imports (if not already present)
- [ ] Replace `dict[int, str]` with `Dict[int, str]`

### 4. Update mypy Configuration (Optional but Recommended)
- [ ] Change `python_version = "3.9"` to `python_version = "3.8"` in `pyproject.toml`
- **Rationale:** This ensures mypy catches Python 3.8 incompatibilities during development

### 5. Testing & Validation
- [ ] Run tests on Python 3.8: `uv run pytest` (with Python 3.8 active)
- [ ] Run tests on Python 3.9: Ensure backward compatibility
- [ ] Run tests on Python 3.10: Ensure backward compatibility
- [ ] Run tests on Python 3.11: Ensure backward compatibility
- [ ] Run tests on Python 3.12: Ensure backward compatibility
- [ ] Run mypy: `uv run mypy src/toon_format`
- [ ] Run ruff check: `uv run ruff check src/toon_format tests`
- [ ] Run ruff format: `uv run ruff format src/toon_format tests`

### 6. Commit & PR
- [ ] Commit changes with message: `fix: replace Python 3.9+ type syntax with Python 3.8-compatible typing imports`
- [ ] Push branch: `git push origin fix/python-38-compatibility`
- [ ] Create PR with detailed description linking to this plan

## Expected Changes Summary

**Files Modified:** 3
- `src/toon_format/constants.py`
- `src/toon_format/utils.py`
- `src/toon_format/writer.py`

**Lines Changed:** ~6 lines (3 type annotations + 3 import additions)

**Breaking Changes:** None (backward compatible with Python 3.9+)

## Verification Checklist

After implementation, verify:
- [x] Branch created: `fix/python-38-compatibility`
- [ ] All 3 files fixed
- [ ] All imports added correctly
- [ ] Python 3.8 tests pass
- [ ] Python 3.9-3.12 tests pass
- [ ] mypy passes
- [ ] ruff check passes
- [ ] ruff format passes
- [ ] No new issues introduced
- [ ] PR created with proper description

## Additional Notes

**Why This Matters:**
- The project explicitly supports Python 3.8+ in `pyproject.toml` (`requires-python = ">=3.8"`)
- Many production environments still use Python 3.8 (EOL: October 2024, but widely deployed)
- This is a **critical bug** that prevents installation/usage on Python 3.8

**Future Prevention:**
- Set `mypy python_version = "3.8"` to catch these issues during development
- Consider adding a pre-commit hook that runs mypy with Python 3.8 target
- CI already tests Python 3.8, but the bug slipped through due to environmental changes

## References

- [PEP 585 - Type Hinting Generics In Standard Collections](https://peps.python.org/pep-0585/)
- [Python 3.8 Release Notes](https://docs.python.org/3/whatsnew/3.8.html)
- [typing module documentation](https://docs.python.org/3/library/typing.html)

