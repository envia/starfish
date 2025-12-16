for i in `seq 2462`
do
    j=`seq -w 2462 | head -n $i | tail -n 1`
    cat khronos_webgl2.res | head -n $i | tail -n 1 | sed 's/# //' > tool/reftest/cairo/khronos_webgl2.res
    timeout 10 ./tool/test_runner.py vendor_test_khronos2 1> $j.out 2> $j.err
done
