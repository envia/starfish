/*
 * Copyright (c) 2019-present Samsung Electronics Co., Ltd
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
#include "core/dom/canvas/webgl/util/TexImageHelper.h"
#include "core/dom/canvas/webgl/WebGLExtensions.h"
#include "core/modules/canvas/image/NativeImageData.h"
#include "platform/canvas/gl/IncludeGL.h"

namespace Starfish {

inline static std::string hex(GLenum name)
{
    return StringUtils::formatString("0x%04X", name);
}

TexImageHelper::TexImageHelper(size_t width, size_t height, size_t stride,
                               GLenum format, void* data)
{
    STARFISH_ASSERT(data != nullptr);

    m_sourceImage.width = width;
    m_sourceImage.height = height;
    m_sourceImage.stride = stride;
    m_sourceImage.format = format;
    m_sourceImage.data = static_cast<unsigned char*>(data);
    m_isNativeImageDataUsed = false;
}

TexImageHelper::TexImageHelper(NativeImageData* imageData, GLenum format)
{
    STARFISH_ASSERT(imageData != nullptr);

    m_sourceImage.width = imageData->width();
    m_sourceImage.height = imageData->height();
    m_sourceImage.stride = imageData->stride();
    m_sourceImage.format = format;
    m_sourceImage.data = static_cast<unsigned char*>(imageData->data());
    m_isNativeImageDataUsed = true;
}

TexImageHelper::~TexImageHelper()
{
}

void TexImageHelper::draw(const bool needsFlipY,
                          const bool needsPremultiplyAlpha, const GLenum type)
{
    const size_t width = m_sourceImage.width;
    const size_t height = m_sourceImage.height;
    const size_t stride = m_sourceImage.stride;
    const unsigned char* image = m_sourceImage.data;

    size_t offset = 0, newOffset = 0, srcOffset = 0, destOffset = 0;

    if (m_sourceImage.format != GL_RGB && m_sourceImage.format != GL_RGBA) {
        return;
    }

    if (m_isNativeImageDataUsed && type != GL_UNSIGNED_BYTE) {
        // NativeImageData is packed as UNSIGNED_BYTE. Type conversion might
        // be needed, but how often this is used is unclear for now. TODO:
        // Convert if necessary.
        STARFISH_UNSUPPORTED(
            "type (%s). GL_UNSIGNED_BYTE is only supported for now.",
            hex(type).c_str());
    }

#if !defined(PORT_PIXEL_ORDER_RGBA) && !defined(PORT_PIXEL_ORDER_BGRA)
    STARFISH_ASSERT_NOT_REACHED();
    return;
#endif

    bool needsColorConversion = false;

#if defined(PORT_PIXEL_ORDER_BGRA)
    if (m_isNativeImageDataUsed) {
        // NativeImageData is formatted as BGRA.
        if (WebGLExtensionRegistry::instance()
                .hasEXT_texture_format_BGRA8888()) {
            m_dataFormat = GL_BGRA_EXT;
            needsColorConversion = false;
        } else {
            needsColorConversion = true;
        }
    }
#endif
    if (!needsFlipY && !needsPremultiplyAlpha && !needsColorConversion) {
        return;
    }

    m_data.resize(height * stride);

    std::vector<uint8_t> order;

    if (needsColorConversion) {
        order = { 2, 1, 0, 3 };
    } else {
        order = { 0, 1, 2, 3 };
    }

    for (size_t row = 0; row < height; row++) {
        // Calculate the memory offset for the current row
        newOffset = offset = row * stride;

        // NOTE: For increasing more performance of this feature, we may
        // consider using fragment shader.
        if (needsFlipY) {
            newOffset = (height - row - 1) * stride;
        }

        for (size_t column = 0; column < width; column++) {
            // Calculate the memory offset for the current pixel
            srcOffset = offset + column * 4;
            destOffset = newOffset + column * 4;

            if (needsPremultiplyAlpha) {
                float alpha = image[srcOffset + order[3]] / 255.f;
                m_data[destOffset + 0] =
                    multiplyAlpha(image[srcOffset + order[0]], alpha);
                m_data[destOffset + 1] =
                    multiplyAlpha(image[srcOffset + order[1]], alpha);
                m_data[destOffset + 2] =
                    multiplyAlpha(image[srcOffset + order[2]], alpha);
                m_data[destOffset + 3] = image[srcOffset + order[3]];
            } else {
                m_data[destOffset + 0] = image[srcOffset + order[0]];
                m_data[destOffset + 1] = image[srcOffset + order[1]];
                m_data[destOffset + 2] = image[srcOffset + order[2]];
                m_data[destOffset + 3] = image[srcOffset + order[3]];
            }
        }
    }
}

const void* TexImageHelper::data() const
{
    return m_data.empty() ? m_sourceImage.data : m_data.data();
}

const TexImageHelper::ImageData& TexImageHelper::sourceImage() const
{
    return m_sourceImage;
}

Optional<GLenum> TexImageHelper::dataFormat() const
{
    return m_dataFormat;
}

unsigned char TexImageHelper::multiplyAlpha(unsigned char color, float alpha)
{
    return ((color / 255.f) * alpha) * 255;
}

} // namespace Starfish

#endif
