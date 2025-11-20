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
    void bufferData(uint32_t&, Escargot::ArrayBufferViewRef*&, uint32_t&, uint64_t&, uint32_t&){}
    void bufferSubData(uint32_t&, int64_t&, Escargot::ArrayBufferViewRef*&, uint64_t&, uint32_t&){}
    void compressedTexImage2D(uint32_t&, int32_t&, uint32_t&, int32_t&, int32_t&, int32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&, uint32_t&){}
    void compressedTexImage2D(uint32_t&, int32_t&, uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int64_t&){}
    void compressedTexSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&, uint32_t&){}
    void compressedTexSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, int32_t&, int64_t&){}
    void readPixels(int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&){}
    void texImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&){}
    void texImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Starfish::ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&){}
    void texSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&){}
    void texSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Starfish::ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&){}
    void uniform1fv(Optional<Starfish::WebGLUniformLocation*>&, Starfish::Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniform1iv(Optional<Starfish::WebGLUniformLocation*>&, Starfish::Int32ArrayOrSequenceOfGLint&, uint64_t&, uint32_t&){}
    void uniform2fv(Optional<Starfish::WebGLUniformLocation*>&, Starfish::Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniform2iv(Optional<Starfish::WebGLUniformLocation*>&, Starfish::Int32ArrayOrSequenceOfGLint&, uint64_t&, uint32_t&){}
    void uniform3fv(Optional<Starfish::WebGLUniformLocation*>&, Starfish::Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniform3iv(Optional<Starfish::WebGLUniformLocation*>&, Starfish::Int32ArrayOrSequenceOfGLint&, uint64_t&, uint32_t&){}
    void uniform4fv(Optional<Starfish::WebGLUniformLocation*>&, Starfish::Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniform4iv(Optional<Starfish::WebGLUniformLocation*>&, Starfish::Int32ArrayOrSequenceOfGLint&, uint64_t&, uint32_t&){}
    void uniformMatrix2fv(Optional<Starfish::WebGLUniformLocation*>&, bool&, Starfish::Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniformMatrix3fv(Optional<Starfish::WebGLUniformLocation*>&, bool&, Starfish::Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniformMatrix4fv(Optional<Starfish::WebGLUniformLocation*>&, bool&, Starfish::Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
};

} // namespace Starfish

#endif // defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)

#endif // __StarfishWebGL2RenderingContext__
