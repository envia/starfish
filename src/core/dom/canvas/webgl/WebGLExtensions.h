/*
 * Copyright (c) 2023-present Samsung Electronics Co., Ltd
 *
 *  This library is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU Lesser General Public
 *  License as published by the Free Software Foundation; either
 *  version 2.1 of the License, or (at your option) any later version.
 *
 *  This library is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *  Lesser General Public License for more details.
 *
 *  You should have received a copy of the GNU Lesser General Public
 *  License along with this library; if not, write to the Free Software
 *  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
 *  USA
 */

#ifndef __StarfishWebGLExtensions__
#define __StarfishWebGLExtensions__

#include <functional>
#include <string>
#include <unordered_map>
#include "core/dom/canvas/webgl/WebGLUtils.h"
#include "StarfishBase.h" // Optional, GCVector

namespace Escargot {
class ObjectRef;
}; // namespace Escargot

namespace Starfish {

class ScriptBindingInstance;
class String;
class WebGLRenderingContext;
class GL;

using ExtensionGenerator = std::function<Escargot::ObjectRef*(
    ScriptBindingInstance*, WebGLRenderingContext*)>;

class WebGLExtensionRegistry {
public:
    static WebGLExtensionRegistry& instance();

    void initialize(GL* gl);
    bool isInitialized()
    {
        return m_isInitialized;
    }

    // WebGL 1 and WebGL 2 expose different extension sets: some WebGL 1
    // extensions were promoted to core or replaced in WebGL 2, and
    // EXT_color_buffer_float exists only for WebGL 2.
    // https://registry.khronos.org/webgl/extensions/
    static constexpr unsigned kWebGL1 = 1u << 1;
    static constexpr unsigned kWebGL2 = 1u << 2;
    static constexpr unsigned kWebGLAll = kWebGL1 | kWebGL2;

    Optional<ExtensionGenerator> getGenerator(const std::string& name,
                                              unsigned webGLVersion);
    GCVector<String*> getSupportedExtensions(unsigned webGLVersion);

    WebGLExtensionRegistry(const WebGLExtensionRegistry&) = delete;
    WebGLExtensionRegistry(const WebGLExtensionRegistry&&) = delete;
    WebGLExtensionRegistry& operator=(const WebGLExtensionRegistry&) = delete;
    WebGLExtensionRegistry& operator=(const WebGLExtensionRegistry&&) = delete;

    bool hasEXT_texture_format_BGRA8888()
    {
        return m_hasEXT_texture_format_BGRA8888;
    }

    // True on an OpenGL ES 3.0+ context. ES 3 promotes OES_texture_float,
    // OES_texture_half_float and OES_vertex_array_object to core and takes
    // sized internal formats; WebGL 1 float textures are mapped onto those.
    bool isES3()
    {
        return m_isES3;
    }

    bool hasTextureCompressionExtension()
    {
        // NOTE: Currently verifiable targets don't support this feature.
        return false;
    }

private:
    WebGLExtensionRegistry();

    struct Extension {
        ExtensionGenerator generator;
        unsigned webGLVersions;
    };

    void registerExtension(const char* name, unsigned webGLVersions,
                           ExtensionGenerator generator);

    std::unordered_map<std::string, Extension, CaseInsensitiveHash,
                       CaseInsensitiveEqual>
        m_interfaceGenerators;

    bool m_hasEXT_texture_format_BGRA8888 = false;
    bool m_isES3 = false;
    bool m_isInitialized = false;
};

} // namespace Starfish

#endif
