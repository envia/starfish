// Make DOM collections iterable (Symbol.iterator) for engines that lack it:
// NamedNodeMap (el.attributes), HTMLCollection (el.children), NodeList
// (querySelectorAll), DOMTokenList (el.classList). Page scope only.
(function () {
    if (typeof document === 'undefined' || typeof Symbol === 'undefined' || !Symbol.iterator) {
        return;
    }

    function indexedIterator() {
        var self = this;
        var i = 0;
        var iter = {
            next: function () {
                if (i < self.length) {
                    var v = typeof self.item === 'function' ? self.item(i) : self[i];
                    i += 1;
                    return { value: v, done: false };
                }
                return { value: undefined, done: true };
            }
        };
        iter[Symbol.iterator] = function () { return iter; };
        return iter;
    }

    function patch(obj, name) {
        if (!obj) {
            console.log('dom-iter-polyfill: cannot reach ' + name);
            return;
        }
        var proto = Object.getPrototypeOf(obj);
        if (proto && !proto[Symbol.iterator]) {
            proto[Symbol.iterator] = indexedIterator;
            console.log('dom-iter-polyfill: patched ' + name);
        }
    }

    var el = document.documentElement;
    patch(el.attributes, 'NamedNodeMap');
    patch(el.children, 'HTMLCollection');
    patch(document.querySelectorAll('html'), 'NodeList');
    patch(el.classList, 'DOMTokenList');
})();
