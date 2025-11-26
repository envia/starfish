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

#ifndef __StarfishWebGL2RenderingContext__
#define __StarfishWebGL2RenderingContext__

#if defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)

#include "binding/ScriptWrappable.h"
#include "core/dom/canvas/webgl/WebGLObject.h"
#include "core/dom/canvas/webgl/WebGLRenderingContext.h"

namespace Starfish {

class Uint32ArrayOrSequenceOfGLuint;

class WebGLQuery : public WebGLObject {
public:
    void init(ScriptBindingInstance* instance, void* domObjectPointer) override;
    bool isWebGLQuery() const override;
};

class WebGLSampler : public WebGLObject {
public:
    void init(ScriptBindingInstance* instance, void* domObjectPointer) override;
    bool isWebGLSampler() const override;
};

class WebGLSync : public WebGLObject {
public:
    void init(ScriptBindingInstance* instance, void* domObjectPointer) override;
    bool isWebGLSync() const override;
};

class WebGLTransformFeedback : public WebGLObject {
public:
    void init(ScriptBindingInstance* instance, void* domObjectPointer) override;
    bool isWebGLTransformFeedback() const override;
};

class WebGLVertexArrayObject : public WebGLObject {
public:
    void init(ScriptBindingInstance* instance, void* domObjectPointer) override;
    bool isWebGLVertexArrayObject() const override;
};

class WebGL2RenderingContextBase : public ScriptWrappable {
public:
    void init(ScriptBindingInstance* instance, void* domObjectPointer);
    bool isWebGL2RenderingContextBase() const;

    /* Buffer objects */
    void copyBufferSubData(uint32_t&, uint32_t&, int64_t&, int64_t&, int64_t&){}
    void getBufferSubData(uint32_t&, int64_t&, Escargot::ArrayBufferViewRef*&, uint64_t&, uint32_t&){}

    /* Framebuffer objects */
    void blitFramebuffer(int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&){}
    void framebufferTextureLayer(uint32_t&, uint32_t&, Optional<WebGLTexture*>&, int32_t&, int32_t&){}
    void invalidateFramebuffer(uint32_t&, GCAtomicVector<unsigned int>&){}
    void invalidateSubFramebuffer(uint32_t&, GCAtomicVector<unsigned int>&, int32_t&, int32_t&, int32_t&, int32_t&){}
    void readBuffer(uint32_t&){}

    /* Renderbuffer objects */
    ScriptValue getInternalformatParameter(uint32_t&, uint32_t&, uint32_t&){ /* INDIGO_TODO */ return scriptNull(); }
    void renderbufferStorageMultisample(uint32_t&, int32_t&, uint32_t&, int32_t&, int32_t&){}

    /* Texture objects */
    void texStorage2D(uint32_t&, int32_t&, uint32_t&, int32_t&, int32_t&){}
    void texStorage3D(uint32_t&, int32_t&, uint32_t&, int32_t&, int32_t&, int32_t&){}

    void texImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&){}
    void texImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&){}
    void texImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&){}
    void texImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, int64_t&){}

    void texSubImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&){}
    void texSubImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&){}
    void texSubImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, int64_t&){}

    void copyTexSubImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&){}

    void compressedTexImage3D(uint32_t&, int32_t&, uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&, uint32_t&){}
    void compressedTexImage3D(uint32_t&, int32_t&, uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int64_t&){}

    void compressedTexSubImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&, uint32_t&){}
    void compressedTexSubImage3D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, int32_t&, int64_t&){}

    /* Programs and shaders */
    GLint getFragDataLocation(WebGLProgram*&, String*&){ /* INDIGO_TODO */ return 0; }

    /* Uniforms */
    void uniform1ui(Optional<WebGLUniformLocation*>&, uint32_t&){}
    void uniform2ui(Optional<WebGLUniformLocation*>&, uint32_t&, uint32_t&){}
    void uniform3ui(Optional<WebGLUniformLocation*>&, uint32_t&, uint32_t&, uint32_t&){}
    void uniform4ui(Optional<WebGLUniformLocation*>&, uint32_t&, uint32_t&, uint32_t&, uint32_t&){}

    void uniform1uiv(Optional<WebGLUniformLocation*>&, Uint32ArrayOrSequenceOfGLuint&, uint64_t&, uint32_t&){}
    void uniform2uiv(Optional<WebGLUniformLocation*>&, Uint32ArrayOrSequenceOfGLuint&, uint64_t&, uint32_t&){}
    void uniform3uiv(Optional<WebGLUniformLocation*>&, Uint32ArrayOrSequenceOfGLuint&, uint64_t&, uint32_t&){}
    void uniform4uiv(Optional<WebGLUniformLocation*>&, Uint32ArrayOrSequenceOfGLuint&, uint64_t&, uint32_t&){}
    void uniformMatrix3x2fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniformMatrix4x2fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}

    void uniformMatrix2x3fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniformMatrix4x3fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}

    void uniformMatrix2x4fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniformMatrix3x4fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}

    /* Vertex attribs */
    void vertexAttribI4i(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&){}
    void vertexAttribI4iv(uint32_t&, Int32ArrayOrSequenceOfGLint&){}
    void vertexAttribI4ui(uint32_t&, uint32_t&, uint32_t&, uint32_t&, uint32_t&){}
    void vertexAttribI4uiv(uint32_t&, Uint32ArrayOrSequenceOfGLuint&){}
    void vertexAttribIPointer(uint32_t&, int32_t&, uint32_t&, int32_t&, int64_t&){}

    /* Writing to the drawing buffer */
    void vertexAttribDivisor(uint32_t&, uint32_t&){}
    void drawArraysInstanced(uint32_t&, int32_t&, int32_t&, int32_t&){}
    void drawElementsInstanced(uint32_t&, int32_t&, uint32_t&, int64_t&, int32_t&){}
    void drawRangeElements(uint32_t&, uint32_t&, uint32_t&, int32_t&, uint32_t&, int64_t&){}

    /* Multiple Render Targets */
    void drawBuffers(GCAtomicVector<unsigned int>&){}

    void clearBufferfv(uint32_t&, int32_t&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&){}
    void clearBufferiv(uint32_t&, int32_t&, Int32ArrayOrSequenceOfGLint&, uint64_t&){}
    void clearBufferuiv(uint32_t&, int32_t&, Uint32ArrayOrSequenceOfGLuint&, uint64_t&){}

    void clearBufferfi(uint32_t&, int32_t&, double&, int32_t&){}

    /* Query Objects */
    Optional<WebGLQuery*> createQuery(){ /* INDIGO_TODO */ return nullptr; }
    void deleteQuery(Optional<WebGLQuery*>&){}
    GLboolean isQuery(Optional<WebGLQuery*>&){ /* INDIGO_TODO */ return false; }
    void beginQuery(uint32_t&, WebGLQuery*&){}
    void endQuery(uint32_t&){}
    Optional<WebGLQuery*> getQuery(uint32_t&, uint32_t&){ /* INDIGO_TODO */ return nullptr; }
    ScriptValue getQueryParameter(WebGLQuery*&, uint32_t&){ /* INDIGO_TODO */ return scriptNull(); }

    /* Sampler Objects */
    Optional<WebGLSampler*> createSampler(){ /* INDIGO_TODO */ return nullptr; }
    void deleteSampler(Optional<WebGLSampler*>&){}
    GLboolean isSampler(Optional<WebGLSampler*>&){ /* INDIGO_TODO */ return false; }
    void bindSampler(uint32_t&, Optional<WebGLSampler*>&){}
    void samplerParameteri(WebGLSampler*&, uint32_t&, int32_t&){}
    void samplerParameterf(WebGLSampler*&, uint32_t&, double&){}
    ScriptValue getSamplerParameter(WebGLSampler*&, uint32_t&){ /* INDIGO_TODO */ return scriptNull(); }

    /* Sync objects */
    Optional<WebGLSync*> fenceSync(uint32_t&, uint32_t&){ /* INDIGO_TODO */ return nullptr; }
    GLboolean isSync(Optional<WebGLSync*>&){ /* INDIGO_TODO */ return false; }
    void deleteSync(Optional<WebGLSync*>&){}
    GLenum clientWaitSync(WebGLSync*&, uint32_t&, uint64_t&){ /* INDIGO_TODO */ return 0; }
    void waitSync(WebGLSync*&, uint32_t&, int64_t&){}
    ScriptValue getSyncParameter(WebGLSync*&, uint32_t&){ /* INDIGO_TODO */ return scriptNull(); }

    /* Transform Feedback */
    Optional<WebGLTransformFeedback*> createTransformFeedback(){ /* INDIGO_TODO */ return nullptr; }
    void deleteTransformFeedback(Optional<WebGLTransformFeedback*>&){}
    GLboolean isTransformFeedback(Optional<WebGLTransformFeedback*>&){ /* INDIGO_TODO */ return false; }
    void bindTransformFeedback(uint32_t&, Optional<WebGLTransformFeedback*>&){}
    void beginTransformFeedback(uint32_t&){}
    void endTransformFeedback(){}
    void transformFeedbackVaryings(WebGLProgram*&, GCVector<String*>&, uint32_t&){}
    Optional<WebGLActiveInfo*> getTransformFeedbackVarying(WebGLProgram*&, uint32_t&){ /* INDIGO_TODO */ return nullptr; }
    void pauseTransformFeedback(){}
    void resumeTransformFeedback(){}

    /* Uniform Buffer Objects and Transform Feedback Buffers */
    void bindBufferBase(uint32_t&, uint32_t&, Optional<WebGLBuffer*>&){}
    void bindBufferRange(uint32_t&, uint32_t&, Optional<WebGLBuffer*>&, int64_t&, int64_t&){}
    ScriptValue getIndexedParameter(uint32_t&, uint32_t&){ /* INDIGO_TODO */ return scriptNull(); }
    Optional<GCAtomicVector<GLuint>> getUniformIndices(WebGLProgram*&, GCVector<String*>&){ /* INDIGO_TODO */ return nullptr; }
    ScriptValue getActiveUniforms(WebGLProgram*&, GCAtomicVector<unsigned int>&, uint32_t&){ /* INDIGO_TODO */ return scriptNull(); }
    GLuint getUniformBlockIndex(WebGLProgram*&, String*&){ /* INDIGO_TODO */ return 0; }
    ScriptValue getActiveUniformBlockParameter(WebGLProgram*&, uint32_t&, uint32_t&){ /* INDIGO_TODO */ return scriptNull(); }
    Optional<String*> getActiveUniformBlockName(WebGLProgram*&, uint32_t&){ /* INDIGO_TODO */ return nullptr; }
    void uniformBlockBinding(WebGLProgram*&, uint32_t&, uint32_t&){}

    /* Vertex Array Objects */
    Optional<WebGLVertexArrayObject*> createVertexArray(){ /* INDIGO_TODO */ return nullptr; }
    void deleteVertexArray(Optional<WebGLVertexArrayObject*>&){}
    GLboolean isVertexArray(Optional<WebGLVertexArrayObject*>&){ /* INDIGO_TODO */ return false; }
    void bindVertexArray(Optional<WebGLVertexArrayObject*>&){}
};

class WebGL2RenderingContextOverloads : public ScriptWrappable {
public:
    void init(ScriptBindingInstance* instance, void* domObjectPointer);
    bool isWebGL2RenderingContextOverloads() const;

    // WebGL1:
    void bufferData(uint32_t&, int64_t&, uint32_t&){}
    void bufferData(uint32_t&, Optional<ArrayBufferOrSharedArrayBufferOrArrayBufferView>&, uint32_t&){}
    void bufferSubData(uint32_t&, int64_t&, ArrayBufferOrSharedArrayBufferOrArrayBufferView&){}
    // WebGL2:
    void bufferData(uint32_t&, Escargot::ArrayBufferViewRef*&, uint32_t&, uint64_t&, uint32_t&){}
    void bufferSubData(uint32_t&, int64_t&, Escargot::ArrayBufferViewRef*&, uint64_t&, uint32_t&){}
    // WebGL1 legacy entrypoints:
    void texImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&){}
    void texImage2D(uint32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&){}

    void texSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&){}
    void texSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&){}

    // WebGL2 entrypoints:
    void texImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, int64_t&){}
    void texImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&){}
    void texImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&){}

    void texSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, int64_t&){}
    void texSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&){}
    void texSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&){}

    void compressedTexImage2D(uint32_t&, int32_t&, uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int64_t&){}
    void compressedTexImage2D(uint32_t&, int32_t&, uint32_t&, int32_t&, int32_t&, int32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&, uint32_t&){}

    void compressedTexSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, int32_t&, int64_t&){}
    void compressedTexSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&, uint32_t&){}

    void uniform1fv(Optional<WebGLUniformLocation*>&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniform2fv(Optional<WebGLUniformLocation*>&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniform3fv(Optional<WebGLUniformLocation*>&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniform4fv(Optional<WebGLUniformLocation*>&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}

    void uniform1iv(Optional<WebGLUniformLocation*>&, Int32ArrayOrSequenceOfGLint&, uint64_t&, uint32_t&){}
    void uniform2iv(Optional<WebGLUniformLocation*>&, Int32ArrayOrSequenceOfGLint&, uint64_t&, uint32_t&){}
    void uniform3iv(Optional<WebGLUniformLocation*>&, Int32ArrayOrSequenceOfGLint&, uint64_t&, uint32_t&){}
    void uniform4iv(Optional<WebGLUniformLocation*>&, Int32ArrayOrSequenceOfGLint&, uint64_t&, uint32_t&){}

    void uniformMatrix2fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniformMatrix3fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniformMatrix4fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}

    /* Reading back pixels */
    // WebGL1:
    void readPixels(int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&){}
    // WebGL2:
    void readPixels(int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, int64_t&){}
    void readPixels(int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&){}
};

class WebGL2RenderingContext : public WebGLRenderingContext,
                               public WebGL2RenderingContextBase,
                               public WebGL2RenderingContextOverloads {
public:
    // WebGL1:
    void bufferData(uint32_t&, int64_t&, uint32_t&){}
    void bufferData(uint32_t&, Optional<ArrayBufferOrSharedArrayBufferOrArrayBufferView>&, uint32_t&){}
    void bufferSubData(uint32_t&, int64_t&, ArrayBufferOrSharedArrayBufferOrArrayBufferView&){}
    // WebGL2:
    void bufferData(uint32_t&, Escargot::ArrayBufferViewRef*&, uint32_t&, uint64_t&, uint32_t&){}
    void bufferSubData(uint32_t&, int64_t&, Escargot::ArrayBufferViewRef*&, uint64_t&, uint32_t&){}
    // WebGL1 legacy entrypoints:
    void texImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&){}
    void texImage2D(uint32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&){}

    void texSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&){}
    void texSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&){}

    // WebGL2 entrypoints:
    void texImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, int64_t&){}
    void texImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&){}
    void texImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&){}

    void texSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, int64_t&){}
    void texSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&){}
    void texSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&){}

    void compressedTexImage2D(uint32_t&, int32_t&, uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int64_t&){}
    void compressedTexImage2D(uint32_t&, int32_t&, uint32_t&, int32_t&, int32_t&, int32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&, uint32_t&){}

    void compressedTexSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, int32_t&, int64_t&){}
    void compressedTexSubImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&, uint32_t&){}

    void uniform1fv(Optional<WebGLUniformLocation*>&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniform2fv(Optional<WebGLUniformLocation*>&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniform3fv(Optional<WebGLUniformLocation*>&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniform4fv(Optional<WebGLUniformLocation*>&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}

    void uniform1iv(Optional<WebGLUniformLocation*>&, Int32ArrayOrSequenceOfGLint&, uint64_t&, uint32_t&){}
    void uniform2iv(Optional<WebGLUniformLocation*>&, Int32ArrayOrSequenceOfGLint&, uint64_t&, uint32_t&){}
    void uniform3iv(Optional<WebGLUniformLocation*>&, Int32ArrayOrSequenceOfGLint&, uint64_t&, uint32_t&){}
    void uniform4iv(Optional<WebGLUniformLocation*>&, Int32ArrayOrSequenceOfGLint&, uint64_t&, uint32_t&){}

    void uniformMatrix2fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniformMatrix3fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}
    void uniformMatrix4fv(Optional<WebGLUniformLocation*>&, bool&, Float32ArrayOrSequenceOfGLfloat&, uint64_t&, uint32_t&){}

    /* Reading back pixels */
    // WebGL1:
    void readPixels(int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&){}
    // WebGL2:
    void readPixels(int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, int64_t&){}
    void readPixels(int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&){}
};

} // namespace Starfish

#endif // defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)

#endif // __StarfishWebGL2RenderingContext__
