// Minimal AbortController/AbortSignal polyfill for engines without them.
// Signals are inert for fetch (no real cancellation) but satisfy maplibre's usage:
// new AbortController(), .signal, .abort(), signal.aborted/.reason,
// add/removeEventListener('abort'), onabort, throwIfAborted().
// Works in both window and worker scopes (uses `self`).
(function (scope) {
    if (typeof scope.AbortController !== 'undefined') {
        return;
    }

    function AbortSignalPoly() {
        this.aborted = false;
        this.reason = undefined;
        this.onabort = null;
        this._listeners = [];
    }
    AbortSignalPoly.prototype.addEventListener = function (type, fn) {
        if (type === 'abort' && typeof fn === 'function') {
            this._listeners.push(fn);
        }
    };
    AbortSignalPoly.prototype.removeEventListener = function (type, fn) {
        if (type !== 'abort') {
            return;
        }
        var i = this._listeners.indexOf(fn);
        if (i >= 0) {
            this._listeners.splice(i, 1);
        }
    };
    AbortSignalPoly.prototype.dispatchEvent = function (ev) {
        if (ev && ev.type === 'abort') {
            fire(this, ev);
        }
        return true;
    };
    AbortSignalPoly.prototype.throwIfAborted = function () {
        if (this.aborted) {
            throw this.reason;
        }
    };

    function fire(signal, ev) {
        if (typeof signal.onabort === 'function') {
            try { signal.onabort.call(signal, ev); } catch (e) {}
        }
        signal._listeners.slice().forEach(function (fn) {
            try { fn.call(signal, ev); } catch (e) {}
        });
    }

    function makeAbortError(reason) {
        if (reason !== undefined) {
            return reason;
        }
        var err = new Error('signal is aborted without reason');
        err.name = 'AbortError';
        return err;
    }

    function AbortControllerPoly() {
        this.signal = new AbortSignalPoly();
    }
    AbortControllerPoly.prototype.abort = function (reason) {
        var s = this.signal;
        if (s.aborted) {
            return;
        }
        s.aborted = true;
        s.reason = makeAbortError(reason);
        fire(s, { type: 'abort', target: s });
    };

    AbortSignalPoly.abort = function (reason) {
        var c = new AbortControllerPoly();
        c.abort(reason);
        return c.signal;
    };
    AbortSignalPoly.timeout = function (ms) {
        var c = new AbortControllerPoly();
        setTimeout(function () {
            var err = new Error('signal timed out');
            err.name = 'TimeoutError';
            c.abort(err);
        }, ms);
        return c.signal;
    };

    scope.AbortController = AbortControllerPoly;
    scope.AbortSignal = AbortSignalPoly;
})(typeof self !== 'undefined' ? self : this);
