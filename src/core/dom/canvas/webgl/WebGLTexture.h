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

#ifndef __StarfishWebGLTexture__
#define __StarfishWebGLTexture__

#if defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)

#include "core/dom/canvas/webgl/WebGLObject.h"

namespace Starfish {

class WebGLTexture : public WebGLObject {
public:
    WebGLTexture(ScriptBindingInstance* instance,
                 WebGLRenderingContext* context, GLuint object);
    void init(ScriptBindingInstance* instance, void* domObjectPointer) override;
    bool isWebGLTexture() const override;
    void setImageType(GLenum target, GLint level, GLenum type);
    void setFilter(GLenum pname, GLint param);
    bool needsFloatLinearExtension(bool floatLinearEnabled) const;

private:
    // One bit per base-level cube face; 2D uses bit zero. Other completeness
    // rules (mip sizes and matching formats) are enforced by native GL.
    uint8_t m_floatFaces = 0;
    uint8_t m_halfFloatFaces = 0;
    uint16_t m_minFilter;
    uint16_t m_magFilter;
};
} // namespace Starfish

#endif
#endif
