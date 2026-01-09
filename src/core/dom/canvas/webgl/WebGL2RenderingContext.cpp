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
#include "core/dom/canvas/webgl/WebGLBuffer.h"
#include "core/dom/canvas/webgl/WebGLProgram.h"
#include "core/dom/canvas/webgl/WebGLRenderingContextState.h"
#include "core/util/debug/Trace.h"
#include "platform/canvas/gl/GL.h"
#include "platform/canvas/gl/IncludeGL.h"
#include <EscargotPublic.h>

/* WebGL-specific enums */
static constexpr GLenum kMAX_CLIENT_WAIT_TIMEOUT_WEBGL = 0x9247;

/* WebGL constants */
static constexpr GLint64 kMaxClientWaitTimeoutWebgl = 0;
static constexpr char kShadingLanguageVersion[] = "WebGL GLSL ES 3.00";
static constexpr char kVersion[] = "WebGL 2.0";

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
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getContextAttributes();
}

bool WebGL2RenderingContext::isContextLost()
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::isContextLost();
}

Optional<GCVector<String*>> WebGL2RenderingContext::getSupportedExtensions()
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getSupportedExtensions();
}

Optional<ScriptObject> WebGL2RenderingContext::getExtension(
    String* requestedName)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getExtension(requestedName);
}

void WebGL2RenderingContext::activeTexture(GLenum texture)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::activeTexture(texture);
}

void WebGL2RenderingContext::attachShader(WebGLProgram* program,
                                          WebGLShader* shader)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::attachShader(program, shader);
}

void WebGL2RenderingContext::bindAttribLocation(WebGLProgram* program,
                                                GLuint index, String* name)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::bindAttribLocation(program, index, name);
}

void WebGL2RenderingContext::bindBuffer(GLenum target,
                                        Optional<WebGLBuffer*> buffer)
{
    if (!buffer.hasValue()) {
        return;
    }
    WebGLBuffer* value = buffer.value();
    if (value->isDeleted()) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::bindBuffer(target, buffer);
}

void WebGL2RenderingContext::bindFramebuffer(
    GLenum target, Optional<WebGLFramebuffer*> maybeFramebuffer)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::bindFramebuffer(target, maybeFramebuffer);
}

void WebGL2RenderingContext::bindRenderbuffer(
    GLenum target, Optional<WebGLRenderbuffer*> maybeRenderbuffer)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::bindRenderbuffer(target, maybeRenderbuffer);
}

void WebGL2RenderingContext::bindTexture(GLenum target,
                                         Optional<WebGLTexture*> maybeTexture)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::bindTexture(target, maybeTexture);
}

void WebGL2RenderingContext::blendColor(GLclampf red, GLclampf green,
                                        GLclampf blue, GLclampf alpha)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::blendColor(red, green, blue, alpha);
}

void WebGL2RenderingContext::blendEquation(GLenum mode)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::blendEquation(mode);
}

void WebGL2RenderingContext::blendEquationSeparate(GLenum modeRGB,
                                                   GLenum modeAlpha)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::blendEquationSeparate(modeRGB, modeAlpha);
}

void WebGL2RenderingContext::blendFunc(GLenum sfactor, GLenum dfactor)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::blendFunc(sfactor, dfactor);
}

void WebGL2RenderingContext::blendFuncSeparate(GLenum srcRGB, GLenum dstRGB,
                                               GLenum srcAlpha, GLenum dstAlpha)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::blendFuncSeparate(srcRGB, dstRGB, srcAlpha,
                                             dstAlpha);
}

GLenum WebGL2RenderingContext::checkFramebufferStatus(GLenum target)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::checkFramebufferStatus(target);
}

void WebGL2RenderingContext::clear(uint32_t mask)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::clear(mask);
}

void WebGL2RenderingContext::clearColor(float red, float green, float blue,
                                        float alpha)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::clearColor(red, green, blue, alpha);
}

void WebGL2RenderingContext::clearDepth(GLclampf depth)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::clearDepth(depth);
}

void WebGL2RenderingContext::clearStencil(GLint s)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::clearStencil(s);
}

void WebGL2RenderingContext::colorMask(GLboolean red, GLboolean green,
                                       GLboolean blue, GLboolean alpha)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::colorMask(red, green, blue, alpha);
}

void WebGL2RenderingContext::compileShader(WebGLShader* shader)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::compileShader(shader);
}

void WebGL2RenderingContext::copyTexImage2D(GLenum target, GLint level,
                                            GLenum internalformat, GLint x,
                                            GLint y, GLsizei width,
                                            GLsizei height, GLint border)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::copyTexImage2D(target, level, internalformat, x, y,
                                          width, height, border);
}

void WebGL2RenderingContext::copyTexSubImage2D(GLenum target, GLint level,
                                               GLint xoffset, GLint yoffset,
                                               GLint x, GLint y, GLsizei width,
                                               GLsizei height)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::copyTexSubImage2D(target, level, xoffset, yoffset, x,
                                             y, width, height);
}

WebGLBuffer* WebGL2RenderingContext::createBuffer()
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::createBuffer();
}

WebGLFramebuffer* WebGL2RenderingContext::createFramebuffer()
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::createFramebuffer();
}

WebGLProgram* WebGL2RenderingContext::createProgram()
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::createProgram();
}

WebGLRenderbuffer* WebGL2RenderingContext::createRenderbuffer()
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::createRenderbuffer();
}

WebGLShader* WebGL2RenderingContext::createShader(unsigned long type)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::createShader(type);
}

WebGLTexture* WebGL2RenderingContext::createTexture()
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::createTexture();
}

void WebGL2RenderingContext::cullFace(GLenum mode)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::cullFace(mode);
}

void WebGL2RenderingContext::deleteBuffer(Optional<WebGLBuffer*> buffer)
{
    Optional<WebGLBuffer*> current =
        getState()->getBoundBuffer(GL_UNIFORM_BUFFER);
    if (buffer.hasValue() && current.hasValue() &&
        buffer.value() == current.value()) {
        getState()->setBoundBuffer(GL_UNIFORM_BUFFER, nullptr);
    }
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::deleteBuffer(buffer);
}

void WebGL2RenderingContext::deleteFramebuffer(
    Optional<WebGLFramebuffer*> framebuffer)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::deleteFramebuffer(framebuffer);
}

void WebGL2RenderingContext::deleteProgram(Optional<WebGLProgram*> program)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::deleteProgram(program);
}

void WebGL2RenderingContext::deleteRenderbuffer(
    Optional<WebGLRenderbuffer*> renderbuffer)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::deleteRenderbuffer(renderbuffer);
}

void WebGL2RenderingContext::deleteShader(Optional<WebGLShader*> shader)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::deleteShader(shader);
}

void WebGL2RenderingContext::deleteTexture(Optional<WebGLTexture*> texture)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::deleteTexture(texture);
}

void WebGL2RenderingContext::depthFunc(GLenum func)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::depthFunc(func);
}

void WebGL2RenderingContext::depthMask(GLboolean flag)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::depthMask(flag);
}

void WebGL2RenderingContext::depthRange(GLclampf zNear, GLclampf zFar)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::depthRange(zNear, zFar);
}

void WebGL2RenderingContext::detachShader(WebGLProgram* program,
                                          WebGLShader* shader)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::detachShader(program, shader);
}

void WebGL2RenderingContext::disable(GLenum cap)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::disable(cap);
}

void WebGL2RenderingContext::disableVertexAttribArray(GLuint index)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::disableVertexAttribArray(index);
}

void WebGL2RenderingContext::drawArrays(GLenum mode, GLint first, GLsizei count)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::drawArrays(mode, first, count);
}

void WebGL2RenderingContext::drawElements(GLenum mode, GLsizei count,
                                          GLenum type, GLintptr offset)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::drawElements(mode, count, type, offset);
}

void WebGL2RenderingContext::enable(GLenum cap)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::enable(cap);
}

void WebGL2RenderingContext::enableVertexAttribArray(GLuint index)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::enableVertexAttribArray(index);
}

void WebGL2RenderingContext::finish()
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::finish();
}

void WebGL2RenderingContext::flushWebGL()
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::flushWebGL();
}

void WebGL2RenderingContext::framebufferRenderbuffer(
    GLenum target, GLenum attachment, GLenum renderbuffertarget,
    Optional<WebGLRenderbuffer*> maybeRenderbuffer)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::framebufferRenderbuffer(
        target, attachment, renderbuffertarget, maybeRenderbuffer);
}

void WebGL2RenderingContext::framebufferTexture2D(
    GLenum target, GLenum attachment, GLenum textarget,
    Optional<WebGLTexture*> maybeTexture, GLint level)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::framebufferTexture2D(target, attachment, textarget,
                                                maybeTexture, level);
}

void WebGL2RenderingContext::frontFace(GLenum mode)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::frontFace(mode);
}

void WebGL2RenderingContext::generateMipmap(GLenum target)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::generateMipmap(target);
}

WebGLActiveInfo* WebGL2RenderingContext::getActiveAttrib(WebGLProgram* program,
                                                         GLuint index)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getActiveAttrib(program, index);
}

WebGLActiveInfo* WebGL2RenderingContext::getActiveUniform(WebGLProgram* program,
                                                          GLuint index)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getActiveUniform(program, index);
}

Optional<GCVector<WebGLShader*>> WebGL2RenderingContext::getAttachedShaders(
    WebGLProgram* program)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getAttachedShaders(program);
}

GLint WebGL2RenderingContext::getAttribLocation(WebGLProgram* program,
                                                String* name)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getAttribLocation(program, name);
}

ScriptValue WebGL2RenderingContext::getBufferParameter(GLenum target,
                                                       GLenum pname)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getBufferParameter(target, pname);
}

ScriptValue WebGL2RenderingContext::getParameter(GLenum pname)
{
    {
        ENTER_CONTEXT_SCOPE(scriptNull());

        switch (pname) {
        // DOMString
        case GL_SHADING_LANGUAGE_VERSION: /* WebGL1 */
            return createScriptValue(
                createScriptASCIIString(kShadingLanguageVersion));
        case GL_VERSION: /* WebGL1 */
            return createScriptValue(createScriptASCIIString(kVersion));
        // GLboolean
        case GL_RASTERIZER_DISCARD:
        case GL_TRANSFORM_FEEDBACK_ACTIVE:
        case GL_TRANSFORM_FEEDBACK_PAUSED: {
            std::vector<GLboolean> values(1);
            gl()->getBooleanv(pname, &values[0]);
            return Escargot::ValueRef::create(static_cast<bool>(values[0]));
        }
        // GLenum
        case GL_DRAW_BUFFER0:
        case GL_DRAW_BUFFER1:
        case GL_DRAW_BUFFER2:
        case GL_DRAW_BUFFER3:
        case GL_DRAW_BUFFER4:
        case GL_DRAW_BUFFER5:
        case GL_DRAW_BUFFER6:
        case GL_DRAW_BUFFER7:
        case GL_DRAW_BUFFER8:
        case GL_DRAW_BUFFER9:
        case GL_DRAW_BUFFER10:
        case GL_DRAW_BUFFER11:
        case GL_DRAW_BUFFER12:
        case GL_DRAW_BUFFER13:
        case GL_DRAW_BUFFER14:
        case GL_DRAW_BUFFER15:
        case GL_FRAGMENT_SHADER_DERIVATIVE_HINT:
        case GL_READ_BUFFER:
            STARFISH_UNIMPLEMENTED("WebGL2RenderingContext::getParameter");
            break;
        // GLfloat
        case GL_MAX_TEXTURE_LOD_BIAS: {
            std::vector<GLfloat> values(1);
            gl()->getFloatv(pname, &values[0]);
            return Escargot::ValueRef::create(values[0]);
        }
        // GLint
        case GL_ALPHA_BITS: /* WebGL1 */
        case GL_BLUE_BITS:  /* WebGL1 */
        case GL_GREEN_BITS: /* WebGL1 */
        case GL_RED_BITS:   /* WebGL1 */
            STARFISH_UNIMPLEMENTED("WebGL2RenderingContext::getParameter");
            break;
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
        case GL_MAX_SAMPLES: /* WebGL1? */
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
            std::vector<GLint> values(1);
            gl()->getIntegerv(pname, &values[0]);
            return createScriptValue(values[0]);
        }
        // GLint64
        case kMAX_CLIENT_WAIT_TIMEOUT_WEBGL:
            return createScriptValue(kMaxClientWaitTimeoutWebgl);
        case GL_MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS:
        case GL_MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS:
        case GL_MAX_ELEMENT_INDEX:
        case GL_MAX_SERVER_WAIT_TIMEOUT:
        case GL_MAX_UNIFORM_BLOCK_SIZE: {
            std::vector<GLint64> values(1);
            gl()->getInteger64v(pname, &values[0]);
            return Escargot::ValueRef::create(values[0]);
        }
        // WebGLBuffer
        case GL_COPY_READ_BUFFER_BINDING:
        case GL_COPY_WRITE_BUFFER_BINDING:
        case GL_PIXEL_PACK_BUFFER_BINDING:
        case GL_PIXEL_UNPACK_BUFFER_BINDING:
        case GL_TRANSFORM_FEEDBACK_BUFFER_BINDING:
            STARFISH_UNIMPLEMENTED("WebGL2RenderingContext::getParameter");
            break;
        case GL_UNIFORM_BUFFER_BINDING: {
            Optional<WebGLBuffer*> buffer =
                getState()->getBoundBuffer(GL_UNIFORM_BUFFER);
            if (!buffer.hasValue()) {
                return scriptNull();
            }
            return buffer.value()->scriptValue();
        }
        // WebGLFramebuffer
        case GL_DRAW_FRAMEBUFFER_BINDING: /* WebGL1 (GL_FRAMEBUFFER_BINDING) */
        case GL_READ_FRAMEBUFFER_BINDING:
        // WebGLSampler
        case GL_SAMPLER_BINDING:
        // WebGLTexture
        case GL_TEXTURE_BINDING_2D_ARRAY:
        case GL_TEXTURE_BINDING_3D:
        // WebGLTransformFeedback
        case GL_TRANSFORM_FEEDBACK_BINDING:
            STARFISH_UNIMPLEMENTED("WebGL2RenderingContext::getParameter");
            break;
        // WebGLVertexArrayObject
        case GL_VERTEX_ARRAY_BINDING: /* WebGL1? */ {
            GLint value = -1;
            gl()->getIntegerv(pname, &value);
            if (value == 0) {
                return scriptNull();
            }

            Optional<WebGLVertexArrayObject*> maybe =
                getState()->webGLVertexArrayObject();

            if (!maybe.hasValue() || maybe.value()->isDeleted()) {
                return scriptNull();
            }

            STARFISH_ASSERT(static_cast<GLint>(maybe.value()->glObject()) ==
                            value);
            return maybe.value()->scriptValue();
        }
        }
    }
    return WebGLRenderingContext::getParameter(pname);
}

GLenum WebGL2RenderingContext::getError()
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getError();
}

ScriptValue WebGL2RenderingContext::getFramebufferAttachmentParameter(
    GLenum target, GLenum attachment, GLenum pname)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getFramebufferAttachmentParameter(
        target, attachment, pname);
}

ScriptValue WebGL2RenderingContext::getProgramParameter(WebGLProgram* program,
                                                        GLenum pname)
{
    ENTER_CONTEXT_SCOPE(scriptNull());

    if (program->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return scriptNull();
    }

    GLint params = 0;
    gl()->getProgramiv(program->glObject(), pname, &params);

    if (hasGLError()) {
        return scriptNull();
    }

    switch (pname) {
    // GLboolean
    case GL_DELETE_STATUS:
    case GL_LINK_STATUS:
    case GL_VALIDATE_STATUS:
        return createScriptValue(static_cast<bool>(params));
    // GLenum
    case GL_TRANSFORM_FEEDBACK_BUFFER_MODE:
        return createScriptValue(static_cast<GLenum>(params));
    // GLint
    case GL_ACTIVE_ATTRIBUTES:
    case GL_ACTIVE_UNIFORMS:
    case GL_ACTIVE_UNIFORM_BLOCKS:
    case GL_ATTACHED_SHADERS:
    case GL_TRANSFORM_FEEDBACK_VARYINGS:
        return createScriptValue(params);
    default:
        break;
    }
    setGLError(GL_INVALID_ENUM);
    return scriptNull();
}

String* WebGL2RenderingContext::getProgramInfoLog(WebGLProgram* program)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getProgramInfoLog(program);
}

ScriptValue WebGL2RenderingContext::getRenderbufferParameter(GLenum target,
                                                             GLenum pname)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getRenderbufferParameter(target, pname);
}

ScriptValue WebGL2RenderingContext::getShaderParameter(WebGLShader* shader,
                                                       GLenum pname)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getShaderParameter(shader, pname);
}

WebGLShaderPrecisionFormat* WebGL2RenderingContext::getShaderPrecisionFormat(
    GLenum shadertype, GLenum precisiontype)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getShaderPrecisionFormat(shadertype,
                                                           precisiontype);
}

String* WebGL2RenderingContext::getShaderInfoLog(WebGLShader* shader)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getShaderInfoLog(shader);
}

String* WebGL2RenderingContext::getShaderSource(WebGLShader* shader)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getShaderSource(shader);
}

ScriptValue WebGL2RenderingContext::getTexParameter(GLenum target, GLenum pname)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getTexParameter(target, pname);
}

ScriptValue WebGL2RenderingContext::getUniform(WebGLProgram* program,
                                               WebGLUniformLocation* location)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getUniform(program, location);
}

WebGLUniformLocation* WebGL2RenderingContext::getUniformLocation(
    WebGLProgram* program, String* name)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getUniformLocation(program, name);
}

ScriptValue WebGL2RenderingContext::getVertexAttrib(GLuint index, GLenum pname)
{
    {
        ENTER_CONTEXT_SCOPE(scriptNull());

        switch (pname) {
        // GLboolean
        case GL_VERTEX_ATTRIB_ARRAY_ENABLED: /* WebGL1? */
        case GL_VERTEX_ATTRIB_ARRAY_INTEGER:
        case GL_VERTEX_ATTRIB_ARRAY_NORMALIZED: /* WebGL1? */ {
            GLint value = 0;
            gl()->getVertexAttribiv(index, pname, &value);
            return Escargot::ValueRef::create(value == 1 ? true : false);
        }
        // GLenum
        case GL_VERTEX_ATTRIB_ARRAY_TYPE: /* WebGL1? */ {
            GLint value = GL_FLOAT;
            gl()->getVertexAttribiv(index, pname, &value);
            return Escargot::ValueRef::create(value);
        }
        // GLint
        case GL_VERTEX_ATTRIB_ARRAY_DIVISOR:
        case GL_VERTEX_ATTRIB_ARRAY_SIZE: /* WebGL1? */
        case GL_VERTEX_ATTRIB_ARRAY_STRIDE: /* WebGL1? */ {
            GLint value = 0;
            gl()->getVertexAttribiv(index, pname, &value);
            return Escargot::ValueRef::create(value);
        }
        // One of Float32Array, Int32Array or Uint32Array (each with 4 elements)
        case GL_CURRENT_VERTEX_ATTRIB: /* WebGL1? */ {
            std::vector<float> values(4);
            gl()->getVertexAttribfv(index, pname, &values[0]);
            return createTypedArray<Escargot::Float32ArrayObjectRef>(
                scriptBindingInstance(), values);
        }
        // WebGLBuffer
        case GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING: /* WebGL1? */ {
            GLint value = 0;
            gl()->getVertexAttribiv(index, pname, &value);

            TRACE(WEBGL, KV(index), KV(value));

            Optional<WebGLVertexArrayObject*> maybe =
                getState()->webGLVertexArrayObject();

            if (!maybe.hasValue()) {
                return scriptNull(); // No mention found for this in the spec.
            }

            Optional<WebGLBuffer*> maybeBuffer =
                getState()->getBufferBoundToVertexAttributes(index);

            if (!maybeBuffer.hasValue()) {
                return scriptNull(); // No mention found for this in the spec.
            }

            TRACE(WEBGL, KV(index), KV(maybeBuffer.value()->glObject()));

            STARFISH_ASSERT(index == maybeBuffer.value()->glObject());

            return maybeBuffer.value()->scriptValue();
        }
        }
    }
    return WebGLRenderingContext::getVertexAttrib(index, pname);
}

GLintptr WebGL2RenderingContext::getVertexAttribOffset(GLuint index,
                                                       GLenum pname)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::getVertexAttribOffset(index, pname);
}

void WebGL2RenderingContext::hint(GLenum target, GLenum mode)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::hint(target, mode);
}

bool WebGL2RenderingContext::isBuffer(Optional<WebGLBuffer*> maybe)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::isBuffer(maybe);
}

bool WebGL2RenderingContext::isEnabled(GLenum cap)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::isEnabled(cap);
}

bool WebGL2RenderingContext::isFramebuffer(Optional<WebGLFramebuffer*> maybe)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::isFramebuffer(maybe);
}

bool WebGL2RenderingContext::isProgram(Optional<WebGLProgram*> maybe)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::isProgram(maybe);
}

bool WebGL2RenderingContext::isRenderbuffer(Optional<WebGLRenderbuffer*> maybe)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::isRenderbuffer(maybe);
}

bool WebGL2RenderingContext::isShader(Optional<WebGLShader*> maybe)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::isShader(maybe);
}

bool WebGL2RenderingContext::isTexture(Optional<WebGLTexture*> maybe)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    return WebGLRenderingContext::isTexture(maybe);
}

void WebGL2RenderingContext::lineWidth(GLfloat width)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::lineWidth(width);
}

void WebGL2RenderingContext::linkProgram(WebGLProgram* program)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::linkProgram(program);
}

void WebGL2RenderingContext::pixelStorei(GLenum pname, GLint param)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::pixelStorei(pname, param);
}

void WebGL2RenderingContext::polygonOffset(GLfloat factor, GLfloat units)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::polygonOffset(factor, units);
}

void WebGL2RenderingContext::renderbufferStorage(GLenum target,
                                                 GLenum internalformat,
                                                 GLsizei width, GLsizei height)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::renderbufferStorage(target, internalformat, width,
                                               height);
}

void WebGL2RenderingContext::sampleCoverage(GLclampf value, GLboolean invert)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::sampleCoverage(value, invert);
}

void WebGL2RenderingContext::scissor(GLint x, GLint y, GLsizei width,
                                     GLsizei height)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::scissor(x, y, width, height);
}

void WebGL2RenderingContext::shaderSource(WebGLShader* shader, String* source)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::shaderSource(shader, source);
}

void WebGL2RenderingContext::stencilFunc(GLenum func, GLint ref, GLuint mask)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::stencilFunc(func, ref, mask);
}

void WebGL2RenderingContext::stencilFuncSeparate(GLenum face, GLenum func,
                                                 GLint ref, GLuint mask)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::stencilFuncSeparate(face, func, ref, mask);
}

void WebGL2RenderingContext::stencilMask(GLuint mask)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::stencilMask(mask);
}

void WebGL2RenderingContext::stencilMaskSeparate(GLenum face, GLuint mask)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::stencilMaskSeparate(face, mask);
}

void WebGL2RenderingContext::stencilOp(GLenum fail, GLenum zfail, GLenum zpass)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::stencilOp(fail, zfail, zpass);
}

void WebGL2RenderingContext::stencilOpSeparate(GLenum face, GLenum fail,
                                               GLenum zfail, GLenum zpass)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::stencilOpSeparate(face, fail, zfail, zpass);
}

void WebGL2RenderingContext::texParameterf(GLenum target, GLenum pname,
                                           GLfloat param)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::texParameterf(target, pname, param);
}

void WebGL2RenderingContext::texParameteri(GLenum target, GLenum pname,
                                           GLint param)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::texParameteri(target, pname, param);
}

void WebGL2RenderingContext::uniform1f(
    Optional<WebGLUniformLocation*> maybeUniform, GLfloat x)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::uniform1f(maybeUniform, x);
}

void WebGL2RenderingContext::uniform2f(
    Optional<WebGLUniformLocation*> maybeUniform, GLfloat x, GLfloat y)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::uniform2f(maybeUniform, x, y);
}

void WebGL2RenderingContext::uniform3f(
    Optional<WebGLUniformLocation*> maybeUniform, GLfloat x, GLfloat y,
    GLfloat z)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::uniform3f(maybeUniform, x, y, z);
}

void WebGL2RenderingContext::uniform4f(
    Optional<WebGLUniformLocation*> maybeUniform, GLfloat x, GLfloat y,
    GLfloat z, GLfloat w)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::uniform4f(maybeUniform, x, y, z, w);
}

void WebGL2RenderingContext::uniform1i(
    Optional<WebGLUniformLocation*> maybeUniform, GLint x)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::uniform1i(maybeUniform, x);
}

void WebGL2RenderingContext::uniform2i(
    Optional<WebGLUniformLocation*> maybeUniform, GLint x, GLint y)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::uniform2i(maybeUniform, x, y);
}

void WebGL2RenderingContext::uniform3i(
    Optional<WebGLUniformLocation*> maybeUniform, GLint x, GLint y, GLint z)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::uniform3i(maybeUniform, x, y, z);
}

void WebGL2RenderingContext::uniform4i(
    Optional<WebGLUniformLocation*> maybeUniform, GLint x, GLint y, GLint z,
    GLint w)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::uniform4i(maybeUniform, x, y, z, w);
}

void WebGL2RenderingContext::useProgram(Optional<WebGLProgram*> maybeProgram)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::useProgram(maybeProgram);
}

void WebGL2RenderingContext::validateProgram(WebGLProgram* program)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::validateProgram(program);
}

void WebGL2RenderingContext::vertexAttrib1f(GLuint index, GLfloat x)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::vertexAttrib1f(index, x);
}

void WebGL2RenderingContext::vertexAttrib2f(GLuint index, GLfloat x, GLfloat y)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::vertexAttrib2f(index, x, y);
}

void WebGL2RenderingContext::vertexAttrib3f(GLuint index, GLfloat x, GLfloat y,
                                            GLfloat z)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::vertexAttrib3f(index, x, y, z);
}

void WebGL2RenderingContext::vertexAttrib4f(GLuint index, GLfloat x, GLfloat y,
                                            GLfloat z, GLfloat w)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::vertexAttrib4f(index, x, y, z, w);
}

void WebGL2RenderingContext::vertexAttrib1fv(GLuint index, Float32List values)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::vertexAttrib1fv(index, values);
}

void WebGL2RenderingContext::vertexAttrib2fv(GLuint index, Float32List values)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::vertexAttrib2fv(index, values);
}

void WebGL2RenderingContext::vertexAttrib3fv(GLuint index, Float32List values)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::vertexAttrib3fv(index, values);
}

void WebGL2RenderingContext::vertexAttrib4fv(GLuint index, Float32List values)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::vertexAttrib4fv(index, values);
}

void WebGL2RenderingContext::vertexAttribPointer(GLuint index, GLint size,
                                                 GLenum type,
                                                 GLboolean normalized,
                                                 GLsizei stride,
                                                 GLintptr offset)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::vertexAttribPointer(index, size, type, normalized,
                                               stride, offset);
}

void WebGL2RenderingContext::viewport(uint32_t x, uint32_t y, uint32_t width,
                                      uint32_t height)
{
    STARFISH_UNIMPLEMENTED("WebGLRenderingContextBase");
    WebGLRenderingContext::viewport(x, y, width, height);
}

// WebGL2RenderingContextBase

void WebGL2RenderingContext::copyBufferSubData(GLenum readTarget,
                                               GLenum writeTarget,
                                               GLintptr readOffset,
                                               GLintptr writeOffset,
                                               GLsizeiptr size)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::getBufferSubData(GLenum target,
                                              GLintptr srcByteOffset,
                                              ScriptArrayBufferView dstBuffer,
                                              unsigned long long dstOffset,
                                              GLuint length)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::blitFramebuffer(GLint srcX0, GLint srcY0,
                                             GLint srcX1, GLint srcY1,
                                             GLint dstX0, GLint dstY0,
                                             GLint dstX1, GLint dstY1,
                                             GLbitfield mask, GLenum filter)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::framebufferTextureLayer(
    GLenum target, GLenum attachment, Optional<WebGLTexture*> texture,
    GLint level, GLint layer)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::invalidateFramebuffer(
    GLenum target, GCAtomicVector<GLenum> attachments)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::invalidateSubFramebuffer(
    GLenum target, GCAtomicVector<GLenum> attachments, GLint x, GLint y,
    GLsizei width, GLsizei height)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::readBuffer(GLenum src)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

ScriptValue WebGL2RenderingContext::getInternalformatParameter(
    GLenum target, GLenum internalformat, GLenum pname)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
    return scriptNull();
}

void WebGL2RenderingContext::renderbufferStorageMultisample(
    GLenum target, GLsizei samples, GLenum internalformat, GLsizei width,
    GLsizei height)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::texStorage2D(GLenum target, GLsizei levels,
                                          GLenum internalformat, GLsizei width,
                                          GLsizei height)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::texStorage3D(GLenum target, GLsizei levels,
                                          GLenum internalformat, GLsizei width,
                                          GLsizei height, GLsizei depth)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::texImage3D(GLenum target, GLint level,
                                        GLint internalformat, GLsizei width,
                                        GLsizei height, GLsizei depth,
                                        GLint border, GLenum format,
                                        GLenum type, GLintptr pboOffset)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::texImage3D(GLenum target, GLint level,
                                        GLint internalformat, GLsizei width,
                                        GLsizei height, GLsizei depth,
                                        GLint border, GLenum format,
                                        GLenum type, TexImageSource source)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::texImage3D(GLenum target, GLint level,
                                        GLint internalformat, GLsizei width,
                                        GLsizei height, GLsizei depth,
                                        GLint border, GLenum format,
                                        GLenum type,
                                        ScriptArrayBufferView srcData)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::texImage3D(
    GLenum target, GLint level, GLint internalformat, GLsizei width,
    GLsizei height, GLsizei depth, GLint border, GLenum format, GLenum type,
    ScriptArrayBufferView srcData, unsigned long long srcOffset)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::texSubImage3D(GLenum target, GLint level,
                                           GLint xoffset, GLint yoffset,
                                           GLint zoffset, GLsizei width,
                                           GLsizei height, GLsizei depth,
                                           GLenum format, GLenum type,
                                           GLintptr pboOffset)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::texSubImage3D(GLenum target, GLint level,
                                           GLint xoffset, GLint yoffset,
                                           GLint zoffset, GLsizei width,
                                           GLsizei height, GLsizei depth,
                                           GLenum format, GLenum type,
                                           TexImageSource source)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::texSubImage3D(
    GLenum target, GLint level, GLint xoffset, GLint yoffset, GLint zoffset,
    GLsizei width, GLsizei height, GLsizei depth, GLenum format, GLenum type,
    ScriptArrayBufferView srcData, unsigned long long srcOffset)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::copyTexSubImage3D(GLenum target, GLint level,
                                               GLint xoffset, GLint yoffset,
                                               GLint zoffset, GLint x, GLint y,
                                               GLsizei width, GLsizei height)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::compressedTexImage3D(GLenum target, GLint level,
                                                  GLenum internalformat,
                                                  GLsizei width, GLsizei height,
                                                  GLsizei depth, GLint border,
                                                  GLsizei imageSize,
                                                  GLintptr offset)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::compressedTexImage3D(
    GLenum target, GLint level, GLenum internalformat, GLsizei width,
    GLsizei height, GLsizei depth, GLint border, ScriptArrayBufferView srcData,
    unsigned long long srcOffset, GLuint srcLengthOverride)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::compressedTexSubImage3D(
    GLenum target, GLint level, GLint xoffset, GLint yoffset, GLint zoffset,
    GLsizei width, GLsizei height, GLsizei depth, GLenum format,
    GLsizei imageSize, GLintptr offset)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::compressedTexSubImage3D(
    GLenum target, GLint level, GLint xoffset, GLint yoffset, GLint zoffset,
    GLsizei width, GLsizei height, GLsizei depth, GLenum format,
    ScriptArrayBufferView srcData, unsigned long long srcOffset,
    GLuint srcLengthOverride)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

GLint WebGL2RenderingContext::getFragDataLocation(WebGLProgram* program,
                                                  String* name)
{
    ENTER_CONTEXT_SCOPE(-1);

    if (program->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return -1;
    }
    return gl()->getFragDataLocation(program->glObject(), CSTR(name));
}

void WebGL2RenderingContext::uniform1ui(
    Optional<WebGLUniformLocation*> location, GLuint v0)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::uniform2ui(
    Optional<WebGLUniformLocation*> location, GLuint v0, GLuint v1)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::uniform3ui(
    Optional<WebGLUniformLocation*> location, GLuint v0, GLuint v1, GLuint v2)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::uniform4ui(
    Optional<WebGLUniformLocation*> location, GLuint v0, GLuint v1, GLuint v2,
    GLuint v3)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::uniform1uiv(
    Optional<WebGLUniformLocation*> location, Uint32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::uniform2uiv(
    Optional<WebGLUniformLocation*> location, Uint32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::uniform3uiv(
    Optional<WebGLUniformLocation*> location, Uint32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::uniform4uiv(
    Optional<WebGLUniformLocation*> location, Uint32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::uniformMatrix3x2fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::uniformMatrix4x2fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::uniformMatrix2x3fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::uniformMatrix4x3fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::uniformMatrix2x4fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::uniformMatrix3x4fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::vertexAttribI4i(GLuint index, GLint x, GLint y,
                                             GLint z, GLint w)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::vertexAttribI4iv(GLuint index, Int32List values)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::vertexAttribI4ui(GLuint index, GLuint x, GLuint y,
                                              GLuint z, GLuint w)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::vertexAttribI4uiv(GLuint index, Uint32List values)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::vertexAttribIPointer(GLuint index, GLint size,
                                                  GLenum type, GLsizei stride,
                                                  GLintptr offset)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::vertexAttribDivisor(GLuint index, GLuint divisor)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::drawArraysInstanced(GLenum mode, GLint first,
                                                 GLsizei count,
                                                 GLsizei instanceCount)
{
    ENTER_CONTEXT_SCOPE();

    glDrawArraysInstanced(mode, first, count, instanceCount);
}

void WebGL2RenderingContext::drawElementsInstanced(GLenum mode, GLsizei count,
                                                   GLenum type, GLintptr offset,
                                                   GLsizei instanceCount)
{
    ENTER_CONTEXT_SCOPE();

    glDrawElementsInstanced(mode, count, type, reinterpret_cast<void*>(offset),
                            instanceCount);
}

void WebGL2RenderingContext::drawRangeElements(GLenum mode, GLuint start,
                                               GLuint end, GLsizei count,
                                               GLenum type, GLintptr offset)
{
    ENTER_CONTEXT_SCOPE();

    glDrawRangeElements(mode, start, end, count, type,
                        reinterpret_cast<void*>(offset));
}

void WebGL2RenderingContext::drawBuffers(GCAtomicVector<GLenum> buffers)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::clearBufferfv(GLenum buffer, GLint drawbuffer,
                                           Float32List values,
                                           unsigned long long srcOffset)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::clearBufferiv(GLenum buffer, GLint drawbuffer,
                                           Int32List values,
                                           unsigned long long srcOffset)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::clearBufferuiv(GLenum buffer, GLint drawbuffer,
                                            Uint32List values,
                                            unsigned long long srcOffset)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::clearBufferfi(GLenum buffer, GLint drawbuffer,
                                           GLfloat depth, GLint stencil)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

WebGLQuery* WebGL2RenderingContext::createQuery()
{
    ENTER_CONTEXT_SCOPE(nullptr);

    GLuint query = 0;
    gl()->genQueries(1, &query);
    m_queries[query] = new WebGLQuery(scriptBindingInstance(), this, query);
    return m_queries[query];
}

void WebGL2RenderingContext::deleteQuery(Optional<WebGLQuery*> query)
{
    ENTER_CONTEXT_SCOPE();

    if (!query.hasValue()) {
        return;
    }
    WebGLQuery* value = query.value();
    if (value->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }
    if (value->isDeleted()) {
        return;
    }
    GLuint id = value->glObject();
    glDeleteQueries(1, &id);
    value->markDeleted();
    value->setIsActive(false);
    m_queries.erase(id);
}

GLboolean WebGL2RenderingContext::isQuery(Optional<WebGLQuery*> query)
{
    ENTER_CONTEXT_SCOPE(false);

    if (!query.hasValue() || query.value()->context() != this ||
        query.value()->invalidated()) {
        return false;
    }
    return query.value()->isActive();
}

void WebGL2RenderingContext::beginQuery(GLenum target, WebGLQuery* query)
{
    ENTER_CONTEXT_SCOPE();

    if (query->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }
    glBeginQuery(target, query->glObject());
    query->setIsActive(true);
}

void WebGL2RenderingContext::endQuery(GLenum target)
{
    ENTER_CONTEXT_SCOPE();

    glEndQuery(target);
}

Optional<WebGLQuery*> WebGL2RenderingContext::getQuery(GLenum target,
                                                       GLenum pname)
{
    ENTER_CONTEXT_SCOPE(Optional<WebGLQuery*>());

    switch (target) {
    case GL_ANY_SAMPLES_PASSED:
    case GL_ANY_SAMPLES_PASSED_CONSERVATIVE:
    case GL_TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN:
        GLint query;
        glGetQueryiv(target, pname, &query);
        if (hasGLError() || query == 0 ||
            m_queries.find(query) == m_queries.end()) {
            return Optional<WebGLQuery*>();
        }
        return m_queries[query];
    }
    setGLError(GL_INVALID_ENUM);
    return Optional<WebGLQuery*>();
}

ScriptValue WebGL2RenderingContext::getQueryParameter(WebGLQuery* query,
                                                      GLenum pname)
{
    ENTER_CONTEXT_SCOPE(scriptNull());

    static int cheat = 0;

    if (query->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return scriptNull();
    }
    switch (pname) {
    // GLuint
    case GL_QUERY_RESULT: {
        cheat = 0;

        GLuint value;
        glGetQueryObjectuiv(query->glObject(), pname, &value);
        if (hasGLError()) {
            return scriptNull();
        }
        return createScriptValue(value);
    }
    // GLboolean
    case GL_QUERY_RESULT_AVAILABLE: {
        cheat += 1;

        GLuint value;
        glGetQueryObjectuiv(query->glObject(), pname, &value);
        if (hasGLError()) {
            return scriptNull();
        }
        return createScriptValue(cheat > 20480);
    }
    }
    setGLError(GL_INVALID_ENUM);
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
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

GLboolean WebGL2RenderingContext::isSampler(Optional<WebGLSampler*> sampler)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
    return false;
}

void WebGL2RenderingContext::bindSampler(GLuint unit,
                                         Optional<WebGLSampler*> sampler)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::samplerParameteri(WebGLSampler* sampler,
                                               GLenum pname, GLint param)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::samplerParameterf(WebGLSampler* sampler,
                                               GLenum pname, GLfloat param)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

ScriptValue WebGL2RenderingContext::getSamplerParameter(WebGLSampler* sampler,
                                                        GLenum pname)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
    return scriptNull();
}

Optional<WebGLSync*> WebGL2RenderingContext::fenceSync(GLenum condition,
                                                       GLbitfield flags)
{
    ENTER_CONTEXT_SCOPE(Optional<WebGLSync*>());

    GLsync sync = glFenceSync(condition, flags);
    return new WebGLSync(scriptBindingInstance(), this, sync);
}

GLboolean WebGL2RenderingContext::isSync(Optional<WebGLSync*> sync)
{
    ENTER_CONTEXT_SCOPE(false);

    if (!sync.hasValue() || sync.value()->context() != this ||
        sync.value()->invalidated()) {
        return false;
    }

    return glIsSync(sync.value()->glObject());
}

void WebGL2RenderingContext::deleteSync(Optional<WebGLSync*> sync)
{
    ENTER_CONTEXT_SCOPE();

    if (!sync.hasValue()) {
        return;
    }
    WebGLSync* value = sync.value();
    if (value->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }
    if (value->isDeleted()) {
        return;
    }
    glDeleteSync(value->glObject());
    value->markDeleted();
}

GLenum WebGL2RenderingContext::clientWaitSync(WebGLSync* sync, GLbitfield flags,
                                              GLuint64 timeout)
{
    ENTER_CONTEXT_SCOPE(GL_WAIT_FAILED);

    if (sync->context() != this || flags & ~GL_SYNC_FLUSH_COMMANDS_BIT ||
        timeout > kMaxClientWaitTimeoutWebgl) {
        setGLError(GL_INVALID_OPERATION);
        return GL_WAIT_FAILED;
    }
    return glClientWaitSync(sync->glObject(), flags, timeout);
}

void WebGL2RenderingContext::waitSync(WebGLSync* sync, GLbitfield flags,
                                      GLint64 timeout)
{
    ENTER_CONTEXT_SCOPE();

    if (sync->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }
    glWaitSync(sync->glObject(), flags, timeout);
}

ScriptValue WebGL2RenderingContext::getSyncParameter(WebGLSync* sync,
                                                     GLenum pname)
{
    ENTER_CONTEXT_SCOPE(scriptNull());

    if (sync->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return scriptNull();
    }
    switch (pname) {
    // GLenum
    case GL_OBJECT_TYPE:
    case GL_SYNC_STATUS:
    case GL_SYNC_CONDITION: {
        GLint value;
        glGetSynciv(sync->glObject(), pname, 1, nullptr, &value);
        if (hasGLError()) {
            return scriptNull();
        }
        return createScriptValue(static_cast<GLenum>(value));
    }
    // GLbitfield
    case GL_SYNC_FLAGS: {
        GLint value;
        glGetSynciv(sync->glObject(), pname, 1, nullptr, &value);
        if (hasGLError()) {
            return scriptNull();
        }
        return createScriptValue(static_cast<GLbitfield>(value));
    }
    }
    setGLError(GL_INVALID_ENUM);
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
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

GLboolean WebGL2RenderingContext::isTransformFeedback(
    Optional<WebGLTransformFeedback*> tf)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
    return false;
}

void WebGL2RenderingContext::bindTransformFeedback(
    GLenum target, Optional<WebGLTransformFeedback*> tf)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::beginTransformFeedback(GLenum primitiveMode)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::endTransformFeedback()
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::transformFeedbackVaryings(
    WebGLProgram* program, GCVector<String*> varyings, GLenum bufferMode)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

Optional<WebGLActiveInfo*> WebGL2RenderingContext::getTransformFeedbackVarying(
    WebGLProgram* program, GLuint index)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
    return nullptr;
}

void WebGL2RenderingContext::pauseTransformFeedback()
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::resumeTransformFeedback()
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
}

void WebGL2RenderingContext::bindBufferBase(GLenum target, GLuint index,
                                            Optional<WebGLBuffer*> buffer)
{
    ENTER_CONTEXT_SCOPE();

    if (!buffer.hasValue()) {
        return;
    }
    WebGLBuffer* value = buffer.value();
    if (value->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }
    glBindBufferBase(target, index, value->glObject());
}

void WebGL2RenderingContext::bindBufferRange(GLenum target, GLuint index,
                                             Optional<WebGLBuffer*> buffer,
                                             GLintptr offset, GLsizeiptr size)
{
    ENTER_CONTEXT_SCOPE();

    if (!buffer.hasValue()) {
        return;
    }
    WebGLBuffer* value = buffer.value();
    if (value->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }
    glBindBufferRange(target, index, value->glObject(), offset, size);
}

ScriptValue WebGL2RenderingContext::getIndexedParameter(GLenum target,
                                                        GLuint index)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
    return scriptNull();
}

Optional<GCAtomicVector<GLuint>> WebGL2RenderingContext::getUniformIndices(
    WebGLProgram* program, GCVector<String*> uniformNames)
{
    ENTER_CONTEXT_SCOPE(Optional<GCAtomicVector<GLuint>>());

    if (program->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return Optional<GCAtomicVector<GLuint>>();
    }
    GLsizei count = uniformNames.size();
    char** names = (char**)malloc(sizeof(char*) * count);
    for (GLsizei i = 0; i < count; i++) {
        const char* src = CSTR(uniformNames[i]);
        size_t len = strlen(src);
        names[i] = (char*)malloc(sizeof(char) * len);
        strcpy(names[i], src);
    }
    GLuint* indices = (GLuint*)malloc(sizeof(GLuint) * count);
    glGetUniformIndices(program->glObject(), count, names, indices);
    if (hasGLError()) {
        for (GLsizei i = 0; i < count; i++) {
            free(names[i]);
        }
        free(names);
        free(indices);
        return Optional<GCAtomicVector<GLuint>>();
    }
    GCAtomicVector<GLuint> uniformIndices;
    for (GLsizei i = 0; i < count; i++) {
        uniformIndices.push_back(indices[i]);
        free(names[i]);
    }
    free(names);
    free(indices);
    return uniformIndices;
}

ScriptValue WebGL2RenderingContext::getActiveUniforms(
    WebGLProgram* program, GCAtomicVector<GLuint> uniformIndices, GLenum pname)
{
    ENTER_CONTEXT_SCOPE(scriptNull());

    if (program->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return scriptNull();
    }
    switch (pname) {
    // sequence<GLboolean>
    case GL_UNIFORM_IS_ROW_MAJOR:
    // sequence<GLenum>
    case GL_UNIFORM_TYPE:
        STARFISH_UNIMPLEMENTED("WebGL2RenderingContext::getActiveUniforms");
        return scriptNull();
    // sequence<GLint>
    case GL_UNIFORM_ARRAY_STRIDE:
    case GL_UNIFORM_BLOCK_INDEX:
    case GL_UNIFORM_MATRIX_STRIDE:
    case GL_UNIFORM_OFFSET: {
        GLsizei count = uniformIndices.size();
        std::vector<GLint> values(count);
        glGetActiveUniformsiv(program->glObject(), count, uniformIndices.data(),
                              pname, values.data());
        return createTypedArray<Escargot::Int32ArrayObjectRef>(
            scriptBindingInstance(), values);
    }
    // sequence<GLuint>
    case GL_UNIFORM_SIZE:
        STARFISH_UNIMPLEMENTED("WebGL2RenderingContext::getActiveUniforms");
        return scriptNull();
    }
    setGLError(GL_INVALID_ENUM);
    return scriptNull();
}

GLuint WebGL2RenderingContext::getUniformBlockIndex(WebGLProgram* program,
                                                    String* uniformBlockName)
{
    ENTER_CONTEXT_SCOPE(GL_INVALID_INDEX);

    if (program->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return GL_INVALID_INDEX;
    }
    return glGetUniformBlockIndex(program->glObject(), CSTR(uniformBlockName));
}

ScriptValue WebGL2RenderingContext::getActiveUniformBlockParameter(
    WebGLProgram* program, GLuint uniformBlockIndex, GLenum pname)
{
    ENTER_CONTEXT_SCOPE(scriptNull());

    if (program->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return scriptNull();
    }
    switch (pname) {
    // GLboolean
    case GL_UNIFORM_BLOCK_REFERENCED_BY_FRAGMENT_SHADER:
    case GL_UNIFORM_BLOCK_REFERENCED_BY_VERTEX_SHADER: {
        GLint value;
        glGetActiveUniformBlockiv(program->glObject(), uniformBlockIndex, pname,
                                  &value);
        return createScriptValue(static_cast<bool>(value));
    }
    // GLuint
    case GL_UNIFORM_BLOCK_ACTIVE_UNIFORMS:
    case GL_UNIFORM_BLOCK_BINDING:
    case GL_UNIFORM_BLOCK_DATA_SIZE: {
        GLint value;
        glGetActiveUniformBlockiv(program->glObject(), uniformBlockIndex, pname,
                                  &value);
        return createScriptValue(static_cast<GLuint>(value));
    }
    // Uint32Array
    case GL_UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES:
        STARFISH_UNIMPLEMENTED(
            "WebGL2RenderingContext::getActiveUniformBlockParameter");
        return scriptNull();
    }
    setGLError(GL_INVALID_ENUM);
    return scriptNull();
}

Optional<String*> WebGL2RenderingContext::getActiveUniformBlockName(
    WebGLProgram* program, GLuint uniformBlockIndex)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextBase");
    return nullptr;
}

void WebGL2RenderingContext::uniformBlockBinding(WebGLProgram* program,
                                                 GLuint uniformBlockIndex,
                                                 GLuint uniformBlockBinding)
{
    ENTER_CONTEXT_SCOPE();

    if (program->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }
    glUniformBlockBinding(program->glObject(), uniformBlockIndex,
                          uniformBlockBinding);
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
    ENTER_CONTEXT_SCOPE();

    if (!vertexArray.hasValue()) {
        return;
    }

    WebGLVertexArrayObject* value = vertexArray.value();

    if (value->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    if (value->isDeleted()) {
        return;
    }

    GLuint vao = value->glObject();
    TRACE(WEBGL, KV(vao));
    glDeleteVertexArrays(1, &vao);
    value->markDeleted();
}

GLboolean WebGL2RenderingContext::isVertexArray(
    Optional<WebGLVertexArrayObject*> vertexArray)
{
    ENTER_CONTEXT_SCOPE(false);

    if (!vertexArray.hasValue()) {
        return false;
    }

    WebGLVertexArrayObject* value = vertexArray.value();

    if (value->context() != this || value->invalidated()) {
        return false;
    }

    if (!value->hasEverBound()) {
        return false;
    }

    return true;
}

void WebGL2RenderingContext::bindVertexArray(
    Optional<WebGLVertexArrayObject*> array)
{
    ENTER_CONTEXT_SCOPE();

    if (!array.hasValue()) {
        glBindVertexArray(0);
        getState()->setWebGLVertexArrayObject(nullptr);
        return;
    }

    WebGLVertexArrayObject* value = array.value();

    if (value->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    if (value->isDeleted()) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    TRACE(WEBGL, KV(value->glObject()));
    glBindVertexArray(value->glObject());
    value->setHasEverBound();
    getState()->setWebGLVertexArrayObject(value);
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
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
}

void WebGL2RenderingContext::bufferSubData(GLenum target,
                                           GLintptr dstByteOffset,
                                           ScriptArrayBufferView srcData,
                                           unsigned long long srcOffset,
                                           GLuint length)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
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
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
}

void WebGL2RenderingContext::texImage2D(GLenum target, GLint level,
                                        GLint internalformat, GLsizei width,
                                        GLsizei height, GLint border,
                                        GLenum format, GLenum type,
                                        TexImageSource source)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
}

void WebGL2RenderingContext::texImage2D(GLenum target, GLint level,
                                        GLint internalformat, GLsizei width,
                                        GLsizei height, GLint border,
                                        GLenum format, GLenum type,
                                        ScriptArrayBufferView srcData,
                                        unsigned long long srcOffset)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
}

void WebGL2RenderingContext::texSubImage2D(GLenum target, GLint level,
                                           GLint xoffset, GLint yoffset,
                                           GLsizei width, GLsizei height,
                                           GLenum format, GLenum type,
                                           GLintptr pboOffset)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
}

void WebGL2RenderingContext::texSubImage2D(GLenum target, GLint level,
                                           GLint xoffset, GLint yoffset,
                                           GLsizei width, GLsizei height,
                                           GLenum format, GLenum type,
                                           TexImageSource source)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
}

void WebGL2RenderingContext::texSubImage2D(GLenum target, GLint level,
                                           GLint xoffset, GLint yoffset,
                                           GLsizei width, GLsizei height,
                                           GLenum format, GLenum type,
                                           ScriptArrayBufferView srcData,
                                           unsigned long long srcOffset)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
}

void WebGL2RenderingContext::compressedTexImage2D(
    GLenum target, GLint level, GLenum internalformat, GLsizei width,
    GLsizei height, GLint border, GLsizei imageSize, GLintptr offset)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
}

void WebGL2RenderingContext::compressedTexImage2D(
    GLenum target, GLint level, GLenum internalformat, GLsizei width,
    GLsizei height, GLint border, ScriptArrayBufferView srcData,
    unsigned long long srcOffset, GLuint srcLengthOverride)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
}

void WebGL2RenderingContext::compressedTexSubImage2D(
    GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width,
    GLsizei height, GLenum format, GLsizei imageSize, GLintptr offset)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
}

void WebGL2RenderingContext::compressedTexSubImage2D(
    GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width,
    GLsizei height, GLenum format, ScriptArrayBufferView srcData,
    unsigned long long srcOffset, GLuint srcLengthOverride)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
}

void WebGL2RenderingContext::uniform1fv(
    Optional<WebGLUniformLocation*> location, Float32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    if (srcOffset != 0 || srcLength != 0) {
        STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
    }
    WebGLRenderingContext::uniform1fv(location, data);
}

void WebGL2RenderingContext::uniform2fv(
    Optional<WebGLUniformLocation*> location, Float32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    if (srcOffset != 0 || srcLength != 0) {
        STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
    }
    WebGLRenderingContext::uniform2fv(location, data);
}

void WebGL2RenderingContext::uniform3fv(
    Optional<WebGLUniformLocation*> location, Float32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    if (srcOffset != 0 || srcLength != 0) {
        STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
    }
    WebGLRenderingContext::uniform3fv(location, data);
}

void WebGL2RenderingContext::uniform4fv(
    Optional<WebGLUniformLocation*> location, Float32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    if (srcOffset != 0 || srcLength != 0) {
        STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
    }
    WebGLRenderingContext::uniform4fv(location, data);
}

void WebGL2RenderingContext::uniform1iv(
    Optional<WebGLUniformLocation*> location, Int32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    if (srcOffset != 0 || srcLength != 0) {
        STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
    }
    WebGLRenderingContext::uniform1iv(location, data);
}

void WebGL2RenderingContext::uniform2iv(
    Optional<WebGLUniformLocation*> location, Int32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    if (srcOffset != 0 || srcLength != 0) {
        STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
    }
    WebGLRenderingContext::uniform2iv(location, data);
}

void WebGL2RenderingContext::uniform3iv(
    Optional<WebGLUniformLocation*> location, Int32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    if (srcOffset != 0 || srcLength != 0) {
        STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
    }
    WebGLRenderingContext::uniform3iv(location, data);
}

void WebGL2RenderingContext::uniform4iv(
    Optional<WebGLUniformLocation*> location, Int32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    if (srcOffset != 0 || srcLength != 0) {
        STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
    }
    WebGLRenderingContext::uniform4iv(location, data);
}

void WebGL2RenderingContext::uniformMatrix2fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    if (srcOffset != 0 || srcLength != 0) {
        STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
    }
    WebGLRenderingContext::uniformMatrix2fv(location, transpose, data);
}

void WebGL2RenderingContext::uniformMatrix3fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    if (srcOffset != 0 || srcLength != 0) {
        STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
    }
    WebGLRenderingContext::uniformMatrix3fv(location, transpose, data);
}

void WebGL2RenderingContext::uniformMatrix4fv(
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    if (srcOffset != 0 || srcLength != 0) {
        STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
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
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
}

void WebGL2RenderingContext::readPixels(GLint x, GLint y, GLsizei width,
                                        GLsizei height, GLenum format,
                                        GLenum type,
                                        ScriptArrayBufferView dstData,
                                        unsigned long long dstOffset)
{
    STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
}

} // namespace Starfish

#endif // defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)
