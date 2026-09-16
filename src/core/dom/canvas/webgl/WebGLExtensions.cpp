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

#if defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)

#include "WebGLExtensions.h"
#include "core/util/String.h"
#include <unordered_set>
#include "core/util/debug/Trace.h"
#include <iostream>
#include <sstream>
#include <vector>
#include <string>
#include <iomanip>
#include <algorithm>
#include <EscargotPublic.h>
#include "binding/ScriptBindingInstance.h"
#include "core/dom/canvas/webgl/WebGLOES_VertexArrayObject.h"

#include "platform/canvas/gl/IncludeGL.h"
#include "platform/canvas/gl/GL.h"

namespace Starfish {

WebGLExtensionRegistry& WebGLExtensionRegistry::instance()
{
    static WebGLExtensionRegistry instance;
    return instance;
}

WebGLExtensionRegistry::WebGLExtensionRegistry()
{
}

void WebGLExtensionRegistry::registerExtension(const char* name,
                                               unsigned webGLVersions,
                                               ExtensionGenerator generator)
{
    m_interfaceGenerators[name] = { std::move(generator), webGLVersions };
}

void WebGLExtensionRegistry::initialize(GL* gl)
{
    // 1. Get a list of extensions supported on this device. The GL context
    // must be current here; without one GL_EXTENSIONS is empty and every
    // extension would be reported as unsupported.
    const char* raw =
        reinterpret_cast<const char*>(gl->getString(GL_EXTENSIONS));
    const std::string extensions = raw ? raw : "";

    // WebGL uses extension names without the 'GL_' prefix.
    std::vector<std::string> tokens;
    std::stringstream ss(extensions);
    std::string token;
    while (getline(ss, token, ' ')) {
        if (token.substr(0, 3) == "GL_") {
            tokens.push_back(token.substr(3));
        } else {
            STARFISH_ASSERT_NOT_REACHED();
        }
    }
#ifndef NDEBUG
    std::sort(tokens.begin(), tokens.end(),
              [](const std::string& a, const std::string& b) -> bool {
                  return a < b;
              });
#endif
#if defined(STARFISH_TIZEN)
    STARFISH_LOG_INFO("GL_EXTENSIONS =\n%s",
                      StringUtils::createAlignedString(tokens, 3).c_str());
#else
    TRACEF(WEBGL, "GL_EXTENSIONS =\n%s",
           StringUtils::createAlignedString(tokens, 3));
#endif
    std::unordered_set<std::string> glExtensions;
    for (const std::string& token : tokens) {
        glExtensions.emplace(token);
    }

    // GL_MAJOR_VERSION is an ES 3.0 query; an ES 2.0 driver rejects it with
    // INVALID_ENUM and leaves the value untouched, so the fallback is ES 2.
    GLint majorVersion = 2;
    gl->getIntegerv(GL_MAJOR_VERSION, &majorVersion);
    while (gl->getError() != GL_NO_ERROR) {
    }
    m_isES3 = majorVersion >= 3;
    if (m_isES3) {
        // OpenGL ES 3.0 folded these ES 2.0 extensions into core, so a
        // driver may omit them from GL_EXTENSIONS while supporting them.
        // https://registry.khronos.org/OpenGL/specs/es/3.0/es_spec_3.0.pdf
        // (Appendix G.1 "Core Additions and Extensions")
        for (const char* core :
             { "OES_texture_float", "OES_texture_half_float",
               "OES_standard_derivatives", "OES_depth_texture",
               "OES_vertex_array_object", "EXT_blend_minmax" }) {
            glExtensions.emplace(core);
        }
    }

    // 2. Add generators for extensions not requiring binding to native
    // objects. The third column tells which WebGL versions expose the
    // extension; WebGL 2 dropped the ones its core absorbed.
    // https://registry.khronos.org/webgl/specs/latest/2.0/#4.3

#define SUPPORTED_GL_EXTENSIONS(V)                                    \
    V(OES_texture_float, OES_texture_float, kWebGL1)                  \
    V(OES_texture_half_float, OES_texture_half_float, kWebGL1)        \
    V(OES_standard_derivatives, OES_standard_derivatives, kWebGL1)    \
    V(OES_depth_texture, WEBGL_depth_texture, kWebGL1)                \
    V(EXT_texture_filter_anisotropic, EXT_texture_filter_anisotropic, \
      kWebGLAll)                                                      \
    V(OES_texture_float_linear, OES_texture_float_linear, kWebGLAll)  \
    V(EXT_blend_minmax, EXT_blend_minmax, kWebGL1)                    \
    V(EXT_color_buffer_float, EXT_color_buffer_float, kWebGL2)

#define V(name, spec, versions)                                                \
    if (glExtensions.find(#name) != glExtensions.end()) {                      \
        registerExtension(#spec, versions,                                     \
                          [](ScriptBindingInstance* instance,                  \
                             WebGLRenderingContext*) -> Escargot::ObjectRef* { \
                              return createScriptObject(instance,              \
                                                        instance->fn##spec(),  \
                                                        #spec, nullptr);       \
                          });                                                  \
    } else {                                                                   \
        STARFISH_LOG_INFO("WebGL supports " #spec                              \
                          ", but this device does not. (Not an error.)");      \
    }
    SUPPORTED_GL_EXTENSIONS(V);
#undef V
#undef SUPPORTED_GL_EXTENSIONS

    // Float color buffers. WEBGL_color_buffer_float is the WebGL 1 form of
    // EXT_color_buffer_float: it needs float textures plus a driver that can
    // render to and read back RGBA32F, which on ES 3 is EXT_color_buffer_float.
    // EXT_color_buffer_half_float only needs RGBA16F to be renderable, which
    // EXT_color_buffer_float also provides.
    // https://registry.khronos.org/webgl/extensions/WEBGL_color_buffer_float/
    // https://registry.khronos.org/webgl/extensions/EXT_color_buffer_half_float/
    const bool hasEXT_color_buffer_float =
        glExtensions.count("EXT_color_buffer_float") > 0;
    if (hasEXT_color_buffer_float &&
        glExtensions.count("OES_texture_float") > 0) {
        registerExtension("WEBGL_color_buffer_float", kWebGL1,
                          [](ScriptBindingInstance* instance,
                             WebGLRenderingContext*) -> Escargot::ObjectRef* {
                              return createScriptObject(
                                  instance,
                                  instance->fnWEBGL_color_buffer_float(),
                                  "WEBGL_color_buffer_float", nullptr);
                          });
    }
    if ((hasEXT_color_buffer_float ||
         glExtensions.count("EXT_color_buffer_half_float") > 0) &&
        glExtensions.count("OES_texture_half_float") > 0) {
        registerExtension("EXT_color_buffer_half_float", kWebGLAll,
                          [](ScriptBindingInstance* instance,
                             WebGLRenderingContext*) -> Escargot::ObjectRef* {
                              return createScriptObject(
                                  instance,
                                  instance->fnEXT_color_buffer_half_float(),
                                  "EXT_color_buffer_half_float", nullptr);
                          });
    }

    // 3. Add generators for extensions bound with native objects

#define SUPPORTED_GL_EXTENSIONS(V) V(OES_vertex_array_object, kWebGL1)

#define V(name, versions)                                                  \
    if (glExtensions.find(#name) != glExtensions.end()) {                  \
        registerExtension(                                                 \
            #name, versions,                                               \
            [](ScriptBindingInstance* instance,                            \
               WebGLRenderingContext* glContext) -> Escargot::ObjectRef* { \
                return (new name(instance, glContext))                     \
                    ->scriptValue()                                        \
                    ->asObject();                                          \
            });                                                            \
    } else {                                                               \
        STARFISH_LOG_WARN(#name " is not supported on this device");       \
    }
    SUPPORTED_GL_EXTENSIONS(V);
#undef V
#undef SUPPORTED_GL_EXTENSIONS

    m_hasEXT_texture_format_BGRA8888 =
        (extensions.find("GL_EXT_texture_format_BGRA8888") !=
         std::string::npos);

    m_isInitialized = true;
}

GCVector<String*> WebGLExtensionRegistry::getSupportedExtensions(
    unsigned webGLVersion)
{
    GCVector<String*> extentions;
    for (const auto& pair : m_interfaceGenerators) {
        if (!(pair.second.webGLVersions & webGLVersion)) {
            continue;
        }
        extentions.push_back(
            String::createASCIIString(pair.first.c_str(), pair.first.length()));
    }
    return extentions;
}

Optional<ExtensionGenerator> WebGLExtensionRegistry::getGenerator(
    const std::string& name, unsigned webGLVersion)
{
    const auto& iter = m_interfaceGenerators.find(name);
    if (iter != m_interfaceGenerators.end() &&
        (iter->second.webGLVersions & webGLVersion)) {
        return iter->second.generator;
    }
    return Optional<ExtensionGenerator>();
}

} // namespace Starfish

#endif
