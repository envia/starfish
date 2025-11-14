if [ ! -f binding_generator/scripts/starfish_code_generator.py ]
then
	git submodule update --init --recursive
fi
rm -rf out/webgl2
cmake -Bout/webgl2 -DMODE=debug -DHOST=linux -DARCH=x64 -DBACKEND=uv_cairo_gl -DSHELL=glfw -DWEBGL=1 -G Ninja
ninja -C out/webgl2 starfish.executable
