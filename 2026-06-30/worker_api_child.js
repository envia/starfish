var apis = ['TextDecoder','TextEncoder','performance','atob','btoa','fetch',
  'ImageData','createImageBitmap','OffscreenCanvas','Response','Request',
  'Headers','URL','Blob','setTimeout','Promise','WebAssembly','self','caches',
  'importScripts','postMessage','ArrayBuffer','DataView','Math','JSON'];
var out = {};
for (var i=0;i<apis.length;i++){ try { out[apis[i]] = typeof eval(apis[i]); } catch(e){ out[apis[i]]='ERR'; } }
// test TextDecoder actually works
try { out['TD_decode'] = (typeof TextDecoder!=='undefined') ? new TextDecoder('utf-8').decode(new Uint8Array([72,105])) : 'no-ctor'; } catch(e){ out['TD_decode']='THREW:'+e; }
try { out['perf_now'] = (typeof performance!=='undefined' && performance.now) ? typeof performance.now() : 'no'; } catch(e){ out['perf_now']='THREW:'+e; }
self.postMessage(out);
