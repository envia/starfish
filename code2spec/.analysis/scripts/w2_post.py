#!/usr/bin/env python3
"""W2 chunk post-processing: validate module docs, mark done, spec-update each file, rebuild indexes.
usage: w2_post.py <module> [<module> ...]   (use --index-only to just rebuild indexes)"""
import sys, os, re, json, subprocess, yaml
ROOT="/home/hwang/work/D/starfish_"; OUT=f"{ROOT}/code2spec"; A=f"{OUT}/.analysis"; S=f"{A}/state/delta"
PY=f"{ROOT}/.code2spec-venv/bin/python"; TOOLS=f"{ROOT}/.code2spec-tools"
groups={g['name']:g for g in yaml.safe_load(open(f"{S}/module-groups.yaml"))['modules']}
pat=re.compile(r"\[`([^`]+)`\]\(src:([^)#]+)#L(\d+)\)")

def validate(path, files_expected=None):
    errs=[]; t=open(path,encoding="utf-8").read(); L=t.splitlines()
    if not L or not L[0].startswith("# "): errs.append("no H1")
    i=1
    while i<len(L) and not L[i].strip(): i+=1
    if i>=len(L) or not L[i].startswith("> **Relevant source files**"): errs.append("no RSF block under H1")
    if re.search(r"\]\(https?://",t): errs.append("absolute http link")
    if "[출처]" in t: errs.append("bare [출처] label")
    for w in ["llm_suggested","llm_identified","promotion","verification"]:
        if w in t: errs.append(f"internal token '{w}'")
    miss=0; tot=0
    for label,p,line in pat.findall(t):
        tot+=1; fp=f"{ROOT}/{p}"
        if not os.path.exists(fp): miss+=1; continue
        ls=open(fp,encoding="utf-8",errors="replace").read().splitlines(); n=int(line)
        win="\n".join(ls[max(0,n-2):n+1]); core=label.split("::")[-1].split(".")[-1].split("(")[0]
        if core not in win and os.path.basename(p)!=label: miss+=1
    if files_expected:
        rsf=set(re.findall(r"\]\(src:([^)#]+)\)",t))
        missing=[f for f in files_expected if f not in rsf]
        if missing: errs.append(f"RSF missing {len(missing)} module files")
    return errs, tot, miss

def rebuild_indexes():
    mods=sorted(m for m in groups if os.path.exists(f"{OUT}/modules/{m}.md"))
    frs=sorted(m for m in groups if os.path.exists(f"{OUT}/functional-requirements/{m}-fr.md"))
    rows="\n".join(f"| {m} | {len(groups[m]['files'])} | [{m}.md](./{m}.md) | "+(f"[{m}-fr.md](../functional-requirements/{m}-fr.md)" if m in frs else "—")+" |" for m in mods)
    open(f"{OUT}/modules/README.md","w",encoding="utf-8").write(f"""# Module Design Cards

> **Relevant source files**
>
> - [src/Starfish.h](src:src/Starfish.h)
> - [inc/LWEWebView.h](src:inc/LWEWebView.h)

Module Design Cards for the {len(mods)} generated modules (of {len(groups)} approved logical modules). Each card lists the module boundary, public interface, IPC/interface contracts, key flows, architectural rules, dependencies, and FR linkage.

| Module | Files | Design Card | FR Document |
|--------|-------|-------------|-------------|
{rows}

Related: [System Architecture](../02-architecture.md) · [Functional Requirements Index](../functional-requirements/index.md)
""")
    all_rows="\n".join(f"| {i+1} | {m} | {len(groups[m]['files'])} | "+(f"[{m}-fr.md](./{m}-fr.md)" if m in frs else f"{m}-fr.md")+" | "+(f"[{m}.md](../modules/{m}.md)" if m in mods else "—")+" | "+("Generated" if m in frs else "Pending (W2)")+" |" for i,m in enumerate(groups))
    open(f"{OUT}/functional-requirements/index.md","w",encoding="utf-8").write(f"""# Functional Requirements Index

> **Relevant source files**
>
> - [README.md](src:README.md)
> - [src/Starfish.h](src:src/Starfish.h)
> - [inc/LWEWebView.h](src:inc/LWEWebView.h)

Functional-requirement documents for the {len(groups)} approved Core modules of Starfish ({len(frs)} generated). Module boundaries were approved via human review in W1 (`.analysis/state/delta/module-groups.yaml`).

| # | Module | Files | FR Document | Design Card | Status |
|---|--------|-------|-------------|-------------|--------|
{all_rows}

Related: [System Architecture](../02-architecture.md) · [Module Design Cards](../modules/README.md) · [IPC Constants and ENUM Catalog](../09-ipc-enum-catalog.md)
""")
    print(f"[index] modules/README.md ({len(mods)}), functional-requirements/index.md ({len(frs)} generated)")

def process(m):
    sdd=f"modules/{m}.md"; fr=f"functional-requirements/{m}-fr.md"
    for rel in (sdd,fr):
        if not os.path.exists(f"{OUT}/{rel}"): print(f"[{m}] MISSING {rel} — not marking done"); return False
    e1,t1,m1=validate(f"{OUT}/{sdd}", groups[m]['files']); e2,t2,m2=validate(f"{OUT}/{fr}")
    print(f"[{m}] card: {t1} links/{m1} miss {e1 or ''} | fr: {t2} links/{m2} miss {e2 or ''}")
    hard=[e for e in e1+e2 if e.startswith(("no H1","no RSF","absolute"))]
    if hard: print(f"[{m}] HARD errors — not marking done"); return False
    r=subprocess.run([PY,f"{TOOLS}/code2spec_progress.py","update","--output-dir",A,"--module",m,"--status","done","--fr-doc",fr,"--sdd-doc",sdd],capture_output=True,text=True)
    if r.returncode: print(r.stdout[-300:], r.stderr[-300:]); return False
    ok=0
    for f in groups[m]['files']:
        r=subprocess.run([PY,f"{TOOLS}/code2spec_cache.py","spec-update","--output-dir",A,"--file",f"{ROOT}/{f}","--sdd-doc",sdd,"--fr-doc",fr,"--mode","detail","--analysis-scope","3","--workspace-root",ROOT],capture_output=True,text=True)
        if "spec-cache updated" in r.stdout: ok+=1
        else: print(f"[{m}] spec-update FAILED for {f}: {(r.stdout+r.stderr)[-200:]}")
    print(f"[{m}] done; spec-cache updated {ok}/{len(groups[m]['files'])} files")
    return ok==len(groups[m]['files'])

if __name__=="__main__":
    args=sys.argv[1:]
    if args and args[0]!="--index-only":
        res={m:process(m) for m in args}
        print("RESULT:", res)
    rebuild_indexes()
