// Observes the unmodified, public demo through its Parcel module exports.
(function () {
    var records = [], installed = false, submitted = false, finished = false;
    var replaying = false, ticks = 0;
    var initialTable = null;
    function finish(error) {
        if (finished) return;
        finished = true;
        console.log('TOXICITY_RESULT ' + JSON.stringify({
            error: error || null, classifications: records,
            rows: document.querySelectorAll('#table-wrapper .row').length,
            initialTable: initialTable
        }));
    }
    var timer = setInterval(function () {
        if (finished) { clearInterval(timer); return; }
        if (typeof parcelRequire !== 'function') return;
        if (!installed) {
            var tf = parcelRequire('PqBP');
            var prototype = parcelRequire('0Ed6').ToxicityClassifier.prototype;
            var classify = prototype.classify;
            prototype.classify = function (inputs) {
                var backend = tf.getBackend();
                var threshold = this.threshold;
                var gpu = tf.backend().gpgpu;
                var gl = gpu && gpu.gl;
                var drawCount = 0, oldDraw = gl && gl.drawElements;
                if (gl) gl.drawElements = function () {
                    drawCount++;
                    return oldDraw.apply(gl, arguments);
                };
                var started = performance.now();
                console.log('TOXICITY_BACKEND ' + JSON.stringify({
                    backend: backend, tfjs: tf.version_core,
                    webglVersion: tf.ENV.getNumber('WEBGL_VERSION'),
                    renderer: gl ? gl.getParameter(gl.RENDERER) : null
                }));
                return classify.apply(this, arguments).then(function (result) {
                    if (gl) gl.drawElements = oldDraw;
                    records.push({inputs: inputs, backend: backend,
                        tfjs: tf.version_core, threshold: threshold,
                        webglVersion: tf.ENV.getNumber('WEBGL_VERSION'),
                        hasWebGLContext: !!gl,
                        renderer: gl ? gl.getParameter(gl.RENDERER) : null,
                        floatRendering: tf.ENV.getBool('WEBGL_RENDER_FLOAT32_ENABLED'),
                        floatDownload: tf.ENV.getBool('WEBGL_DOWNLOAD_FLOAT_ENABLED'),
                        bufferSupported: gl ? tf.ENV.getBool('WEBGL_BUFFER_SUPPORTED') : false,
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
        if (rows === 5 && records.length === 2) finish();
    }, 100);
}());
