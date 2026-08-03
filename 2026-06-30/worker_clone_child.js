self.onmessage = function(e){
  // Build a deeply nested structured-clone payload like MapLibre tile results
  var result = {
    buckets: [
      { layerId:'water', type:'fill',
        arrays: { layoutVertexArray: new Float32Array([0,1,2,3]).buffer,
                  indexArray: new Uint16Array([0,1,2]).buffer },
        segments: [{vertexOffset:0, primitiveLength:1}, {vertexOffset:4, primitiveLength:2}] },
      { layerId:'boundary', type:'line', nested:{ a:{ b:{ c:[1,2,3] } } },
        arr: new Int32Array([9,8,7]).buffer }
    ],
    featureIndex: new Uint8Array([1,2,3,4,5,6]).buffer,
    map: null
  };
  var transfers = [result.buckets[0].arrays.layoutVertexArray,
                   result.buckets[0].arrays.indexArray,
                   result.buckets[1].arr, result.featureIndex];
  self.postMessage(result, transfers);
};
