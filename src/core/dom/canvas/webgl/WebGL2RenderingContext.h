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

class Uint32ArrayOrSequenceOfGLuint;

class WebGL2RenderingContext : public WebGLRenderingContext {
public:
    void beginQuery(){}
    void beginQuery(uint32_t&, WebGLQuery*&){}
    void beginTransformFeedback(){}
    void beginTransformFeedback(uint32_t&){}
    void bindBufferBase(){}
    void bindBufferBase(uint32_t&, uint32_t&, Optional<WebGLBuffer*>&){}
    void bindBufferRange(){}
    void bindBufferRange(uint32_t&, uint32_t&, Optional<WebGLBuffer*>&, int64_t&, int64_t&){}
    void bindSampler(){}
    void bindSampler(uint32_t&, Optional<WebGLSampler*>&){}
    void bindTransformFeedback(){}
    void bindTransformFeedback(uint32_t&, Optional<WebGLTransformFeedback*>&){}
    void bindVertexArray(){}
    void bindVertexArray(Optional<WebGLVertexArrayObject*>&){}
    void blitFramebuffer(){}
    void blitFramebuffer(int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&){}
    void bufferData(){}
    void bufferData(uint32_t&, Escargot::ArrayBufferViewRef*&, uint32_t&, uint64_t&, uint32_t&){}
    void bufferData(uint32_t&, Optional<ArrayBufferOrSharedArrayBufferOrArrayBufferView>&, uint32_t&){}
    void bufferData(uint32_t&, int64_t&, uint32_t&){}
    void bufferSubData(){}
    void bufferSubData(uint32_t&, int64_t&, ArrayBufferOrSharedArrayBufferOrArrayBufferView&){}
    void bufferSubData(uint32_t&, int64_t&, Escargot::ArrayBufferViewRef*&, uint64_t&, uint32_t&){}
    void clearBufferfi(){}
    void clearBufferfi(uint32_t&, int32_t&, double&, int32_t&){}
    void clearBufferfv(){}
    void clearBufferfv(uint32_t&, int32_t&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&){}
    void clearBufferiv(){}
    void clearBufferiv(uint32_t&, int32_t&, Int32ArrayOrSequenceOfGLint&, uint64_t&){}
    void clearBufferuiv(){}
    void clearBufferuiv(uint32_t&, int32_t&, Uint32ArrayOrSequenceOfGLuint&, uint64_t&){}
    void clientWaitSync(){}
    void clientWaitSync(WebGLSync*&, uint32_t&, uint64_t&){}
    void compressedTexImage2D(){}
    void compressedTexImage2D(uint32_t&, int32_t&, uint32_t&, int32_t&, int32_t&, int32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&, uint32_t&){}
    void compressedTexImage2D(uint32_t&, int32_t&, uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int64_t&){}
    void compressedTexImage3D(){}
    void compressedTexImage3D(uint32_t&, int32_t&, uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&, uint32_t&){}
    void compressedTexImage3D(uint32_t&, int32_t&, uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int64_t&){}
    void compressedTexSubImage2D(){}
    void compressedTexSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&, uint32_t&){}
    void compressedTexSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, int32_t&, int64_t&){}
    void compressedTexSubImage3D(){}
    void compressedTexSubImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&, uint32_t&){}
    void compressedTexSubImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, int32_t&, int64_t&){}
    void copyBufferSubData(){}
    void copyBufferSubData(uint32_t&, uint32_t&, int64_t&, int64_t&, int64_t&){}
    void copyTexSubImage3D(){}
    void copyTexSubImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&){}
    void createQuery(){}
    void createSampler(){}
    void createTransformFeedback(){}
    void createVertexArray(){}
    void deleteQuery(){}
    void deleteQuery(Optional<WebGLQuery*>&){}
    void deleteSampler(){}
    void deleteSampler(Optional<WebGLSampler*>&){}
    void deleteSync(){}
    void deleteSync(Optional<WebGLSync*>&){}
    void deleteTransformFeedback(){}
    void deleteTransformFeedback(Optional<WebGLTransformFeedback*>&){}
    void deleteVertexArray(){}
    void deleteVertexArray(Optional<WebGLVertexArrayObject*>&){}
    void drawArraysInstanced(){}
    void drawArraysInstanced(uint32_t&, int32_t&, int32_t&, int32_t&){}
    void drawBuffers(){}
    void drawBuffers(GCAtomicVector<unsigned int>&){}
    void drawElementsInstanced(){}
    void drawElementsInstanced(uint32_t&, int32_t&, uint32_t&, int64_t&, int32_t&){}
    void drawRangeElements(){}
    void drawRangeElements(uint32_t&, uint32_t&, uint32_t&, int32_t&, uint32_t&, int64_t&){}
    void endQuery(){}
    void endQuery(uint32_t&){}
    void endTransformFeedback(){}
    void fenceSync(){}
    void fenceSync(uint32_t&, uint32_t&){}
    void framebufferTextureLayer(){}
    void framebufferTextureLayer(uint32_t&, uint32_t&, Optional<WebGLTexture*>&, int32_t&, int32_t&){}
    void getActiveUniformBlockName(){}
    void getActiveUniformBlockName(WebGLProgram*&, uint32_t&){}
    void getActiveUniformBlockParameter(){}
    void getActiveUniformBlockParameter(WebGLProgram*&, uint32_t&, uint32_t&){}
    void getActiveUniforms(){}
    void getActiveUniforms(WebGLProgram*&, GCAtomicVector<unsigned int>&, uint32_t&){}
    void getBufferSubData(){}
    void getBufferSubData(uint32_t&, int64_t&, Escargot::ArrayBufferViewRef*&, uint64_t&, uint32_t&){}
    void getFragDataLocation(){}
    void getFragDataLocation(WebGLProgram*&, String*&){}
    void getIndexedParameter(){}
    void getIndexedParameter(uint32_t&, uint32_t&){}
    void getInternalformatParameter(){}
    void getInternalformatParameter(uint32_t&, uint32_t&, uint32_t&){}
    void getQuery(){}
    void getQuery(uint32_t&, uint32_t&){}
    void getQueryParameter(){}
    void getQueryParameter(WebGLQuery*&, uint32_t&){}
    void getSamplerParameter(){}
    void getSamplerParameter(WebGLSampler*&, uint32_t&){}
    void getSyncParameter(){}
    void getSyncParameter(WebGLSync*&, uint32_t&){}
    void getTransformFeedbackVarying(){}
    void getTransformFeedbackVarying(WebGLProgram*&, uint32_t&){}
    void getUniformBlockIndex(){}
    void getUniformBlockIndex(WebGLProgram*&, String*&){}
    void getUniformIndices(){}
    void getUniformIndices(WebGLProgram*&, GCVector<String*>&){}
    void invalidateFramebuffer(){}
    void invalidateFramebuffer(uint32_t&, GCAtomicVector<unsigned int>&){}
    void invalidateSubFramebuffer(){}
    void invalidateSubFramebuffer(uint32_t&, GCAtomicVector<unsigned int>&, int32_t&, int32_t&, int32_t&, int32_t&){}
    void isQuery(){}
    void isQuery(Optional<WebGLQuery*>&){}
    void isSampler(){}
    void isSampler(Optional<WebGLSampler*>&){}
    void isSync(){}
    void isSync(Optional<WebGLSync*>&){}
    void isTransformFeedback(){}
    void isTransformFeedback(Optional<WebGLTransformFeedback*>&){}
    void isVertexArray(){}
    void isVertexArray(Optional<WebGLVertexArrayObject*>&){}
    void pauseTransformFeedback(){}
    void readBuffer(){}
    void readBuffer(uint32_t&){}
    void readPixels(){}
    void readPixels(int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&){}
    void readPixels(int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&){}
    void readPixels(int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, int64_t&){}
    void renderbufferStorageMultisample(){}
    void renderbufferStorageMultisample(uint32_t&, int32_t&, uint32_t&, int32_t&, int32_t&){}
    void resumeTransformFeedback(){}
    void samplerParameterf(){}
    void samplerParameterf(WebGLSampler*&, uint32_t&, double&){}
    void samplerParameteri(){}
    void samplerParameteri(WebGLSampler*&, uint32_t&, int32_t&){}
    void texImage2D(){}
    void texImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&){}
    void texImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&){}
    void texImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&){}
    void texImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, int64_t&){}
    void texImage2D(uint32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&){}
    void texImage3D(){}
    void texImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&){}
    void texImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&){}
    void texImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&){}
    void texImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, int64_t&){}
    void texStorage2D(){}
    void texStorage2D(uint32_t&, int32_t&, uint32_t&, int32_t&, int32_t&){}
    void texStorage3D(){}
    void texStorage3D(uint32_t&, int32_t&, uint32_t&, int32_t&, int32_t&, int32_t&){}
    void texSubImage2D(){}
    void texSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&){}
    void texSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&){}
    void texSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&){}
    void texSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, int64_t&){}
    void texSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&){}
    void texSubImage3D(){}
    void texSubImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&){}
    void texSubImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&){}
    void texSubImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, int64_t&){}
    void transformFeedbackVaryings(){}
    void transformFeedbackVaryings(WebGLProgram*&, GCVector<String*>&, uint32_t&){}
    void uniform1fv(){}
    void uniform1fv(Optional<WebGLUniformLocation*>&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniform1iv(){}
    void uniform1iv(Optional<WebGLUniformLocation*>&, Int32ArrayOrSequenceOfGLint&, uint64_t&, uint32_t&){}
    void uniform1ui(){}
    void uniform1ui(Optional<WebGLUniformLocation*>&, uint32_t&){}
    void uniform1uiv(){}
    void uniform1uiv(Optional<WebGLUniformLocation*>&, Uint32ArrayOrSequenceOfGLuint&, uint64_t&, uint32_t&){}
    void uniform2fv(){}
    void uniform2fv(Optional<WebGLUniformLocation*>&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniform2iv(){}
    void uniform2iv(Optional<WebGLUniformLocation*>&, Int32ArrayOrSequenceOfGLint&, uint64_t&, uint32_t&){}
    void uniform2ui(){}
    void uniform2ui(Optional<WebGLUniformLocation*>&, uint32_t&, uint32_t&){}
    void uniform2uiv(){}
    void uniform2uiv(Optional<WebGLUniformLocation*>&, Uint32ArrayOrSequenceOfGLuint&, uint64_t&, uint32_t&){}
    void uniform3fv(){}
    void uniform3fv(Optional<WebGLUniformLocation*>&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniform3iv(){}
    void uniform3iv(Optional<WebGLUniformLocation*>&, Int32ArrayOrSequenceOfGLint&, uint64_t&, uint32_t&){}
    void uniform3ui(){}
    void uniform3ui(Optional<WebGLUniformLocation*>&, uint32_t&, uint32_t&, uint32_t&){}
    void uniform3uiv(){}
    void uniform3uiv(Optional<WebGLUniformLocation*>&, Uint32ArrayOrSequenceOfGLuint&, uint64_t&, uint32_t&){}
    void uniform4fv(){}
    void uniform4fv(Optional<WebGLUniformLocation*>&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniform4iv(){}
    void uniform4iv(Optional<WebGLUniformLocation*>&, Int32ArrayOrSequenceOfGLint&, uint64_t&, uint32_t&){}
    void uniform4ui(){}
    void uniform4ui(Optional<WebGLUniformLocation*>&, uint32_t&, uint32_t&, uint32_t&, uint32_t&){}
    void uniform4uiv(){}
    void uniform4uiv(Optional<WebGLUniformLocation*>&, Uint32ArrayOrSequenceOfGLuint&, uint64_t&, uint32_t&){}
    void uniformBlockBinding(){}
    void uniformBlockBinding(WebGLProgram*&, uint32_t&, uint32_t&){}
    void uniformMatrix2fv(){}
    void uniformMatrix2fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniformMatrix2x3fv(){}
    void uniformMatrix2x3fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniformMatrix2x4fv(){}
    void uniformMatrix2x4fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniformMatrix3fv(){}
    void uniformMatrix3fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniformMatrix3x2fv(){}
    void uniformMatrix3x2fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniformMatrix3x4fv(){}
    void uniformMatrix3x4fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniformMatrix4fv(){}
    void uniformMatrix4fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniformMatrix4x2fv(){}
    void uniformMatrix4x2fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniformMatrix4x3fv(){}
    void uniformMatrix4x3fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void vertexAttribDivisor(){}
    void vertexAttribDivisor(uint32_t&, uint32_t&){}
    void vertexAttribI4i(){}
    void vertexAttribI4i(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&){}
    void vertexAttribI4iv(){}
    void vertexAttribI4iv(uint32_t&, Int32ArrayOrSequenceOfGLint&){}
    void vertexAttribI4ui(){}
    void vertexAttribI4ui(uint32_t&, uint32_t&, uint32_t&, uint32_t&, uint32_t&){}
    void vertexAttribI4uiv(){}
    void vertexAttribI4uiv(uint32_t&, Uint32ArrayOrSequenceOfGLuint&){}
    void vertexAttribIPointer(){}
    void vertexAttribIPointer(uint32_t&, int32_t&, uint32_t&, int32_t&, int64_t&){}
    void waitSync(){}
    void waitSync(WebGLSync*&, uint32_t&, int64_t&){}
};

} // namespace Starfish

#endif // defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)

#endif // __StarfishWebGL2RenderingContext__
