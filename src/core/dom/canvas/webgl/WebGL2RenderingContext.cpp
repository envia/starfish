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

#if defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)

#include "StarfishConfig.h"
#include "core/dom/canvas/webgl/WebGL2RenderingContext.h"
#include "core/dom/ExecutionContext.h"
#include "core/util/debug/Trace.h"
#include "binding/generated/Float32ArrayOrSequenceOfGLfloatUnion.h"
#include "binding/generated/Int32ArrayOrSequenceOfGLintUnion.h"
#include "binding/generated/ArrayBufferOrSharedArrayBufferOrArrayBufferViewUnion.h"
#include "binding/generated/ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElementUnion.h"
#include "binding/generated/Uint32ArrayOrSequenceOfGLuintUnion.h"

#include "platform/canvas/gl/IncludeGL.h"
#include "platform/canvas/gl/GL.h"

#include <EscargotPublic.h>

namespace Starfish {

WebGLQuery::WebGLQuery(ScriptBindingInstance* instance,
                       WebGLRenderingContext* context, GLuint object)
    : WebGLObject(instance, context, object)
{
}

WebGLSampler::WebGLSampler(ScriptBindingInstance* instance,
                           WebGLRenderingContext* context, GLuint object)
    : WebGLObject(instance, context, object)
{
}

WebGLTransformFeedback::WebGLTransformFeedback(ScriptBindingInstance* instance,
                                               WebGLRenderingContext* context,
                                               GLuint object)
    : WebGLObject(instance, context, object)
{
}

WebGLVertexArrayObject::WebGLVertexArrayObject(ScriptBindingInstance* instance,
                                               WebGLRenderingContext* context,
                                               GLuint object)
    : WebGLObject(instance, context, object)
{
}

WebGL2RenderingContext::WebGL2RenderingContext(HTMLCanvasElement* canvasElement)
    : WebGLRenderingContext(canvasElement)
{
}

WebGL2RenderingContext::~WebGL2RenderingContext()
{
}

ScriptBindingInstance* WebGL2RenderingContext::scriptBindingInstance()
{
    return executionContext()->scriptBindingInstance();
}

// WebGLRenderingContextBase

#define ENTER_CONTEXT_SCOPE_IMPL(bailoutValue, ...) \
    GLContextScope contextScope_(m_context);        \
    if (contextScope_.hasError()) {                 \
        TRACE(WEBGL,                                \
              "\033[33m"                            \
              "GL Context error detected."          \
              "\033[0m");                           \
        return bailoutValue;                        \
    }

#if defined(NDEBUG) and !defined(ENABLE_TRACE)
#define ENTER_CONTEXT_SCOPE(bailoutValue, ...) \
    ENTER_CONTEXT_SCOPE_IMPL(bailoutValue);
#else
#define ENTER_CONTEXT_SCOPE(bailoutValue, ...)       \
    ENTER_CONTEXT_SCOPE_IMPL(bailoutValue);          \
    auto onScopeLeave = OnScopeLeave::create([&]() { \
        if (hasGLError()) {                          \
            TRACE(WEBGL,                             \
                  "\033[33m"                         \
                  "GL error detected."               \
                  "\033[0m");                        \
        }                                            \
    });
#endif

ScriptValue WebGL2RenderingContext::getParameter(GLenum pname)
{
    STARFISH_LOG_WARN("WebGL2RenderingContext::getParameter()");
    {
        ENTER_CONTEXT_SCOPE(scriptNull());

        switch (pname) {
        case GL_MAX_3D_TEXTURE_SIZE: {
            std::vector<int> values(1);
            gl()->getIntegerv(pname, &values[0]);
            STARFISH_LOG_WARN("INDIGO_TEMP: MAX_3D_TEXTURE_SIZE=%d", values[0]);
            return Escargot::ValueRef::create(values[0]);
        }
        case GL_MAX_COLOR_ATTACHMENTS: {
            std::vector<int> values(1);
            gl()->getIntegerv(pname, &values[0]);
            STARFISH_LOG_WARN("INDIGO_TEMP: MAX_COLOR_ATTACHMENTS=%d",
                              values[0]);
            return Escargot::ValueRef::create(values[0]);
        }
        case GL_MAX_COMBINED_UNIFORM_BLOCKS: {
            std::vector<int> values(1);
            gl()->getIntegerv(pname, &values[0]);
            STARFISH_LOG_WARN("INDIGO_TEMP: MAX_COMBINED_UNIFORM_BLOCKS=%d",
                              values[0]);
            return Escargot::ValueRef::create(values[0]);
        }
        case GL_MAX_DRAW_BUFFERS: {
            std::vector<int> values(1);
            gl()->getIntegerv(pname, &values[0]);
            STARFISH_LOG_WARN("INDIGO_TEMP: MAX_DRAW_BUFFERS=%d", values[0]);
            return Escargot::ValueRef::create(values[0]);
        }
        case GL_MAX_FRAGMENT_INPUT_COMPONENTS: {
            std::vector<int> values(1);
            gl()->getIntegerv(pname, &values[0]);
            STARFISH_LOG_WARN("INDIGO_TEMP: MAX_FRAGMENT_INPUT_COMPONENTS=%d",
                              values[0]);
            return Escargot::ValueRef::create(values[0]);
        }

        case GL_MAX_UNIFORM_BUFFER_BINDINGS: {
            std::vector<int> values(1);
            gl()->getIntegerv(pname, &values[0]);
            STARFISH_LOG_WARN("INDIGO_TEMP: MAX_UNIFORM_BUFFER_BINDINGS=%d",
                              values[0]);
            return Escargot::ValueRef::create(values[0]);
        }

        case GL_MAX_VERTEX_UNIFORM_BLOCKS: {
            std::vector<int> values(1);
            gl()->getIntegerv(pname, &values[0]);
            STARFISH_LOG_WARN("INDIGO_TEMP: MAX_VERTEX_UNIFORM_BLOCKS=%d",
                              values[0]);
            return Escargot::ValueRef::create(values[0]);
        }
        }
    }
    return WebGLRenderingContext::getParameter(pname);
}

// WebGL2RenderingContextBase

void WebGL2RenderingContext::copyBufferSubData(GLenum readTarget,
                                               GLenum writeTarget,
                                               GLintptr readOffset,
                                               GLintptr writeOffset,
                                               GLsizeiptr size)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::getBufferSubData(GLenum target,
                                              GLintptr srcByteOffset,
                                              ScriptArrayBufferView dstBuffer,
                                              unsigned long long dstOffset,
                                              GLuint length)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::blitFramebuffer(GLint srcX0, GLint srcY0,
                                             GLint srcX1, GLint srcY1,
                                             GLint dstX0, GLint dstY0,
                                             GLint dstX1, GLint dstY1,
                                             GLbitfield mask, GLenum filter)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::framebufferTextureLayer(
    GLenum target, GLenum attachment, Optional<WebGLTexture*> texture,
    GLint level, GLint layer)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::invalidateFramebuffer(
    GLenum target, GCAtomicVector<GLenum> attachments)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::invalidateSubFramebuffer(
    GLenum target, GCAtomicVector<GLenum> attachments, GLint x, GLint y,
    GLsizei width, GLsizei height)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::readBuffer(GLenum src)
{
    STARFISH_UNIMPLEMENTED();
}

ScriptValue WebGL2RenderingContext::getInternalformatParameter(
    GLenum target, GLenum internalformat, GLenum pname)
{
    STARFISH_UNIMPLEMENTED();
    return scriptNull();
}

void WebGL2RenderingContext::renderbufferStorageMultisample(
    GLenum target, GLsizei samples, GLenum internalformat, GLsizei width,
    GLsizei height)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::texStorage2D(GLenum target, GLsizei levels,
                                          GLenum internalformat, GLsizei width,
                                          GLsizei height)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::texStorage3D(GLenum target, GLsizei levels,
                                          GLenum internalformat, GLsizei width,
                                          GLsizei height, GLsizei depth)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::texImage3D(GLenum target, GLint level,
                                        GLint internalformat, GLsizei width,
                                        GLsizei height, GLsizei depth,
                                        GLint border, GLenum format,
                                        GLenum type, GLintptr pboOffset)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::texImage3D(GLenum target, GLint level,
                                        GLint internalformat, GLsizei width,
                                        GLsizei height, GLsizei depth,
                                        GLint border, GLenum format,
                                        GLenum type, TexImageSource source)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::texImage3D(GLenum target, GLint level,
                                        GLint internalformat, GLsizei width,
                                        GLsizei height, GLsizei depth,
                                        GLint border, GLenum format,
                                        GLenum type,
                                        ScriptArrayBufferView srcData)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::texImage3D(
    GLenum target, GLint level, GLint internalformat, GLsizei width,
    GLsizei height, GLsizei depth, GLint border, GLenum format, GLenum type,
    ScriptArrayBufferView srcData, unsigned long long srcOffset)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::texSubImage3D(GLenum target, GLint level,
                                           GLint xoffset, GLint yoffset,
                                           GLint zoffset, GLsizei width,
                                           GLsizei height, GLsizei depth,
                                           GLenum format, GLenum type,
                                           GLintptr pboOffset)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::texSubImage3D(GLenum target, GLint level,
                                           GLint xoffset, GLint yoffset,
                                           GLint zoffset, GLsizei width,
                                           GLsizei height, GLsizei depth,
                                           GLenum format, GLenum type,
                                           TexImageSource source)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::texSubImage3D(
    GLenum target, GLint level, GLint xoffset, GLint yoffset, GLint zoffset,
    GLsizei width, GLsizei height, GLsizei depth, GLenum format, GLenum type,
    ScriptArrayBufferView srcData, unsigned long long srcOffset)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::copyTexSubImage3D(GLenum target, GLint level,
                                               GLint xoffset, GLint yoffset,
                                               GLint zoffset, GLint x, GLint y,
                                               GLsizei width, GLsizei height)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::compressedTexImage3D(GLenum target, GLint level,
                                                  GLenum internalformat,
                                                  GLsizei width, GLsizei height,
                                                  GLsizei depth, GLint border,
                                                  GLsizei imageSize,
                                                  GLintptr offset)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::compressedTexImage3D(
    GLenum target, GLint level, GLenum internalformat, GLsizei width,
    GLsizei height, GLsizei depth, GLint border, ScriptArrayBufferView srcData,
    unsigned long long srcOffset, GLuint srcLengthOverride)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::compressedTexSubImage3D(
    GLenum target, GLint level, GLint xoffset, GLint yoffset, GLint zoffset,
    GLsizei width, GLsizei height, GLsizei depth, GLenum format,
    GLsizei imageSize, GLintptr offset)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::compressedTexSubImage3D(
    GLenum target, GLint level, GLint xoffset, GLint yoffset, GLint zoffset,
    GLsizei width, GLsizei height, GLsizei depth, GLenum format,
    ScriptArrayBufferView srcData, unsigned long long srcOffset,
    GLuint srcLengthOverride)
{
    STARFISH_UNIMPLEMENTED();
}

GLint WebGL2RenderingContext::getFragDataLocation(WebGLProgram* program,
                                                  String* name)
{
    STARFISH_UNIMPLEMENTED();
    return 0;
}

void WebGL2RenderingContext::uniform1ui(
    Optional<WebGLUniformLocation*> location, GLuint v0)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniform2ui(
    Optional<WebGLUniformLocation*> location, GLuint v0, GLuint v1)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniform3ui(
    Optional<WebGLUniformLocation*> location, GLuint v0, GLuint v1, GLuint v2)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniform4ui(
    Optional<WebGLUniformLocation*> location, GLuint v0, GLuint v1, GLuint v2,
    GLuint v3)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniform1uiv(
    Optional<WebGLUniformLocation*> location, Uint32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniform2uiv(
    Optional<WebGLUniformLocation*> location, Uint32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniform3uiv(
    Optional<WebGLUniformLocation*> location, Uint32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniform4uiv(
    Optional<WebGLUniformLocation*> location, Uint32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniformMatrix3x2fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniformMatrix4x2fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniformMatrix2x3fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniformMatrix4x3fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniformMatrix2x4fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniformMatrix3x4fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::vertexAttribI4i(GLuint index, GLint x, GLint y,
                                             GLint z, GLint w)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::vertexAttribI4iv(GLuint index, Int32List values)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::vertexAttribI4ui(GLuint index, GLuint x, GLuint y,
                                              GLuint z, GLuint w)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::vertexAttribI4uiv(GLuint index, Uint32List values)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::vertexAttribIPointer(GLuint index, GLint size,
                                                  GLenum type, GLsizei stride,
                                                  GLintptr offset)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::vertexAttribDivisor(GLuint index, GLuint divisor)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::drawArraysInstanced(GLenum mode, GLint first,
                                                 GLsizei count,
                                                 GLsizei instanceCount)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::drawElementsInstanced(GLenum mode, GLsizei count,
                                                   GLenum type, GLintptr offset,
                                                   GLsizei instanceCount)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::drawRangeElements(GLenum mode, GLuint start,
                                               GLuint end, GLsizei count,
                                               GLenum type, GLintptr offset)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::drawBuffers(GCAtomicVector<GLenum> buffers)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::clearBufferfv(GLenum buffer, GLint drawbuffer,
                                           Float32List values,
                                           unsigned long long srcOffset)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::clearBufferiv(GLenum buffer, GLint drawbuffer,
                                           Int32List values,
                                           unsigned long long srcOffset)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::clearBufferuiv(GLenum buffer, GLint drawbuffer,
                                            Uint32List values,
                                            unsigned long long srcOffset)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::clearBufferfi(GLenum buffer, GLint drawbuffer,
                                           GLfloat depth, GLint stencil)
{
    STARFISH_UNIMPLEMENTED();
}

WebGLQuery* WebGL2RenderingContext::createQuery()
{
    ENTER_CONTEXT_SCOPE(nullptr);

    GLuint query = 0;
    gl()->genQueries(1, &query);
    return new WebGLQuery(scriptBindingInstance(), this, query);
}

void WebGL2RenderingContext::deleteQuery(Optional<WebGLQuery*> query)
{
    STARFISH_UNIMPLEMENTED();
}

GLboolean WebGL2RenderingContext::isQuery(Optional<WebGLQuery*> query)
{
    STARFISH_UNIMPLEMENTED();
    return false;
}

void WebGL2RenderingContext::beginQuery(GLenum target, WebGLQuery* query)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::endQuery(GLenum target)
{
    STARFISH_UNIMPLEMENTED();
}

Optional<WebGLQuery*> WebGL2RenderingContext::getQuery(GLenum target,
                                                       GLenum pname)
{
    STARFISH_UNIMPLEMENTED();
    return nullptr;
}

ScriptValue WebGL2RenderingContext::getQueryParameter(WebGLQuery* query,
                                                      GLenum pname)
{
    STARFISH_UNIMPLEMENTED();
    return scriptNull();
}

WebGLSampler* WebGL2RenderingContext::createSampler()
{
    ENTER_CONTEXT_SCOPE(nullptr);

    GLuint sampler = 0;
    gl()->genSamplers(1, &sampler);
    return new WebGLSampler(scriptBindingInstance(), this, sampler);
}

void WebGL2RenderingContext::deleteSampler(Optional<WebGLSampler*> sampler)
{
    STARFISH_UNIMPLEMENTED();
}

GLboolean WebGL2RenderingContext::isSampler(Optional<WebGLSampler*> sampler)
{
    STARFISH_UNIMPLEMENTED();
    return false;
}

void WebGL2RenderingContext::bindSampler(GLuint unit,
                                         Optional<WebGLSampler*> sampler)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::samplerParameteri(WebGLSampler* sampler,
                                               GLenum pname, GLint param)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::samplerParameterf(WebGLSampler* sampler,
                                               GLenum pname, GLfloat param)
{
    STARFISH_UNIMPLEMENTED();
}

ScriptValue WebGL2RenderingContext::getSamplerParameter(WebGLSampler* sampler,
                                                        GLenum pname)
{
    STARFISH_UNIMPLEMENTED();
    return scriptNull();
}

Optional<WebGLSync*> WebGL2RenderingContext::fenceSync(GLenum condition,
                                                       GLbitfield flags)
{
    STARFISH_UNIMPLEMENTED();
    return nullptr;
}

GLboolean WebGL2RenderingContext::isSync(Optional<WebGLSync*> sync)
{
    STARFISH_UNIMPLEMENTED();
    return false;
}

void WebGL2RenderingContext::deleteSync(Optional<WebGLSync*> sync)
{
    STARFISH_UNIMPLEMENTED();
}

GLenum WebGL2RenderingContext::clientWaitSync(WebGLSync* sync, GLbitfield flags,
                                              GLuint64 timeout)
{
    STARFISH_UNIMPLEMENTED();
    return 0;
}

void WebGL2RenderingContext::waitSync(WebGLSync* sync, GLbitfield flags,
                                      GLint64 timeout)
{
    STARFISH_UNIMPLEMENTED();
}

ScriptValue WebGL2RenderingContext::getSyncParameter(WebGLSync* sync,
                                                     GLenum pname)
{
    STARFISH_UNIMPLEMENTED();
    return scriptNull();
}

WebGLTransformFeedback* WebGL2RenderingContext::createTransformFeedback()
{
    ENTER_CONTEXT_SCOPE(nullptr);

    GLuint tf = 0;
    gl()->genTransformFeedback(1, &tf);
    return new WebGLTransformFeedback(scriptBindingInstance(), this, tf);
}

void WebGL2RenderingContext::deleteTransformFeedback(
    Optional<WebGLTransformFeedback*> tf)
{
    STARFISH_UNIMPLEMENTED();
}

GLboolean WebGL2RenderingContext::isTransformFeedback(
    Optional<WebGLTransformFeedback*> tf)
{
    STARFISH_UNIMPLEMENTED();
    return false;
}

void WebGL2RenderingContext::bindTransformFeedback(
    GLenum target, Optional<WebGLTransformFeedback*> tf)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::beginTransformFeedback(GLenum primitiveMode)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::endTransformFeedback()
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::transformFeedbackVaryings(
    WebGLProgram* program, GCVector<String*> varyings, GLenum bufferMode)
{
    STARFISH_UNIMPLEMENTED();
}

Optional<WebGLActiveInfo*> WebGL2RenderingContext::getTransformFeedbackVarying(
    WebGLProgram* program, GLuint index)
{
    STARFISH_UNIMPLEMENTED();
    return nullptr;
}

void WebGL2RenderingContext::pauseTransformFeedback()
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::resumeTransformFeedback()
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::bindBufferBase(GLenum target, GLuint index,
                                            Optional<WebGLBuffer*> buffer)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::bindBufferRange(GLenum target, GLuint index,
                                             Optional<WebGLBuffer*> buffer,
                                             GLintptr offset, GLsizeiptr size)
{
    STARFISH_UNIMPLEMENTED();
}

ScriptValue WebGL2RenderingContext::getIndexedParameter(GLenum target,
                                                        GLuint index)
{
    STARFISH_UNIMPLEMENTED();
    return scriptNull();
}

Optional<GCAtomicVector<GLuint>> WebGL2RenderingContext::getUniformIndices(
    WebGLProgram* program, GCVector<String*> uniformNames)
{
    STARFISH_UNIMPLEMENTED();
    return nullptr;
}

ScriptValue WebGL2RenderingContext::getActiveUniforms(
    WebGLProgram* program, GCAtomicVector<GLuint> uniformIndices, GLenum pname)
{
    STARFISH_UNIMPLEMENTED();
    return scriptNull();
}

GLuint WebGL2RenderingContext::getUniformBlockIndex(WebGLProgram* program,
                                                    String* uniformBlockName)
{
    STARFISH_UNIMPLEMENTED();
    return 0;
}

ScriptValue WebGL2RenderingContext::getActiveUniformBlockParameter(
    WebGLProgram* program, GLuint uniformBlockIndex, GLenum pname)
{
    STARFISH_UNIMPLEMENTED();
    return scriptNull();
}

Optional<String*> WebGL2RenderingContext::getActiveUniformBlockName(
    WebGLProgram* program, GLuint uniformBlockIndex)
{
    STARFISH_UNIMPLEMENTED();
    return nullptr;
}

void WebGL2RenderingContext::uniformBlockBinding(WebGLProgram* program,
                                                 GLuint uniformBlockIndex,
                                                 GLuint uniformBlockBinding)
{
    STARFISH_UNIMPLEMENTED();
}

WebGLVertexArrayObject* WebGL2RenderingContext::createVertexArray()
{
    ENTER_CONTEXT_SCOPE(nullptr);

    GLuint vao = 0;
    gl()->genVertexArrays(1, &vao);
    return new WebGLVertexArrayObject(scriptBindingInstance(), this, vao);
}

void WebGL2RenderingContext::deleteVertexArray(
    Optional<WebGLVertexArrayObject*> vertexArray)
{
    STARFISH_UNIMPLEMENTED();
}

GLboolean WebGL2RenderingContext::isVertexArray(
    Optional<WebGLVertexArrayObject*> vertexArray)
{
    STARFISH_UNIMPLEMENTED();
    return false;
}

void WebGL2RenderingContext::bindVertexArray(
    Optional<WebGLVertexArrayObject*> array)
{
    STARFISH_UNIMPLEMENTED();
}

// WebGL2RenderingContextOverloads

void WebGL2RenderingContext::bufferData(GLenum target, GLsizeiptr size,
                                        GLenum usage)
{
    WebGLRenderingContext::bufferData(target, size, usage);
}

void WebGL2RenderingContext::bufferData(
    GLenum target, Optional<AllowSharedBufferSource> srcData, GLenum usage)
{
    WebGLRenderingContext::bufferData(target, srcData, usage);
}

void WebGL2RenderingContext::bufferSubData(GLenum target,
                                           GLintptr dstByteOffset,
                                           AllowSharedBufferSource srcData)
{
    WebGLRenderingContext::bufferSubData(target, dstByteOffset, srcData);
}

void WebGL2RenderingContext::bufferData(GLenum target,
                                        ScriptArrayBufferView srcData,
                                        GLenum usage,
                                        unsigned long long srcOffset,
                                        GLuint length)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::bufferSubData(GLenum target,
                                           GLintptr dstByteOffset,
                                           ScriptArrayBufferView srcData,
                                           unsigned long long srcOffset,
                                           GLuint length)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::texImage2D(GLenum target, GLint level,
                                        GLint internalformat, GLsizei width,
                                        GLsizei height, GLint border,
                                        GLenum format, GLenum type,
                                        Optional<ScriptArrayBufferView> pixels)
{
    WebGLRenderingContext::texImage2D(target, level, internalformat, width,
                                      height, border, format, type, pixels);
}

void WebGL2RenderingContext::texImage2D(GLenum target, GLint level,
                                        GLint internalformat, GLenum format,
                                        GLenum type, TexImageSource source)
{
    WebGLRenderingContext::texImage2D(target, level, internalformat, format,
                                      type, source);
}

void WebGL2RenderingContext::texSubImage2D(
    GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width,
    GLsizei height, GLenum format, GLenum type,
    Optional<ScriptArrayBufferView> pixels)
{
    WebGLRenderingContext::texSubImage2D(target, level, xoffset, yoffset, width,
                                         height, format, type, pixels);
}

void WebGL2RenderingContext::texSubImage2D(GLenum target, GLint level,
                                           GLint xoffset, GLint yoffset,
                                           GLenum format, GLenum type,
                                           TexImageSource source)
{
    WebGLRenderingContext::texSubImage2D(target, level, xoffset, yoffset,
                                         format, type, source);
}

void WebGL2RenderingContext::texImage2D(GLenum target, GLint level,
                                        GLint internalformat, GLsizei width,
                                        GLsizei height, GLint border,
                                        GLenum format, GLenum type,
                                        GLintptr pboOffset)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::texImage2D(GLenum target, GLint level,
                                        GLint internalformat, GLsizei width,
                                        GLsizei height, GLint border,
                                        GLenum format, GLenum type,
                                        TexImageSource source)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::texImage2D(GLenum target, GLint level,
                                        GLint internalformat, GLsizei width,
                                        GLsizei height, GLint border,
                                        GLenum format, GLenum type,
                                        ScriptArrayBufferView srcData,
                                        unsigned long long srcOffset)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::texSubImage2D(GLenum target, GLint level,
                                           GLint xoffset, GLint yoffset,
                                           GLsizei width, GLsizei height,
                                           GLenum format, GLenum type,
                                           GLintptr pboOffset)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::texSubImage2D(GLenum target, GLint level,
                                           GLint xoffset, GLint yoffset,
                                           GLsizei width, GLsizei height,
                                           GLenum format, GLenum type,
                                           TexImageSource source)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::texSubImage2D(GLenum target, GLint level,
                                           GLint xoffset, GLint yoffset,
                                           GLsizei width, GLsizei height,
                                           GLenum format, GLenum type,
                                           ScriptArrayBufferView srcData,
                                           unsigned long long srcOffset)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::compressedTexImage2D(
    GLenum target, GLint level, GLenum internalformat, GLsizei width,
    GLsizei height, GLint border, GLsizei imageSize, GLintptr offset)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::compressedTexImage2D(
    GLenum target, GLint level, GLenum internalformat, GLsizei width,
    GLsizei height, GLint border, ScriptArrayBufferView srcData,
    unsigned long long srcOffset, GLuint srcLengthOverride)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::compressedTexSubImage2D(
    GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width,
    GLsizei height, GLenum format, GLsizei imageSize, GLintptr offset)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::compressedTexSubImage2D(
    GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width,
    GLsizei height, GLenum format, ScriptArrayBufferView srcData,
    unsigned long long srcOffset, GLuint srcLengthOverride)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniform1fv(
    Optional<WebGLUniformLocation*> location, Float32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniform2fv(
    Optional<WebGLUniformLocation*> location, Float32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniform3fv(
    Optional<WebGLUniformLocation*> location, Float32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniform4fv(
    Optional<WebGLUniformLocation*> location, Float32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniform1iv(
    Optional<WebGLUniformLocation*> location, Int32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniform2iv(
    Optional<WebGLUniformLocation*> location, Int32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniform3iv(
    Optional<WebGLUniformLocation*> location, Int32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniform4iv(
    Optional<WebGLUniformLocation*> location, Int32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniformMatrix2fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniformMatrix3fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::uniformMatrix4fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::readPixels(GLint x, GLint y, GLsizei width,
                                        GLsizei height, GLenum format,
                                        GLenum type,
                                        Optional<ScriptArrayBufferView> dstData)
{
    WebGLRenderingContext::readPixels(x, y, width, height, format, type,
                                      dstData);
}

void WebGL2RenderingContext::readPixels(GLint x, GLint y, GLsizei width,
                                        GLsizei height, GLenum format,
                                        GLenum type, GLintptr offset)
{
    STARFISH_UNIMPLEMENTED();
}

void WebGL2RenderingContext::readPixels(GLint x, GLint y, GLsizei width,
                                        GLsizei height, GLenum format,
                                        GLenum type,
                                        ScriptArrayBufferView dstData,
                                        unsigned long long dstOffset)
{
    STARFISH_UNIMPLEMENTED();
}

} // namespace Starfish

#endif // defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)
