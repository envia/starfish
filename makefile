.PHONY: all try clean

all: binding_generator/scripts/starfish_code_generator.py out/webgl2
	ninja -C out/webgl2 starfish.executable

try: binding_generator/scripts/starfish_code_generator.py out/webgl2
	ninja -k 0 -C out/webgl2 starfish.executable

out/webgl2:
	cmake -Bout/webgl2 -DMODE=debug -DHOST=linux -DARCH=x64 -DBACKEND=uv_cairo_gl -DSHELL=glfw -DWEBGL=1 -G Ninja

binding_generator/scripts/starfish_code_generator.py:
	git submodule update --init --recursive

clean:
	rm -rf Starfish out/webgl2
