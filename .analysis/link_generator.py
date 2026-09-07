import os
import glob

workspace = "/home/hwang/work/F/starfish_/code2spec"

def prepend_header(filepath, header):
    with open(filepath, 'r') as f:
        content = f.read()
    if "**관련 문서**:" not in content and "**Related Documents**:" not in content:
        with open(filepath, 'w') as f:
            f.write(header + "\n\n" + content)

sdd_files = sorted(glob.glob(f"{workspace}/0*.md"))
module_files = sorted(glob.glob(f"{workspace}/modules/*.md"))
fr_files = sorted(glob.glob(f"{workspace}/functional-requirements/*-fr.md"))

# Filter out README.md so we don't link it to itself
module_files = [m for m in module_files if not m.endswith('README.md')]

for sdd in sdd_files:
    header = f"**Related Documents**: [README](README.md) | [Quick Reference](code2spec-quick-reference.md) | [Modules Index](modules/README.md) | [FR Index](functional-requirements/index.md)"
    prepend_header(sdd, header)

for mod in module_files:
    basename = os.path.basename(mod)
    mod_name = basename.replace(".md", "")
    fr_name = f"{mod_name}-fr.md"
    header = f"**Related Documents**: [README](../README.md) | [Functional Req](../functional-requirements/{fr_name}) | [Quick Reference](../code2spec-quick-reference.md)"
    prepend_header(mod, header)

for fr in fr_files:
    basename = os.path.basename(fr)
    mod_name = basename.replace("-fr.md", ".md")
    header = f"**Related Documents**: [README](../README.md) | [Module Card](../modules/{mod_name}) | [Quick Reference](../code2spec-quick-reference.md)"
    prepend_header(fr, header)

print("Headers prepended successfully.")
