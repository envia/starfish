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
#include "binding/generated/ArrayBufferOrSharedArrayBufferOrArrayBufferViewUnion.h"
#include "binding/generated/Float32ArrayOrSequenceOfGLfloatUnion.h"
#include "binding/generated/ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElementUnion.h"
#include "binding/generated/Int32ArrayOrSequenceOfGLintUnion.h"
#include "binding/generated/Uint32ArrayOrSequenceOfGLuintUnion.h"
#include "core/dom/ExecutionContext.h"
#include "core/util/debug/Trace.h"
#include "platform/canvas/gl/GL.h"
#include "platform/canvas/gl/IncludeGL.h"
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

WebGLSync::WebGLSync(ScriptBindingInstance* instance,
                     WebGLRenderingContext* context, GLsync object)
    : WebGLObject(instance, context, /* dummy */ 0)
    , m_glObject(object)
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

Optional<WebGLContextAttributes> WebGL2RenderingContext::getContextAttributes()
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getContextAttributes();
}

bool WebGL2RenderingContext::isContextLost()
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::isContextLost();
}

Optional<GCVector<String*>> WebGL2RenderingContext::getSupportedExtensions()
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getSupportedExtensions();
}

Optional<ScriptObject> WebGL2RenderingContext::getExtension(
    String* requestedName)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getExtension(requestedName);
}

void WebGL2RenderingContext::activeTexture(GLenum texture)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::activeTexture(texture);
}

void WebGL2RenderingContext::attachShader(WebGLProgram* program,
                                          WebGLShader* shader)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::attachShader(program, shader);
}

void WebGL2RenderingContext::bindAttribLocation(WebGLProgram* program,
                                                GLuint index, String* name)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::bindAttribLocation(program, index, name);
}

void WebGL2RenderingContext::bindBuffer(GLenum target,
                                        Optional<WebGLBuffer*> buffer)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::bindBuffer(target, buffer);
}

void WebGL2RenderingContext::bindFramebuffer(
    GLenum target, Optional<WebGLFramebuffer*> maybeFramebuffer)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::bindFramebuffer(target, maybeFramebuffer);
}

void WebGL2RenderingContext::bindRenderbuffer(
    GLenum target, Optional<WebGLRenderbuffer*> maybeRenderbuffer)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::bindRenderbuffer(target, maybeRenderbuffer);
}

void WebGL2RenderingContext::bindTexture(GLenum target,
                                         Optional<WebGLTexture*> maybeTexture)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::bindTexture(target, maybeTexture);
}

void WebGL2RenderingContext::blendColor(GLclampf red, GLclampf green,
                                        GLclampf blue, GLclampf alpha)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::blendColor(red, green, blue, alpha);
}

void WebGL2RenderingContext::blendEquation(GLenum mode)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::blendEquation(mode);
}

void WebGL2RenderingContext::blendEquationSeparate(GLenum modeRGB,
                                                   GLenum modeAlpha)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::blendEquationSeparate(modeRGB, modeAlpha);
}

void WebGL2RenderingContext::blendFunc(GLenum sfactor, GLenum dfactor)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::blendFunc(sfactor, dfactor);
}

void WebGL2RenderingContext::blendFuncSeparate(GLenum srcRGB, GLenum dstRGB,
                                               GLenum srcAlpha, GLenum dstAlpha)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::blendFuncSeparate(srcRGB, dstRGB, srcAlpha,
                                             dstAlpha);
}

GLenum WebGL2RenderingContext::checkFramebufferStatus(GLenum target)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::checkFramebufferStatus(target);
}

void WebGL2RenderingContext::clear(uint32_t mask)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::clear(mask);
}

void WebGL2RenderingContext::clearColor(float red, float green, float blue,
                                        float alpha)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::clearColor(red, green, blue, alpha);
}

void WebGL2RenderingContext::clearDepth(GLclampf depth)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::clearDepth(depth);
}

void WebGL2RenderingContext::clearStencil(GLint s)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::clearStencil(s);
}

void WebGL2RenderingContext::colorMask(GLboolean red, GLboolean green,
                                       GLboolean blue, GLboolean alpha)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::colorMask(red, green, blue, alpha);
}

void WebGL2RenderingContext::compileShader(WebGLShader* shader)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::compileShader(shader);
}

void WebGL2RenderingContext::copyTexImage2D(GLenum target, GLint level,
                                            GLenum internalformat, GLint x,
                                            GLint y, GLsizei width,
                                            GLsizei height, GLint border)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::copyTexImage2D(target, level, internalformat, x, y,
                                          width, height, border);
}

void WebGL2RenderingContext::copyTexSubImage2D(GLenum target, GLint level,
                                               GLint xoffset, GLint yoffset,
                                               GLint x, GLint y, GLsizei width,
                                               GLsizei height)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::copyTexSubImage2D(target, level, xoffset, yoffset, x,
                                             y, width, height);
}

WebGLBuffer* WebGL2RenderingContext::createBuffer()
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::createBuffer();
}

WebGLFramebuffer* WebGL2RenderingContext::createFramebuffer()
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::createFramebuffer();
}

WebGLProgram* WebGL2RenderingContext::createProgram()
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::createProgram();
}

WebGLRenderbuffer* WebGL2RenderingContext::createRenderbuffer()
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::createRenderbuffer();
}

WebGLShader* WebGL2RenderingContext::createShader(unsigned long type)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::createShader(type);
}

WebGLTexture* WebGL2RenderingContext::createTexture()
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::createTexture();
}

void WebGL2RenderingContext::cullFace(GLenum mode)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::cullFace(mode);
}

void WebGL2RenderingContext::deleteBuffer(Optional<WebGLBuffer*> buffer)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::deleteBuffer(buffer);
}

void WebGL2RenderingContext::deleteFramebuffer(
    Optional<WebGLFramebuffer*> framebuffer)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::deleteFramebuffer(framebuffer);
}

void WebGL2RenderingContext::deleteProgram(Optional<WebGLProgram*> program)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::deleteProgram(program);
}

void WebGL2RenderingContext::deleteRenderbuffer(
    Optional<WebGLRenderbuffer*> renderbuffer)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::deleteRenderbuffer(renderbuffer);
}

void WebGL2RenderingContext::deleteShader(Optional<WebGLShader*> shader)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::deleteShader(shader);
}

void WebGL2RenderingContext::deleteTexture(Optional<WebGLTexture*> texture)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::deleteTexture(texture);
}

void WebGL2RenderingContext::depthFunc(GLenum func)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::depthFunc(func);
}

void WebGL2RenderingContext::depthMask(GLboolean flag)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::depthMask(flag);
}

void WebGL2RenderingContext::depthRange(GLclampf zNear, GLclampf zFar)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::depthRange(zNear, zFar);
}

void WebGL2RenderingContext::detachShader(WebGLProgram* program,
                                          WebGLShader* shader)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::detachShader(program, shader);
}

void WebGL2RenderingContext::disable(GLenum cap)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::disable(cap);
}

void WebGL2RenderingContext::disableVertexAttribArray(GLuint index)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::disableVertexAttribArray(index);
}

void WebGL2RenderingContext::drawArrays(GLenum mode, GLint first, GLsizei count)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::drawArrays(mode, first, count);
}

void WebGL2RenderingContext::drawElements(GLenum mode, GLsizei count,
                                          GLenum type, GLintptr offset)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::drawElements(mode, count, type, offset);
}

void WebGL2RenderingContext::enable(GLenum cap)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::enable(cap);
}

void WebGL2RenderingContext::enableVertexAttribArray(GLuint index)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::enableVertexAttribArray(index);
}

void WebGL2RenderingContext::finish()
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::finish();
}

void WebGL2RenderingContext::flushWebGL()
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::flushWebGL();
}

void WebGL2RenderingContext::framebufferRenderbuffer(
    GLenum target, GLenum attachment, GLenum renderbuffertarget,
    Optional<WebGLRenderbuffer*> maybeRenderbuffer)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::framebufferRenderbuffer(
        target, attachment, renderbuffertarget, maybeRenderbuffer);
}

void WebGL2RenderingContext::framebufferTexture2D(
    GLenum target, GLenum attachment, GLenum textarget,
    Optional<WebGLTexture*> maybeTexture, GLint level)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::framebufferTexture2D(target, attachment, textarget,
                                                maybeTexture, level);
}

void WebGL2RenderingContext::frontFace(GLenum mode)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::frontFace(mode);
}

void WebGL2RenderingContext::generateMipmap(GLenum target)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::generateMipmap(target);
}

WebGLActiveInfo* WebGL2RenderingContext::getActiveAttrib(WebGLProgram* program,
                                                         GLuint index)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getActiveAttrib(program, index);
}

WebGLActiveInfo* WebGL2RenderingContext::getActiveUniform(WebGLProgram* program,
                                                          GLuint index)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getActiveUniform(program, index);
}

Optional<GCVector<WebGLShader*>> WebGL2RenderingContext::getAttachedShaders(
    WebGLProgram* program)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getAttachedShaders(program);
}

GLint WebGL2RenderingContext::getAttribLocation(WebGLProgram* program,
                                                String* name)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getAttribLocation(program, name);
}

ScriptValue WebGL2RenderingContext::getBufferParameter(GLenum target,
                                                       GLenum pname)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getBufferParameter(target, pname);
}

ScriptValue WebGL2RenderingContext::getParameter(GLenum pname)
{
    {
        ENTER_CONTEXT_SCOPE(scriptNull());

        switch (pname) {
        case GL_MAX_3D_TEXTURE_SIZE:
        case GL_MAX_ARRAY_TEXTURE_LAYERS:
        case GL_MAX_COLOR_ATTACHMENTS:
        case GL_MAX_COMBINED_UNIFORM_BLOCKS:
        case GL_MAX_DRAW_BUFFERS:
        case GL_MAX_ELEMENTS_INDICES:
        case GL_MAX_ELEMENTS_VERTICES:
        case GL_MAX_FRAGMENT_INPUT_COMPONENTS:
        case GL_MAX_FRAGMENT_UNIFORM_BLOCKS:
        case GL_MAX_FRAGMENT_UNIFORM_COMPONENTS:
        case GL_MAX_PROGRAM_TEXEL_OFFSET:
        case GL_MAX_SAMPLES:
        case GL_MAX_TRANSFORM_FEEDBACK_INTERLEAVED_COMPONENTS:
        case GL_MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS:
        case GL_MAX_TRANSFORM_FEEDBACK_SEPARATE_COMPONENTS:
        case GL_MAX_UNIFORM_BUFFER_BINDINGS:
        case GL_MAX_VARYING_COMPONENTS:
        case GL_MAX_VERTEX_OUTPUT_COMPONENTS:
        case GL_MAX_VERTEX_UNIFORM_BLOCKS:
        case GL_MAX_VERTEX_UNIFORM_COMPONENTS:
        case GL_MIN_PROGRAM_TEXEL_OFFSET:
        case GL_PACK_ROW_LENGTH:
        case GL_PACK_SKIP_PIXELS:
        case GL_PACK_SKIP_ROWS:
        case GL_UNIFORM_BUFFER_OFFSET_ALIGNMENT:
        case GL_UNPACK_IMAGE_HEIGHT:
        case GL_UNPACK_ROW_LENGTH:
        case GL_UNPACK_SKIP_IMAGES:
        case GL_UNPACK_SKIP_PIXELS:
        case GL_UNPACK_SKIP_ROWS: {
            std::vector<int> values(1);
            gl()->getIntegerv(pname, &values[0]);
            return Escargot::ValueRef::create(values[0]);
        }
        }
    }
    return WebGLRenderingContext::getParameter(pname);
}

GLenum WebGL2RenderingContext::getError()
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getError();
}

ScriptValue WebGL2RenderingContext::getFramebufferAttachmentParameter(
    GLenum target, GLenum attachment, GLenum pname)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getFramebufferAttachmentParameter(
        target, attachment, pname);
}

ScriptValue WebGL2RenderingContext::getProgramParameter(WebGLProgram* program,
                                                        GLenum pname)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getProgramParameter(program, pname);
}

String* WebGL2RenderingContext::getProgramInfoLog(WebGLProgram* program)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getProgramInfoLog(program);
}

ScriptValue WebGL2RenderingContext::getRenderbufferParameter(GLenum target,
                                                             GLenum pname)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getRenderbufferParameter(target, pname);
}

ScriptValue WebGL2RenderingContext::getShaderParameter(WebGLShader* shader,
                                                       GLenum pname)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getShaderParameter(shader, pname);
}

WebGLShaderPrecisionFormat* WebGL2RenderingContext::getShaderPrecisionFormat(
    GLenum shadertype, GLenum precisiontype)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getShaderPrecisionFormat(shadertype,
                                                           precisiontype);
}

String* WebGL2RenderingContext::getShaderInfoLog(WebGLShader* shader)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getShaderInfoLog(shader);
}

String* WebGL2RenderingContext::getShaderSource(WebGLShader* shader)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getShaderSource(shader);
}

ScriptValue WebGL2RenderingContext::getTexParameter(GLenum target, GLenum pname)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getTexParameter(target, pname);
}

ScriptValue WebGL2RenderingContext::getUniform(WebGLProgram* program,
                                               WebGLUniformLocation* location)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getUniform(program, location);
}

WebGLUniformLocation* WebGL2RenderingContext::getUniformLocation(
    WebGLProgram* program, String* name)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getUniformLocation(program, name);
}

ScriptValue WebGL2RenderingContext::getVertexAttrib(GLuint index, GLenum pname)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getVertexAttrib(index, pname);
}

GLintptr WebGL2RenderingContext::getVertexAttribOffset(GLuint index,
                                                       GLenum pname)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::getVertexAttribOffset(index, pname);
}

void WebGL2RenderingContext::hint(GLenum target, GLenum mode)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::hint(target, mode);
}

bool WebGL2RenderingContext::isBuffer(Optional<WebGLBuffer*> maybe)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::isBuffer(maybe);
}

bool WebGL2RenderingContext::isEnabled(GLenum cap)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::isEnabled(cap);
}

bool WebGL2RenderingContext::isFramebuffer(Optional<WebGLFramebuffer*> maybe)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::isFramebuffer(maybe);
}

bool WebGL2RenderingContext::isProgram(Optional<WebGLProgram*> maybe)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::isProgram(maybe);
}

bool WebGL2RenderingContext::isRenderbuffer(Optional<WebGLRenderbuffer*> maybe)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::isRenderbuffer(maybe);
}

bool WebGL2RenderingContext::isShader(Optional<WebGLShader*> maybe)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::isShader(maybe);
}

bool WebGL2RenderingContext::isTexture(Optional<WebGLTexture*> maybe)
{
    STARFISH_UNIMPLEMENTED();
    return WebGLRenderingContext::isTexture(maybe);
}

void WebGL2RenderingContext::lineWidth(GLfloat width)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::lineWidth(width);
}

void WebGL2RenderingContext::linkProgram(WebGLProgram* program)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::linkProgram(program);
}

void WebGL2RenderingContext::pixelStorei(GLenum pname, GLint param)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::pixelStorei(pname, param);
}

void WebGL2RenderingContext::polygonOffset(GLfloat factor, GLfloat units)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::polygonOffset(factor, units);
}

void WebGL2RenderingContext::renderbufferStorage(GLenum target,
                                                 GLenum internalformat,
                                                 GLsizei width, GLsizei height)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::renderbufferStorage(target, internalformat, width,
                                               height);
}

void WebGL2RenderingContext::sampleCoverage(GLclampf value, GLboolean invert)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::sampleCoverage(value, invert);
}

void WebGL2RenderingContext::scissor(GLint x, GLint y, GLsizei width,
                                     GLsizei height)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::scissor(x, y, width, height);
}

void WebGL2RenderingContext::shaderSource(WebGLShader* shader, String* source)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::shaderSource(shader, source);
}

void WebGL2RenderingContext::stencilFunc(GLenum func, GLint ref, GLuint mask)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::stencilFunc(func, ref, mask);
}

void WebGL2RenderingContext::stencilFuncSeparate(GLenum face, GLenum func,
                                                 GLint ref, GLuint mask)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::stencilFuncSeparate(face, func, ref, mask);
}

void WebGL2RenderingContext::stencilMask(GLuint mask)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::stencilMask(mask);
}

void WebGL2RenderingContext::stencilMaskSeparate(GLenum face, GLuint mask)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::stencilMaskSeparate(face, mask);
}

void WebGL2RenderingContext::stencilOp(GLenum fail, GLenum zfail, GLenum zpass)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::stencilOp(fail, zfail, zpass);
}

void WebGL2RenderingContext::stencilOpSeparate(GLenum face, GLenum fail,
                                               GLenum zfail, GLenum zpass)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::stencilOpSeparate(face, fail, zfail, zpass);
}

void WebGL2RenderingContext::texParameterf(GLenum target, GLenum pname,
                                           GLfloat param)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::texParameterf(target, pname, param);
}

void WebGL2RenderingContext::texParameteri(GLenum target, GLenum pname,
                                           GLint param)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::texParameteri(target, pname, param);
}

void WebGL2RenderingContext::uniform1f(
    Optional<WebGLUniformLocation*> maybeUniform, GLfloat x)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::uniform1f(maybeUniform, x);
}

void WebGL2RenderingContext::uniform2f(
    Optional<WebGLUniformLocation*> maybeUniform, GLfloat x, GLfloat y)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::uniform2f(maybeUniform, x, y);
}

void WebGL2RenderingContext::uniform3f(
    Optional<WebGLUniformLocation*> maybeUniform, GLfloat x, GLfloat y,
    GLfloat z)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::uniform3f(maybeUniform, x, y, z);
}

void WebGL2RenderingContext::uniform4f(
    Optional<WebGLUniformLocation*> maybeUniform, GLfloat x, GLfloat y,
    GLfloat z, GLfloat w)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::uniform4f(maybeUniform, x, y, z, w);
}

void WebGL2RenderingContext::uniform1i(
    Optional<WebGLUniformLocation*> maybeUniform, GLint x)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::uniform1i(maybeUniform, x);
}

void WebGL2RenderingContext::uniform2i(
    Optional<WebGLUniformLocation*> maybeUniform, GLint x, GLint y)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::uniform2i(maybeUniform, x, y);
}

void WebGL2RenderingContext::uniform3i(
    Optional<WebGLUniformLocation*> maybeUniform, GLint x, GLint y, GLint z)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::uniform3i(maybeUniform, x, y, z);
}

void WebGL2RenderingContext::uniform4i(
    Optional<WebGLUniformLocation*> maybeUniform, GLint x, GLint y, GLint z,
    GLint w)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::uniform4i(maybeUniform, x, y, z, w);
}

void WebGL2RenderingContext::useProgram(Optional<WebGLProgram*> maybeProgram)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::useProgram(maybeProgram);
}

void WebGL2RenderingContext::validateProgram(WebGLProgram* program)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::validateProgram(program);
}

void WebGL2RenderingContext::vertexAttrib1f(GLuint index, GLfloat x)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::vertexAttrib1f(index, x);
}

void WebGL2RenderingContext::vertexAttrib2f(GLuint index, GLfloat x, GLfloat y)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::vertexAttrib2f(index, x, y);
}

void WebGL2RenderingContext::vertexAttrib3f(GLuint index, GLfloat x, GLfloat y,
                                            GLfloat z)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::vertexAttrib3f(index, x, y, z);
}

void WebGL2RenderingContext::vertexAttrib4f(GLuint index, GLfloat x, GLfloat y,
                                            GLfloat z, GLfloat w)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::vertexAttrib4f(index, x, y, z, w);
}

void WebGL2RenderingContext::vertexAttrib1fv(GLuint index, Float32List values)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::vertexAttrib1fv(index, values);
}

void WebGL2RenderingContext::vertexAttrib2fv(GLuint index, Float32List values)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::vertexAttrib2fv(index, values);
}

void WebGL2RenderingContext::vertexAttrib3fv(GLuint index, Float32List values)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::vertexAttrib3fv(index, values);
}

void WebGL2RenderingContext::vertexAttrib4fv(GLuint index, Float32List values)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::vertexAttrib4fv(index, values);
}

void WebGL2RenderingContext::vertexAttribPointer(GLuint index, GLint size,
                                                 GLenum type,
                                                 GLboolean normalized,
                                                 GLsizei stride,
                                                 GLintptr offset)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::vertexAttribPointer(index, size, type, normalized,
                                               stride, offset);
}

void WebGL2RenderingContext::viewport(uint32_t x, uint32_t y, uint32_t width,
                                      uint32_t height)
{
    STARFISH_UNIMPLEMENTED();
    WebGLRenderingContext::viewport(x, y, width, height);
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
    STARFISH_UNIMPLEMENTED();
    return nullptr;
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
    STARFISH_UNIMPLEMENTED();
    return nullptr;
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
    STARFISH_UNIMPLEMENTED();
    return nullptr;
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
    STARFISH_UNIMPLEMENTED();
    return nullptr;
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
    if (srcOffset != 0 || srcLength != 0) {
        STARFISH_UNIMPLEMENTED();
    }
    WebGLRenderingContext::uniformMatrix2fv(location, transpose, data);
}

void WebGL2RenderingContext::uniformMatrix3fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    if (srcOffset != 0 || srcLength != 0) {
        STARFISH_UNIMPLEMENTED();
    }
    WebGLRenderingContext::uniformMatrix3fv(location, transpose, data);
}

void WebGL2RenderingContext::uniformMatrix4fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    if (srcOffset != 0 || srcLength != 0) {
        STARFISH_UNIMPLEMENTED();
    }
    WebGLRenderingContext::uniformMatrix4fv(location, transpose, data);
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
