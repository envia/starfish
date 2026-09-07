---
paths:
- "**/functional_spec/**"
---

## Functional Level Specification Guideline

**Purpose**: Generate detailed Functional Specification for Implementation, Embedding Search and Documentation

**CONSTRAINTS:**
- **Keep entire context within 50K tokens**
- **Split into sub-function units when content exceeds limit**
- **Define clear boundaries and dependencies for each split document**
- **Limit scope to a single component or system per function**
- **Split documents for broad features regardless of token size**
- **Clearly distinguish between implementation content and reference/external content**

**Guidelines Rule:**
- **[GUIDELINE]** placeholders mark required content sections.
- You **must replace** all `[GUIDELINE]` markers with actual content.
- Do not leave `[GUIDELINE]` placeholders in the final document.

**File Name Guidelines:**
- Unique identifier
- **snake_case** format required
	- e.g., `streaming_audio_data_001.md`
	- Use lowercase nouns with underscores and ID number

**Splitting Guidelines**:
1. **Document Size Limit**: Maintain entire document under 50K tokens
2. **Splitting Criteria**:
   - If function exceeds 50K tokens → Split into 2+ units
   - Reorganize related Classes/Functions per feature boundary
3. **Mandatory Information for Splits**:
   - `[Function ID]`: Unique identifier (e.g., `preprocessing_audio_data_001`)
   - `[Parent Scope]`: Reference to parent feature (e.g., `streaming_audio_data_001`)
   - `[Dependencies]`: Clarify inter-document dependencies
4. **Maintain Connectivity**:
   - Express relationships between split documents using Cross-reference links
   - Reference shared Classes/Functions (avoid duplication)

**Version Guidelines**
Versions follow **Semantic Versioning** (MAJOR.MINOR.PATCH):
- **MAJOR version**: Incremented for incompatible API changes that break backward compatibility
- **MINOR version**: Incremented for new features that maintain backward compatibility
- **PATCH version**: Incremented for backward-compatible bug fixes
  - Examples:
    - `1.0.0` → `2.0.0`: Breaking API changes
    - `1.0.0` → `1.1.0`: New feature added (backward compatible)
    - `1.0.0` → `1.0.1`: Bug fix (backward compatible)
- **Version History Order**: List version history in descending order with the latest version at the top (newest → oldest)
  - Examples:
    - `1.1.0` (latest)
    - `1.0.1`
    - `1.0.0` (initial)

**Acceptance Criteria**
- [ ] [Criterion 1]: [Verification Method]
- [ ] [Criterion 2]: [Verification Method]
