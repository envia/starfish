// Worker-scope diagnostics + shims for engines with gaps.
console.log('worker-scope: fetch=' + typeof fetch +
            ' AbortController=' + typeof AbortController +
            ' MessageChannel=' + typeof MessageChannel +
            ' TextDecoder=' + typeof TextDecoder +
            ' performance=' + typeof performance +
            ' URL=' + typeof URL +
            ' WorkerGlobalScope=' + typeof WorkerGlobalScope);

// maplibre's worker bundle gates on a BARE `typeof WorkerGlobalScope` +
// `self instanceof WorkerGlobalScope`; define it as a top-level var so the
// bare identifier resolves even if `self` is not the global object itself.
if (typeof WorkerGlobalScope === 'undefined') {
    var WorkerGlobalScope = function WorkerGlobalScope() {};
    WorkerGlobalScope.prototype = Object.getPrototypeOf(self) || Object.prototype;
    try { globalThis.WorkerGlobalScope = WorkerGlobalScope; } catch (e) {}
    try { self.WorkerGlobalScope = WorkerGlobalScope; } catch (e) {}
}
console.log('worker-scope: bare typeof WorkerGlobalScope=' + typeof WorkerGlobalScope +
            ', self instanceof=' + (typeof WorkerGlobalScope !== 'undefined' && self instanceof WorkerGlobalScope));

(function (scope) {
    function makePort() {
        return {
            onmessage: null,
            _peer: null,
            postMessage: function (data) {
                var peer = this._peer;
                console.log('worker-scope: MC port delivery scheduled (handler=' + (peer && typeof peer.onmessage) + ')');
                setTimeout(function () {
                    if (peer && typeof peer.onmessage === 'function') {
                        peer.onmessage({ type: 'message', data: data });
                    }
                }, 0);
            },
            start: function () {},
            close: function () {},
            addEventListener: function (type, fn) { if (type === 'message') { this.onmessage = fn; } },
            removeEventListener: function () {}
        };
    }
    function FakeMessageChannel() {
        this.port1 = makePort();
        this.port2 = makePort();
        this.port1._peer = this.port2;
        this.port2._peer = this.port1;
    }
    scope.MessageChannel = FakeMessageChannel;
    console.log('worker-scope: MessageChannel shimmed');

    // maplibre's Actor drops messages whose envelope `origin` doesn't match
    // location.origin; this engine's worker location.origin differs from the
    // page's, so force the allowlisted 'null' origin on outgoing envelopes.
    console.log('worker-scope: location.href=' + (typeof location !== 'undefined' ? location.href : 'NO LOCATION') +
                ' location.origin=' + (typeof location !== 'undefined' ? location.origin : '-'));
    var workerOrigPost = scope.postMessage.bind(scope);
    scope.postMessage = function (msg, opts) {
        if (msg && typeof msg === 'object' && 'origin' in msg) { msg.origin = 'null'; }
        try { return workerOrigPost(msg, opts); }
        catch (e) { return workerOrigPost(msg); }
    };
    console.log('worker-scope: postMessage origin-rewrite installed');

    var workerOrigFetch = typeof fetch !== 'undefined' ? fetch.bind(scope) : null;
    if (workerOrigFetch) {
        scope.fetch = function (u, o) {
            console.log('worker-scope: fetch called: ' + (u && u.url ? u.url : u));
            return workerOrigFetch(u, o);
        };
        console.log('worker-scope: fetch logger installed');
    }
})(self);
