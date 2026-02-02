for old_url in "$1"
do
    case ${old_url} in
        *1.0.3*)
            new_url=$(echo ${old_url} | sed 's/.*1.0.3/https:\/\/registry.khronos.org\/webgl\/conformance-suites\/1.0.3/')
            ;;
        *2.0.0*)
            new_url=$(echo ${old_url} | sed 's/.*2.0.0/https:\/\/registry.khronos.org\/webgl\/conformance-suites\/2.0.0/')
            ;;
        *)
            new_url=${old_url}
            ;;
    esac
done
echo ${new_url}
./Starfish ${new_url}
