.PHONY: all try clean revert reland submodule webgl1 webgl2

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
	rm -rf tool/__pycache__ tool/drivers/basics/__pycache__

revert: binding_generator/scripts/starfish_code_generator.py
	git -C test am ../0001-Revert-Update-WebGL-2-tests-to-ensure-termination.patch > /dev/null 2>&1 || git -C test am --abort

reland: binding_generator/scripts/starfish_code_generator.py
	git -C test reset --hard master

submodule:
	git submodule update --init --recursive

webgl1:
	./tool/test_runner.py vendor_test_khronos

webgl2:
	./tool/test_runner.py vendor_test_khronos2

webglsdk:
	./tool/test_runner.py vendor_test_khronossdk
