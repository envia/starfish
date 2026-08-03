self.onmessage = function(e){
  var d = e.data || {};
  var inLen = (d.buf && d.buf.byteLength !== undefined) ? d.buf.byteLength : -1;
  var out = new Uint8Array([1,2,3,4,5]);
  // structured object + transferable ArrayBuffer back to main
  self.postMessage({from:'worker', inLen:inLen, tag:d.tag, out:out.buffer}, [out.buffer]);
};
self.postMessage({from:'worker', ready:true});
