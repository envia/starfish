---
CONSTITUTION:
- Always reference documents in **code2spec/** directory (ignore if unavailable)
- Always reference source codes if you need to inferrence.
- Write content matching the project type and attributes
- Request detailed **development environment** information for unknown environments
- Follow coding style, Naming conventions, and API standards
- Ask user immediately for unclear parts during documentation (no arbitrary writing)
- Ask user for untrained content (no arbitrary writing)
- Target successful build and execution
- Prioritize Dependency Injection structure for Unit Testing
title: [Brief this functionality]
author: [User Name]
date: [Written Date]
---

# Version History
| Version | Date | Author | Change Description |
|---------|------|--------|--------------------|
| 1.0.0   | yyyy-mm-dd | Name | Initial version |

# Business Specification

## Business Overview
[1-2 sentences describing this feature's overall purpose. State the business problem being solved]
*TIP: For split documents, specify upper-level/related scope*

## Business Logic
[Core logic required to achieve business overview. Stay within Factors]

## Functional Requirements
[List all features to be provided for this business logic. Assign IDs, stay within Factors]
*TIP: Split complex features into atomic functional units*

## Non-Functional Requirements
[List reasonable non-functional requirements for this business logic. Assign IDs, stay within Factors. Estimate measurable reasonable levels.]

## Quality
[Quality attributes: Performance, Security, Maintainability, Testability, etc.]

## Constraints
[List constraints (performance limits, security requirements, data validation, etc.). Stay within Factors]

## Risk Assessment
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| [Description] | High/Med/Low | High/Med/Low | [Action Plan] |

---

# Technical Specification

## Code Factors

### Module/Package
- `[Name]`: [Namespace/File Path]

### Class
- `[ClassName]`: [Class proposal and identification needed for feature development]

### Function
- `[FunctionName]`: [Function description, Parameters → Return Type]

### Variable
- `[VarName]`: [Type, Scope, State Info]

### External
- `[Lib/API Name]`: [Purpose/Version]

### Environment
- `[Environment Info]`: [OS, Platform, Programming Language, Building, Environment Variables]

## API Specification

## Dependencies
[Internal modules, external APIs/DB/services, etc.]
*TIP: Include Cross-reference links to other functional units*

## Configuration [Optional]
[Detailed configuration methods for this feature]

## Diagrams

### Class Diagram [Mandatory]
[Detailed Class Diagram based on Code Factors (mermaid)]
*Tip: Use `<br>` for line breaks in nodes, no whitespace between numbers and text, LR direction for depth ≤3*

### Sequence Diagram [Mandatory]
[Sequence diagram showing component interactions (mermaid)]
*Tip: Use `<br>` for line breaks in nodes, no whitespace between numbers and text, LR direction for depth ≤3*

## Algorithms [Optional]

### [Brief Algorithm: Detailed explanation for achieving functional requirements]
1. [Describe Steps for Algorithm]
2. [Additional items]

## Error Handling
- `[Error Code]`: [Error Message], [Response Plan]
- `[Retry Policy]`: [Retry Count/Delay Time]

## Unit Test

### Test Configuration
- [Configuration plan for Unit Test]
- [Consider Positive & Negative unit tests per functional requirements]
- [Consider Dependency Injection for Mocking]

### [Brief Unit Test: Positive & Negative Unit Tests]
- [Unit test description]
  - [positive/negative]
  - [Scenario for this unit test]
  - [Target code (e.g., MyClass.test())]
  - [Input data]
  - [Expected result]
  - [Mocking plan]
- [More items]
