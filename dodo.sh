rm -f tool/reftest/cairo/khronos_webgl2.res
for i in `seq 2462`
do
    j=`seq -w 2462 | head -n $i | tail -n 1`
    if tail -n 1 $j.out | grep -q "1 test cases rans successfully"
    then
        cat khronos_webgl2.res | head -n $i | tail -n 1 | sed 's/# //' >> tool/reftest/cairo/khronos_webgl2.res
    elif tail -n 1 $j.out | grep -q "Running 32 jobs in parallel"
    then
        cat khronos_webgl2.res | head -n $i | tail -n 1 | sed 's/# //' | sed 's/^/# T /' >> tool/reftest/cairo/khronos_webgl2.res
    elif tail -n 1 $j.out | grep -q "test tool/reftest/cairo/khronos_webgl2.res is failed"
    then
        cat khronos_webgl2.res | head -n $i | tail -n 1 | sed 's/# //' | sed 's/^/# F /' >> tool/reftest/cairo/khronos_webgl2.res
    else
        cat khronos_webgl2.res | head -n $i | tail -n 1 | sed 's/# //' | sed 's/^/# X /' >> tool/reftest/cairo/khronos_webgl2.res
    fi
done
