"""Light syntactic checks for every generated ``.md``.

Five cheap checks, suitable for running on each edit:

1. **cross-link** — the target of a relative markdown link actually exists
2. **link-syntax** — no empty link text, empty URL or whitespace inside a URL
3. **deep-link-host-scheme** — an absolute URL's host is a known one and its
   path+query+hash matches that host's established deep-link shape, so a GitHub host
   carrying a Gerrit gitweb URL is rejected immediately
4. **heading** — no skipped heading level (``#`` → ``###``), maximum depth 4
5. **generic-name** — a category index (``<NN>-<slug>/index.md``) may not use a
   generic H1 such as "Overview" or "Modules"

Severity: link-syntax, heading-skip, heading-depth, generic-name and a
host/scheme *mismatch* are hard errors (exit 1). A broken cross-link (the section may
be planned but unwritten) and an *unknown* host (the dictionary below may simply be
missing an entry) are warnings and do not fail the run. ``--strict`` promotes every
warning to an error.

Output is silent when nothing is wrong; otherwise violations are listed per file.

Usage: python3 validate_wiki_structure.py [--strict] <file.md> [<file.md> ...]
"""

from __future__ import annotations

import os
import re
import sys
import traceback
from typing import Any
from urllib.parse import urlsplit

FORBIDDEN_GENERIC_NAMES = {
    "overview",
    "modules",
    "architecture",
    "api reference",
    "api",
    "documentation",
    "introduction",
    "getting started",
    "reference",
    "general",
    "misc",
}

# Host-specific deep-link URL patterns.
#
# Keep this in sync with the deep-link bases the doc-generation skill emits: if a host
# produces links but has no entry here, its URLs are silently skipped and defects slip
# through. A host is matched by exact name or by prefix/suffix (so enterprise
# installations such as `github.example.com` are covered), and several path shapes can
# be legal for one host — matching any one pattern is enough.
#
# The pattern is applied to pathname + search + hash; the origin has already been used
# for the host match. For `https://github.com/foo/bar/blob/main/src/x.ts#L42` that is
# `/foo/bar/blob/main/src/x.ts#L42`.
HOST_PATTERNS: list[dict[str, Any]] = [
    # GitHub — 공개 github.com 및 사내 enterprise 인스턴스(github.<org>)
    {
        "match": lambda h: h == "github.com" or h.startswith("github."),
        "patterns": [
            # /<owner>/<repo>/blob/<branch-or-sha>/<path>[#L<n>[-L<n>]]
            re.compile(r"^/[^/]+/[^/]+/blob/[^/]+/.+?(#L\d+(-L\d+)?)?$"),
            # /<owner>/<repo>/tree/<branch>[/<path>]
            re.compile(r"^/[^/]+/[^/]+/tree/[^/]+(/.+)?$"),
            # /<owner>/<repo>/commit/<sha>[/<...>]
            re.compile(r"^/[^/]+/[^/]+/commit/[0-9a-f]+(/.+)?$"),
            # repo root: /<owner>/<repo> or /<owner>/<repo>/
            re.compile(r"^/[^/]+/[^/]+/?$"),
        ],
        "hint": "GitHub 패턴: /<owner>/<repo>/blob/<branch>/<path>#L<n>",
    },
    # GitLab (public + self-hosted)
    {
        "match": lambda h: h == "gitlab.com" or h.startswith("gitlab."),
        "patterns": [
            # /<owner>(/<group>)*/<repo>/-/blob/<branch>/<path>[#L<n>]
            re.compile(r"^(/[^/]+){2,}/-/blob/[^/]+/.+?(#L\d+(-\d+)?)?$"),
            re.compile(r"^(/[^/]+){2,}/-/tree/[^/]+(/.+)?$"),
            re.compile(r"^(/[^/]+){2,}/?$"),
        ],
        "hint": "GitLab 패턴: /<owner>/<repo>/-/blob/<branch>/<path>#L<n>",
    },
    # Bitbucket Cloud (self-hosted Server/DC는 경로 체계가 달라 여기 매칭하면 안 된다)
    {
        "match": lambda h: h == "bitbucket.org",
        "patterns": [
            # /<owner>/<repo>/src/<branch>/<path>[#lines-<n>]
            re.compile(r"^/[^/]+/[^/]+/src/[^/]+/.+?(#lines-\d+(:\d+)?)?$"),
            re.compile(r"^/[^/]+/[^/]+/?$"),
        ],
        "hint": "Bitbucket 패턴: /<owner>/<repo>/src/<branch>/<path>#lines-<n>",
    },
    # Gerrit gitweb (아래 패턴은 /gerrit/ 마운트를 전제한다 — 인스턴스마다 다르므로 호스트명
    # 휴리스틱("gerrit" in h · review. 접두사)으로 넓히면 오판을 그대로 승인하게 된다)
    {
        "match": lambda h: h == "review.tizen.org",
        "patterns": [
            # /gerrit/gitweb?p=<repo>.git;a=blob;f=<path>;hb=refs/heads/<branch>[#l<n>]
            re.compile(r"^/gerrit/gitweb\?p=[^;]+\.git;a=blob;f=[^;]+;"
                       r"(h=[0-9a-f]+;)?hb=[^#]+(#l\d+)?$"),
            # a=tree;hb=<branch> 또는 a=tree;hb=...;f=<path>
            re.compile(r"^/gerrit/gitweb\?p=[^;]+\.git;a=tree;hb=[^#;]+(;f=[^#]+)?$"),
            # a=commit / a=commitdiff;h=<sha>
            re.compile(r"^/gerrit/gitweb\?p=[^;]+\.git;a=(commit|commitdiff);h=[0-9a-f]+$"),
            # a=summary / a=shortlog / a=log / a=tags / a=heads (repo-level views)
            re.compile(r"^/gerrit/gitweb\?p=[^;]+\.git;a=(summary|shortlog|log|tags|heads)$"),
            # a=history;f=<path>;hb=<branch> (파일 history)
            re.compile(r"^/gerrit/gitweb\?p=[^;]+\.git;a=history;f=[^;]+;hb=[^#;]+$"),
            # Gerrit gitiles 일부 서버: /<repo>/+/refs/heads/<branch>/<path>
            re.compile(r"^/[^/]+(/[^/]+)*/\+/refs/heads/[^/]+/.+$"),
        ],
        "hint": "Gerrit gitweb: ?p=<repo>.git;a=blob|tree|commit|summary|history;... "
                "(블롭은 #l<n> 소문자 l)",
    },
    # cgit (git.tizen.org)
    {
        "match": lambda h: h == "git.tizen.org" or h.endswith(".git.tizen.org"),
        "patterns": [
            # /cgit/<project>/tree/<path>?h=<branch>[#n<n>]
            re.compile(r"^/cgit/.+/tree/.+\?h=[^#]+(#n\d+)?$"),
            # /cgit/<project>/log[/<path>]?h=<branch>
            re.compile(r"^/cgit/.+/log(/.+)?\?h=[^#]+$"),
            # /cgit/<project>[/]
            re.compile(r"^/cgit/.+/?$"),
        ],
        "hint": "cgit 패턴: /cgit/<project>/tree/<path>?h=<branch>#n<n>",
    },
]

_SOURCE_SENTINEL = "src:"
# `src:` deep-links are repo-relative source citations, not page-to-page links: a
# `src:docs/guide.md#L3` resolved against the page's own directory would be reported as
# a broken cross-link (it lives in the analysed repo, not next to the wiki).
_CROSS_LINK_RE = re.compile(
    rf"\[([^\]]+?)\]\((?!https?://|{_SOURCE_SENTINEL})([^)\s]+\.md(?:#[^)]*)?)\)")
# A well-formed sentinel: repo-relative path, optional `#L<n>` / `#L<n>-L<m>` anchor.
_SENTINEL_LINK_RE = re.compile(rf"\[[^\]]*?\]\(({_SOURCE_SENTINEL}[^)\s]*)\)")
_SENTINEL_OK_RE = re.compile(
    rf"^{_SOURCE_SENTINEL}(?![/#])[^\s#?:]+(?:#L[0-9]+(?:-L?[0-9]+)?)?$")
_LINK_RE = re.compile(r"\[([^\]]*?)\]\(([^)]*?)\)")
_FENCE_RE = re.compile(r"^```")
_HEADING_RE = re.compile(r"^(#{1,6})\s+\S")
_ABS_URL_RE = re.compile(r"\[[^\]]*?\]\((https?://[^)\s]+)\)|<(https?://[^>\s]+)>")
_INLINE_CODE_RE = re.compile(r"`[^`]*`")
_CATEGORY_INDEX_RE = re.compile(r"/\d{2}-[^/]+/index\.md$")
_H1_RE = re.compile(r"^# (.+)$")


def lookup_host_scheme(host: str) -> dict[str, Any] | None:
    return next((p for p in HOST_PATTERNS if p["match"](host)), None)


def parse_url(url: str) -> tuple[str, str]:
    """Split a URL into ``(host, pathname + search + hash)``.

    The default port is dropped from the host so ``https://h:443/x`` and
    ``https://h/x`` compare equal. Raises ValueError when there is no host.
    """
    sp = urlsplit(url)
    if sp.hostname is None:
        raise ValueError("no host")
    host = sp.hostname
    port = sp.port
    if port is not None and not ((sp.scheme == "http" and port == 80)
                                 or (sp.scheme == "https" and port == 443)):
        host = f"{host}:{port}"
    path_part = sp.path + (("?" + sp.query) if sp.query else "") \
        + (("#" + sp.fragment) if sp.fragment else "")
    return host, path_part


def check_cross_links(text: str, file_path: str) -> list[dict[str, Any]]:
    errors = []
    dir_ = os.path.dirname(file_path)
    # [text](relative-or-absolute.md) — must NOT start with http(s)
    for m in _CROSS_LINK_RE.finditer(text):
        link_text = m.group(1)
        target_raw = m.group(2)
        target = re.sub(r"#.*$", "", target_raw)
        if not target:
            continue
        abs_path = target if os.path.isabs(target) \
            else os.path.abspath(os.path.join(dir_, target))
        if not os.path.exists(abs_path):
            line = text[:m.start()].count("\n") + 1
            errors.append({
                "line": line,
                "type": "cross-link",
                "message": f'broken cross-link "{link_text}" → {target_raw}',
            })
    return errors


def check_deep_link_syntax(text: str) -> list[dict[str, Any]]:
    errors = []
    lines = text.split("\n")
    for i, line in enumerate(lines):
        for m in _LINK_RE.finditer(line):
            link_text = m.group(1)
            url = m.group(2)
            if not link_text.strip():
                errors.append({
                    "line": i + 1,
                    "type": "link-syntax",
                    "message": f"empty link text in: {m.group(0)[:60]}",
                })
            if not url.strip():
                errors.append({
                    "line": i + 1,
                    "type": "link-syntax",
                    "message": f"empty URL in: [{link_text}]()",
                })
            if re.search(r"\s", url) and not url.startswith("#"):
                errors.append({
                    "line": i + 1,
                    "type": "link-syntax",
                    "message": f"whitespace inside URL: {url[:60]}",
                })
    return errors


def check_sentinel_deep_links(text: str) -> list[dict[str, Any]]:
    """Deep-links written in the compact `src:` form must stay expandable (issue #54).

    The renderer turns `src:<path>[#L<n>]` into `deepLink.base` + path, so a sentinel
    holding an absolute path, a scheme, or an anchor that is not a line number would
    expand into a broken URL. That is invisible in the markdown itself — nothing else
    checks it, since `check_deep_link_host_scheme` only sees absolute URLs.
    """
    errors = []
    for i, line in enumerate(text.split("\n")):
        # Inline code holds the *documentation* of the form, not a link to check.
        code_stripped = _INLINE_CODE_RE.sub("", line)
        for m in _SENTINEL_LINK_RE.finditer(code_stripped):
            url = m.group(1)
            if _SENTINEL_OK_RE.match(url):
                continue
            errors.append({
                "line": i + 1,
                "type": "deep-link-sentinel",
                "message": f'malformed src: deep-link "{url[:80]}" — '
                           f"src:<repo-상대경로>[#L<n>] 형태여야 한다"
                           f"(선행 `/`·스킴·`?` 금지, 앵커는 #L<라인>)",
            })
    return errors


def check_heading_hierarchy(text: str) -> list[dict[str, Any]]:
    errors = []
    lines = text.split("\n")
    prev_level = 0
    in_fence = False
    for i, line in enumerate(lines):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = _HEADING_RE.match(line)
        if not m:
            continue
        level = len(m.group(1))
        if level > 4:
            errors.append({
                "line": i + 1,
                "type": "heading-depth",
                "message": f"heading depth {level} exceeds 4 (SKILL.md: 계층은 2-3 depth)",
            })
        if prev_level > 0 and level > prev_level + 1:
            errors.append({
                "line": i + 1,
                "type": "heading-skip",
                "message": f"heading level jumps from H{prev_level} to H{level} "
                           f"(skipped intermediate)",
            })
        prev_level = level
    return errors


def check_deep_link_host_scheme(text: str) -> list[dict[str, Any]]:
    # 외부 절대 URL (http(s)://...)의 host가 HOST_PATTERNS에 등록되어 있는지, 그리고
    # path+search+hash 가 그 host의 정착된 deep-link 패턴 중 하나와 매치되는지 검사한다.
    # 등록 안 된 host는 warning (사전 등록 누락 가능성), 등록은 됐는데 패턴이 안 맞으면 error.
    errors = []
    lines = text.split("\n")
    for i, line in enumerate(lines):
        # 인라인 코드 블록 안의 URL은 검사 대상에서 제외 (`...`) — 가장 흔한 false positive.
        code_stripped = _INLINE_CODE_RE.sub("", line)
        for m in _ABS_URL_RE.finditer(code_stripped):
            url = m.group(1) or m.group(2)
            try:
                host, path_part = parse_url(url)
            except Exception:
                errors.append({
                    "line": i + 1,
                    "type": "deep-link-host-scheme",
                    "message": f"unparseable URL: {url[:80]}",
                })
                continue
            host = host.lower()
            entry = lookup_host_scheme(host)
            if not entry:
                # 등록 안 된 host — warning. 자주 등장하는 일반 외부 docs(www.qemu.org,
                # wiki.qemu.org, www.gnu.org, MDN 등)는 deep-link가 아닌 *참고 링크*라 검사 면제.
                if is_reference_only_host(host):
                    continue
                errors.append({
                    "line": i + 1,
                    "type": "deep-link-host-scheme",
                    "severity_hint": "warn",
                    "message": f'unknown host "{host}" — HOST_PATTERNS 사전에 등록 필요 '
                               f"(SKILL.md Step 1 case 문도 동기)",
                })
                continue
            ok = any(p.search(path_part) for p in entry["patterns"])
            if not ok:
                errors.append({
                    "line": i + 1,
                    "type": "deep-link-host-scheme",
                    "message": f'URL path mismatches "{host}" scheme — '
                               f'got "{path_part[:100]}", 예상: {entry["hint"]}',
                })
    return errors


# 사전에 없어도 OK인 외부 host (참고용 일반 docs). deep-link이 아니라 단순 외부 자료 인용.
_REFERENCE_HOSTS = [
    re.compile(r"\.wikipedia\.org$"),
    re.compile(r"^(www\.)?gnu\.org$"),
    re.compile(r"^(www\.)?ietf\.org$"),
    re.compile(r"^datatracker\.ietf\.org$"),
    re.compile(r"\.rfc-editor\.org$"),
    re.compile(r"^developer\.mozilla\.org$"),
    re.compile(r"^stackoverflow\.com$"),
    re.compile(r"\.stackexchange\.com$"),
    re.compile(r"^(www\.|wiki\.|docs\.)?qemu\.org$"),
    re.compile(r"\.npmjs\.com$"),
    re.compile(r"^pypi\.org$"),
    re.compile(r"^crates\.io$"),
    re.compile(r"^(www\.)?notion\.so$"),
    re.compile(r"^medium\.com$"),
    re.compile(r"^(www\.)?tizen\.org$"),
    re.compile(r"^docs\.tizen\.org$"),
    re.compile(r"^developer\.tizen\.org$"),
]


def is_reference_only_host(host: str) -> bool:
    # 공식 docs·표준·블로그성 host. 새 host가 등장하면 여기에 추가하거나 HOST_PATTERNS로 정식 등록.
    return any(r.search(host) for r in _REFERENCE_HOSTS)


def check_generic_category_name(text: str, file_path: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    # 카테고리 index.md만 대상: 경로 끝이 `/<NN>-<slug>/index.md`
    if not _CATEGORY_INDEX_RE.search(file_path):
        return errors
    lines = text.split("\n")
    for i, line in enumerate(lines):
        m = _H1_RE.match(line)
        if not m:
            continue
        title = re.sub(r"[`*_]", "", m.group(1).lower()).strip()
        if title in FORBIDDEN_GENERIC_NAMES:
            errors.append({
                "line": i + 1,
                "type": "generic-name",
                "message": f'category H1 "{m.group(1)}" is generic — 카테고리는 repo '
                           f"고유의 기능 영역 이름이어야 합니다(동적 발견). 이 repo에서만 "
                           f"의미가 통하는 이름으로 바꾸세요.",
            })
        break  # only first H1
    return errors


WARNING_TYPES = {"cross-link"}


def main() -> int:
    argv = sys.argv[1:]
    strict = "--strict" in argv
    args = [a for a in argv if a != "--strict"]
    if len(args) == 0:
        print("usage: python3 validate_wiki_structure.py [--strict] <file.md> [<file.md> ...]",
              file=sys.stderr)
        return 2
    error_count = 0
    warning_count = 0
    per_file = []
    for fp in args:
        if not fp.endswith(".md"):
            continue
        try:
            with open(fp, encoding="utf-8", errors="replace") as f:
                text = f.read()
        except OSError:
            continue
        all_ = [
            *check_cross_links(text, fp),
            *check_deep_link_syntax(text),
            *check_deep_link_host_scheme(text),
            *check_sentinel_deep_links(text),
            *check_heading_hierarchy(text),
            *check_generic_category_name(text, fp),
        ]
        if len(all_) == 0:
            continue
        for e in all_:
            # severity_hint 가 있으면 우선 (e.g. unknown host = warn). strict 시 모두 error.
            want_warn = e.get("severity_hint") == "warn"
            is_warning = (not strict) and (e["type"] in WARNING_TYPES or want_warn)
            if is_warning:
                warning_count += 1
            else:
                error_count += 1
            e["severity"] = "warn" if is_warning else "err"
        per_file.append({"file": fp, "errors": all_})
    if error_count == 0 and warning_count == 0:
        return 0
    if error_count > 0:
        header = f"[wiki-structure] FAIL — {error_count} error(s)"
        if warning_count > 0:
            header += f" + {warning_count} warning(s)"
    else:
        header = f"[wiki-structure] {warning_count} warning(s) (non-blocking)"
    print(f"{header} across {len(per_file)} file(s)", file=sys.stderr)
    for entry in per_file:
        print(f"\n  {entry['file']}", file=sys.stderr)
        for e in entry["errors"][:10]:
            sev = "✗" if e["severity"] == "err" else "⚠"
            print(f"    {sev} L{e['line']}  {e['type'].ljust(22)} {e['message']}",
                  file=sys.stderr)
        if len(entry["errors"]) > 10:
            print(f"    … {len(entry['errors']) - 10} more", file=sys.stderr)
    return 1 if error_count > 0 else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as e:
        print(f"validate-wiki-structure: {traceback.format_exc().rstrip()}"
              if not isinstance(e, str) else f"validate-wiki-structure: {e}",
              file=sys.stderr)
        sys.exit(3)
