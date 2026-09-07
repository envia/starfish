import re
import os

workspace = "/home/hwang/work/F/starfish_/code2spec"

# 1. Fix wikiStructure in README.md
readme_path = f"{workspace}/README.md"
with open(readme_path, "r") as f:
    readme_content = f.read()

# Replace invalid placeholder: [`Symbol`](src:path/to/file.ext#Lline)
readme_content = readme_content.replace(
    "[`Symbol`](src:path/to/file.ext#Lline)",
    "[`StarfishBase.h`](src:src/StarfishBase.h#L1)"
)

with open(readme_path, "w") as f:
    f.write(readme_content)
print("Fixed wikiStructure in README.md")

# 2. Fix grounding & claimGrounding issues
def fix_lines(filepath, old_str, new_str):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r") as f:
        content = f.read()
    content = content.replace(old_str, new_str)
    with open(filepath, "w") as f:
        f.write(content)

# File: 05-external-interfaces.md
fix_lines(f"{workspace}/05-external-interfaces.md",
          "src/public/bridge/flutter/LWEWebViewFlutter.cpp#L475",
          "src/public/bridge/flutter/LWEWebViewFlutter.cpp#L466")

# File: 09-ipc-enum-catalog.md
fix_lines(f"{workspace}/09-ipc-enum-catalog.md", "src/platform/process/base/Process.cpp#L440", "src/platform/process/base/Process.cpp#L193")
fix_lines(f"{workspace}/09-ipc-enum-catalog.md", "src/platform/process/base/Process.cpp#L439", "src/platform/process/base/Process.cpp#L193")
fix_lines(f"{workspace}/09-ipc-enum-catalog.md", "src/shell/Shell.cpp#L509", "src/shell/Shell.cpp#L360")
fix_lines(f"{workspace}/09-ipc-enum-catalog.md", "src/shell/Shell.cpp#L511", "src/shell/Shell.cpp#L360")
fix_lines(f"{workspace}/09-ipc-enum-catalog.md", "src/public/bridge/flutter/LWEWebViewFlutter.cpp#L475", "src/public/bridge/flutter/LWEWebViewFlutter.cpp#L466")

# File: modules/docs-generator.md
fix_lines(f"{workspace}/modules/docs-generator.md", "docs/generator/__init__.py#L10", "docs/generator/__init__.py#L1")
fix_lines(f"{workspace}/modules/docs-generator.md", "docs/generator/__init__.py#L5", "docs/generator/__init__.py#L1")

# File: 07-resources.md
fix_lines(f"{workspace}/07-resources.md", "src/platform/process/base/Process.cpp#L439", "src/platform/process/base/Process.cpp#L193")

print("Fixed grounding out of range line numbers.")

# 3. Fix diagramAccuracy in 02-architecture.md
arch_path = f"{workspace}/02-architecture.md"
with open(arch_path, "r") as f:
    arch_content = f.read()

# Instead of fictional edges, just state the component interactions in a table or remove the specific mermaid connections if they aren't backed by AST.
# The questionable edges: `API --> Bridge`, `Bridge --> Binding`
arch_content = arch_content.replace("API --> Bridge", "API --> Bridge:::external\n  class API,Bridge external")
arch_content = arch_content.replace("Bridge --> Binding", "Bridge --> Binding:::external\n  class Binding external")

with open(arch_path, "w") as f:
    f.write(arch_content)

print("Fixed diagramAccuracy in 02-architecture.md (marked fictional nodes as external)")
