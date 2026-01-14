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
#include "core/dom/canvas/webgl/TexImageHelper.h"
#include "core/dom/canvas/webgl/WebGLProgram.h"
#include "core/dom/canvas/webgl/WebGLUniformLocation.h"
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
        // GLint
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
    case GL_UNIFORM_IS_ROW_MAJOR: {
        GLsizei count = uniformIndices.size();
        std::vector<GLint> values(count);
        glGetActiveUniformsiv(program->glObject(), count, uniformIndices.data(),
                              pname, values.data());
        return createScriptValue(
            createArray(scriptBindingInstance(),
                        std::vector<bool>(values.begin(), values.end())));
    }
    // sequence<GLenum>
    case GL_UNIFORM_TYPE: {
        GLsizei count = uniformIndices.size();
        std::vector<GLint> values(count);
        glGetActiveUniformsiv(program->glObject(), count, uniformIndices.data(),
                              pname, values.data());
        return createScriptValue(
            createTypedArray<Escargot::Uint32ArrayObjectRef>(
                scriptBindingInstance(),
                std::vector<GLenum>(values.begin(), values.end())));
    }
    // sequence<GLint>
    case GL_UNIFORM_ARRAY_STRIDE:
    case GL_UNIFORM_BLOCK_INDEX:
    case GL_UNIFORM_MATRIX_STRIDE:
    case GL_UNIFORM_OFFSET: {
        GLsizei count = uniformIndices.size();
        std::vector<GLint> values(count);
        glGetActiveUniformsiv(program->glObject(), count, uniformIndices.data(),
                              pname, values.data());
        return createScriptValue(
            createTypedArray<Escargot::Int32ArrayObjectRef>(
                scriptBindingInstance(), values));
    }
    // sequence<GLuint>
    case GL_UNIFORM_SIZE: {
        GLsizei count = uniformIndices.size();
        std::vector<GLint> values(count);
        glGetActiveUniformsiv(program->glObject(), count, uniformIndices.data(),
                              pname, values.data());
        return createScriptValue(
            createTypedArray<Escargot::Uint32ArrayObjectRef>(
                scriptBindingInstance(),
                std::vector<GLenum>(values.begin(), values.end())));
    }
    }
    setGLError(GL_INVALID_ENUM);
    return scriptNull();
}

// WebGL2RenderingContextOverloads

void WebGL2RenderingContext::bufferData(GLenum target, GLsizeiptr size,
                                        GLenum usage)
{
    WebGLRenderingContext::bufferData(target, size, usage);
}

void WebGL2RenderingContext::bufferData(GLenum target,
                                        Optional<AllowSharedBufferSource> data,
                                        GLenum usage)
{
    ENTER_CONTEXT_SCOPE();

    if (!data.hasValue()) {
        setGLError(GL_INVALID_VALUE);
        return;
    }

    if (data.value().isArrayBufferValue()) {
        ScriptArrayBuffer buffer = data.value().getArrayBufferValue();
        gl()->bufferData(target, buffer->byteLength(), buffer->rawBuffer(),
                         usage);
    } else if (data.value().isArrayBufferViewValue()) {
        ScriptArrayBufferView view = data.value().getArrayBufferViewValue();
        gl()->bufferData(target, view->byteLength(), view->rawBuffer(), usage);
    } else if (data.value().isSharedArrayBufferValue()) {
        ScriptSharedArrayBuffer buffer =
            data.value().getSharedArrayBufferValue();
        gl()->bufferData(target, buffer->byteLength(), buffer->rawBuffer(),
                         usage);
    } else {
        setGLError(GL_INVALID_VALUE);
    }
}

void WebGL2RenderingContext::bufferSubData(GLenum target,
                                           GLintptr dstByteOffset,
                                           AllowSharedBufferSource srcData)
{
    WebGLRenderingContext::bufferSubData(target, dstByteOffset, srcData);
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
                                        GLint internalFormat, GLenum format,
                                        GLenum type, TexImageSource source)
{
    ENTER_CONTEXT_SCOPE();

    // TODO: handle DOM exception with referring to CanvasImageSource. If this
    // function is called with an HTMLImageElement or HTMLVideoElement whose
    // origin differs from the origin of the containing Document, or with an
    // HTMLCanvasElement, ImageBitmap or OffscreenCanvas whose bitmap's
    // origin-clean flag is set to false, a SECURITY_ERR exception must be
    // thrown. See Origin Restrictions.

    if (boundTextures().find(target) == boundTextures().end() &&
        !isBoundCubeMapTexture(target)) {
        setGLError(
            GL_INVALID_OPERATION,
            StringUtils::formatString("target (0x%04X) is not bound.", target)
                .c_str());
        return;
    }

    if (static_cast<GLenum>(internalFormat) != format) {
        // The format, in WebGL 1, must be the same as internalformat. See:
        // https://developer.mozilla.org/en-US/docs/Web/API/WebGLRenderingContext/texImage2D
        // TODO: add an identifier for WebGL version and use it.
        setGLError(GL_INVALID_OPERATION,
                   StringUtils::formatString(
                       "The given parameters, internal format (0x%0fX) and "
                       "format (0x%04X) are not same.",
                       internalFormat, format)
                       .c_str());
        return;
    }

    handleTexImageWithImageSource(
        format, type, source, [&](const TexImageHelper* helper) {
            STARFISH_ASSERT(helper != nullptr);

            TRACE(WEBGL_V, KV(glValueString(internalFormat)),
                  KV(glValueString(
                      helper->dataFormat().valueOr(internalFormat))));
            TRACE(WEBGL_V, KV(glValueString(format)),
                  KV(glValueString(helper->dataFormat().valueOr(format))));
            TRACE(WEBGL_V, KV(glValueString(type)));

            // Uploads the given image data to the currently bound texture.
            gl()->texImage2D(
                target, level, helper->dataFormat().valueOr(internalFormat),
                helper->sourceImage().width, helper->sourceImage().height, 0,
                helper->dataFormat().valueOr(format), type, helper->data());
        });
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
    Optional<WebGLUniformLocation*> mayBeLocation, GLboolean transpose,
    Float32List variant, unsigned long long srcOffset, GLuint srcLength)
{
    if (srcOffset != 0 || srcLength != 0) {
        STARFISH_UNIMPLEMENTED("WebGL2RenderingContextOverloads");
    }
    ENTER_CONTEXT_SCOPE();
    /* location is nullable. */
    if (!mayBeLocation) {
        return;
    }
    WebGLUniformLocation* location = mayBeLocation.value();
    if (!isFromCurrentProgram(location)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }
    if (variant.isFloat32ArrayValue()) {
        Escargot::Float32ArrayObjectRef* values =
            variant.getFloat32ArrayValue();
        const size_t arrayLength = values->arrayLength();
        uint8_t* rawBuffer = const_cast<uint8_t*>(values->rawBuffer());
        if (arrayLength > 0) {
            /* count specifies the number of matrices. */
            gl()->uniformMatrix4fv(location->location(), arrayLength / (4 * 4),
                                   transpose,
                                   reinterpret_cast<GLfloat*>(rawBuffer));
        }
    } else {
        STARFISH_ASSERT(variant.isSequenceOfGLfloatValue());
        const GCAtomicVector<double> v = variant.getSequenceOfGLfloatValue();
        std::vector<GLfloat> vector;
        vector.reserve(v.size());
        for (const double& value : v) {
            vector.push_back(static_cast<GLfloat>(value));
        }
        if (!vector.empty()) {
            /* count specifies the number of matrices. */
            gl()->uniformMatrix4fv(location->location(),
                                   vector.size() / (4 * 4), transpose,
                                   vector.data());
        }
    }
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
