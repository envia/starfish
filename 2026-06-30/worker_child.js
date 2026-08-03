self.postMessage('child-started');
self.onmessage = function(e){
  self.postMessage('child-got:' + e.data);
};
