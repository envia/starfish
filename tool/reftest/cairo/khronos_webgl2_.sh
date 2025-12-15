for new_test in `cat khronos_webgl2.res | sed 's/^# //'`
do
    old_test=`echo ${new_test} | sed 's/2.0.0/1.0.3/'`
    if grep -q "^${old_test}$" khronos_webgl.res
    then
        echo ${new_test}
    else
        echo "# ${new_test}"
    fi
done
