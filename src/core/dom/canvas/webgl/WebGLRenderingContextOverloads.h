/*
 * Copyright (c) 2025-present Samsung Electronics Co., Ltd
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

#ifndef __StarfishWebGLRenderingContextOverloads__
#define __StarfishWebGLRenderingContextOverloads__

#if defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)

namespace Starfish {

class WebGLRenderingContextOverloads {
public:
    void bufferData(GLenum target, GLsizeiptr size, GLenum usage);
    void bufferData(GLenum target, Optional<AllowSharedBufferSource> data,
                    GLenum usage);
    void bufferSubData(GLenum target, GLintptr offset,
                       AllowSharedBufferSource data);

    void compressedTexImage2D(GLenum target, GLint level, GLenum internalformat,
                              GLsizei width, GLsizei height, GLint border,
                              ScriptArrayBufferView data);
    void compressedTexSubImage2D(GLenum target, GLint level, GLint xoffset,
                                 GLint yoffset, GLsizei width, GLsizei height,
                                 GLenum format, ScriptArrayBufferView data);

    void readPixels(GLint x, GLint y, GLsizei width, GLsizei height,
                    GLenum format, GLenum type,
                    Optional<ScriptArrayBufferView> pixels);

    void texImage2D(GLenum target, GLint level, GLint internalFormat,
                    GLsizei width, GLsizei height, GLint border, GLenum format,
                    GLenum type, Optional<ScriptArrayBufferView> pixels);
    void texImage2D(GLenum target, GLint level, GLint internalFormat,
                    GLenum format, GLenum type, TexImageSource source);
    void texSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset,
                       GLsizei width, GLsizei height, GLenum format,
                       GLenum type, Optional<ScriptArrayBufferView> pixels);
    void texSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset,
                       GLenum format, GLenum type, TexImageSource source);

    void uniform1fv(Optional<WebGLUniformLocation*> location, Float32List v);
    void uniform2fv(Optional<WebGLUniformLocation*> location, Float32List v);
    void uniform3fv(Optional<WebGLUniformLocation*> location, Float32List v);
    void uniform4fv(Optional<WebGLUniformLocation*> location, Float32List v);

    void uniform1iv(Optional<WebGLUniformLocation*> location, Int32List v);
    void uniform2iv(Optional<WebGLUniformLocation*> location, Int32List v);
    void uniform3iv(Optional<WebGLUniformLocation*> location, Int32List v);
    void uniform4iv(Optional<WebGLUniformLocation*> location, Int32List v);

    void uniformMatrix2fv(Optional<WebGLUniformLocation*> uniform,
                          GLboolean transpose, Float32List value);
    void uniformMatrix3fv(Optional<WebGLUniformLocation*> uniform,
                          GLboolean transpose, Float32List value);
    void uniformMatrix4fv(Optional<WebGLUniformLocation*> uniform,
                          GLboolean transpose, Float32List value);
};

} // namespace Starfish

#endif // defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)

#endif // __StarfishWebGLRenderingContextOverloads__
