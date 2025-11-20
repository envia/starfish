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
    void beginQuery(){}
    void beginTransformFeedback(){}
    void bindBufferBase(){}
    void bindBufferRange(){}
    void bindSampler(){}
    void bindTransformFeedback(){}
    void bindVertexArray(){}
    void blitFramebuffer(){}
    void bufferData(){}
    void bufferSubData(){}
    void clearBufferfi(){}
    void clearBufferfv(){}
    void clearBufferiv(){}
    void clearBufferuiv(){}
    void clientWaitSync(){}
    void compressedTexImage2D(){}
    void compressedTexImage3D(){}
    void compressedTexSubImage2D(){}
    void compressedTexSubImage3D(){}
    void copyBufferSubData(){}
    void copyTexSubImage3D(){}
    void createQuery(){}
    void createSampler(){}
    void createTransformFeedback(){}
    void createVertexArray(){}
    void deleteQuery(){}
    void deleteSampler(){}
    void deleteSync(){}
    void deleteTransformFeedback(){}
    void deleteVertexArray(){}
    void drawArraysInstanced(){}
    void drawBuffers(){}
    void drawElementsInstanced(){}
    void drawRangeElements(){}
    void endQuery(){}
    void endTransformFeedback(){}
    void fenceSync(){}
    void framebufferTextureLayer(){}
    void getActiveUniformBlockName(){}
    void getActiveUniformBlockParameter(){}
    void getActiveUniforms(){}
    void getBufferSubData(){}
    void getFragDataLocation(){}
    void getIndexedParameter(){}
    void getInternalformatParameter(){}
    void getQuery(){}
    void getQueryParameter(){}
    void getSamplerParameter(){}
    void getSyncParameter(){}
    void getTransformFeedbackVarying(){}
    void getUniformBlockIndex(){}
    void getUniformIndices(){}
    void invalidateFramebuffer(){}
    void invalidateSubFramebuffer(){}
    void isQuery(){}
    void isSampler(){}
    void isSync(){}
    void isTransformFeedback(){}
    void isVertexArray(){}
    void pauseTransformFeedback(){}
    void readBuffer(){}
    void readPixels(){}
    void renderbufferStorageMultisample(){}
    void resumeTransformFeedback(){}
    void samplerParameterf(){}
    void samplerParameteri(){}
    void texImage2D(){}
    void texImage3D(){}
    void texStorage2D(){}
    void texStorage3D(){}
    void texSubImage2D(){}
    void texSubImage3D(){}
    void transformFeedbackVaryings(){}
    void uniform1fv(){}
    void uniform1iv(){}
    void uniform1ui(){}
    void uniform1uiv(){}
    void uniform2fv(){}
    void uniform2iv(){}
    void uniform2ui(){}
    void uniform2uiv(){}
    void uniform3fv(){}
    void uniform3iv(){}
    void uniform3ui(){}
    void uniform3uiv(){}
    void uniform4fv(){}
    void uniform4iv(){}
    void uniform4ui(){}
    void uniform4uiv(){}
    void uniformBlockBinding(){}
    void uniformMatrix2fv(){}
    void uniformMatrix2x3fv(){}
    void uniformMatrix2x4fv(){}
    void uniformMatrix3fv(){}
    void uniformMatrix3x2fv(){}
    void uniformMatrix3x4fv(){}
    void uniformMatrix4fv(){}
    void uniformMatrix4x2fv(){}
    void uniformMatrix4x3fv(){}
    void vertexAttribDivisor(){}
    void vertexAttribI4i(){}
    void vertexAttribI4iv(){}
    void vertexAttribI4ui(){}
    void vertexAttribI4uiv(){}
    void vertexAttribIPointer(){}
    void waitSync(){}
};

} // namespace Starfish

#endif // defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)

#endif // __StarfishWebGL2RenderingContext__
