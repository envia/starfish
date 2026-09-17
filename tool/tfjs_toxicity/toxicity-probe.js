// Observes the unmodified, public TensorFlow.js toxicity demo through its
// Parcel module exports. Injected over the Starfish console (stdin) by run.py;
// it changes no backend flag before the demo's own classifications.
//
// Output lines (all prefixed for run.py):
//   TOXICITY_PROBE_READY  probe installed
//   TOXICITY_PROGRESS     one classification record
//   TOXICITY_STATE        periodic heartbeat
//   TOXICITY_RESULT       final payload (exactly once)
(function () {
    var records = [], installed = false, submitted = false, finished = false;
    var replaying = false, ticks = 0;
    var initialTable = null;
    var matmul = null;

    function flag(tf, name, getter) {
        try {
            return tf.ENV[getter](name);
        } catch (error) {
            return null;
        }
    }

    function finish(error) {
        if (finished) return;
        finished = true;
        console.log('TOXICITY_RESULT ' + JSON.stringify({
            error: error || null, classifications: records, matmul: matmul,
            rows: document.querySelectorAll('#table-wrapper .row').length,
            initialTable: initialTable
        }));
    }

    // Small matrix multiplications on the GL path with CPU forwarding off.
    // Integer operands keep the expected products exact in float32 and in
    // half float, so any deviation comes from the texture or readback path.
    function checkMatMul(tf) {
        var result = {cpuForwardDisabled: null, float32: null, halfFloat: null};
        if (tf.getBackend() !== 'webgl') {
            result.skipped = 'backend is ' + tf.getBackend();
            return Promise.resolve(result);
        }
        var a = [[1, 2, 3], [4, 5, 6]];
        var b = [[7, 8], [9, 10], [11, 12]];
        var expected = [58, 64, 139, 154];
        function run(label, tolerance) {
            return tf.tidy(function () {
                return tf.matMul(tf.tensor2d(a), tf.tensor2d(b));
            }).data().then(function (values) {
                var actual = Array.from(values);
                var maxError = 0;
                for (var i = 0; i < expected.length; i++) {
                    maxError = Math.max(maxError, Math.abs(actual[i] - expected[i]));
                }
                result[label] = {
                    values: actual, maxError: maxError,
                    pass: actual.length === expected.length && maxError <= tolerance,
                    renderFloat32: flag(tf, 'WEBGL_RENDER_FLOAT32_ENABLED', 'getBool'),
                    downloadFloat: flag(tf, 'WEBGL_DOWNLOAD_FLOAT_ENABLED', 'getBool')
                };
            });
        }
        var savedForward = flag(tf, 'WEBGL_CPU_FORWARD', 'getBool');
        var savedFloat32 = flag(tf, 'WEBGL_RENDER_FLOAT32_ENABLED', 'getBool');
        tf.ENV.set('WEBGL_CPU_FORWARD', false);
        result.cpuForwardDisabled = flag(tf, 'WEBGL_CPU_FORWARD', 'getBool') === false;
        return run('float32', 1e-3).then(function () {
            // Half float is opt-in through the same flag TFJS uses when the
            // driver cannot render float32. Whether a flag change after
            // backend initialization takes effect is recorded, not assumed.
            tf.ENV.set('WEBGL_RENDER_FLOAT32_ENABLED', false);
            return run('halfFloat', 1e-2);
        }).then(function () {
            tf.ENV.set('WEBGL_RENDER_FLOAT32_ENABLED', savedFloat32);
            tf.ENV.set('WEBGL_CPU_FORWARD', savedForward);
            return result;
        }, function (error) {
            tf.ENV.set('WEBGL_RENDER_FLOAT32_ENABLED', savedFloat32);
            tf.ENV.set('WEBGL_CPU_FORWARD', savedForward);
            result.error = String(error.stack || error);
            return result;
        });
    }

    var timer = setInterval(function () {
        if (finished) { clearInterval(timer); return; }
        if (typeof parcelRequire !== 'function') return;
        var tf;
        if (!installed) {
            tf = parcelRequire('PqBP');
            var prototype = parcelRequire('0Ed6').ToxicityClassifier.prototype;
            var classify = prototype.classify;
            prototype.classify = function (inputs) {
                var backend = tf.getBackend();
                var gpu = tf.backend().gpgpu;
                var gl = gpu && gpu.gl;
                var drawCount = 0, oldDraw = gl && gl.drawElements;
                if (gl) gl.drawElements = function () {
                    drawCount++;
                    return oldDraw.apply(gl, arguments);
                };
                var started = performance.now();
                return classify.apply(this, arguments).then(function (result) {
                    if (gl) gl.drawElements = oldDraw;
                    records.push({inputs: inputs, backend: backend,
                        tfjs: tf.version_core,
                        webglVersion: flag(tf, 'WEBGL_VERSION', 'getNumber'),
                        hasWebGLContext: !!gl,
                        renderer: gl ? gl.getParameter(gl.RENDERER) : null,
                        vendor: gl ? gl.getParameter(gl.VENDOR) : null,
                        glVersion: gl ? gl.getParameter(gl.VERSION) : null,
                        floatRendering: flag(tf, 'WEBGL_RENDER_FLOAT32_ENABLED', 'getBool'),
                        floatDownload: flag(tf, 'WEBGL_DOWNLOAD_FLOAT_ENABLED', 'getBool'),
                        bufferSupported: flag(tf, 'WEBGL_BUFFER_SUPPORTED', 'getBool'),
                        fenceApi: flag(tf, 'WEBGL_FENCE_API_ENABLED', 'getBool'),
                        cpuForward: flag(tf, 'WEBGL_CPU_FORWARD', 'getBool'),
                        glError: gl ? gl.getError() : null,
                        drawCount: drawCount, milliseconds: performance.now() - started,
                        predictions: result.map(function (head) {
                            return {label: head.label, results: head.results.map(function (item) {
                                return {match: item.match,
                                    probabilities: Array.from(item.probabilities)};
                            })};
                        })});
                    console.log('TOXICITY_PROGRESS ' + JSON.stringify(records[records.length - 1]));
                    return result;
                }, function (error) {
                    if (gl) gl.drawElements = oldDraw;
                    finish(String(error.stack || error));
                    throw error;
                });
            };
            installed = true;
            console.log('TOXICITY_PROBE_READY ' + JSON.stringify({
                rows: document.querySelectorAll('#table-wrapper .row').length,
                backend: tf.getBackend()}));
        }
        var rows = document.querySelectorAll('#table-wrapper .row').length;
        if (rows === 4 && !initialTable) {
            initialTable = Array.from(document.querySelectorAll('#table-wrapper .row'))
                .slice(1).map(function (row) {
                    return Array.from(row.querySelectorAll('.label'))
                        .map(function (cell) { return cell.textContent.trim(); });
                });
        }
        if (++ticks % 50 === 0) console.log('TOXICITY_STATE ' + JSON.stringify({
            rows: rows, classifications: records.length, replaying: replaying}));
        // A cached demo may finish before the shell accepts its first command.
        // Replay the same samples using unchanged model code, then exercise the
        // original page's input handler. No backend flags are changed here.
        if (rows === 4 && records.length === 0 && !replaying) {
            replaying = true;
            parcelRequire('0Ed6').load().then(function (model) {
                return model.classify([
                    "We're dudes on computers, moron.  You are quite astonishingly stupid.",
                    'Please stop. If you continue to vandalize Wikipedia, as you did to Kmart, you will be blocked from editing.',
                    'I respect your point of view, and when this discussion originated on 8th April I would have tended to agree with you.'
                ]).then(function () { model.model.dispose(); });
            }).catch(function (error) { finish(String(error.stack || error)); });
        }
        if (rows === 4 && records.length === 1 && !submitted) {
            submitted = true;
            document.getElementById('classify-new-text-input').value =
                'Thank you for helping me.';
            document.getElementById('classify-new-text').dispatchEvent(new Event('click'));
        }
        if (rows === 5 && records.length === 2 && matmul === null) {
            matmul = {pending: true};
            checkMatMul(parcelRequire('PqBP')).then(function (result) {
                matmul = result;
                finish();
            });
        }
    }, 100);
}());
