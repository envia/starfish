/*
 * Copyright (c) 2018-present Samsung Electronics Co., Ltd
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

#ifndef __StarfishWebGL2RenderingContext__
#define __StarfishWebGL2RenderingContext__

#if defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)

#include "core/dom/canvas/webgl/WebGLRenderingContext.h"

namespace Starfish {

class WebGL2RenderingContext : public WebGLRenderingContext {
public:
    WebGL2RenderingContext(HTMLCanvasElement* canvasElement);
    ~WebGL2RenderingContext() override;

    DECLARE_SCRIPT_BINDING_REQUIRED_FUNCTIONS(WebGL2RenderingContext);

    ScriptValue getParameter(GLenum pname);

    // Implement WebGLRenderingContextOverloads
    void bufferData(GLenum target, GLsizeiptr size, GLenum usage);
    void bufferData(GLenum target, Optional<AllowSharedBufferSource> data,
                    GLenum usage);
    // INDIGO_TODO: Starfish::WebGL2RenderingContext::bufferData(uint32_t&, Escargot::ArrayBufferViewRef*&, uint32_t&, uint64_t&, uint32_t&)
    void bufferData(GLenum target, ScriptArrayBufferView srcData, GLenum usage, unsigned long long srcOffset, GLuint length);
};

} // namespace Starfish

#endif // defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)

#endif // __StarfishWebGL2RenderingContext__
