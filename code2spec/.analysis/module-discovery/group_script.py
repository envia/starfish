import yaml

# Read files from llm-prompt.md
files = []
with open('/home/hwang/work/F/starfish_/code2spec/.analysis/module-discovery/llm-prompt.md') as f:
    in_list = False
    for line in f:
        if '## File List' in line:
            continue
        if line.strip() == '```' and not in_list:
            in_list = True
            continue
        elif line.strip() == '```' and in_list:
            in_list = False
            break
        if in_list:
            path = line.strip()
            if path:
                files.append(path)

print(f'Read {len(files)} files from prompt')

# Define grouping logic
def get_module(path):
    if path.startswith('compat/tizen_5.0'):
        return 'compat-tizen', 'Tizen 5.0 compatibility layer and headers'
    if path.startswith('docs'):
        return 'docs-generator', 'Documentation generators and static web pages for API exploration'
    if path.startswith('inc/'):
        return 'inc-headers', 'Public Lightweight Web Engine API headers'
    if path.startswith('src/binding/'):
        return 'bindings', 'JavaScript custom bindings for Web APIs and DOM objects'
    if path.startswith('src/browser/'):
        return 'browser', 'Browser management components, history manager, and frame tree'
    if path.startswith('src/launcher/'):
        return 'launcher', 'Service worker and shared worker entry points'
    if path.startswith('src/platform/canvas/'):
        return 'platform-canvas', 'Canvas rendering backend using GL, Cairo, and Mock renderers'
    if path.startswith('src/platform/file/'):
        return 'platform-file', 'File and directory system abstractions'
    if path.startswith('src/platform/multimedia/'):
        return 'platform-multimedia', 'Media player and demuxer core for audio/video playback'
    if path.startswith('src/platform/network/'):
        return 'platform-network', 'Network abstraction layer, cURL multi managers, and HTTP caching'
    if path.startswith('src/platform/lo') or path.startswith('src/platform/loader/'):
        return 'platform-loader', 'Resource loaders, element clients, and network cache interfaces'
    if path.startswith('src/platform/'):
        return 'platform-core', 'Operating system process management, thread loops, key events, and feedback'
    if path.startswith('src/public/'):
        return 'public-bridge', 'Public interface delegates and native window-manager bridge wrappers for EFL, Android JNI, and Flutter'
    if path.startswith('src/shell/'):
        return 'shell', 'MiniBrowser main interface, API replayer, window hooks, and unit tests'
    if path.startswith('third_party/'):
        return 'third-party', 'Third-party libraries (e.g. robin_map) integrated into the project'
    if path.startswith('tool/'):
        return 'tooling', 'CI checks, WPT test runner, lint tools, and local testing servers'
    if path.startswith('src/'):
        return 'engine-core', 'Starfish engine startup, central configuration, static strings, and entry points'
    return 'misc', 'Unclassified files'

grouped = {}
for path in files:
    mod, rational = get_module(path)
    if mod not in grouped:
        grouped[mod] = {'name': mod, 'files': [], 'rationale': rational, 'confidence': 0.95}
    grouped[mod]['files'].append(path)

# Verify all files are mapped
all_mapped = []
for m in grouped.values():
    all_mapped.extend(m['files'])
print(f'Mapped {len(all_mapped)} files')
assert len(files) == len(all_mapped), 'Mismatch in mapped count!'

output = {'modules': list(grouped.values())}
with open('/home/hwang/work/F/starfish_/code2spec/.analysis/module-discovery/llm-response.yaml', 'w') as out_f:
    yaml.dump(output, out_f, default_flow_style=False)

print('Successfully generated llm-response.yaml')
