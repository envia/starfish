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

#include "StarfishConfig.h"
#include "WebGLTexture.h"
#include "platform/canvas/gl/IncludeGL.h"

namespace Starfish {

WebGLTexture::WebGLTexture(ScriptBindingInstance* instance,
                           WebGLRenderingContext* context, GLuint object)
    : WebGLObject(instance, context, object)
    , m_minFilter(GL_NEAREST_MIPMAP_LINEAR)
    , m_magFilter(GL_LINEAR)
{
}

void WebGLTexture::setImageType(GLenum target, GLint level, GLenum type)
{
    if (level != 0) {
        return;
    }
    unsigned face =
        target == GL_TEXTURE_2D ? 0 : target - GL_TEXTURE_CUBE_MAP_POSITIVE_X;
    if (face >= 6) {
        return;
    }
    const uint8_t mask = 1 << face;
    m_floatFaces = (m_floatFaces & ~mask) | (type == GL_FLOAT ? mask : 0);
    m_halfFloatFaces =
        (m_halfFloatFaces & ~mask) | (type == GL_HALF_FLOAT_OES ? mask : 0);
}

void WebGLTexture::setFilter(GLenum pname, GLint param)
{
    if (pname == GL_TEXTURE_MIN_FILTER) {
        m_minFilter = param;
    } else if (pname == GL_TEXTURE_MAG_FILTER) {
        m_magFilter = param;
    }
}

bool WebGLTexture::needsFloatLinearExtension(bool floatLinearEnabled) const
{
    return (m_halfFloatFaces || (m_floatFaces && !floatLinearEnabled)) &&
           (m_magFilter != GL_NEAREST ||
            (m_minFilter != GL_NEAREST &&
             m_minFilter != GL_NEAREST_MIPMAP_NEAREST));
}

} // namespace Starfish

#endif
