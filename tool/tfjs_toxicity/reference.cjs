// Optional: regenerate the numerical reference with Node.js 18+ and fetch.
// Only the Parcel demo entry is suppressed; model and TFJS code are unchanged.
const fs = require('node:fs');
const vm = require('node:vm');
const crypto = require('node:crypto');
const baseline = require('./toxicity-reference.json');
const sha256 = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const downloads = [];

async function recordedFetch(url, options) {
    const response = await fetch(url, options);
    if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
    const bytes = Buffer.from(await response.arrayBuffer());
    downloads.push({url: String(url), sha256: sha256(bytes), bytes: bytes.length});
    return new Response(bytes, {status: response.status, headers: response.headers});
}

(async function () {
    const url = new URL(baseline.bundle, baseline.demo_url).href;
    const source = await (await recordedFetch(url)).text();
    if (sha256(source) !== baseline.bundle_sha256) {
        throw new Error('Demo bundle changed; review the new TFJS/model version first.');
    }
    const entry = '},{},["Focm"], null)';
    if (!source.includes(entry)) throw new Error('Unexpected Parcel entry');
    const context = {console, fetch: recordedFetch, performance, TextEncoder,
        TextDecoder, setTimeout, clearTimeout, setInterval, clearInterval,
        URL, atob, btoa, location: {search: ''},
        navigator: {userAgent: 'toxicity CPU numerical reference'},
        document: {createElement: () => ({getContext: () => null})}};
    context.window = context;
    vm.createContext(context);
    vm.runInContext(source.replace(entry, '},{},[], null)'), context);
    const tf = context.parcelRequire('PqBP');
    await tf.setBackend('cpu');
    const model = await context.parcelRequire('0Ed6').load();
    const result = await model.classify(baseline.inputs);
    const reference = {...baseline, tfjs: tf.version_core, backend: tf.getBackend(),
        predictions: result.map(head => ({label: head.label,
            results: head.results.map(item => ({match: item.match,
                probabilities: Array.from(item.probabilities)}))})), downloads};
    fs.writeFileSync(process.argv[2] || 'toxicity-reference.json',
        JSON.stringify(reference, null, 2) + '\n');
    console.log('CPU reference written; TFJS', tf.version_core);
}()).catch(error => {console.error(error); process.exitCode = 1;});
