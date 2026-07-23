// Replace MessageChannel with a setTimeout-based shim. The native one in this
// engine constructs fine but never delivers messages (maplibre's
// ThrottledInvoker relies on port delivery, so tile processing stalls).
(function () {
    // Probe the native implementation first, for the engine bug report.
    try {
        if (typeof MessageChannel !== 'undefined') {
            var probe = new MessageChannel();
            var fired = false;
            probe.port2.onmessage = function () {
                fired = true;
                console.log('mc-polyfill: native MessageChannel IS functional');
            };
            probe.port1.postMessage(1);
            setTimeout(function () {
                if (!fired) {
                    console.log('mc-polyfill: native MessageChannel is BROKEN (no delivery)');
                }
            }, 2000);
        } else {
            console.log('mc-polyfill: no native MessageChannel');
        }
    } catch (e) {
        console.log('mc-polyfill: native probe threw: ' + e);
    }

    function makePort() {
        return {
            onmessage: null,
            _peer: null,
            postMessage: function (data) {
                var peer = this._peer;
                setTimeout(function () {
                    if (peer && typeof peer.onmessage === 'function') {
                        peer.onmessage({ type: 'message', data: data });
                    }
                }, 0);
            },
            start: function () {},
            close: function () {},
            addEventListener: function (type, fn) {
                if (type === 'message') { this.onmessage = fn; }
            },
            removeEventListener: function () {}
        };
    }

    function FakeMessageChannel() {
        this.port1 = makePort();
        this.port2 = makePort();
        this.port1._peer = this.port2;
        this.port2._peer = this.port1;
    }

    window.MessageChannel = FakeMessageChannel;
    console.log('mc-polyfill: MessageChannel replaced with setTimeout shim');

    // maplibre's Actor drops envelopes whose `origin` mismatches the receiving
    // scope's location.origin; the engine's worker location.origin differs from
    // the page's, so force the allowlisted 'null' origin both ways.
    if (typeof Worker !== 'undefined' && Worker.prototype && Worker.prototype.postMessage) {
        var origWorkerPost = Worker.prototype.postMessage;
        Worker.prototype.postMessage = function (msg, opts) {
            if (msg && typeof msg === 'object' && 'origin' in msg) { msg.origin = 'null'; }
            try { return origWorkerPost.call(this, msg, opts); }
            catch (e) { return origWorkerPost.call(this, msg); }
        };
        console.log('mc-polyfill: Worker.postMessage origin-rewrite installed');
    }

    // Tile images fail with InvalidStateError through createImageBitmap here;
    // remove it so maplibre falls back to the HTMLImageElement decode path.
    if (typeof window.createImageBitmap !== 'undefined') {
        try {
            window.createImageBitmap = undefined;
            console.log('mc-polyfill: createImageBitmap disabled (Image fallback)');
        } catch (e) {
            console.log('mc-polyfill: could not disable createImageBitmap: ' + e);
        }
    }
})();
