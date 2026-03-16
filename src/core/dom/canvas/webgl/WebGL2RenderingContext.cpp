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
#include "core/dom/ExecutionContext.h"
#include "core/dom/canvas/webgl/WebGLExtensions.h"
#include "core/dom/canvas/webgl/WebGLProgram.h"
#include "core/dom/canvas/webgl/WebGLRenderingContextState.h"
#include "core/dom/canvas/webgl/util/TexImageHelper.h"
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

ScriptValue WebGL2RenderingContext::getParameter(GLenum pname)
{
    {
        ENTER_CONTEXT_SCOPE(scriptNull());

        switch (pname) {
        // DOMString
        case GL_SHADING_LANGUAGE_VERSION:
            return createScriptValue(
                createScriptASCIIString(kShadingLanguageVersion));
        case GL_VERSION:
            return createScriptValue(createScriptASCIIString(kVersion));
        // GLboolean
        case GL_RASTERIZER_DISCARD:
        case GL_TRANSFORM_FEEDBACK_ACTIVE:
        case GL_TRANSFORM_FEEDBACK_PAUSED: {
            std::vector<GLboolean> values(1);
            gl()->getBooleanv(pname, &values[0]);
            return createScriptValue(static_cast<bool>(values[0]));
        }
        // GLfloat
        case GL_MAX_TEXTURE_LOD_BIAS: {
            std::vector<GLfloat> values(1);
            gl()->getFloatv(pname, &values[0]);
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
            return createScriptValue(values[0]);
        }
        }
    }
    return WebGLRenderingContext::getParameter(pname);
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

// WebGL2RenderingContextBase

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

Optional<WebGLSync*> WebGL2RenderingContext::fenceSync(GLenum condition,
                                                       GLbitfield flags)
{
    ENTER_CONTEXT_SCOPE(Optional<WebGLSync*>());

    GLsync sync = gl()->fenceSync(condition, flags);
    return new WebGLSync(scriptBindingInstance(), this, sync);
}

GLboolean WebGL2RenderingContext::isSync(Optional<WebGLSync*> sync)
{
    ENTER_CONTEXT_SCOPE(false);

    if (!sync.hasValue() || sync.value()->context() != this ||
        sync.value()->invalidated()) {
        return false;
    }
    return gl()->isSync(sync.value()->glObject());
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
    value->markDeleted();
    gl()->deleteSync(value->glObject());
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
    return gl()->clientWaitSync(sync->glObject(), flags, timeout);
}

void WebGL2RenderingContext::waitSync(WebGLSync* sync, GLbitfield flags,
                                      GLint64 timeout)
{
    ENTER_CONTEXT_SCOPE();

    if (sync->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }
    gl()->waitSync(sync->glObject(), flags, timeout);
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
    // GLbitfield
    case GL_SYNC_FLAGS: {
        GLint value;
        gl()->getSynciv(sync->glObject(), pname, 1, nullptr, &value);
        if (hasGLError()) {
            return scriptNull();
        }
        return createScriptValue(static_cast<GLbitfield>(value));
    }
    // GLenum
    case GL_OBJECT_TYPE:
    case GL_SYNC_STATUS:
    case GL_SYNC_CONDITION: {
        GLint value;
        gl()->getSynciv(sync->glObject(), pname, 1, nullptr, &value);
        if (hasGLError()) {
            return scriptNull();
        }
        return createScriptValue(static_cast<GLenum>(value));
    }
    }
    setGLError(GL_INVALID_ENUM);
    return scriptNull();
}

WebGLVertexArrayObject* WebGL2RenderingContext::createVertexArray()
{
    ENTER_CONTEXT_SCOPE(nullptr);

    GLuint vao = 0;
    gl()->genVertexArrays(1, &vao);
    return new WebGLVertexArrayObject(scriptBindingInstance(), this, vao);
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

struct Combination {
    GLint internalFormat;
    GLenum format;
    GLenum type;
};

static const Combination combinations[] = {
    { GL_RGB, GL_RGB, GL_UNSIGNED_BYTE },
    { GL_RGB, GL_RGB, GL_UNSIGNED_SHORT_5_6_5 },
    { GL_RGBA, GL_RGBA, GL_UNSIGNED_BYTE },
    { GL_RGBA, GL_RGBA, GL_UNSIGNED_SHORT_4_4_4_4 },
    { GL_RGBA, GL_RGBA, GL_UNSIGNED_SHORT_5_5_5_1 },
    { GL_LUMINANCE_ALPHA, GL_LUMINANCE_ALPHA, GL_UNSIGNED_BYTE },
    { GL_LUMINANCE, GL_LUMINANCE, GL_UNSIGNED_BYTE },
    { GL_ALPHA, GL_ALPHA, GL_UNSIGNED_BYTE },
    { GL_R8, GL_RED, GL_UNSIGNED_BYTE },
    { GL_R8_SNORM, GL_RED, GL_BYTE },
    { GL_R16F, GL_RED, GL_HALF_FLOAT },
    { GL_R16F, GL_RED, GL_FLOAT },
    { GL_R32F, GL_RED, GL_FLOAT },
    { GL_R8UI, GL_RED_INTEGER, GL_UNSIGNED_BYTE },
    { GL_R8I, GL_RED_INTEGER, GL_BYTE },
    { GL_R16UI, GL_RED_INTEGER, GL_UNSIGNED_SHORT },
    { GL_R16I, GL_RED_INTEGER, GL_SHORT },
    { GL_R32UI, GL_RED_INTEGER, GL_UNSIGNED_INT },
    { GL_R32I, GL_RED_INTEGER, GL_INT },
    { GL_RG8, GL_RG, GL_UNSIGNED_BYTE },
    { GL_RG8_SNORM, GL_RG, GL_BYTE },
    { GL_RG16F, GL_RG, GL_HALF_FLOAT },
    { GL_RG16F, GL_RG, GL_FLOAT },
    { GL_RG32F, GL_RG, GL_FLOAT },
    { GL_RG8UI, GL_RG_INTEGER, GL_UNSIGNED_BYTE },
    { GL_RG8I, GL_RG_INTEGER, GL_BYTE },
    { GL_RG16UI, GL_RG_INTEGER, GL_UNSIGNED_SHORT },
    { GL_RG16I, GL_RG_INTEGER, GL_SHORT },
    { GL_RG32UI, GL_RG_INTEGER, GL_UNSIGNED_INT },
    { GL_RG32I, GL_RG_INTEGER, GL_INT },
    { GL_RGB8, GL_RGB, GL_UNSIGNED_BYTE },
    { GL_SRGB8, GL_RGB, GL_UNSIGNED_BYTE },
    { GL_RGB565, GL_RGB, GL_UNSIGNED_BYTE },
    { GL_RGB565, GL_RGB, GL_UNSIGNED_SHORT_5_6_5 },
    { GL_RGB8_SNORM, GL_RGB, GL_BYTE },
    { GL_R11F_G11F_B10F, GL_RGB, GL_UNSIGNED_INT_10F_11F_11F_REV },
    { GL_R11F_G11F_B10F, GL_RGB, GL_HALF_FLOAT },
    { GL_R11F_G11F_B10F, GL_RGB, GL_FLOAT },
    { GL_RGB9_E5, GL_RGB, GL_UNSIGNED_INT_5_9_9_9_REV },
    { GL_RGB9_E5, GL_RGB, GL_HALF_FLOAT },
    { GL_RGB9_E5, GL_RGB, GL_FLOAT },
    { GL_RGB16F, GL_RGB, GL_HALF_FLOAT },
    { GL_RGB16F, GL_RGB, GL_FLOAT },
    { GL_RGB32F, GL_RGB, GL_FLOAT },
    { GL_RGB8UI, GL_RGB_INTEGER, GL_UNSIGNED_BYTE },
    { GL_RGB8I, GL_RGB_INTEGER, GL_BYTE },
    { GL_RGB16UI, GL_RGB_INTEGER, GL_UNSIGNED_SHORT },
    { GL_RGB16I, GL_RGB_INTEGER, GL_SHORT },
    { GL_RGB32UI, GL_RGB_INTEGER, GL_UNSIGNED_INT },
    { GL_RGB32I, GL_RGB_INTEGER, GL_INT },
    { GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE },
    { GL_SRGB8_ALPHA8, GL_RGBA, GL_UNSIGNED_BYTE },
    { GL_RGBA8_SNORM, GL_RGBA, GL_BYTE },
    { GL_RGB5_A1, GL_RGBA, GL_UNSIGNED_BYTE },
    { GL_RGB5_A1, GL_RGBA, GL_UNSIGNED_SHORT_5_5_5_1 },
    { GL_RGB5_A1, GL_RGBA, GL_UNSIGNED_INT_2_10_10_10_REV },
    { GL_RGBA4, GL_RGBA, GL_UNSIGNED_BYTE },
    { GL_RGBA4, GL_RGBA, GL_UNSIGNED_SHORT_4_4_4_4 },
    { GL_RGB10_A2, GL_RGBA, GL_UNSIGNED_INT_2_10_10_10_REV },
    { GL_RGBA16F, GL_RGBA, GL_HALF_FLOAT },
    { GL_RGBA16F, GL_RGBA, GL_FLOAT },
    { GL_RGBA32F, GL_RGBA, GL_FLOAT },
    { GL_RGBA8UI, GL_RGBA_INTEGER, GL_UNSIGNED_BYTE },
    { GL_RGBA8I, GL_RGBA_INTEGER, GL_BYTE },
    { GL_RGB10_A2UI, GL_RGBA_INTEGER, GL_UNSIGNED_INT_2_10_10_10_REV },
    { GL_RGBA16UI, GL_RGBA_INTEGER, GL_UNSIGNED_SHORT },
    { GL_RGBA16I, GL_RGBA_INTEGER, GL_SHORT },
    { GL_RGBA32I, GL_RGBA_INTEGER, GL_INT },
    { GL_RGBA32UI, GL_RGBA_INTEGER, GL_UNSIGNED_INT },
    { GL_DEPTH_COMPONENT16, GL_DEPTH_COMPONENT, GL_UNSIGNED_SHORT },
    { GL_DEPTH_COMPONENT16, GL_DEPTH_COMPONENT, GL_UNSIGNED_INT },
    { GL_DEPTH_COMPONENT24, GL_DEPTH_COMPONENT, GL_UNSIGNED_INT },
    { GL_DEPTH_COMPONENT32F, GL_DEPTH_COMPONENT, GL_FLOAT },
    { GL_DEPTH24_STENCIL8, GL_DEPTH_STENCIL, GL_UNSIGNED_INT_24_8 },
    { GL_DEPTH32F_STENCIL8, GL_DEPTH_STENCIL,
      GL_FLOAT_32_UNSIGNED_INT_24_8_REV },
};

static bool isInternalFormatValid(GLint internalFormat, GLenum format,
                                  GLenum type)
{
    for (const Combination& combination : combinations) {
        if (internalFormat == combination.internalFormat &&
            format == combination.format && type == combination.type) {
            return true;
        }
    }
    return false;
}

static bool isSrcDataValid(Optional<ScriptArrayBufferView> pixels, GLenum type)
{
    if (pixels.hasValue() &&
        ((pixels.value()->isInt8ArrayObject() && type == GL_BYTE) ||
         (pixels.value()->isUint8ArrayObject() && type == GL_UNSIGNED_BYTE) ||
         (pixels.value()->isUint8ClampedArrayObject() &&
          type == GL_UNSIGNED_BYTE) ||
         (pixels.value()->isInt16ArrayObject() && type == GL_SHORT) ||
         (pixels.value()->isUint16ArrayObject() &&
          (type == GL_UNSIGNED_SHORT || type == GL_UNSIGNED_SHORT_5_6_5 ||
           type == GL_UNSIGNED_SHORT_5_5_5_1 ||
           type == GL_UNSIGNED_SHORT_4_4_4_4 || type == GL_HALF_FLOAT)) ||
         (pixels.value()->isInt32ArrayObject() && type == GL_INT) ||
         (pixels.value()->isUint32ArrayObject() &&
          (type == GL_UNSIGNED_INT || type == GL_UNSIGNED_INT_5_9_9_9_REV ||
           type == GL_UNSIGNED_INT_2_10_10_10_REV ||
           type == GL_UNSIGNED_INT_10F_11F_11F_REV ||
           type == GL_UNSIGNED_INT_24_8)) ||
         (pixels.value()->isFloat32ArrayObject() && type == GL_FLOAT))) {
        return true;
    }
    return false;
}

void WebGL2RenderingContext::texImage2D(GLenum target, GLint level,
                                        GLint internalFormat, GLsizei width,
                                        GLsizei height, GLint border,
                                        GLenum format, GLenum type,
                                        Optional<ScriptArrayBufferView> pixels)
{
    ENTER_CONTEXT_SCOPE();

    if (boundTextures().find(target) == boundTextures().end() &&
        !isBoundCubeMapTexture(target)) {
        setGLError(
            GL_INVALID_OPERATION,
            StringUtils::formatString("target (0x%04X) is not bound.", target)
                .c_str());
        return;
    }

    if (!isInternalFormatValid(internalFormat, format, type)) {
        setGLError(GL_INVALID_OPERATION,
                   StringUtils::formatString(
                       "The given parameters, internal format (0x%0fX), format "
                       "(0x%04X), and type (0x%04X) are not valid.",
                       internalFormat, format)
                       .c_str());
        return;
    }

    if (!isSrcDataValid(pixels, type)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    handleTexImageWithArrayBufferView(
        target, level, width, height, format, type, pixels,
        [&](const TexImageHelper* helper) {
            STARFISH_ASSERT(helper != nullptr);
            gl()->texImage2D(target, level, internalFormat, width, height, 0,
                             format, type, helper->data());
        },
        [&](const std::vector<GLubyte>& blackData) {
#if defined(PORT_PIXEL_ORDER_BGRA)
            if (format == GL_RGBA) {
                if (WebGLExtensionRegistry::instance()
                        .hasEXT_texture_format_BGRA8888()) {
                    // According to OpenGL ES specification, the format must
                    // match the base internal format (no conversions from
                    // one format to another during texture image processing
                    // are supported.)
                    internalFormat = GL_BGRA_EXT;
                    format = GL_BGRA_EXT;
                }
            }
#endif
            gl()->texImage2D(target, level, internalFormat, width, height, 0,
                             format, type, blackData.data());
        },
        [&](const std::vector<GLushort>& blackData) {
            gl()->texImage2D(target, level, internalFormat, width, height, 0,
                             format, type, blackData.data());
        });
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

} // namespace Starfish

#endif // defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)
