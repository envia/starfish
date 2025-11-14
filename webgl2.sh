#git submodule update --init --recursive
rm -rf out/webgl2
cmake -Bout/webgl2 -DMODE=debug -DHOST=linux -DARCH=x64 -DBACKEND=uv_cairo_gl -DSHELL=glfw -DWEBGL=1 -G Ninja
ninja -C out/webgl2 starfish.executable
