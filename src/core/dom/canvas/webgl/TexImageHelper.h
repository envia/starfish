/*
 * Copyright (c) 2026-present Samsung Electronics Co., Ltd
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

#ifndef __StarfishTexImageHelper__
#define __StarfishTexImageHelper__

#if defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)

#include "core/modules/canvas/image/NativeImageData.h"

namespace Starfish {

class TexImageHelper final {
public:
    // NOTE: Better to use common utilities for image manipulation. Canvas
    // is not possible due to its WebView dependency.
    struct ImageData {
        ImageData() = default;
        size_t width = 0;
        size_t height = 0;
        size_t stride = 0;
        GLenum format = 0;
        unsigned char* data = nullptr;
    };

    TexImageHelper(size_t width, size_t height, size_t stride, GLenum format,
                   void* data);

    TexImageHelper(NativeImageData* imageData, GLenum format);

    ~TexImageHelper();

    void draw(const bool needsFlipY, const bool needsPremultiplyAlpha,
              const GLenum type);

    const void* data() const;

    const ImageData& sourceImage() const;

    Optional<GLenum> dataFormat() const;

private:
    unsigned char multiplyAlpha(unsigned char color, float alpha);

    ImageData m_sourceImage;
    std::vector<unsigned char> m_data;
    bool m_isNativeImageDataUsed;
    Optional<GLenum> m_dataFormat;
};

} // namespace Starfish

#endif
#endif
