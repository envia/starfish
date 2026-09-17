/*
 * Copyright (c) 2019-present Samsung Electronics Co., Ltd
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
#include "core/dom/canvas/webgl/WebGLRenderingContext.h"
#include "core/dom/canvas/HTMLCanvasElement.h"
#include "core/dom/canvas/CanvasImageSource.h"
#include "core/dom/HTMLImageElement.h"
#include "core/dom/ImageBitmap.h"
#include "core/dom/ExecutionContext.h"
#include "core/dom/canvas/webgl/WebGLExtensions.h"
#include "core/modules/canvas/image/NativeImageData.h"
#include "core/util/debug/Trace.h"
#include "core/util/String.h"
#include "core/dom/canvas/webgl/gl/GLContext.h"
#include "core/dom/canvas/webgl/WebGLActiveInfo.h"
#include "core/dom/canvas/webgl/WebGLBuffer.h"
#include "core/dom/canvas/webgl/WebGLShader.h"
#include "core/dom/canvas/webgl/WebGLProgram.h"
#include "core/dom/canvas/webgl/WebGLTexture.h"
#include "core/dom/canvas/webgl/WebGLFramebuffer.h"
#include "core/dom/canvas/webgl/WebGLRenderbuffer.h"
#include "core/dom/canvas/webgl/WebGLUniformLocation.h"
#include "core/modules/canvas/Canvas.h"
#include "core/dom/canvas/CanvasRenderingContext.h"
#include "core/dom/canvas/CanvasRenderingContext2DMixIn.h"
#include "core/dom/canvas/webgl/WebGLRenderingContextState.h"
#include "binding/ScriptBindingInstance.h"
#include "binding/generated/Float32ArrayOrSequenceOfGLfloatUnion.h"
#include "binding/generated/Int32ArrayOrSequenceOfGLintUnion.h"
#include "binding/generated/ArrayBufferOrSharedArrayBufferOrArrayBufferViewUnion.h"
#include "binding/generated/ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElementUnion.h"
#include "core/dom/canvas/webgl/WebGLOES_VertexArrayObject.h"
#include "core/dom/canvas/webgl/WebGLShaderPrecisionFormat.h"
#include "core/page/WebView.h"
#include "core/modules/renderer/Renderer.h"

#include "platform/canvas/gl/IncludeGL.h"
#include "platform/canvas/gl/GL.h"

#include <EscargotPublic.h>
#include <cstdlib>
#include <sstream>
#include <iomanip>
#include <limits>

#define kMaximumUniformAndAttributeLocationLengths 256
#define kMaximumSupportedStride 255

/* WebGL-specific enums */
static const GLenum kUNPACK_FLIP_Y_WEBGL = 0x9240;
static const GLenum kUNPACK_PREMULTIPLY_ALPHA_WEBGL = 0x9241;
static const GLenum kCONTEXT_LOST_WEBGL = 0x9242;
static const GLenum kUNPACK_COLORSPACE_CONVERSION_WEBGL = 0x9243;
static const GLenum kBROWSER_DEFAULT_WEBGL = 0x9244;
static const GLenum kIMPLEMENTATION_COLOR_READ_TYPE = 0x8B9A;
static const GLenum kIMPLEMENTATION_COLOR_READ_FORMAT = 0x8B9B;

/* WebGL constants */
static constexpr char kShadingLanguageVersion[] = "WebGL GLSL ES 1.0";
static constexpr char kVersion[] = "WebGL 1.0";

namespace Starfish {

inline static std::string hex(GLenum name)
{
    return StringUtils::formatString("0x%04X", name);
}

WebGLRenderingContext::WebGLRenderingContext(HTMLCanvasElement* canvasElement)
    : WebGLRenderingContextBaseMixIn(canvasElement)
{
    m_unpackFlipY = false;
    m_unpackPremultiplyAlpha = false;
    m_unpackColorspaceConversion = kBROWSER_DEFAULT_WEBGL;
    m_isContextLost = false;
    m_hasPendingJobsBetweenFrames = false;
    m_pendingClearMask = 0;
    m_activeTexture = GL_TEXTURE0;
    m_unpackColorSpace = String::createASCIIString("srgb");
    m_drawingBufferColorSpace = String::createASCIIString("srgb");
    m_state = new WebGLRenderingContextState();
    m_gl = m_ownerHTMLCanvasElement->webView()->renderer()->gl();
    GC_REGISTER_FINALIZER_NO_ORDER(
        this,
        [](void* obj, void* cd) {
            auto self = reinterpret_cast<WebGLRenderingContext*>(obj);
            GLErrorSet().swap(self->m_GLErrors);
            GLTextureMap().swap(self->m_boundTextures);
        },
        NULL, NULL, NULL);
}

WebGLRenderingContext::~WebGLRenderingContext()
{
}

ScriptBindingInstance* WebGLRenderingContext::scriptBindingInstance()
{
    return executionContext()->scriptBindingInstance();
}

void WebGLRenderingContext::preInitialize(ScriptValue contextAttributes)
{
    STARFISH_ASSERT(m_isContextAttributesChecked == false);

    // Check context attributes
    m_isContextAttributesChecked = true;

    if (contextAttributes->isObject()) {
#define SET_ATTRIBUTE(str, attribute)                           \
    {                                                           \
        auto key = StringRef::createFromASCII(#str);            \
        if (object->has(state, key)) {                          \
            ValueRef* value = object->get(state, key);          \
            if (value->isBoolean()) {                           \
                STARFISH_LOG_INFO("%s : %d", #str,              \
                                  value->asBoolean() ? 1 : 0);  \
                attributes->set##attribute(value->asBoolean()); \
            }                                                   \
        }                                                       \
    }

        Evaluator::EvaluatorResult evaluated = Evaluator::execute(
            scriptBindingInstance()->scriptContext(),
            [](ExecutionStateRef* state, ObjectRef* object,
               WebGLContextAttributes* attributes) -> ValueRef* {
                // powerPreference: string
                auto key = StringRef::createFromASCII("powerPreference");
                if (object->has(state, key)) {
                    ValueRef* value = object->get(state, key);
                    if (value->isString()) {
                        std::string powerPreference =
                            value->asString()->toStdUTF8String();
                        STARFISH_LOG_INFO("powerPreference : %s",
                                          powerPreference.c_str());
                        attributes->setPowerPreference(String::fromUTF8(
                            powerPreference.c_str(), powerPreference.length()));
                    }
                }

                // the others: bool
                SET_ATTRIBUTE(alpha, Alpha);
                SET_ATTRIBUTE(depth, Depth);
                SET_ATTRIBUTE(stencil, Stencil);
                SET_ATTRIBUTE(antialias, Antialias);
                SET_ATTRIBUTE(premultipliedAlpha, PremultipliedAlpha);
                SET_ATTRIBUTE(preserveDrawingBuffer, PreserveDrawingBuffer);
                SET_ATTRIBUTE(desynchronized, Desynchronized);
                SET_ATTRIBUTE(failIfMajorPerformanceCaveat,
                              FailIfMajorPerformanceCaveat);
                return ValueRef::createUndefined();
            },
            contextAttributes->asObject(), &m_attributes);

#undef SET_ATTRIBUTE
        m_frameBufferAttributes.alpha = m_attributes.alpha();
        m_frameBufferAttributes.antialias = m_attributes.antialias();
        m_frameBufferAttributes.depth = m_attributes.depth();
        m_frameBufferAttributes.stencil = m_attributes.stencil();
    }
}

void WebGLRenderingContext::initialize()
{
    WebGLRenderingContextBaseMixIn::initialize();

    STARFISH_ASSERT(m_canvasSurface != nullptr);

    // 2.3 The WebGL Viewport
    //
    // Upon creation of WebGL context context, the viewport is initialized to a
    // rectangle with origin at (0, 0) and width and height equal to
    // (context.drawingBufferWidth, context.drawingBufferHeight).

    viewport(0, 0, drawingBufferWidth(), drawingBufferHeight());

    // bind default frame buffer
    GLContextScope contextScope(m_context);
    if (contextScope.hasError()) {
        return;
    }
    ensureExtensionRegistryInitialized();
    m_gl->bindFramebuffer(GL_FRAMEBUFFER, m_framebufferTexture->fbo());
}

void WebGLRenderingContext::flushDrawingCommands()
{
    GLRevertableContextScope scope(
        m_context, executionContext()->webBase()->asWebView()->renderer());
    // we need to bind 0(screen) buffer for sending commands to gpu
    m_gl->bindFramebuffer(GL_DRAW_FRAMEBUFFER, 0);
    m_gl->bindFramebuffer(GL_DRAW_FRAMEBUFFER, getCurrentFBO());
}

void WebGLRenderingContext::flushForReadback()
{
    if (!m_canvasSurface) {
        return;
    }

    WebGLRenderingContextBaseMixIn::flushForReadback();

    flushDrawingCommands();

    GLRevertableContextScope scope(
        m_context, executionContext()->webBase()->asWebView()->renderer());

    GLint prevReadFbo = 0;
    m_gl->getIntegerv(GL_READ_FRAMEBUFFER_BINDING, &prevReadFbo);
    m_gl->bindFramebuffer(GL_READ_FRAMEBUFFER, m_framebufferTexture->fbo());

    size_t width = m_canvasSurface->bufferWidth();
    size_t height = m_canvasSurface->bufferHeight();
    size_t stride = m_canvasSurface->bufferStride();
    STARFISH_ASSERT(stride % 4 == 0 && stride >= width * 4);

    uint8_t* buffer = m_canvasSurface->mapBuffer();

    GLint prevPackAlignment = 4;
    GLint prevPackRowLength = 0;
    GLint prevPackSkipPixels = 0;
    GLint prevPackSkipRows = 0;
    GLint prevPixelPackBuffer = 0;
    m_gl->getIntegerv(GL_PACK_ALIGNMENT, &prevPackAlignment);
    m_gl->getIntegerv(GL_PACK_ROW_LENGTH, &prevPackRowLength);
    m_gl->getIntegerv(GL_PACK_SKIP_PIXELS, &prevPackSkipPixels);
    m_gl->getIntegerv(GL_PACK_SKIP_ROWS, &prevPackSkipRows);
    m_gl->getIntegerv(GL_PIXEL_PACK_BUFFER_BINDING, &prevPixelPackBuffer);
    m_gl->pixelStorei(GL_PACK_ALIGNMENT, 1);
    m_gl->pixelStorei(GL_PACK_ROW_LENGTH, static_cast<GLint>(stride / 4));
    m_gl->pixelStorei(GL_PACK_SKIP_PIXELS, 0);
    m_gl->pixelStorei(GL_PACK_SKIP_ROWS, 0);
    m_gl->bindBuffer(GL_PIXEL_PACK_BUFFER, 0);

    m_gl->readPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, buffer);

    m_gl->pixelStorei(GL_PACK_ALIGNMENT, prevPackAlignment);
    m_gl->pixelStorei(GL_PACK_ROW_LENGTH, prevPackRowLength);
    m_gl->pixelStorei(GL_PACK_SKIP_PIXELS, prevPackSkipPixels);
    m_gl->pixelStorei(GL_PACK_SKIP_ROWS, prevPackSkipRows);
    m_gl->bindBuffer(GL_PIXEL_PACK_BUFFER,
                     static_cast<GLuint>(prevPixelPackBuffer));

    m_gl->bindFramebuffer(GL_READ_FRAMEBUFFER,
                          static_cast<GLuint>(prevReadFbo));

    for (size_t top = 0; top < height / 2; ++top) {
        size_t bot = height - 1 - top;
        uint8_t* pTop = buffer + top * stride;
        uint8_t* pBot = buffer + bot * stride;
        std::swap_ranges(pTop, pTop + width * 4, pBot);
    }

#if defined(PORT_PIXEL_ORDER_BGRA)
    for (size_t row = 0; row < height; ++row) {
        uint8_t* p = buffer + row * stride;
        for (size_t col = 0; col < width; ++col) {
            std::swap(p[col * 4 + 0], p[col * 4 + 2]);
        }
    }
#endif
}

void WebGLRenderingContext::flushForCompositing()
{
    // Unlike other rendering contexts, do not flushForReadback() here.
    // The compositor consumes the GPU texture directly, and the CPU
    // readback in flushForReadback() is too expensive to run every frame.
    flushDrawingCommands();

    // NOTE: According to the specification, by default the contents of
    // the drawing buffer shall be cleared to their default values after
    // compositing.
    // However, as of now, it's difficult to know when compositing and GL
    // rendering actually end, so we leave the clearing as a pending job
    // and let it be done lazily. The assumption here is that the engine will
    // invoke this `flushForCompositing()` every frame after we call
    // `setNeedsComposite()`.

    m_hasPendingJobsBetweenFrames = true;
}

void WebGLRenderingContext::onResize()
{
    WebGLRenderingContextBaseMixIn::onResize();

    // bind default frame buffer
    GLContextScope contextScope(m_context);
    m_gl->bindFramebuffer(GL_FRAMEBUFFER, m_framebufferTexture->fbo());
}

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
        if (hasNewGLError()) {                       \
            TRACE(WEBGL,                             \
                  "\033[33m"                         \
                  "GL error detected."               \
                  "\033[0m");                        \
        }                                            \
    });
#endif

GLenum WebGLRenderingContext::getError()
{
    GLContextScope contextScope(m_context);

    hasNewGLError();

    GLenum code = GL_NO_ERROR;
    if (!m_GLErrors.empty()) {
        code = *m_GLErrors.begin();
        m_GLErrors.erase(m_GLErrors.begin());
    }
    return code;
}

GLsizei WebGLRenderingContext::drawingBufferWidth() const
{
    return m_canvasSurface->bufferWidth();
}

GLsizei WebGLRenderingContext::drawingBufferHeight() const
{
    return m_canvasSurface->bufferHeight();
}

static bool isPredefinedColorSpace(String* value)
{
    STARFISH_ASSERT(value != nullptr);
    // Refs: https://html.spec.whatwg.org/multipage/canvas.html#2dcontext
    // enum PredefinedColorSpace { "srgb", "display-p3" };
    if (value->equals("srgb") || value->equals("display-p3")) {
        return true;
    }
    return false;
}

String* WebGLRenderingContext::drawingBufferColorSpace()
{
    return m_drawingBufferColorSpace;
}

void WebGLRenderingContext::setDrawingBufferColorSpace(String* value)
{
    if (isPredefinedColorSpace(value)) {
        m_drawingBufferColorSpace = value;
    }
}

String* WebGLRenderingContext::unpackColorSpace()
{
    return m_unpackColorSpace;
}

void WebGLRenderingContext::setUnpackColorSpace(String* value)
{
    if (isPredefinedColorSpace(value)) {
        m_unpackColorSpace = value;
    }
}

Optional<WebGLContextAttributes> WebGLRenderingContext::getContextAttributes()
{
    ENTER_CONTEXT_SCOPE(Optional<WebGLContextAttributes>());

    return m_attributes;
}

Optional<GCVector<String*>> WebGLRenderingContext::getSupportedExtensions()
{
    ENTER_CONTEXT_SCOPE(Optional<GCVector<String*>>());

    if (!ensureExtensionRegistryInitialized()) {
        return Optional<GCVector<String*>>();
    }
    return WebGLExtensionRegistry::instance().getSupportedExtensions(
        webGLVersion());
}

bool WebGLRenderingContext::ensureExtensionRegistryInitialized()
{
    return WebGLExtensionRegistry::instance().initialize(m_gl);
}

bool WebGLRenderingContext::isContextLost()
{
    return m_isContextLost;
}

Optional<ScriptObject> WebGLRenderingContext::getExtension(
    String* requestedName)
{
    ENTER_CONTEXT_SCOPE(Optional<ScriptObject>());

    if (!ensureExtensionRegistryInitialized()) {
        return Optional<ScriptObject>();
    }
    // TODO: An attempt to use any features of an extension without first
    // calling getExtension to enable it must generate an appropriate GL
    // error and must not make use of the feature.

    std::string name = requestedName->toUTF8NonGCString();
    const auto& iter = m_enabledExtensions.find(name);
    if (iter != m_enabledExtensions.end()) {
        // Multiple calls to getExtension with the same extension
        // string, taking into account case-insensitive comparison, must
        // return the same object as long as the extension is enabled.
        return iter->second;
    }

    Optional<ExtensionGenerator> maybeGenerator =
        WebGLExtensionRegistry::instance().getGenerator(name, webGLVersion());

    if (!maybeGenerator.hasValue()) {
        return Optional<ScriptObject>();
    }

    ScriptObject object = maybeGenerator.value()(scriptBindingInstance(), this);
    m_enabledExtensions.insert({ name, object });
    return object;
}

void WebGLRenderingContext::activeTexture(GLenum texture)
{
    ENTER_CONTEXT_SCOPE();

    // Preserve older native errors before testing whether this state change
    // succeeded. Release builds do not drain errors at every API exit.
    hasNewGLError();
    m_gl->activeTexture(texture);
    if (!hasNewGLError()) {
        m_activeTexture = texture;
    }
}

void WebGLRenderingContext::attachShader(WebGLProgram* program,
                                         WebGLShader* shader)
{
    if (!isFromCurrentContext(program) || !isFromCurrentContext(shader)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    ENTER_CONTEXT_SCOPE();

    m_gl->attachShader(program->glObject(), shader->glObject());
    program->addAttachedShader(shader);
}

void WebGLRenderingContext::bindAttribLocation(WebGLProgram* program,
                                               GLuint index, String* name)
{
    ENTER_CONTEXT_SCOPE();

    if (!isFromCurrentContext(program)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    if (!checkAttribOrUniformName(name)) {
        return;
    }

    m_gl->bindAttribLocation(program->glObject(), index, CSTR(name));
}

void WebGLRenderingContext::bindBuffer(GLenum target,
                                       Optional<WebGLBuffer*> buffer)
{
    ENTER_CONTEXT_SCOPE();

    if (buffer.hasValue()) {
        WebGLBuffer* value = buffer.value();

        if (value->target() != GL_NONE && value->target() != target) {
            // An attempt to bind a buffer object to the other target will
            // generate an INVALID_OPERATION error, and the current binding will
            // remain untouched. (Note: This isn't a GLES Spec., but WebGL one.
            // We need to set it directly, not use a retrieved value.)
            setGLError(GL_INVALID_OPERATION);
            return;
        }

        m_gl->bindBuffer(target, value->glObject());
        m_state->setBoundBuffer(target, value);

        // A given WebGLBuffer object may only be bound to one of the
        // ARRAY_BUFFER or ELEMENT_ARRAY_BUFFER target in its lifetime.
        value->setTargetOnce(target);
    } else {
        // If the buffer is null then any buffer currently bound is unbound.
        m_gl->bindBuffer(target, 0);
        m_state->setBoundBuffer(target, nullptr);
    }
}

void WebGLRenderingContext::bindFramebuffer(
    GLenum target, Optional<WebGLFramebuffer*> maybeFramebuffer)
{
    ENTER_CONTEXT_SCOPE();

    if (maybeFramebuffer.hasValue()) {
        WebGLFramebuffer* frameBuffer = maybeFramebuffer.value();

        if (!isFromCurrentContext(frameBuffer)) {
            setGLError(GL_INVALID_OPERATION);
            return;
        }

        if (frameBuffer->isDeleted()) {
            setGLError(GL_INVALID_OPERATION);
            return;
        }

        if (target != GL_FRAMEBUFFER) {
            // NOTE: how to handle this case is not found in the specification.
            return;
        }

        m_gl->bindFramebuffer(target, frameBuffer->glObject());
        m_state->setWebGLFramebuffer(frameBuffer);
    } else {
        m_gl->bindFramebuffer(target, m_framebufferTexture->fbo());
        m_state->setWebGLFramebuffer(nullptr);
    }
}

void WebGLRenderingContext::bindRenderbuffer(
    GLenum target, Optional<WebGLRenderbuffer*> maybeRenderbuffer)
{
    ENTER_CONTEXT_SCOPE();

    if (maybeRenderbuffer.hasValue()) {
        WebGLRenderbuffer* renderBuffer = maybeRenderbuffer.value();

        if (!isFromCurrentContext(renderBuffer)) {
            setGLError(GL_INVALID_OPERATION);
            return;
        }

        if (renderBuffer->isDeleted()) {
            setGLError(GL_INVALID_OPERATION);
            return;
        }

        if (target != GL_RENDERBUFFER) {
            // NOTE: how to handle this case is not found in the specification.
            return;
        }

        m_gl->bindRenderbuffer(target, renderBuffer->glObject());
    } else {
        m_gl->bindRenderbuffer(target, 0);
    }
}

void WebGLRenderingContext::bindTexture(GLenum target,
                                        Optional<WebGLTexture*> maybeTexture)
{
    ENTER_CONTEXT_SCOPE();
    hasNewGLError();

    if (maybeTexture.hasValue()) {
        WebGLTexture* texture = maybeTexture.value();

        if (!isFromCurrentContext(texture)) {
            setGLError(GL_INVALID_OPERATION);
            return;
        }

        if (texture->isDeleted()) {
            setGLError(GL_INVALID_OPERATION);
            return;
        }

        m_gl->bindTexture(target, texture->glObject());
        if (!hasNewGLError()) {
            m_boundTextures[(uint64_t(m_activeTexture) << 32) | target] =
                texture;
        }
    } else {
        m_gl->bindTexture(target, 0);
        if (!hasNewGLError()) {
            m_boundTextures.erase((uint64_t(m_activeTexture) << 32) | target);
        }
    }
}

void WebGLRenderingContext::blendColor(GLclampf red, GLclampf green,
                                       GLclampf blue, GLclampf alpha)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->blendColor(red, green, blue, alpha);
}

void WebGLRenderingContext::blendEquation(GLenum mode)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->blendEquation(mode);
}

void WebGLRenderingContext::blendEquationSeparate(GLenum modeRGB,
                                                  GLenum modeAlpha)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->blendEquationSeparate(modeRGB, modeAlpha);
}

void WebGLRenderingContext::blendFunc(GLenum sfactor, GLenum dfactor)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->blendFunc(sfactor, dfactor);
}

void WebGLRenderingContext::blendFuncSeparate(GLenum srcRGB, GLenum dstRGB,
                                              GLenum srcAlpha, GLenum dstAlpha)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->blendFuncSeparate(srcRGB, dstRGB, srcAlpha, dstAlpha);
}

GLenum WebGLRenderingContext::checkFramebufferStatus(GLenum target)
{
    ENTER_CONTEXT_SCOPE(GL_FRAMEBUFFER_UNSUPPORTED);

    if (m_isContextLost) {
        return GL_FRAMEBUFFER_UNSUPPORTED;
    }

    return m_gl->checkFramebufferStatus(target);
}

void WebGLRenderingContext::clear(uint32_t mask)
{
    ENTER_CONTEXT_SCOPE();

    completePendingJobs();

    m_gl->clear(mask);
    m_ownerHTMLCanvasElement->setNeedsComposite();
}

void WebGLRenderingContext::clearColor(float red, float green, float blue,
                                       float alpha)
{
    ENTER_CONTEXT_SCOPE();

    setPendingClearMask(GL_COLOR_BUFFER_BIT);

    m_gl->clearColor(red, green, blue, alpha);

    TRACE(WEBGL_V, KV(red), KV(green), KV(blue), KV(alpha));
}

void WebGLRenderingContext::clearDepth(GLclampf depth)
{
    ENTER_CONTEXT_SCOPE();

    if (!m_attributes.depth()) {
        return;
    }

    setPendingClearMask(GL_DEPTH_BUFFER_BIT);

    m_gl->clearDepthf(depth);

    TRACE(WEBGL_V, KV(depth));
}

void WebGLRenderingContext::clearStencil(GLint s)
{
    ENTER_CONTEXT_SCOPE();

    if (!m_attributes.stencil()) {
        return;
    }

    setPendingClearMask(GL_STENCIL_BUFFER_BIT);

    m_gl->clearStencil(s);
    TRACE(WEBGL_V, KV(s));
}

void WebGLRenderingContext::colorMask(GLboolean red, GLboolean green,
                                      GLboolean blue, GLboolean alpha)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->colorMask(red, green, blue, alpha);
}

void WebGLRenderingContext::compileShader(WebGLShader* shader)
{
    ENTER_CONTEXT_SCOPE();

    if (!isFromCurrentContext(shader)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    m_gl->compileShader(shader->glObject());
}

void WebGLRenderingContext::copyTexImage2D(GLenum target, GLint level,
                                           GLenum internalformat, GLint x,
                                           GLint y, GLsizei width,
                                           GLsizei height, GLint border)
{
    ENTER_CONTEXT_SCOPE();

    if (!boundTexture(target)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    hasNewGLError();
    m_gl->copyTexImage2D(target, level, internalformat, x, y, width, height,
                         border);
    recordTextureImage(target, level, GL_UNSIGNED_BYTE);
}

void WebGLRenderingContext::copyTexSubImage2D(GLenum target, GLint level,
                                              GLint xoffset, GLint yoffset,
                                              GLint x, GLint y, GLsizei width,
                                              GLsizei height)
{
    ENTER_CONTEXT_SCOPE();

    if (!boundTexture(target)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }
    m_gl->copyTexSubImage2D(target, level, xoffset, yoffset, x, y, width,
                            height);
}

WebGLBuffer* WebGLRenderingContext::createBuffer()
{
    ENTER_CONTEXT_SCOPE(nullptr);

    GLuint buffer = 0;
    m_gl->genBuffers(1, &buffer);
    return new WebGLBuffer(scriptBindingInstance(), this, buffer);
}

WebGLFramebuffer* WebGLRenderingContext::createFramebuffer()
{
    ENTER_CONTEXT_SCOPE(nullptr);

    GLuint fbo = 0;
    m_gl->genFramebuffers(1, &fbo);
    return new WebGLFramebuffer(scriptBindingInstance(), this, fbo);
}

WebGLProgram* WebGLRenderingContext::createProgram()
{
    ENTER_CONTEXT_SCOPE(nullptr);
    return new WebGLProgram(scriptBindingInstance(), this,
                            m_gl->createProgram());
}

WebGLRenderbuffer* WebGLRenderingContext::createRenderbuffer()
{
    ENTER_CONTEXT_SCOPE(nullptr);

    GLuint rbo = 0;
    m_gl->genRenderbuffers(1, &rbo);
    return new WebGLRenderbuffer(scriptBindingInstance(), this, rbo);
}

WebGLShader* WebGLRenderingContext::createShader(unsigned long type)
{
    ENTER_CONTEXT_SCOPE(nullptr);

    if (type != GL_VERTEX_SHADER && type != GL_FRAGMENT_SHADER) {
        setGLError(GL_INVALID_ENUM);
        return nullptr;
    }
    return new WebGLShader(scriptBindingInstance(), this,
                           m_gl->createShader(type));
}

WebGLTexture* WebGLRenderingContext::createTexture()
{
    ENTER_CONTEXT_SCOPE(nullptr);

    GLuint textureId = 0;
    m_gl->genTextures(1, &textureId);
    return new WebGLTexture(scriptBindingInstance(), this, textureId);
}

void WebGLRenderingContext::cullFace(GLenum mode)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->cullFace(mode);
}

#define IMPLEMENT_DELETE_BUFFERS(Name, Deleter)                            \
    void WebGLRenderingContext::delete##Name(Optional<WebGL##Name*> maybe) \
    {                                                                      \
        ENTER_CONTEXT_SCOPE();                                             \
        if (maybe.hasValue()) {                                            \
            WebGL##Name* value = maybe.value();                            \
            if (!isFromCurrentContext(value)) {                            \
                setGLError(GL_INVALID_OPERATION);                          \
                return;                                                    \
            }                                                              \
            if (value->isDeleted()) {                                      \
                return;                                                    \
            }                                                              \
            GLuint buffer = value->glObject();                             \
            Deleter(1, &buffer);                                           \
            value->markDeleted();                                          \
        }                                                                  \
    }

IMPLEMENT_DELETE_BUFFERS(Buffer, m_gl->deleteBuffers);
IMPLEMENT_DELETE_BUFFERS(Framebuffer, m_gl->deleteFramebuffers);
IMPLEMENT_DELETE_BUFFERS(Renderbuffer, m_gl->deleteRenderbuffers);
#undef IMPLEMENT_DELETE_BUFFERS

void WebGLRenderingContext::deleteTexture(Optional<WebGLTexture*> texture)
{
    ENTER_CONTEXT_SCOPE();
    if (!texture) {
        return;
    }
    if (!isFromCurrentContext(texture.value())) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }
    if (texture->isDeleted()) {
        return;
    }
    GLuint object = texture->glObject();
    m_gl->deleteTextures(1, &object);
    texture->markDeleted();
    for (auto it = m_boundTextures.begin(); it != m_boundTextures.end();) {
        if (it->second == texture.value()) {
            it = m_boundTextures.erase(it);
        } else {
            ++it;
        }
    }
}

#define IMPLEMENT_DELETE_OBJECT(Name, Deleter)                             \
    void WebGLRenderingContext::delete##Name(Optional<WebGL##Name*> maybe) \
    {                                                                      \
        ENTER_CONTEXT_SCOPE();                                             \
        if (maybe.hasValue()) {                                            \
            WebGL##Name* value = maybe.value();                            \
            if (!isFromCurrentContext(value)) {                            \
                setGLError(GL_INVALID_OPERATION);                          \
                return;                                                    \
            }                                                              \
            if (value->isDeleted()) {                                      \
                return;                                                    \
            }                                                              \
            Deleter(value->glObject());                                    \
            value->markDeleted();                                          \
        }                                                                  \
    }

IMPLEMENT_DELETE_OBJECT(Program, m_gl->deleteProgram);
IMPLEMENT_DELETE_OBJECT(Shader, m_gl->deleteShader);
#undef IMPLEMENT_DELETE_OBJECT

void WebGLRenderingContext::depthFunc(GLenum func)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->depthFunc(func);
}

void WebGLRenderingContext::depthMask(GLboolean flag)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->depthMask(flag);
}

void WebGLRenderingContext::depthRange(GLclampf zNear, GLclampf zFar)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->depthRangef(zNear, zFar);
}

void WebGLRenderingContext::detachShader(WebGLProgram* program,
                                         WebGLShader* shader)
{
    ENTER_CONTEXT_SCOPE();

    STARFISH_ASSERT(program != nullptr);
    STARFISH_ASSERT(shader != nullptr);

    m_gl->detachShader(program->glObject(), shader->glObject());
    program->removeDetachedShader(shader);
}

void WebGLRenderingContext::disable(GLenum cap)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->disable(cap);
}

void WebGLRenderingContext::disableVertexAttribArray(GLuint index)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->disableVertexAttribArray(index);
    if (hasNewGLError()) {
        return;
    }
    getState()->disableVertexAttribArray(index);
}

void WebGLRenderingContext::drawArrays(GLenum mode, GLint first, GLsizei count)
{
    ENTER_CONTEXT_SCOPE();

    completePendingJobs();

    if (first < 0) {
        // If first is negative, an INVALID_VALUE error will be generated.
        setGLError(GL_INVALID_VALUE);
        return;
    }

    if (!getCurrentProgram()) {
        // If the CURRENT_PROGRAM is null, an INVALID_OPERATION error will be
        // generated.
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    for (GLuint array : getState()->arraysEnabled()) {
        // If a vertex attribute is enabled as an array via
        // enableVertexAttribArray but no buffer is bound to that attribute
        // (generally via bindBuffer and vertexAttribPointer), then draw
        // commands (drawArrays or drawElements) will generate an
        // INVALID_OPERATION error.
        if (!m_state->getBufferBoundToVertexAttributes(array)) {
            setGLError(GL_INVALID_OPERATION);
            return;
        }
    }

    applyTextureCompleteness(false);
    m_gl->drawArrays(mode, first, count);
    applyTextureCompleteness(true);
    m_ownerHTMLCanvasElement->setNeedsComposite();
}

void WebGLRenderingContext::drawElements(GLenum mode, GLsizei count,
                                         GLenum type, GLintptr offset)
{
    ENTER_CONTEXT_SCOPE();

    completePendingJobs();

    if (count > 0) {
        // TODO: verify a non-null WebGLBuffer is bound to the
        // ELEMENT_ARRAY_BUFFER binding point if count is greater than zero. If
        // not, an INVALID_OPERATION error will be generated.
    }

    if (offset < 0) {
        // the offset must be non-negative or an INVALID_VALUE error will be
        // generated.
        setGLError(GL_INVALID_VALUE);
        return;
    }

    if (!getCurrentProgram()) {
        // If the CURRENT_PROGRAM is null, an INVALID_OPERATION error will be
        // generated.
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    applyTextureCompleteness(false);
    m_gl->drawElements(mode, count, type, reinterpret_cast<void*>(offset));
    applyTextureCompleteness(true);
    m_ownerHTMLCanvasElement->setNeedsComposite();
}

void WebGLRenderingContext::enable(GLenum cap)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->enable(cap);
}

void WebGLRenderingContext::enableVertexAttribArray(GLuint index)
{
    ENTER_CONTEXT_SCOPE();
    /*
        NOTE: No idea to handle the following for now. It may already be handled
        in GLES3: WebGL imposes additional rules beyond OpenGL ES 2.0 regarding
        enabled vertex attributes; see Enabled Vertex Attributes and Range
        Checking.
    */
    m_gl->enableVertexAttribArray(index);
    if (hasNewGLError()) {
        return;
    }
    getState()->enableVertexAttribArray(index);
}

void WebGLRenderingContext::finish()
{
    ENTER_CONTEXT_SCOPE();

    completePendingJobs();

    m_gl->finish();
    m_ownerHTMLCanvasElement->setNeedsComposite();
}

void WebGLRenderingContext::flush()
{
    ENTER_CONTEXT_SCOPE();

    completePendingJobs();

    m_gl->flush();
    m_ownerHTMLCanvasElement->setNeedsComposite();
}

void WebGLRenderingContext::framebufferRenderbuffer(
    GLenum target, GLenum attachment, GLenum renderbuffertarget,
    Optional<WebGLRenderbuffer*> maybeRenderbuffer)
{
    ENTER_CONTEXT_SCOPE();

    Optional<WebGLFramebuffer*> webGLFramebuffer = m_state->webGLFramebuffer();

    if (maybeRenderbuffer.hasValue()) {
        WebGLRenderbuffer* renderBuffer = maybeRenderbuffer.value();

        if (!isFromCurrentContext(renderBuffer)) {
            setGLError(GL_INVALID_OPERATION);
            return;
        }

        m_gl->framebufferRenderbuffer(target, attachment, renderbuffertarget,
                                      renderBuffer->glObject());
        if (webGLFramebuffer) {
            webGLFramebuffer->setAttachedRenderBuffer(renderBuffer);
        }
    } else {
        m_gl->framebufferRenderbuffer(target, attachment, renderbuffertarget,
                                      0);
        if (webGLFramebuffer) {
            webGLFramebuffer->setAttachedRenderBuffer(nullptr);
        }
        if (isDefaultFramebufferBound()) {
            setGLError(GL_INVALID_OPERATION);
        }
    }
}

void WebGLRenderingContext::framebufferTexture2D(
    GLenum target, GLenum attachment, GLenum textarget,
    Optional<WebGLTexture*> maybeTexture, GLint level)
{
    ENTER_CONTEXT_SCOPE();

    Optional<WebGLFramebuffer*> webGLFramebuffer = m_state->webGLFramebuffer();

    if (maybeTexture.hasValue()) {
        WebGLTexture* texture = maybeTexture.value();

        if (!isFromCurrentContext(texture)) {
            setGLError(GL_INVALID_OPERATION);
            return;
        }

        if (texture->isDeleted()) {
            setGLError(GL_INVALID_OPERATION);
            return;
        }

        GLuint textureId = texture->glObject();
        m_gl->framebufferTexture2D(target, attachment, textarget, textureId,
                                   level);
        if (webGLFramebuffer) {
            webGLFramebuffer->setAttachedTexture(texture);
        }
    } else {
        m_gl->framebufferTexture2D(target, attachment, textarget, 0, level);
        if (webGLFramebuffer) {
            webGLFramebuffer->setAttachedTexture(nullptr);
        }
        if (isDefaultFramebufferBound()) {
            setGLError(GL_INVALID_OPERATION);
        }
    }
}

void WebGLRenderingContext::frontFace(GLenum mode)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->frontFace(mode);
}

void WebGLRenderingContext::generateMipmap(GLenum target)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->generateMipmap(target);
}

void WebGLRenderingContext::shaderSource(WebGLShader* shader, String* source)
{
    ENTER_CONTEXT_SCOPE();

    std::string str = source->toUTF8NonGCString();
    const char* sourceArray[1] = { str.c_str() };

    m_gl->shaderSource(shader->glObject(), 1, sourceArray, nullptr);
}

void WebGLRenderingContext::stencilFunc(GLenum func, GLint ref, GLuint mask)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->stencilFunc(func, ref, mask);
}

void WebGLRenderingContext::stencilFuncSeparate(GLenum face, GLenum func,
                                                GLint ref, GLuint mask)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->stencilFuncSeparate(face, func, ref, mask);
}

void WebGLRenderingContext::stencilMask(GLuint mask)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->stencilMask(mask);
}

void WebGLRenderingContext::stencilMaskSeparate(GLenum face, GLuint mask)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->stencilMaskSeparate(face, mask);
}

void WebGLRenderingContext::stencilOp(GLenum fail, GLenum zfail, GLenum zpass)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->stencilOp(fail, zfail, zpass);
}

void WebGLRenderingContext::stencilOpSeparate(GLenum face, GLenum fail,
                                              GLenum zfail, GLenum zpass)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->stencilOpSeparate(face, fail, zfail, zpass);
}

ScriptValue WebGLRenderingContext::getBufferParameter(GLenum target,
                                                      GLenum pname)
{
    ENTER_CONTEXT_SCOPE(scriptNull());

    if (target != GL_ARRAY_BUFFER && target != GL_ELEMENT_ARRAY_BUFFER) {
        setGLError(GL_INVALID_ENUM);
        return scriptNull();
    }

    switch (pname) {
    // GLint
    case GL_BUFFER_SIZE: {
        GLint value;
        gl()->getBufferParameteriv(target, pname, &value);
        if (hasNewGLError()) {
            return scriptNull();
        }
        return createScriptValue(value);
    }
    // GLenum
    case GL_BUFFER_USAGE: {
        GLint value;
        gl()->getBufferParameteriv(target, pname, &value);
        if (hasNewGLError()) {
            return scriptNull();
        }
        return createScriptValue(static_cast<GLenum>(value));
    }
    default:
        break;
    }
    setGLError(GL_INVALID_ENUM);
    return scriptNull();
}

ScriptValue WebGLRenderingContext::getParameter(GLenum pname)
{
    ENTER_CONTEXT_SCOPE(scriptNull());

    switch (pname) {
    // GLint
    case GL_ALPHA_BITS:
    case GL_BLUE_BITS:
    case GL_DEPTH_BITS:
    case GL_GREEN_BITS:
    case GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS:
    case GL_MAX_CUBE_MAP_TEXTURE_SIZE:
    case GL_MAX_FRAGMENT_UNIFORM_VECTORS:
    case GL_MAX_RENDERBUFFER_SIZE:
    case GL_MAX_TEXTURE_IMAGE_UNITS:
    case GL_MAX_TEXTURE_SIZE:
    case GL_MAX_VARYING_VECTORS:
    case GL_MAX_VERTEX_ATTRIBS:
    case GL_MAX_VERTEX_TEXTURE_IMAGE_UNITS:
    case GL_MAX_VERTEX_UNIFORM_VECTORS:
    case GL_PACK_ALIGNMENT:
    case GL_RED_BITS:
    case GL_SAMPLE_BUFFERS:
    case GL_SAMPLES:
    case GL_STENCIL_BACK_REF:
    case GL_STENCIL_BITS:
    case GL_STENCIL_CLEAR_VALUE:
    case GL_STENCIL_REF:
    case GL_SUBPIXEL_BITS:
    case GL_MAX_SAMPLES:
    case GL_UNPACK_ALIGNMENT: {
        std::vector<int> values(1);
        m_gl->getIntegerv(pname, &values[0]);
        return ValueRef::create(values[0]);
    }
    // GLfloat
    case GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT: {
        if (!isExtensionEnabled("EXT_texture_filter_anisotropic")) {
            setGLError(GL_INVALID_ENUM);
            return scriptNull();
        }
        std::vector<GLfloat> values(1);
        gl()->getFloatv(pname, &values[0]);
        return createScriptValue(values[0]);
    }
    // WebGLProgram
    case GL_CURRENT_PROGRAM: {
        GLint value = -1;
        m_gl->getIntegerv(pname, &value);

        Optional<WebGLProgram*> maybe = m_state->webGLProgram();
        if (!maybe.hasValue() || maybe.value()->isDeleted()) {
            return scriptNull();
        }
        STARFISH_ASSERT(static_cast<GLint>(maybe.value()->glObject()) == value);
        return maybe.value()->scriptValue();
    }
    // WebGLFramebuffer
    case GL_FRAMEBUFFER_BINDING: {
        GLint value = -1;
        m_gl->getIntegerv(pname, &value);

        if (isDefaultFramebufferBound()) {
            return scriptNull();
        }

        Optional<WebGLFramebuffer*> maybe = m_state->webGLFramebuffer();
        if (!maybe.hasValue() || maybe.value()->isDeleted()) {
            return scriptNull();
        }
        TRACE(WEBGL, KV(maybe.value()->glObject()), KV(value));
        STARFISH_ASSERT(static_cast<GLint>(maybe.value()->glObject()) == value);
        return maybe.value()->scriptValue();
    }
    // WebGLVertexArrayObjectOES
    case GL_VERTEX_ARRAY_BINDING: {
        // GL_VERTEX_ARRAY_BINDING_OES
        if (!isExtensionEnabled("OES_vertex_array_object")) {
            setGLError(GL_INVALID_ENUM);
            return scriptNull();
        }
        GLint value = -1;
        m_gl->getIntegerv(pname, &value);
        if (value == 0) {
            return scriptNull();
        }

        Optional<WebGLVertexArrayObjectOES*> maybe =
            m_state->webGLVertexArrayObjectOES();

        if (!maybe.hasValue() || maybe.value()->isDeleted()) {
            return scriptNull();
        }

        STARFISH_ASSERT(static_cast<GLint>(maybe.value()->glObject()) == value);
        return maybe.value()->scriptValue();
    }
    // WebGLBuffer
    case GL_ARRAY_BUFFER_BINDING:
    case GL_ELEMENT_ARRAY_BUFFER_BINDING: {
        GLuint target = (pname == GL_ARRAY_BUFFER_BINDING)
                            ? GL_ARRAY_BUFFER
                            : GL_ELEMENT_ARRAY_BUFFER;
        WebGLBuffer* buffer = m_state->getBoundBuffer(target).valueOr(nullptr);
        GLint value = 0;
        m_gl->getIntegerv(pname, &value);
        STARFISH_ASSERT((value == 0 && buffer == nullptr) ||
                        (static_cast<GLuint>(value) == buffer->glObject()));
        return buffer ? buffer->scriptValue() : scriptNull();
    }
    // GLenum
    case GL_ACTIVE_TEXTURE: {
        GLint value = 0;
        m_gl->getIntegerv(pname, &value);
        return ValueRef::create(value);
    }
    case kIMPLEMENTATION_COLOR_READ_TYPE:
    case kIMPLEMENTATION_COLOR_READ_FORMAT: {
        GLenum target =
            webGLVersion() == 2 ? GL_READ_FRAMEBUFFER : GL_FRAMEBUFFER;
        if (m_gl->checkFramebufferStatus(target) != GL_FRAMEBUFFER_COMPLETE) {
            setGLError(GL_INVALID_OPERATION);
            return scriptNull();
        }
        GLint value = 0;
        m_gl->getIntegerv(pname, &value);
        if (hasNewGLError()) {
            return scriptNull();
        }
        if (webGLVersion() == 1 && value == GL_HALF_FLOAT) {
            value = GL_HALF_FLOAT_OES;
        }
        return ValueRef::create(value);
    }
    case GL_TEXTURE_BINDING_2D:
    case GL_TEXTURE_BINDING_CUBE_MAP: {
        auto texture =
            boundTexture(pname == GL_TEXTURE_BINDING_2D ? GL_TEXTURE_2D
                                                        : GL_TEXTURE_CUBE_MAP);
        return texture ? texture->scriptValue() : scriptNull();
    }
    // DOMString
    case GL_SHADING_LANGUAGE_VERSION:
        return createScriptASCIIString(kShadingLanguageVersion);
    case GL_VERSION:
        return createScriptASCIIString(kVersion);
    case GL_RENDERER:
    case GL_VENDOR: {
        const std::string output =
            reinterpret_cast<const char*>(glGetString(pname));
        return StringRef::createFromASCII(output.c_str(), output.length());
    }
    // GLboolean
    case GL_BLEND:
    case GL_CULL_FACE:
    case GL_DEPTH_TEST:
    case GL_DEPTH_WRITEMASK:
    case GL_DITHER:
    case GL_POLYGON_OFFSET_FILL:
    case GL_SAMPLE_ALPHA_TO_COVERAGE:
    case GL_SAMPLE_COVERAGE:
    case GL_SAMPLE_COVERAGE_INVERT:
    case GL_SCISSOR_TEST:
    case GL_STENCIL_TEST: {
        std::vector<GLboolean> values(1);
        m_gl->getBooleanv(pname, &values[0]);
        return createScriptValue(static_cast<bool>(values[0]));
    }
    case kUNPACK_FLIP_Y_WEBGL: {
        return createScriptValue(m_unpackFlipY);
    }
    case kUNPACK_PREMULTIPLY_ALPHA_WEBGL: {
        return createScriptValue(m_unpackPremultiplyAlpha);
    }
    // Int32Array (with 2 elements)
    case GL_MAX_VIEWPORT_DIMS: {
        std::vector<int> values(2);
        m_gl->getIntegerv(pname, &values[0]);
        return createTypedArray<Int32ArrayObjectRef>(scriptBindingInstance(),
                                                     values);
    }
    // Int32Array (with 4 elements)
    case GL_SCISSOR_BOX:
    case GL_VIEWPORT: {
        std::vector<int> values(4);
        m_gl->getIntegerv(pname, &values[0]);
        return createTypedArray<Int32ArrayObjectRef>(scriptBindingInstance(),
                                                     values);
    }
    // Uint32Array
    case GL_COMPRESSED_TEXTURE_FORMATS: {
        STARFISH_ASSERT(WebGLExtensionRegistry::instance()
                            .hasTextureCompressionExtension() == false);
        return createTypedArray<Int32ArrayObjectRef>(scriptBindingInstance(),
                                                     std::vector<int>());
    }
    default:
        STARFISH_UNSUPPORTED("pname: 0x%04X(%s)", pname, __PRETTY_FUNCTION__);
        return scriptNull();
    }
    return scriptNull();
}

WebGLActiveInfo* WebGLRenderingContext::getActiveAttrib(WebGLProgram* program,
                                                        GLuint index)
{
    ENTER_CONTEXT_SCOPE(nullptr);

    if (!isFromCurrentContext(program)) {
        setGLError(GL_INVALID_OPERATION);
        return nullptr;
    }

    GLint maxNameLength;
    m_gl->getProgramiv(program->glObject(), GL_ACTIVE_ATTRIBUTE_MAX_LENGTH,
                       &maxNameLength);

    if (hasNewGLError()) {
        return nullptr;
    }

    GLint size;
    GLenum type;
    GLsizei length;

    std::vector<char> name;
    name.resize(maxNameLength, '\0');
    m_gl->getActiveAttrib(program->glObject(), index, maxNameLength, &length,
                          &size, &type, &name[0]);

    if (hasNewGLError()) {
        // a) If the passed index is out of range, generates an INVALID_VALUE
        // error and returns null. b) Returns null if any OpenGL errors are
        // generated during the execution of this function.
        return nullptr;
    }

    return new WebGLActiveInfo(scriptBindingInstance(), size, type,
                               String::createASCIIString(name.data(), length));
}

WebGLActiveInfo* WebGLRenderingContext::getActiveUniform(WebGLProgram* program,
                                                         GLuint index)
{
    ENTER_CONTEXT_SCOPE(nullptr);

    if (!isFromCurrentContext(program)) {
        setGLError(GL_INVALID_OPERATION);
        return nullptr;
    }

    GLint maxNameLength;
    m_gl->getProgramiv(program->glObject(), GL_ACTIVE_UNIFORM_MAX_LENGTH,
                       &maxNameLength);

    if (hasNewGLError()) {
        return nullptr;
    }

    GLint size;
    GLenum type;
    GLsizei length;

    std::vector<char> name;
    name.resize(maxNameLength, '\0');
    m_gl->getActiveUniform(program->glObject(), index, maxNameLength, &length,
                           &size, &type, &name[0]);

    if (hasNewGLError()) {
        // a) If the passed index is out of range, generates an INVALID_VALUE
        // error and returns null. b) Returns null if any OpenGL errors are
        // generated during the execution of this function.
        return nullptr;
    }

    return new WebGLActiveInfo(scriptBindingInstance(), size, type,
                               String::createASCIIString(name.data(), length));
}

Optional<GCVector<WebGLShader*>> WebGLRenderingContext::getAttachedShaders(
    WebGLProgram* program)
{
    ENTER_CONTEXT_SCOPE(nullptr);

    if (!isFromCurrentContext(program)) {
        return nullptr;
    }

    const GCVector<WebGLShader*>& webGLShaders = program->getWebGLShaders();
#if !defined(NDEBUG)
    GLint maxCount;
    m_gl->getProgramiv(program->glObject(), GL_ATTACHED_SHADERS, &maxCount);

    GLsizei returnedCount;
    std::vector<GLuint> shaders(maxCount);
    m_gl->getAttachedShaders(program->glObject(), maxCount, &returnedCount,
                             shaders.data());
    STARFISH_ASSERT(shaders.size() == webGLShaders.size());
#endif
    return webGLShaders;
}

GLint WebGLRenderingContext::getAttribLocation(WebGLProgram* program,
                                               String* name)
{
    ENTER_CONTEXT_SCOPE(-1);

    if (!isFromCurrentContext(program)) {
        setGLError(GL_INVALID_OPERATION);
        return -1;
    }

    if (!checkAttribOrUniformName(name)) {
        return -1;
    }

    // TODO: Returns -1 if the context's webgl context lost flag is set.

    if (program->invalidated()) {
        // If the invalidated flag of the passed program is set, generates an
        // INVALID_OPERATION error and returns -1.
        setGLError(GL_INVALID_OPERATION);
        return -1;
    }

    return m_gl->getAttribLocation(program->glObject(), CSTR(name));
}

ScriptValue WebGLRenderingContext::getFramebufferAttachmentParameter(
    GLenum target, GLenum attachment, GLenum pname)
{
    ENTER_CONTEXT_SCOPE(scriptNull());

    if (attachment != GL_COLOR_ATTACHMENT0 &&
        attachment != GL_DEPTH_ATTACHMENT &&
        attachment != GL_STENCIL_ATTACHMENT &&
        attachment != GL_DEPTH_STENCIL_ATTACHMENT) {
        setGLError(GL_INVALID_ENUM);
        return scriptNull();
    }

    GLint params = 0;
    m_gl->getFramebufferAttachmentParameteriv(target, attachment, pname,
                                              &params);

    if (hasNewGLError()) {
        return scriptNull();
    }

    switch (pname) {
    case GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE: {
        return params != 0
                   ? Escargot::ValueRef::create(static_cast<GLenum>(params))
                   : scriptNull();
    }
    case GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_LEVEL:
    case GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_CUBE_MAP_FACE:
        return Escargot::ValueRef::create(params);
    case GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME: {
        Optional<WebGLFramebuffer*> webGLFramebuffer =
            m_state->webGLFramebuffer();
        if (!webGLFramebuffer) {
            return scriptNull();
        }
        GLint rboOrTextureID;
        m_gl->getFramebufferAttachmentParameteriv(
            target, attachment, GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME,
            &rboOrTextureID);

        GLint type;
        m_gl->getFramebufferAttachmentParameteriv(
            target, attachment, GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE, &type);
        if (type == GL_RENDERBUFFER) {
            return webGLFramebuffer->attachedRenderBuffer()->scriptValue();
        } else if (type == GL_TEXTURE) {
            return webGLFramebuffer->attachedTexture()->scriptValue();
        }
        STARFISH_LOG_DEBUG("Unknown type %d", type);
        return scriptNull();
    }
    default:
        setGLError(GL_INVALID_ENUM);
        break;
    }
    return scriptNull();
}

ScriptValue WebGLRenderingContext::getProgramParameter(WebGLProgram* program,
                                                       GLenum pname)
{
    ENTER_CONTEXT_SCOPE(scriptNull());

    if (!isFromCurrentContext(program)) {
        setGLError(GL_INVALID_OPERATION);
        return scriptNull();
    }

    GLint params = 0;
    m_gl->getProgramiv(program->glObject(), pname, &params);

    if (hasNewGLError()) {
        /*
         - GL_INVALID_ENUM if pname is not an accepted value.
         - GL_INVALID_VALUE if program is not a value generated by OpenGL.
         - GL_INVALID_OPERATION if program does not refer to a program object.
        */
        return scriptNull();
    }

    switch (pname) {
    case GL_DELETE_STATUS:
        return Escargot::ValueRef::create(static_cast<bool>(params));
    case GL_LINK_STATUS:
        if (program->linkFailed()) {
            return Escargot::ValueRef::create(false);
        }
        return Escargot::ValueRef::create(static_cast<bool>(params));
    case GL_VALIDATE_STATUS:
        return Escargot::ValueRef::create(static_cast<bool>(params));
    case GL_ATTACHED_SHADERS:
    case GL_ACTIVE_ATTRIBUTES:
    case GL_ACTIVE_UNIFORMS:
        return Escargot::ValueRef::create(static_cast<GLint>(params));
    default:
        break;
    }
    setGLError(GL_INVALID_ENUM);
    return scriptNull();
}

String* WebGLRenderingContext::getProgramInfoLog(WebGLProgram* program)
{
    ENTER_CONTEXT_SCOPE(nullptr);

    GLsizei length = 0, bufferSize = 0;
    m_gl->getProgramiv(program->glObject(), GL_INFO_LOG_LENGTH, &bufferSize);

    std::string buffer;
    buffer.reserve(bufferSize);
    m_gl->getProgramInfoLog(program->glObject(), bufferSize, &length,
                            &buffer[0]);

    if (hasNewGLError()) {
        return nullptr;
    }

    TRACE(WEBGL, buffer);

    return String::fromUTF8(buffer.data(), length);
}

ScriptValue WebGLRenderingContext::getRenderbufferParameter(GLenum target,
                                                            GLenum pname)
{
    ENTER_CONTEXT_SCOPE(scriptNull());

    GLint params = 0;
    m_gl->getRenderbufferParameteriv(target, pname, &params);

    if (hasNewGLError()) {
        return scriptNull();
    }

    switch (pname) {
    case GL_RENDERBUFFER_INTERNAL_FORMAT:
        return createScriptValue(static_cast<GLenum>(params));
    case GL_RENDERBUFFER_WIDTH:
    case GL_RENDERBUFFER_HEIGHT:
    case GL_RENDERBUFFER_RED_SIZE:
    case GL_RENDERBUFFER_GREEN_SIZE:
    case GL_RENDERBUFFER_BLUE_SIZE:
    case GL_RENDERBUFFER_ALPHA_SIZE:
    case GL_RENDERBUFFER_DEPTH_SIZE:
    case GL_RENDERBUFFER_STENCIL_SIZE:
        return createScriptValue(params);
    default:
        setGLError(GL_INVALID_ENUM);
        break;
    }
    return scriptNull();
}

ScriptValue WebGLRenderingContext::getShaderParameter(WebGLShader* shader,
                                                      GLenum pname)
{
    ENTER_CONTEXT_SCOPE(scriptNull());

    if (!isFromCurrentContext(shader)) {
        setGLError(GL_INVALID_OPERATION);
        return scriptNull();
    }

    GLint params = 0;
    m_gl->getShaderiv(shader->glObject(), pname, &params);

    if (hasNewGLError()) {
        /*
        - GL_INVALID_ENUM if pname is not an accepted value.
        - GL_INVALID_VALUE if shader is not a value generated by OpenGL.
        - GL_INVALID_OPERATION if shader does not refer to a shader object.
        */
        return scriptNull();
    }

    switch (pname) {
    case GL_SHADER_TYPE:
        return Escargot::ValueRef::create(static_cast<GLenum>(params));
    case GL_DELETE_STATUS:
    case GL_COMPILE_STATUS:
        return Escargot::ValueRef::create(static_cast<bool>(params));
    default:
        break;
    }
    setGLError(GL_INVALID_ENUM);
    return scriptNull();
}

WebGLShaderPrecisionFormat* WebGLRenderingContext::getShaderPrecisionFormat(
    GLenum shadertype, GLenum precisiontype)
{
    ENTER_CONTEXT_SCOPE(nullptr);

    GLint range[2];
    GLint precision;

    m_gl->getShaderPrecisionFormat(shadertype, precisiontype, range,
                                   &precision);
    if (hasNewGLError()) {
        return nullptr;
    }

    return new WebGLShaderPrecisionFormat(scriptBindingInstance(), range[0],
                                          range[1], precision);
}

String* WebGLRenderingContext::getShaderInfoLog(WebGLShader* shader)
{
    ENTER_CONTEXT_SCOPE(nullptr);

    GLsizei length = 0, bufferSize = 0;
    m_gl->getShaderiv(shader->glObject(), GL_INFO_LOG_LENGTH, &bufferSize);

    std::string buffer;
    buffer.reserve(bufferSize);
    m_gl->getShaderInfoLog(shader->glObject(), bufferSize, &length, &buffer[0]);

    if (hasNewGLError()) {
        return nullptr;
    }

    TRACE(WEBGL, buffer);

    return String::fromUTF8(buffer.data(), length);
}

String* WebGLRenderingContext::getShaderSource(WebGLShader* shader)
{
    ENTER_CONTEXT_SCOPE(nullptr);

    GLsizei length = 0, bufferSize = 0;
    m_gl->getShaderiv(shader->glObject(), GL_SHADER_SOURCE_LENGTH, &bufferSize);

    std::string buffer;
    buffer.reserve(bufferSize);
    m_gl->getShaderSource(shader->glObject(), bufferSize, &length, &buffer[0]);

    if (hasNewGLError()) {
        return nullptr;
    }

    return String::fromUTF8(buffer.data(), length);
}

Optional<WebGLTexture*> WebGLRenderingContext::boundTexture(GLenum target) const
{
    if (target >= GL_TEXTURE_CUBE_MAP_POSITIVE_X &&
        target <= GL_TEXTURE_CUBE_MAP_NEGATIVE_Z) {
        target = GL_TEXTURE_CUBE_MAP;
    }
    const auto it =
        m_boundTextures.find((uint64_t(m_activeTexture) << 32) | target);
    return it == m_boundTextures.end() ? Optional<WebGLTexture*>()
                                       : Optional<WebGLTexture*>(it->second);
}

void WebGLRenderingContext::recordTextureImage(GLenum target, GLint level,
                                               GLenum type)
{
    if (!hasNewGLError()) {
        if (auto texture = boundTexture(target)) {
            texture->setImageType(target, level, type);
        }
    }
}

void WebGLRenderingContext::applyTextureCompleteness(bool restore)
{
    if (webGLVersion() != 1) {
        return;
    }
    // Native GL enables all supported extensions. WebGL requires float
    // linear filtering to remain incomplete until getExtension enables it.
    // Incomplete ES 2 textures sample (0, 0, 0, 1), as does texture zero.
    // https://registry.khronos.org/OpenGL/extensions/OES/OES_texture_float.txt
    const bool linear = isExtensionEnabled("OES_texture_float_linear");
    bool changed = false;
    for (const auto& binding : m_boundTextures) {
        if (binding.second->needsFloatLinearExtension(linear)) {
            m_gl->activeTexture(binding.first >> 32);
            m_gl->bindTexture(static_cast<GLenum>(binding.first),
                              restore ? binding.second->glObject() : 0);
            changed = true;
        }
    }
    if (changed) {
        m_gl->activeTexture(m_activeTexture);
    }
}

bool WebGLRenderingContext::hasBoundTexture(GLenum target) const
{
    GLenum binding;
    switch (target) {
    case GL_TEXTURE_2D:
        binding = GL_TEXTURE_BINDING_2D;
        break;
    case GL_TEXTURE_3D:
        binding = GL_TEXTURE_BINDING_3D;
        break;
    case GL_TEXTURE_2D_ARRAY:
        binding = GL_TEXTURE_BINDING_2D_ARRAY;
        break;
    case GL_TEXTURE_CUBE_MAP:
        binding = GL_TEXTURE_BINDING_CUBE_MAP;
        break;
    default:
        return false;
    }
    GLint boundTexture = 0;
    m_gl->getIntegerv(binding, &boundTexture);
    return boundTexture != 0;
}

ScriptValue WebGLRenderingContext::getTexParameter(GLenum target, GLenum pname)
{
    ENTER_CONTEXT_SCOPE(scriptNull());

    if (target != GL_TEXTURE_2D && target != GL_TEXTURE_CUBE_MAP) {
        setGLError(GL_INVALID_ENUM);
        return scriptNull();
    }

    if (!hasBoundTexture(target)) {
        setGLError(GL_INVALID_OPERATION);
        return scriptNull();
    }

    if (pname == GL_TEXTURE_MAX_ANISOTROPY_EXT &&
        isExtensionEnabled("EXT_texture_filter_anisotropic")) {
        GLfloat params = 0;
        m_gl->getTexParameterfv(target, pname, &params);
        if (hasNewGLError()) {
            return scriptNull();
        }
        return createScriptValue(params);
    }

    if (pname != GL_TEXTURE_MAG_FILTER && pname != GL_TEXTURE_MIN_FILTER &&
        pname != GL_TEXTURE_WRAP_S && pname != GL_TEXTURE_WRAP_T) {
        setGLError(GL_INVALID_ENUM);
        return scriptNull();
    }

    GLint params = 0;
    m_gl->getTexParameteriv(target, pname, &params);

    if (hasNewGLError()) {
        return scriptNull();
    }

    return createScriptValue(static_cast<GLenum>(params));
}

GLenum WebGLRenderingContext::getUniformType(WebGLProgram* program,
                                             WebGLUniformLocation* location)
{
    ENTER_CONTEXT_SCOPE(GL_NONE);

    GLint count = 0;
    m_gl->getProgramiv(program->glObject(), GL_ACTIVE_UNIFORMS, &count);
    GLint maxNameLength = 0;
    m_gl->getProgramiv(program->glObject(), GL_ACTIVE_UNIFORM_MAX_LENGTH,
                       &maxNameLength);
    for (GLint index = 0; index < count; index++) {
        GLint size;
        GLenum type;
        GLsizei length;
        std::vector<char> name;
        name.resize(maxNameLength, '\0');
        m_gl->getActiveUniform(program->glObject(), index, maxNameLength,
                               &length, &size, &type, &name[0]);
        if (size > 1) {
            std::string arrayName(&name[0]);
            if (arrayName.length() > 3 &&
                arrayName.substr(arrayName.length() - 3, arrayName.length()) ==
                    "[0]") {
                arrayName = arrayName.substr(0, arrayName.length() - 3);
            }
            for (GLint arrayIndex = 0; arrayIndex < size; arrayIndex++) {
                std::string elementName =
                    arrayName + "[" + std::to_string(arrayIndex) + "]";
                GLint uniformLocation = m_gl->getUniformLocation(
                    program->glObject(), elementName.data());
                if (uniformLocation == location->location()) {
                    return type;
                }
            }
        } else {
            GLint uniformLocation =
                m_gl->getUniformLocation(program->glObject(), &name[0]);
            if (uniformLocation == location->location()) {
                return type;
            }
        }
    }
    return GL_NONE;
}

Optional<ScriptValue> WebGLRenderingContext::getUniformImpl(
    WebGLProgram* program, WebGLUniformLocation* location, GLenum type)
{
    ENTER_CONTEXT_SCOPE(Optional<ScriptValue>());

    switch (type) {
    case GL_BOOL: {
        GLint value;
        m_gl->getUniformiv(program->glObject(), location->location(), &value);
        return createScriptValue(static_cast<bool>(value));
    }
    case GL_INT: {
        GLint value;
        m_gl->getUniformiv(program->glObject(), location->location(), &value);
        return createScriptValue(value);
    }
    case GL_FLOAT: {
        GLfloat value;
        m_gl->getUniformfv(program->glObject(), location->location(), &value);
        return createScriptValue(value);
    }
    case GL_FLOAT_VEC2: {
        std::vector<GLfloat> values(2);
        m_gl->getUniformfv(program->glObject(), location->location(),
                           &values[0]);
        return createTypedArray<Float32ArrayObjectRef>(scriptBindingInstance(),
                                                       values);
    }
    case GL_INT_VEC2: {
        std::vector<GLint> values(2);
        m_gl->getUniformiv(program->glObject(), location->location(),
                           &values[0]);
        return createTypedArray<Int32ArrayObjectRef>(scriptBindingInstance(),
                                                     values);
    }
    case GL_BOOL_VEC2: {
        std::vector<GLint> values(2);
        m_gl->getUniformiv(program->glObject(), location->location(),
                           &values[0]);
        return createScriptValue(
            createArray(scriptBindingInstance(),
                        std::vector<bool>(values.begin(), values.end())));
    }
    case GL_FLOAT_VEC3: {
        std::vector<GLfloat> values(3);
        m_gl->getUniformfv(program->glObject(), location->location(),
                           &values[0]);
        return createTypedArray<Float32ArrayObjectRef>(scriptBindingInstance(),
                                                       values);
    }
    case GL_INT_VEC3: {
        std::vector<GLint> values(3);
        m_gl->getUniformiv(program->glObject(), location->location(),
                           &values[0]);
        return createTypedArray<Int32ArrayObjectRef>(scriptBindingInstance(),
                                                     values);
    }
    case GL_BOOL_VEC3: {
        std::vector<GLint> values(3);
        m_gl->getUniformiv(program->glObject(), location->location(),
                           &values[0]);
        return createScriptValue(
            createArray(scriptBindingInstance(),
                        std::vector<bool>(values.begin(), values.end())));
    }
    case GL_FLOAT_VEC4: {
        std::vector<GLfloat> values(4);
        m_gl->getUniformfv(program->glObject(), location->location(),
                           &values[0]);
        return createTypedArray<Float32ArrayObjectRef>(scriptBindingInstance(),
                                                       values);
    }
    case GL_INT_VEC4: {
        std::vector<GLint> values(4);
        m_gl->getUniformiv(program->glObject(), location->location(),
                           &values[0]);
        return createTypedArray<Int32ArrayObjectRef>(scriptBindingInstance(),
                                                     values);
    }
    case GL_BOOL_VEC4: {
        std::vector<GLint> values(4);
        m_gl->getUniformiv(program->glObject(), location->location(),
                           &values[0]);
        return createScriptValue(
            createArray(scriptBindingInstance(),
                        std::vector<bool>(values.begin(), values.end())));
    }
    case GL_FLOAT_MAT2: {
        std::vector<GLfloat> values(4);
        m_gl->getUniformfv(program->glObject(), location->location(),
                           &values[0]);
        return createTypedArray<Float32ArrayObjectRef>(scriptBindingInstance(),
                                                       values);
    }
    case GL_FLOAT_MAT3: {
        std::vector<GLfloat> values(9);
        m_gl->getUniformfv(program->glObject(), location->location(),
                           &values[0]);
        return createTypedArray<Float32ArrayObjectRef>(scriptBindingInstance(),
                                                       values);
    }
    case GL_FLOAT_MAT4: {
        std::vector<GLfloat> values(16);
        m_gl->getUniformfv(program->glObject(), location->location(),
                           &values[0]);
        return createTypedArray<Float32ArrayObjectRef>(scriptBindingInstance(),
                                                       values);
    }
    case GL_SAMPLER_2D:
    case GL_SAMPLER_CUBE: {
        GLint value;
        m_gl->getUniformiv(program->glObject(), location->location(), &value);
        return createScriptValue(value);
    }
    default:
        break;
    }
    return Optional<ScriptValue>();
}

ScriptValue WebGLRenderingContext::getUniform(WebGLProgram* program,
                                              WebGLUniformLocation* location)
{
    if (!isFromCurrentContext(program)) {
        setGLError(GL_INVALID_OPERATION);
        return scriptNull();
    }

    if (location->program()->context() != this) {
        setGLError(GL_INVALID_OPERATION);
        return scriptNull();
    }

    GLenum type = getUniformType(program, location);
    Optional<ScriptValue> uniform = getUniformImpl(program, location, type);
    return uniform.valueOr(scriptNull());
}

WebGLUniformLocation* WebGLRenderingContext::getUniformLocation(
    WebGLProgram* program, String* name)
{
    ENTER_CONTEXT_SCOPE(nullptr);

    if (!isFromCurrentContext(program)) {
        setGLError(GL_INVALID_OPERATION);
        return nullptr;
    }

    if (!checkAttribOrUniformName(name)) {
        return nullptr;
    }

    GLint location = m_gl->getUniformLocation(program->glObject(), CSTR(name));
    if (location == -1) {
        /*
          - WebGL: The return value is null if name does not correspond to an
            active uniform variable in the passed program.
          - GLES: glGetUniformLocation returns -1 if name does not correspond to
            an active uniform variable in program or if name is associated with
            a named uniform block.
        */

        return nullptr;
    }

    if (hasNewGLError()) {
        // Returns null if any OpenGL errors are generated during the execution
        // of this function.
        return nullptr;
    }

    return new WebGLUniformLocation(scriptBindingInstance(), program, location);
}

ScriptValue WebGLRenderingContext::getVertexAttrib(GLuint index, GLenum pname)
{
    ENTER_CONTEXT_SCOPE(scriptNull());

    switch (pname) {
    case GL_CURRENT_VERTEX_ATTRIB: {
        std::vector<float> values(4);
        m_gl->getVertexAttribfv(index, pname, &values[0]);
        return createTypedArray<Float32ArrayObjectRef>(scriptBindingInstance(),
                                                       values);
    }
    case GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING: {
        GLint value = 0;
        m_gl->getVertexAttribiv(index, pname, &value);

        TRACE(WEBGL, KV(index), KV(value));

        Optional<WebGLVertexArrayObjectOES*> maybe =
            m_state->webGLVertexArrayObjectOES();

        if (!maybe.hasValue()) {
            return scriptNull(); // No mention found for this in the spec.
        }

        Optional<WebGLBuffer*> maybeBuffer =
            m_state->getBufferBoundToVertexAttributes(index);

        if (!maybeBuffer.hasValue()) {
            return scriptNull(); // No mention found for this in the spec.
        }

        TRACE(WEBGL, KV(index), KV(maybeBuffer.value()->glObject()));

        STARFISH_ASSERT(static_cast<GLuint>(value) ==
                        maybeBuffer.value()->glObject());

        return maybeBuffer.value()->scriptValue();
    }
    case GL_VERTEX_ATTRIB_ARRAY_ENABLED: {
        GLint value = 0;
        m_gl->getVertexAttribiv(index, pname, &value);
        return ValueRef::create(value == 1 ? true : false);
    }
    case GL_VERTEX_ATTRIB_ARRAY_SIZE: {
        GLint value = 4;
        m_gl->getVertexAttribiv(index, pname, &value);
        return ValueRef::create(value);
    }
    case GL_VERTEX_ATTRIB_ARRAY_STRIDE: {
        GLint value = 0;
        m_gl->getVertexAttribiv(index, pname, &value);
        return ValueRef::create(value);
    }
    case GL_VERTEX_ATTRIB_ARRAY_TYPE: {
        GLint value = GL_FLOAT;
        m_gl->getVertexAttribiv(index, pname, &value);
        return ValueRef::create(value);
    }
    case GL_VERTEX_ATTRIB_ARRAY_NORMALIZED: {
        GLint value = 0;
        m_gl->getVertexAttribiv(index, pname, &value);
        return ValueRef::create(value == 1 ? true : false);
    }
    default:
        setGLError(GL_INVALID_ENUM);
        break;
    }
    return scriptNull();
}

GLintptr WebGLRenderingContext::getVertexAttribOffset(GLuint index,
                                                      GLenum pname)
{
    ENTER_CONTEXT_SCOPE(0);

    GLvoid* pointer = nullptr;
    m_gl->getVertexAttribPointerv(index, pname, &pointer);
    return reinterpret_cast<GLintptr>(pointer);
}

void WebGLRenderingContext::hint(GLenum target, GLenum mode)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->hint(target, mode);
}

bool WebGLRenderingContext::isBuffer(Optional<WebGLBuffer*> maybe)
{
    ENTER_CONTEXT_SCOPE(false);

    if (!maybe.hasValue() || !isFromCurrentContext(maybe.value()) ||
        maybe.value()->invalidated()) {
        return false;
    }

    return m_gl->isBuffer(maybe.value()->glObject());
}

bool WebGLRenderingContext::isEnabled(GLenum cap)
{
    ENTER_CONTEXT_SCOPE(false);

    if (m_isContextLost) {
        return false;
    }

    return m_gl->isEnabled(cap);
}

bool WebGLRenderingContext::isFramebuffer(Optional<WebGLFramebuffer*> maybe)
{
    ENTER_CONTEXT_SCOPE(false);

    if (!maybe.hasValue() || !isFromCurrentContext(maybe.value()) ||
        maybe.value()->invalidated()) {
        return false;
    }

    return true;
}

bool WebGLRenderingContext::isProgram(Optional<WebGLProgram*> maybe)
{
    ENTER_CONTEXT_SCOPE(false);

    if (!maybe.hasValue() || !isFromCurrentContext(maybe.value()) ||
        maybe.value()->invalidated()) {
        return false;
    }

    return true;
}

bool WebGLRenderingContext::isRenderbuffer(Optional<WebGLRenderbuffer*> maybe)
{
    ENTER_CONTEXT_SCOPE(false);

    if (!maybe.hasValue() || !isFromCurrentContext(maybe.value()) ||
        maybe.value()->invalidated()) {
        return false;
    }

    return true;
}

bool WebGLRenderingContext::isShader(Optional<WebGLShader*> maybe)
{
    ENTER_CONTEXT_SCOPE(false);

    if (!maybe.hasValue() || !isFromCurrentContext(maybe.value()) ||
        maybe.value()->invalidated()) {
        return false;
    }

    return true;
}

bool WebGLRenderingContext::isTexture(Optional<WebGLTexture*> maybe)
{
    ENTER_CONTEXT_SCOPE(false);

    if (!maybe.hasValue() || !isFromCurrentContext(maybe.value()) ||
        maybe.value()->invalidated()) {
        return false;
    }

    return true;
}

void WebGLRenderingContext::lineWidth(GLfloat width)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->lineWidth(width);
}

void WebGLRenderingContext::linkProgram(WebGLProgram* program)
{
    ENTER_CONTEXT_SCOPE();

    if (!isFromCurrentContext(program)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    /*
        NOTE: No idea to handle the following for now. It may already be handled
        in GLES3: 6.26 Packing Restrictions for Uniforms and Varyings: The WebGL
        API further requires that if the packing algorithm fails either for the
        uniform variables of a shader or for the varying variables of a program,
        compilation or linking must fail.
    */

    m_gl->linkProgram(program->glObject());

    if (hasNewGLError()) {
        /*
            NOTE: No idea to handle the following for now. It may already be
            handled in GLES3: If the given program is also the the current
            program object in use as defined by useProgram, then: If the program
            is not linked successfully, the executable code referenced by the
            current rendering state is immediately invalidated. Further draw
            calls that utilize the current program generate an INVALID_OPERATION
            error. See Current program invalidated upon unsuccessful
            link(https://registry.khronos.org/webgl/specs/latest/1.0/#6.43).
        */
        STARFISH_UNIMPLEMENTED();
    }

    program->setLinkFailed(false);

    GLint linkStatus = 0;
    m_gl->getProgramiv(program->glObject(), GL_LINK_STATUS, &linkStatus);
    if (linkStatus != GL_TRUE) {
        program->setLinkFailed(true);
        return;
    }

    GLint maxVertexAttribs = 0;
    m_gl->getIntegerv(GL_MAX_VERTEX_ATTRIBS, &maxVertexAttribs);

    GLint numActiveAttribs = 0;
    m_gl->getProgramiv(program->glObject(), GL_ACTIVE_ATTRIBUTES,
                       &numActiveAttribs);

    GLint maxNameLength = 0;
    m_gl->getProgramiv(program->glObject(), GL_ACTIVE_ATTRIBUTE_MAX_LENGTH,
                       &maxNameLength);

    std::vector<std::tuple<std::string, GLuint, GLint>> activeAttribs;
    for (GLint i = 0; i < numActiveAttribs; ++i) {
        GLint size = 0;
        GLenum type = 0;
        GLsizei length = 0;
        std::vector<char> nameBuf(maxNameLength, '\0');
        m_gl->getActiveAttrib(program->glObject(), i, maxNameLength, &length,
                              &size, &type, &nameBuf[0]);
        std::string name(nameBuf.data(), length);

        GLint numLocations = 1;
        switch (type) {
        case GL_FLOAT_MAT2:
            numLocations = 2;
            break;
        case GL_FLOAT_MAT3:
            numLocations = 3;
            break;
        case GL_FLOAT_MAT4:
            numLocations = 4;
            break;
        default:
            break;
        }

        GLint location =
            m_gl->getAttribLocation(program->glObject(), name.c_str());
        if (location >= 0) {
            activeAttribs.push_back(std::make_tuple(
                name, static_cast<GLuint>(location), numLocations));
        }
    }

    for (const auto& attrib : activeAttribs) {
        const std::string& name = std::get<0>(attrib);
        GLuint location = std::get<1>(attrib);
        GLint numLocations = std::get<2>(attrib);

        if (location + numLocations > static_cast<GLuint>(maxVertexAttribs)) {
            program->setLinkFailed(true);
            return;
        }

        for (const auto& other : activeAttribs) {
            const std::string& otherName = std::get<0>(other);
            if (otherName == name) {
                continue;
            }

            GLuint otherLocation = std::get<1>(other);
            GLint otherNumLocations = std::get<2>(other);

            if (otherLocation >= location &&
                otherLocation < location + static_cast<GLuint>(numLocations)) {
                program->setLinkFailed(true);
                return;
            }
        }
    }
}

void WebGLRenderingContext::pixelStorei(GLenum pname, GLint param)
{
    ENTER_CONTEXT_SCOPE();

    switch (pname) {
    case kUNPACK_FLIP_Y_WEBGL:
        TRACE(WEBGL, "UNPACK_FLIP_Y_WEBGL", param);
        m_unpackFlipY = static_cast<bool>(param);
        break;
    case kUNPACK_PREMULTIPLY_ALPHA_WEBGL:
        TRACE(WEBGL, "UNPACK_PREMULTIPLY_ALPHA_WEBGL", param);
        m_unpackPremultiplyAlpha = static_cast<bool>(param);
        break;
    case kUNPACK_COLORSPACE_CONVERSION_WEBGL:
        TRACE(WEBGL, "UNPACK_COLORSPACE_CONVERSION_WEBGL", param);
        if (param == kBROWSER_DEFAULT_WEBGL || param == GL_NONE) {
            // NOTE: we don't do nothing for this as default.
            m_unpackColorspaceConversion = param;
        }
        break;
    default:
        TRACE(WEBGL, KV(glValueString(pname)), KV(glValueString(param)));
        m_gl->pixelStorei(pname, param);
        break;
    }
}

void WebGLRenderingContext::polygonOffset(GLfloat factor, GLfloat units)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->polygonOffset(factor, units);
}

void WebGLRenderingContext::renderbufferStorage(GLenum target,
                                                GLenum internalformat,
                                                GLsizei width, GLsizei height)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->renderbufferStorage(target, internalformat, width, height);
}

void WebGLRenderingContext::sampleCoverage(GLclampf value, GLboolean invert)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->sampleCoverage(value, invert);
}

void WebGLRenderingContext::scissor(GLint x, GLint y, GLsizei width,
                                    GLsizei height)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->scissor(x, y, width, height);
}

void WebGLRenderingContext::texParameterf(GLenum target, GLenum pname,
                                          GLfloat param)
{
    ENTER_CONTEXT_SCOPE();

    if (pname == GL_TEXTURE_MAX_ANISOTROPY_EXT &&
        !isExtensionEnabled("EXT_texture_filter_anisotropic")) {
        setGLError(GL_INVALID_ENUM);
        return;
    }

    if (target != GL_TEXTURE_2D && target != GL_TEXTURE_CUBE_MAP) {
        setGLError(GL_INVALID_ENUM);
        return;
    }

    if (!hasBoundTexture(target)) {
        // If an attempt is made to call this function with no WebGLTexture
        // bound, an INVALID_OPERATION error is generated.
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    hasNewGLError();
    m_gl->texParameterf(target, pname, param);
    if (!hasNewGLError()) {
        if (auto texture = boundTexture(target)) {
            texture->setFilter(pname, param);
        }
    }
}

void WebGLRenderingContext::texParameteri(GLenum target, GLenum pname,
                                          GLint param)
{
    ENTER_CONTEXT_SCOPE();

    if (pname == GL_TEXTURE_MAX_ANISOTROPY_EXT &&
        !isExtensionEnabled("EXT_texture_filter_anisotropic")) {
        setGLError(GL_INVALID_ENUM);
        return;
    }

    if (target != GL_TEXTURE_2D && target != GL_TEXTURE_CUBE_MAP) {
        setGLError(GL_INVALID_ENUM);
        return;
    }

    if (!hasBoundTexture(target)) {
        // If an attempt is made to call this function with no WebGLTexture
        // bound, an INVALID_OPERATION error is generated.
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    hasNewGLError();
    m_gl->texParameteri(target, pname, param);
    if (!hasNewGLError()) {
        if (auto texture = boundTexture(target)) {
            texture->setFilter(pname, param);
        }
    }
}

void WebGLRenderingContext::uniform1f(
    Optional<WebGLUniformLocation*> maybeUniform, GLfloat x)
{
    ENTER_CONTEXT_SCOPE();

    if (!maybeUniform.hasValue()) {
        return;
    }

    WebGLUniformLocation* uniform = maybeUniform.value();

    // Each of the uniform* functions sets the specified uniform or uniforms to
    // the values provided.
    if (!isFromCurrentProgram(uniform)) {
        // If the passed location is not null and was not obtained from the
        // currently used program via an earlier call to getUniformLocation, an
        // INVALID_OPERATION error will be generated.
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    // If the passed location is null, the data passed in will be silently
    // ignored and no uniform variables will be changed.
    m_gl->uniform1f(uniform->location(), x);
}

void WebGLRenderingContext::uniform2f(
    Optional<WebGLUniformLocation*> maybeUniform, GLfloat x, GLfloat y)
{
    ENTER_CONTEXT_SCOPE();

    if (!maybeUniform.hasValue()) {
        return;
    }

    WebGLUniformLocation* uniform = maybeUniform.value();

    if (!isFromCurrentProgram(uniform)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    m_gl->uniform2f(uniform->location(), x, y);
}

void WebGLRenderingContext::uniform3f(
    Optional<WebGLUniformLocation*> maybeUniform, GLfloat x, GLfloat y,
    GLfloat z)
{
    ENTER_CONTEXT_SCOPE();

    if (!maybeUniform.hasValue()) {
        return;
    }

    WebGLUniformLocation* uniform = maybeUniform.value();

    if (!isFromCurrentProgram(uniform)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    m_gl->uniform3f(uniform->location(), x, y, z);
}

void WebGLRenderingContext::uniform4f(
    Optional<WebGLUniformLocation*> maybeUniform, GLfloat x, GLfloat y,
    GLfloat z, GLfloat w)
{
    ENTER_CONTEXT_SCOPE();

    if (!maybeUniform.hasValue()) {
        return;
    }

    WebGLUniformLocation* uniform = maybeUniform.value();

    if (!isFromCurrentProgram(uniform)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    m_gl->uniform4f(uniform->location(), x, y, z, w);
}

void WebGLRenderingContext::uniform1i(
    Optional<WebGLUniformLocation*> maybeUniform, GLint x)
{
    ENTER_CONTEXT_SCOPE();

    if (!maybeUniform.hasValue()) {
        return;
    }

    WebGLUniformLocation* uniform = maybeUniform.value();

    if (!isFromCurrentProgram(uniform)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    m_gl->uniform1i(uniform->location(), x);
}

void WebGLRenderingContext::uniform2i(
    Optional<WebGLUniformLocation*> maybeUniform, GLint x, GLint y)
{
    ENTER_CONTEXT_SCOPE();

    if (!maybeUniform.hasValue()) {
        return;
    }

    WebGLUniformLocation* uniform = maybeUniform.value();

    if (!isFromCurrentProgram(uniform)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    m_gl->uniform2i(uniform->location(), x, y);
}

void WebGLRenderingContext::uniform3i(
    Optional<WebGLUniformLocation*> maybeUniform, GLint x, GLint y, GLint z)
{
    ENTER_CONTEXT_SCOPE();

    if (!maybeUniform.hasValue()) {
        return;
    }

    WebGLUniformLocation* uniform = maybeUniform.value();

    if (!isFromCurrentProgram(uniform)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    m_gl->uniform3i(uniform->location(), x, y, z);
}

void WebGLRenderingContext::uniform4i(
    Optional<WebGLUniformLocation*> maybeUniform, GLint x, GLint y, GLint z,
    GLint w)
{
    ENTER_CONTEXT_SCOPE();

    if (!maybeUniform.hasValue()) {
        return;
    }

    WebGLUniformLocation* uniform = maybeUniform.value();

    if (!isFromCurrentProgram(uniform)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    m_gl->uniform4i(uniform->location(), x, y, z, w);
}

void WebGLRenderingContext::useProgram(Optional<WebGLProgram*> maybeProgram)
{
    ENTER_CONTEXT_SCOPE();

    if (maybeProgram.hasValue()) {
        WebGLProgram* program = maybeProgram.value();
        if (!isFromCurrentContext(program)) {
            setGLError(GL_INVALID_OPERATION);
            return;
        }
        m_gl->useProgram(program->glObject());
        m_state->setWebGLProgram(program);
    } else {
        m_gl->useProgram(0);
        m_state->setWebGLProgram(nullptr);
    }
}

void WebGLRenderingContext::validateProgram(WebGLProgram* program)
{
    ENTER_CONTEXT_SCOPE();

    STARFISH_ASSERT(program != nullptr);

    // If program was generated by a different WebGLRenderingContext than this
    // one, generates an INVALID_OPERATION error.
    m_gl->validateProgram(program->glObject());
}

void WebGLRenderingContext::vertexAttrib1f(GLuint index, GLfloat x)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->vertexAttrib1f(index, x);
}

void WebGLRenderingContext::vertexAttrib2f(GLuint index, GLfloat x, GLfloat y)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->vertexAttrib2f(index, x, y);
}

void WebGLRenderingContext::vertexAttrib3f(GLuint index, GLfloat x, GLfloat y,
                                           GLfloat z)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->vertexAttrib3f(index, x, y, z);
}

void WebGLRenderingContext::vertexAttrib4f(GLuint index, GLfloat x, GLfloat y,
                                           GLfloat z, GLfloat w)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->vertexAttrib4f(index, x, y, z, w);
}

#define IMPLEMENT_VERTEX_ATTRIB_NFV(N)                                        \
    void WebGLRenderingContext::vertexAttrib##N##fv(GLuint index,             \
                                                    Float32List variant)      \
    {                                                                         \
        ENTER_CONTEXT_SCOPE();                                                \
        if (variant.isFloat32ArrayValue()) {                                  \
            Float32ArrayObjectRef* values = variant.getFloat32ArrayValue();   \
            const size_t arrayLength = values->arrayLength();                 \
            uint8_t* rawBuffer = const_cast<uint8_t*>(values->rawBuffer());   \
            if (arrayLength < N) {                                            \
                setGLError(GL_INVALID_VALUE);                                 \
                return;                                                       \
            }                                                                 \
            m_gl->vertexAttrib##N##fv(index,                                  \
                                      reinterpret_cast<GLfloat*>(rawBuffer)); \
        } else {                                                              \
            STARFISH_ASSERT(variant.isSequenceOfGLfloatValue());              \
            /* Due to the memory size of double and float types, the raw      \
             * buffer returned by GCAtomicVector<double>::data() cannot be    \
             * used directly. Reconstructs a float buffer including values    \
             * converted from double. */                                      \
            const GCAtomicVector<double> v =                                  \
                variant.getSequenceOfGLfloatValue();                          \
            if (v.size() < N) {                                               \
                setGLError(GL_INVALID_VALUE);                                 \
                return;                                                       \
            }                                                                 \
            std::vector<GLfloat> vector;                                      \
            vector.reserve(v.size());                                         \
            for (const double& value : v) {                                   \
                vector.push_back(static_cast<GLfloat>(value));                \
            }                                                                 \
            m_gl->vertexAttrib##N##fv(index, vector.data());                  \
        }                                                                     \
    }

IMPLEMENT_VERTEX_ATTRIB_NFV(1)
IMPLEMENT_VERTEX_ATTRIB_NFV(2)
IMPLEMENT_VERTEX_ATTRIB_NFV(3)
IMPLEMENT_VERTEX_ATTRIB_NFV(4)

#undef IMPLEMENT_VERTEX_ATTRIB_NFV

void WebGLRenderingContext::vertexAttribPointer(GLuint index, GLint size,
                                                GLenum type,
                                                GLboolean normalized,
                                                GLsizei stride, GLintptr offset)
{
    ENTER_CONTEXT_SCOPE();

    // See Buffer Offset and Stride Requirements.
    switch (type) {
    case GL_BYTE:
    case GL_UNSIGNED_BYTE:
        break;
    case GL_SHORT:
    case GL_UNSIGNED_SHORT:
        if (offset % 2 != 0 || stride % 2 != 0) {
            setGLError(GL_INVALID_OPERATION);
            return;
        }
        break;
    case GL_FLOAT:
        if (offset % 4 != 0 || stride % 4 != 0) {
            setGLError(GL_INVALID_OPERATION);
            return;
        }
        break;
    default:
        setGLError(GL_INVALID_ENUM);
        return;
    }

    if (offset < 0) {
        // If offset is negative, an INVALID_VALUE error will be generated.
        setGLError(GL_INVALID_VALUE);
        return;
    }

    if (!getState()->getBoundBuffer(GL_ARRAY_BUFFER).hasValue() &&
        offset != 0) {
        // If no WebGLBuffer is bound to the ARRAY_BUFFER target and offset is
        // non-zero, an INVALID_OPERATION error will be generated.
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    if (stride > kMaximumSupportedStride) {
        // In WebGL, the maximum supported stride is 255
        setGLError(GL_INVALID_VALUE);
        return;
    }

    /*
        The following errors are handled in GLES3.
        (https://docs.gl/es3/glVertexAttribPointer)
        We don't do any additional validation for them:
        - GL_INVALID_VALUE if size is not 1, 2, 3 or 4.
        - GL_INVALID_ENUM if type is not an accepted value.
        - GL_INVALID_VALUE if stride is negative.
        - GL_INVALID_VALUE if index is greater than or equal to
            GL_MAX_VERTEX_ATTRIBS.
        - GL_INVALID_OPERATION if type is GL_INT_2_10_10_10_REV or
            GL_UNSIGNED_INT_2_10_10_10_REV and size is not 4.
        - GL_INVALID_OPERATION a non-zero vertex array object is bound, zero is
            bound to the GL_ARRAY_BUFFER buffer object binding point and the
            pointer argument is not NULL.
    */
    m_gl->vertexAttribPointer(index, size, type, normalized, stride,
                              reinterpret_cast<void*>(offset));
    if (hasNewGLError()) {
        return;
    }
    m_state->setBufferBoundToVertexAttributes(
        index, m_state->getBoundBuffer(GL_ARRAY_BUFFER));
}

void WebGLRenderingContext::viewport(uint32_t x, uint32_t y, uint32_t width,
                                     uint32_t height)
{
    ENTER_CONTEXT_SCOPE();

    m_gl->viewport(x, y, width, height);
}

// WebGLRenderingContextOverloads

void WebGLRenderingContext::bufferData(GLenum target, GLsizeiptr size,
                                       GLenum usage)
{
    ENTER_CONTEXT_SCOPE();

    // Set the size of the currently bound WebGLBuffer object for the passed
    // target. The buffer is initialized to 0.
    std::vector<unsigned char> zeros(size);
    m_gl->bufferData(target, size, zeros.data(), usage);
}

void WebGLRenderingContext::bufferData(GLenum target,
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
        m_gl->bufferData(target, buffer->byteLength(), buffer->rawBuffer(),
                         usage);
    } else if (data.value().isArrayBufferViewValue()) {
        ScriptArrayBufferView view = data.value().getArrayBufferViewValue();
        m_gl->bufferData(target, view->byteLength(), view->rawBuffer(), usage);
    } else if (data.value().isSharedArrayBufferValue()) {
        ScriptSharedArrayBuffer buffer =
            data.value().getSharedArrayBufferValue();
        m_gl->bufferData(target, buffer->byteLength(), buffer->rawBuffer(),
                         usage);
    } else {
        setGLError(GL_INVALID_VALUE);
    }
}

void WebGLRenderingContext::bufferSubData(GLenum target, GLintptr offset,
                                          AllowSharedBufferSource data)
{
    ENTER_CONTEXT_SCOPE();

    if (data.isArrayBufferValue()) {
        ScriptArrayBuffer buffer = data.getArrayBufferValue();
        m_gl->bufferSubData(target, offset, buffer->byteLength(),
                            buffer->rawBuffer());
    } else if (data.isArrayBufferViewValue()) {
        ScriptArrayBufferView view = data.getArrayBufferViewValue();
        m_gl->bufferSubData(target, offset, view->byteLength(),
                            view->rawBuffer());
    } else if (data.isSharedArrayBufferValue()) {
        ScriptSharedArrayBuffer buffer = data.getSharedArrayBufferValue();
        m_gl->bufferSubData(target, offset, buffer->byteLength(),
                            buffer->rawBuffer());
    } else {
        setGLError(GL_INVALID_VALUE);
    }
}

void WebGLRenderingContext::compressedTexImage2D(GLenum target, GLint level,
                                                 GLenum internalformat,
                                                 GLsizei width, GLsizei height,
                                                 GLint border,
                                                 ScriptArrayBufferView data)
{
    if (!boundTexture(target)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    STARFISH_ASSERT(
        WebGLExtensionRegistry::instance().hasTextureCompressionExtension() ==
        false);

    // The core WebGL specification does not define any supported compressed
    // texture formats. By default, these methods generate an INVALID_ENUM error
    // and return immediately. See Compressed Texture Support.

    setGLError(GL_INVALID_ENUM);
}

void WebGLRenderingContext::compressedTexSubImage2D(
    GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width,
    GLsizei height, GLenum format, ScriptArrayBufferView data)
{
    if (!boundTexture(target)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    STARFISH_ASSERT(
        WebGLExtensionRegistry::instance().hasTextureCompressionExtension() ==
        false);

    setGLError(GL_INVALID_ENUM);
}

bool WebGLRenderingContext::validatePixelTransferSize(
    GLsizei width, GLsizei height, GLenum format, GLenum type, bool unpack,
    size_t bufferSize, size_t& stride, size_t& offset)
{
    if (width < 0 || height < 0) {
        setGLError(GL_INVALID_VALUE);
        return false;
    }
    const size_t bytesPerPixel = getBytesPerPixel(format, type);
    if (!bytesPerPixel) {
        setGLError(GL_INVALID_ENUM);
        return false;
    }
    GLint alignment = 0, rowLength = 0, skipRows = 0, skipPixels = 0;
    m_gl->getIntegerv(unpack ? GL_UNPACK_ALIGNMENT : GL_PACK_ALIGNMENT,
                      &alignment);
    if (webGLVersion() == 2) {
        m_gl->getIntegerv(unpack ? GL_UNPACK_ROW_LENGTH : GL_PACK_ROW_LENGTH,
                          &rowLength);
        m_gl->getIntegerv(unpack ? GL_UNPACK_SKIP_ROWS : GL_PACK_SKIP_ROWS,
                          &skipRows);
        m_gl->getIntegerv(unpack ? GL_UNPACK_SKIP_PIXELS : GL_PACK_SKIP_PIXELS,
                          &skipPixels);
    }
    const uint64_t storeWidth = rowLength ? rowLength : width;
    if (uint64_t(skipPixels) + width > storeWidth) {
        setGLError(GL_INVALID_OPERATION);
        return false;
    }
    stride = offset = 0;
    if (width == 0 || height == 0) {
        return true;
    }
    const uint64_t rowBytes = storeWidth * bytesPerPixel;
    const uint64_t rowStride =
        (rowBytes + alignment - 1) / alignment * alignment;
    const uint64_t lastRowBytes =
        (uint64_t(skipPixels) + width) * bytesPerPixel;
    const uint64_t precedingRows = uint64_t(skipRows) + height - 1;
    // The final row has no trailing padding. Division bounds all arithmetic
    // before native GL can read or write outside the supplied view.
    // https://registry.khronos.org/webgl/specs/latest/2.0/#PixelStoreParams
    if (lastRowBytes > bufferSize ||
        precedingRows > (bufferSize - lastRowBytes) / rowStride) {
        setGLError(GL_INVALID_OPERATION);
        return false;
    }
    stride = rowStride;
    offset =
        uint64_t(skipRows) * rowStride + uint64_t(skipPixels) * bytesPerPixel;
    return true;
}

size_t WebGLRenderingContext::getBytesPerPixel(GLenum format, GLenum type)
{
    return Pixel::getBytesPerPixel(format, type, 1);
}

void WebGLRenderingContext::readPixels(GLint x, GLint y, GLsizei width,
                                       GLsizei height, GLenum format,
                                       GLenum type,
                                       Optional<ScriptArrayBufferView> pixels)
{
    ENTER_CONTEXT_SCOPE();

    if (!pixels) {
        setGLError(GL_INVALID_VALUE);
        return;
    }
    if (width < 0 || height < 0) {
        setGLError(GL_INVALID_VALUE);
        return;
    }
    if (format != GL_RGBA && format != GL_RGB && format != GL_ALPHA) {
        setGLError(GL_INVALID_ENUM);
        return;
    }
    if (!isSrcDataValid(pixels.value(), type)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }
    if (m_gl->checkFramebufferStatus(GL_FRAMEBUFFER) !=
        GL_FRAMEBUFFER_COMPLETE) {
        setGLError(GL_INVALID_FRAMEBUFFER_OPERATION);
        return;
    }
    size_t stride = 0, offset = 0;
    if (!validatePixelTransferSize(width, height, format, type, false,
                                   pixels->byteLength(), stride, offset)) {
        return;
    }
    // Escargot's rawBuffer() already points to the beginning of this view.
    m_gl->readPixels(x, y, width, height, format,
                     promotedWebGL1Type(format, type), pixels->rawBuffer());
}

class TexImageHelper final {
public:
    // NOTE: Better to use common utilities for image manipulation. Canvas
    // is not possible due to its WebView dependency.
    struct ImageData {
        ImageData() = default;
        size_t width = 0;
        size_t height = 0;
        size_t stride = 0;
        GLenum format = 0;
        unsigned char* data = nullptr;
    };

    TexImageHelper(size_t width, size_t height, size_t stride, GLenum format,
                   void* data)
    {
        STARFISH_ASSERT(data != nullptr);

        m_sourceImage.width = width;
        m_sourceImage.height = height;
        m_sourceImage.stride = stride;
        m_sourceImage.format = format;
        m_sourceImage.data = static_cast<unsigned char*>(data);
        m_isNativeImageDataUsed = false;
    }

    TexImageHelper(NativeImageData* imageData, GLenum format)
    {
        STARFISH_ASSERT(imageData != nullptr);

        m_sourceImage.width = imageData->width();
        m_sourceImage.height = imageData->height();
        m_sourceImage.stride = imageData->stride();
        m_sourceImage.format = format;
        m_sourceImage.data = static_cast<unsigned char*>(imageData->data());
        m_isNativeImageDataUsed = true;
    }

    ~TexImageHelper()
    {
    }

    void draw(const bool needsFlipY, const bool needsPremultiplyAlpha,
              const GLenum type, const size_t bytesPerPixel)
    {
        const size_t width = m_sourceImage.width;
        const size_t height = m_sourceImage.height;
        const unsigned char* image = m_sourceImage.data;

        size_t offset = 0, newOffset = 0, srcOffset = 0, destOffset = 0;

        if (type == GL_FLOAT || type == GL_HALF_FLOAT_OES ||
            type == GL_HALF_FLOAT) {
            drawFloatingPoint(needsFlipY, needsPremultiplyAlpha, type,
                              bytesPerPixel);
            return;
        }

        if (m_sourceImage.format != GL_RGB && m_sourceImage.format != GL_RGBA) {
            return;
        }

        if (m_isNativeImageDataUsed && type != GL_UNSIGNED_BYTE &&
            !Pixel::isTwoBytesPerPixel(type)) {
            STARFISH_UNSUPPORTED(
                "type (%s). Only GL_UNSIGNED_BYTE and packed short types are "
                "supported for NativeImageData sources.",
                hex(type).c_str());
        }

#if !defined(PORT_PIXEL_ORDER_RGBA) && !defined(PORT_PIXEL_ORDER_BGRA)
        STARFISH_ASSERT_NOT_REACHED();
        return;
#endif

        bool needsColorConversion = false;

#if defined(PORT_PIXEL_ORDER_BGRA)
        if (m_isNativeImageDataUsed) {
            // NativeImageData is formatted as BGRA.
            if (m_sourceImage.format == GL_RGBA && type == GL_UNSIGNED_BYTE &&
                WebGLExtensionRegistry::instance()
                    .hasEXT_texture_format_BGRA8888()) {
                m_dataFormat = GL_BGRA_EXT;
                needsColorConversion = false;
            } else {
                needsColorConversion = true;
            }
        }
#endif

        const size_t srcBytesPerPixel =
            m_isNativeImageDataUsed ? 4 : bytesPerPixel;
        const size_t srcStride = m_sourceImage.stride;
        const size_t dstBytesPerPixel = bytesPerPixel;
        const bool needsStrideConversion =
            (srcBytesPerPixel != dstBytesPerPixel);

        if (!needsFlipY && !needsPremultiplyAlpha && !needsColorConversion &&
            !needsStrideConversion) {
            return;
        }

        const size_t dstStride = dstBytesPerPixel * width;
        m_data.resize(height * dstStride);

        std::vector<uint8_t> order;

        if (needsColorConversion) {
            order = { 2, 1, 0, 3 };
        } else {
            order = { 0, 1, 2, 3 };
        }

        for (size_t row = 0; row < height; row++) {
            // Calculate the memory offset for the current row
            offset = row * srcStride;

            // NOTE: For increasing more performance of this feature, we may
            // consider using fragment shader.
            if (needsFlipY) {
                newOffset = (height - row - 1) * dstStride;
            } else {
                newOffset = row * dstStride;
            }

            for (size_t column = 0; column < width; column++) {
                // Calculate the memory offset for the current pixel
                srcOffset = offset + column * srcBytesPerPixel;
                destOffset = newOffset + column * dstBytesPerPixel;

                if (Pixel::isTwoBytesPerPixel(type)) {
                    if (m_isNativeImageDataUsed) {
                        uint8_t r = image[srcOffset + order[0]];
                        uint8_t g = image[srcOffset + order[1]];
                        uint8_t b = image[srcOffset + order[2]];
                        uint8_t a = image[srcOffset + order[3]];
                        if (needsPremultiplyAlpha) {
                            float alpha = a / 255.f;
                            r = multiplyAlpha(r, alpha);
                            g = multiplyAlpha(g, alpha);
                            b = multiplyAlpha(b, alpha);
                        }
                        GLushort packed;
                        if (type == GL_UNSIGNED_SHORT_5_5_5_1) {
                            packed = Pixel::makePixel5551(r, g, b, a);
                        } else if (type == GL_UNSIGNED_SHORT_4_4_4_4) {
                            packed = Pixel::makePixel4444(r, g, b, a);
                        } else if (type == GL_UNSIGNED_SHORT_5_6_5) {
                            packed = Pixel::makePixel565(r, g, b);
                        } else {
                            STARFISH_ASSERT_NOT_REACHED();
                        }
                        memcpy(&m_data[destOffset], &packed, sizeof(GLushort));
                    } else {
                        m_data[destOffset + 0] = image[srcOffset + 0];
                        m_data[destOffset + 1] = image[srcOffset + 1];
                    }
                } else if (needsPremultiplyAlpha && srcBytesPerPixel == 4) {
                    float alpha = image[srcOffset + order[3]] / 255.f;
                    m_data[destOffset + 0] =
                        multiplyAlpha(image[srcOffset + order[0]], alpha);
                    m_data[destOffset + 1] =
                        multiplyAlpha(image[srcOffset + order[1]], alpha);
                    m_data[destOffset + 2] =
                        multiplyAlpha(image[srcOffset + order[2]], alpha);
                    if (dstBytesPerPixel == 4) {
                        m_data[destOffset + 3] = image[srcOffset + order[3]];
                    }
                } else {
                    m_data[destOffset + 0] = image[srcOffset + order[0]];
                    m_data[destOffset + 1] = image[srcOffset + order[1]];
                    m_data[destOffset + 2] = image[srcOffset + order[2]];
                    if (dstBytesPerPixel == 4) {
                        m_data[destOffset + 3] = image[srcOffset + order[3]];
                    }
                }
            }
        }
    }

    const void* data() const
    {
        return m_data.empty() ? m_sourceImage.data : m_data.data();
    }

    const ImageData& sourceImage() const
    {
        return m_sourceImage;
    }

    Optional<GLenum> dataFormat() const
    {
        return m_dataFormat;
    }

    bool converted() const
    {
        return !m_data.empty();
    }

private:
    static float fromHalf(uint16_t value)
    {
        const unsigned exponent = (value >> 10) & 31;
        const unsigned mantissa = value & 1023;
        float result;
        if (exponent == 31) {
            result = mantissa ? std::numeric_limits<float>::quiet_NaN()
                              : std::numeric_limits<float>::infinity();
        } else {
            result = exponent ? std::ldexp(float(1024 + mantissa),
                                           int(exponent) - 25)
                              : std::ldexp(float(mantissa), -24);
        }
        return value & 0x8000 ? -result : result;
    }

    static uint16_t toHalf(float value)
    {
        uint32_t bits;
        memcpy(&bits, &value, sizeof(bits));
        const uint16_t sign = (bits >> 16) & 0x8000;
        const unsigned rawExponent = (bits >> 23) & 255;
        uint32_t mantissa = bits & 0x7fffff;
        const int exponent = int(rawExponent) - 127 + 15;
        if (exponent >= 31) {
            return sign | (rawExponent == 255 && mantissa ? 0x7e00 : 0x7c00);
        }
        if (exponent <= 0) {
            if (exponent < -10) {
                return sign;
            }
            mantissa |= 0x800000;
            const unsigned shift = 14 - exponent;
            const unsigned halfway = 1u << (shift - 1);
            return sign |
                   ((mantissa + halfway - 1 + ((mantissa >> shift) & 1)) >>
                    shift);
        }
        // IEEE 754 round-to-nearest, ties-to-even, including mantissa carry.
        return sign | ((exponent << 10) +
                       ((mantissa + 0xfff + ((mantissa >> 13) & 1)) >> 13));
    }

    void drawFloatingPoint(bool flipY, bool premultiply, GLenum type,
                           size_t bytesPerPixel)
    {
        if (!m_isNativeImageDataUsed && !flipY && !premultiply) {
            return;
        }
        const size_t componentSize = type == GL_FLOAT ? 4 : 2;
        const size_t components = bytesPerPixel / componentSize;
        const size_t rowBytes = m_sourceImage.width * bytesPerPixel;
        m_data.resize(m_sourceImage.height * rowBytes);
        for (size_t y = 0; y < m_sourceImage.height; ++y) {
            const unsigned char* source =
                m_sourceImage.data + y * m_sourceImage.stride;
            unsigned char* dest =
                m_data.data() +
                rowBytes * (flipY ? m_sourceImage.height - y - 1 : y);
            if (!m_isNativeImageDataUsed && !premultiply) {
                memcpy(dest, source, rowBytes);
                continue;
            }
            for (size_t x = 0; x < m_sourceImage.width; ++x) {
                float values[4] = { 0, 0, 0, 1 };
                if (m_isNativeImageDataUsed) {
#if defined(PORT_PIXEL_ORDER_BGRA)
                    const unsigned order[] = { 2, 1, 0, 3 };
#else
                    const unsigned order[] = { 0, 1, 2, 3 };
#endif
                    for (size_t c = 0; c < 4; ++c) {
                        values[c] = source[x * 4 + order[c]] / 255.f;
                    }
                    // Native canvas/image surfaces store premultiplied color.
                    // WebGL's default upload requests straight color; retain
                    // the native premultiplication only when requested.
                    if (!premultiply && values[3] > 0) {
                        for (size_t c = 0; c < 3; ++c) {
                            values[c] /= values[3];
                        }
                    }
                    if (m_sourceImage.format == GL_ALPHA) {
                        values[0] = values[3];
                    } else if (m_sourceImage.format == GL_LUMINANCE_ALPHA) {
                        values[1] = values[3];
                    }
                } else {
                    for (size_t c = 0; c < components; ++c) {
                        const unsigned char* component =
                            source + x * bytesPerPixel + c * componentSize;
                        if (type == GL_FLOAT) {
                            memcpy(&values[c], component, componentSize);
                        } else {
                            uint16_t half;
                            memcpy(&half, component, componentSize);
                            values[c] = fromHalf(half);
                        }
                    }
                }
                const size_t alphaIndex =
                    m_sourceImage.format == GL_RGBA              ? 3
                    : m_sourceImage.format == GL_LUMINANCE_ALPHA ? 1
                                                                 : 0;
                if (premultiply && !m_isNativeImageDataUsed) {
                    for (size_t c = 0; c < alphaIndex; ++c) {
                        values[c] *= values[alphaIndex];
                    }
                }
                for (size_t c = 0; c < components; ++c) {
                    unsigned char* component =
                        dest + x * bytesPerPixel + c * componentSize;
                    if (type == GL_FLOAT) {
                        memcpy(component, &values[c], componentSize);
                    } else {
                        const uint16_t half = toHalf(values[c]);
                        memcpy(component, &half, componentSize);
                    }
                }
            }
        }
    }

    unsigned char multiplyAlpha(unsigned char color, float alpha)
    {
        return ((color / 255.f) * alpha) * 255;
    }

    ImageData m_sourceImage;
    std::vector<unsigned char> m_data;
    bool m_isNativeImageDataUsed;
    Optional<GLenum> m_dataFormat;
};

bool WebGLRenderingContext::isSrcDataValid(ScriptArrayBufferView srcData,
                                           GLenum type)
{
    if (type == GL_UNSIGNED_BYTE && (!srcData->isUint8ArrayObject() &&
                                     !srcData->isUint8ClampedArrayObject())) {
        // If it is UNSIGNED_BYTE, a Uint8Array or Uint8ClampedArray
        // must be supplied.
        return false;
    }
    if ((type == GL_UNSIGNED_SHORT_5_6_5 || type == GL_UNSIGNED_SHORT_4_4_4_4 ||
         type == GL_UNSIGNED_SHORT_5_5_5_1) &&
        !srcData->isUint16ArrayObject()) {
        // If it is UNSIGNED_SHORT_5_6_5, UNSIGNED_SHORT_4_4_4_4, or
        // UNSIGNED_SHORT_5_5_5_1, a Uint16Array must be supplied.
        return false;
    }
    if ((type == GL_FLOAT && !srcData->isFloat32ArrayObject()) ||
        (type == GL_HALF_FLOAT_OES && !srcData->isUint16ArrayObject())) {
        return false;
    }
    return true;
}

void WebGLRenderingContext::handleTexImageWithArrayBufferView(
    GLenum target, GLint level, GLsizei width, GLsizei height, GLenum format,
    GLenum type, Optional<ScriptArrayBufferView> pixels,
    std::function<void(const void*)> updateImage)
{
    ensureExtensionRegistryInitialized();
    if (width < 0 || height < 0) {
        setGLError(GL_INVALID_VALUE);
        return;
    }

    // OES_texture_float is required in WebGL 1 for both data uploads and
    // null allocations; float uploads are a core feature in WebGL 2.
    // https://registry.khronos.org/webgl/extensions/OES_texture_float/
    if (type == GL_FLOAT && webGLVersion() == 1 &&
        !isExtensionEnabled("OES_texture_float")) {
        setGLError(GL_INVALID_ENUM);
        return;
    }
    // HALF_FLOAT_OES is a WebGL 1 extension enum, not WebGL 2's HALF_FLOAT.
    // https://registry.khronos.org/webgl/extensions/OES_texture_half_float/
    if (type == GL_HALF_FLOAT_OES &&
        (webGLVersion() != 1 ||
         !isExtensionEnabled("OES_texture_half_float"))) {
        setGLError(GL_INVALID_ENUM);
        return;
    }

    if (webGLVersion() == 2) {
        GLint unpackBuffer = 0;
        m_gl->getIntegerv(GL_PIXEL_UNPACK_BUFFER_BINDING, &unpackBuffer);
        if (unpackBuffer != 0) {
            // The ArrayBufferView overload cannot read from a pixel buffer.
            setGLError(GL_INVALID_OPERATION);
            return;
        }
    }

    if (pixels && !isSrcDataValid(pixels.getValue(), type)) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }

    const size_t bytesPerPixel = getBytesPerPixel(format, type);
    if (bytesPerPixel == 0) {
        setGLError(GL_INVALID_ENUM);
        return;
    }
    const size_t maxByteLength = std::numeric_limits<size_t>::max();
    if (static_cast<size_t>(width) > maxByteLength / bytesPerPixel) {
        setGLError(pixels ? GL_INVALID_OPERATION : GL_OUT_OF_MEMORY);
        return;
    }
    const size_t rowByteLength = static_cast<size_t>(width) * bytesPerPixel;
    if (height != 0 &&
        rowByteLength > maxByteLength / static_cast<size_t>(height)) {
        setGLError(pixels ? GL_INVALID_OPERATION : GL_OUT_OF_MEMORY);
        return;
    }
    const size_t byteLengthOfPixels = rowByteLength * height;

    if (pixels) {
        ArrayBufferViewRef* pixelsView = pixels.getValue();

        // If pixels is non-null but its size is less than what is required by
        // the specified width, height, format, type, and pixel storage
        // parameters, generates an INVALID_OPERATION error.
        size_t byteLengthOfView = pixels->byteLength();

        TRACEF(WEBGL, "\n%s",
               StringUtils::createTableString(20, KV(hex(target)), KV(width),
                                              KV(height), KV(bytesPerPixel),
                                              KV(byteLengthOfPixels)));

        size_t sourceStride = 0, sourceOffset = 0;
        if (!validatePixelTransferSize(width, height, format, type, true,
                                       byteLengthOfView, sourceStride,
                                       sourceOffset)) {
            return;
        }

        if (width == 0 || height == 0) {
            updateImage(pixelsView->rawBuffer());
            return;
        }
        GLvoid* data = pixelsView->rawBuffer() + sourceOffset;

        // Handle WebGL-specific pixel storage parameters that affect the
        // behavior of this function.
        TexImageHelper image(width, height, sourceStride, format, data);
        image.draw(m_unpackFlipY, m_unpackPremultiplyAlpha, type,
                   bytesPerPixel);

        if (!image.converted()) {
            updateImage(pixelsView->rawBuffer());
            return;
        }
        const GLenum parameters[] = { GL_UNPACK_ALIGNMENT, GL_UNPACK_ROW_LENGTH,
                                      GL_UNPACK_SKIP_ROWS,
                                      GL_UNPACK_SKIP_PIXELS };
        GLint saved[4];
        size_t count = webGLVersion() == 2 ? 4 : 1;
        for (size_t i = 0; i < count; ++i) {
            m_gl->getIntegerv(parameters[i], &saved[i]);
            m_gl->pixelStorei(parameters[i], i == 0 ? 1 : 0);
        }
        updateImage(image.data());
        for (size_t i = 0; i < count; ++i) {
            m_gl->pixelStorei(parameters[i], saved[i]);
        }
    } else {
        // WebGL 1.0, 5.14.8 requires all components (including alpha) to be
        // zero when pixels is null. calloc avoids an extra full-buffer fill
        // and lets the allocator use demand-zero pages for large textures.
        // https://registry.khronos.org/webgl/specs/latest/1.0/#5.14.8
        void* zeroData =
            std::calloc(std::max<size_t>(byteLengthOfPixels, 1), 1);
        if (!zeroData) {
            setGLError(GL_OUT_OF_MEMORY);
            return;
        }

        // Application unpack state must not change the layout of this
        // implementation-owned, tightly packed zero buffer.
        const GLenum unpackParameters[] = { GL_UNPACK_ALIGNMENT,
                                            GL_UNPACK_ROW_LENGTH,
                                            GL_UNPACK_SKIP_ROWS,
                                            GL_UNPACK_SKIP_PIXELS };
        GLint savedUnpackParameters[4];
        const size_t parameterCount = webGLVersion() == 2 ? 4 : 1;
        for (size_t i = 0; i < parameterCount; ++i) {
            m_gl->getIntegerv(unpackParameters[i], &savedUnpackParameters[i]);
            m_gl->pixelStorei(unpackParameters[i], i == 0 ? 1 : 0);
        }
        auto onScopeLeave = OnScopeLeave::create([&]() {
            for (size_t i = 0; i < parameterCount; ++i) {
                m_gl->pixelStorei(unpackParameters[i],
                                  savedUnpackParameters[i]);
            }
            std::free(zeroData);
        });

        updateImage(zeroData);
    }
}

void WebGLRenderingContext::handleTexImageWithImageSource(
    const GLenum format, const GLenum type, const TexImageSource& source,
    std::function<void(const TexImageHelper*)> updateImage)
{
    ensureExtensionRegistryInitialized();
    if ((type == GL_FLOAT && webGLVersion() == 1 &&
         !isExtensionEnabled("OES_texture_float")) ||
        (type == GL_HALF_FLOAT_OES &&
         (webGLVersion() != 1 ||
          !isExtensionEnabled("OES_texture_half_float")))) {
        setGLError(GL_INVALID_ENUM);
        return;
    }
    STARFISH_ASSERT(updateImage != nullptr);

    GLsizei width = 0;
    GLsizei height = 0;
    GLsizei stride = 0;
    NativeImageData* imageData = nullptr;

    if (source.isNoneValue()) {
        setGLError(GL_INVALID_VALUE);
        return;
    } else if (source.isImageBitmapValue()) {
        TRACE(WEBGL, "source.isImageBitmapValue");
        ImageBitmap* imageBitmap = source.getImageBitmapValue();
        imageData = imageBitmap->nativeImageData();
        width = imageData->width();
        height = imageData->height();
    } else if (source.isImageDataValue()) {
        STARFISH_UNIMPLEMENTED("ImageData");
    } else if (source.isHTMLImageElementValue()) {
        TRACE(WEBGL, "source.isHTMLImageElementValue");
        HTMLImageElement* element = source.getHTMLImageElementValue();
        imageData = element->imageData();
        if (imageData == nullptr) {
            // For suppressing annoying coverity issue (false positive)
            STARFISH_ASSERT_NOT_REACHED();
            return;
        }
        if (imageData->isSVGNativeImageData()) {
            STARFISH_UNIMPLEMENTED("SVGNativeImageData");
            width = element->width();
            height = element->height();
        } else {
            width = imageData->width();
            height = imageData->height();
        }
    } else if (source.isHTMLCanvasElementValue()) {
        TRACE(WEBGL, "source.isHTMLCanvasElementValue");
        // TODO: Consider using CanvasImageSourceUtils::toNativeImageData
        HTMLCanvasElement* element = source.getHTMLCanvasElementValue();
        CanvasRenderingContext* context = element->canvasRenderingContext();
        STARFISH_ASSERT(context != nullptr);
        auto context2d = static_cast<CanvasRenderingContext2DMixIn*>(context);
        context2d->flushForReadback();
        imageData = NativeImageData::attach(context2d->canvas());
        width = element->width();
        height = element->height();
    }
#ifdef STARFISH_ENABLE_MULTIMEDIA
    else if (source.isHTMLVideoElementValue()) {
        STARFISH_UNIMPLEMENTED("HTMLVideoElement");
    }
#endif
    else {
        STARFISH_ASSERT_NOT_REACHED();
        return;
    }

    if (imageData == nullptr) {
        STARFISH_ASSERT_NOT_REACHED();
        return;
    }

    size_t bytesPerPixel = getBytesPerPixel(format, type);
    if (bytesPerPixel == 0) {
        setGLError(GL_INVALID_ENUM);
        return;
    }
    size_t byteLengthOfPixels = width * height * bytesPerPixel;
    stride = bytesPerPixel * width;

    // Handle WebGL-specific pixel storage parameters that affect the behavior
    // of this function.
    TexImageHelper image(imageData, format);
    image.draw(m_unpackFlipY, m_unpackPremultiplyAlpha, type, bytesPerPixel);

    TRACE(WEBGL_V, "source:", KV(width), KV(height), KV(stride),
          KV(byteLengthOfPixels), KV(imageData));

    GLint savedAlignment = 4;
    m_gl->getIntegerv(GL_UNPACK_ALIGNMENT, &savedAlignment);
    if (savedAlignment != 1) {
        m_gl->pixelStorei(GL_UNPACK_ALIGNMENT, 1);
    }
    updateImage(&image);
    if (savedAlignment != 1) {
        m_gl->pixelStorei(GL_UNPACK_ALIGNMENT, savedAlignment);
    }
}

bool WebGLRenderingContext::checkInternalFormat(GLint internalFormat,
                                                GLenum format, GLenum type)
{
    if (!Pixel::isInternalFormatValid(internalFormat, format, type, 1)) {
        // The format, in WebGL 1, must be the same as internalFormat. See:
        // https://developer.mozilla.org/en-US/docs/Web/API/WebGLRenderingContext/texImage2D
        // WebGL 2 checks combination of internalFormat, format, and type.
        setGLError(GL_INVALID_OPERATION,
                   StringUtils::formatString(
                       "The given parameters, internal format (0x%04X) and "
                       "format (0x%04X), are not the same.",
                       internalFormat, format)
                       .c_str());
        return false;
    }
    return true;
}

// EXT_color_buffer_float requires ES 3 and makes sized RGBA32F/RGBA16F
// color-renderable. Use sized storage for WebGL 1's unsized float formats
// on those drivers while retaining the WebGL enums for input validation.
// https://registry.khronos.org/OpenGL/extensions/EXT/EXT_color_buffer_float.txt
GLint WebGLRenderingContext::promotedWebGL1InternalFormat(GLint internalFormat,
                                                          GLenum type)
{
    // Query native support through the WebGL 2 registry entry; this does not
    // expose or enable the WebGL 2-only extension on a WebGL 1 context.
    if (webGLVersion() != 1 || !ensureExtensionRegistryInitialized() ||
        !WebGLExtensionRegistry::instance().getGenerator(
            "EXT_color_buffer_float", 2)) {
        return internalFormat;
    }
    if (type == GL_FLOAT) {
        if (internalFormat == GL_RGBA) {
            return GL_RGBA32F;
        } else if (internalFormat == GL_RGB) {
            return GL_RGB32F;
        }
    } else if (type == GL_HALF_FLOAT_OES) {
        if (internalFormat == GL_RGBA) {
            return GL_RGBA16F;
        } else if (internalFormat == GL_RGB) {
            return GL_RGB16F;
        }
    }
    return internalFormat;
}

GLenum WebGLRenderingContext::promotedWebGL1Type(GLenum format, GLenum type)
{
    // Only RGB/RGBA were promoted to sized ES 3 storage. Legacy alpha and
    // luminance uploads still require the OES type with unsized formats.
    if (webGLVersion() != 1 || (format != GL_RGB && format != GL_RGBA) ||
        !ensureExtensionRegistryInitialized() ||
        !WebGLExtensionRegistry::instance().getGenerator(
            "EXT_color_buffer_float", 2)) {
        return type;
    }
    if (type == GL_HALF_FLOAT_OES) {
        return GL_HALF_FLOAT;
    }
    return type;
}

void WebGLRenderingContext::texImage2D(GLenum target, GLint level,
                                       GLint internalFormat, GLsizei width,
                                       GLsizei height, GLint border,
                                       GLenum format, GLenum type,
                                       Optional<ScriptArrayBufferView> pixels)
{
    ENTER_CONTEXT_SCOPE();

    if (!boundTexture(target)) {
        setGLError(
            GL_INVALID_OPERATION,
            StringUtils::formatString("target (0x%04X) is not bound.", target)
                .c_str());
        return;
    }

    if (!checkInternalFormat(internalFormat, format, type)) {
        return;
    }

    // Validate dimensions before allocating the null-pixels backing buffer.
    GLint maxTextureSize = 0;
    m_gl->getIntegerv(target == GL_TEXTURE_2D ? GL_MAX_TEXTURE_SIZE
                                              : GL_MAX_CUBE_MAP_TEXTURE_SIZE,
                      &maxTextureSize);
    if (border != 0 || width < 0 || height < 0 || level < 0 ||
        level >= std::numeric_limits<GLint>::digits ||
        (maxTextureSize >> level) == 0 || width > (maxTextureSize >> level) ||
        height > (maxTextureSize >> level)) {
        setGLError(GL_INVALID_VALUE);
        return;
    }

    const GLint glInternalFormat =
        promotedWebGL1InternalFormat(internalFormat, type);
    const GLenum glType = promotedWebGL1Type(format, type);

    handleTexImageWithArrayBufferView(
        target, level, width, height, format, type, pixels,
        [&](const void* data) {
            GLint uploadInternalFormat = glInternalFormat;
            GLenum uploadFormat = format;
#if defined(PORT_PIXEL_ORDER_BGRA)
            if (!pixels && internalFormat == GL_RGBA && format == GL_RGBA &&
                type == GL_UNSIGNED_BYTE &&
                WebGLExtensionRegistry::instance()
                    .hasEXT_texture_format_BGRA8888()) {
                // GLES 2.0 section 3.7.2 requires texSubImage2D's format
                // to match the texture's internal format. Keep these byte
                // allocations compatible with later NativeImageData BGRA
                // uploads, without rewriting float or sized formats.
                // https://registry.khronos.org/OpenGL/specs/es/2.0/es_full_spec_2.0.pdf
                uploadInternalFormat = GL_BGRA_EXT;
                uploadFormat = GL_BGRA_EXT;
            }
#endif
            hasNewGLError();
            m_gl->texImage2D(target, level, uploadInternalFormat, width, height,
                             0, uploadFormat, glType, data);
            recordTextureImage(target, level, type);
        });
}

void WebGLRenderingContext::texImage2D(GLenum target, GLint level,
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

    if (!boundTexture(target)) {
        setGLError(
            GL_INVALID_OPERATION,
            StringUtils::formatString("target (0x%04X) is not bound.", target)
                .c_str());
        return;
    }

    if (!checkInternalFormat(internalFormat, format, type)) {
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
            hasNewGLError();
            m_gl->texImage2D(
                target, level,
                helper->dataFormat().valueOr(
                    promotedWebGL1InternalFormat(internalFormat, type)),
                helper->sourceImage().width, helper->sourceImage().height, 0,
                helper->dataFormat().valueOr(format),
                promotedWebGL1Type(format, type), helper->data());
            recordTextureImage(target, level, type);
        });
}

void WebGLRenderingContext::texSubImage2D(
    GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width,
    GLsizei height, GLenum format, GLenum type,
    Optional<ScriptArrayBufferView> pixels)
{
    ENTER_CONTEXT_SCOPE();

    // Unlike texImage2D, texSubImage2D must not initialize null pixels.
    // https://registry.khronos.org/webgl/specs/latest/1.0/#5.14.8
    if (!pixels) {
        setGLError(GL_INVALID_VALUE);
        return;
    }

    const GLenum glType = promotedWebGL1Type(format, type);

    handleTexImageWithArrayBufferView(
        target, level, width, height, format, type, pixels,
        [&](const void* data) {
            m_gl->texSubImage2D(target, level, xoffset, yoffset, width, height,
                                format, glType, data);
        });
}

void WebGLRenderingContext::texSubImage2D(GLenum target, GLint level,
                                          GLint xoffset, GLint yoffset,
                                          GLenum format, GLenum type,
                                          TexImageSource source)
{
    ENTER_CONTEXT_SCOPE();

    handleTexImageWithImageSource(
        format, type, source, [&](const TexImageHelper* helper) {
            STARFISH_ASSERT(helper != nullptr);

            TRACE(WEBGL_V, KV(glValueString(format)),
                  KV(glValueString(helper->dataFormat().valueOr(format))));
            TRACE(WEBGL_V, KV(glValueString(type)));

            // Uploads the given image data to the currently bound texture.
            m_gl->texSubImage2D(
                target, level, xoffset, yoffset, helper->sourceImage().width,
                helper->sourceImage().height,
                helper->dataFormat().valueOr(format),
                promotedWebGL1Type(format, type), helper->data());
        });
}

void WebGLRenderingContext::implementUniformNfv(
    size_t n, void (GL::*uniformNfv)(GLint, GLsizei, const GLfloat*),
    Optional<WebGLUniformLocation*> location, Float32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    ENTER_CONTEXT_SCOPE();
    /* location is nullable. */
    if (!location.hasValue()) {
        return;
    }
    if (!isFromCurrentProgram(location.value())) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }
    if (data.isFloat32ArrayValue()) {
        const ScriptFloat32Array values = data.getFloat32ArrayValue();
        const size_t dataLength = values->arrayLength();
        if (srcOffset >= dataLength) {
            setGLError(GL_INVALID_VALUE);
            return;
        }
        if (srcLength == 0) {
            srcLength = dataLength - srcOffset;
        }
        if (srcLength > dataLength - srcOffset || srcLength < n ||
            srcLength % n != 0) {
            setGLError(GL_INVALID_VALUE);
            return;
        }
        /* count specifies the number of sets. */
        (gl()->*uniformNfv)(
            location.value()->location(), srcLength / n,
            reinterpret_cast<const GLfloat*>(values->rawBuffer()) + srcOffset);
    } else if (data.isSequenceOfGLfloatValue()) {
        const GCAtomicVector<double> values = data.getSequenceOfGLfloatValue();
        const size_t dataLength = values.size();
        if (srcOffset >= dataLength) {
            setGLError(GL_INVALID_VALUE);
            return;
        }
        if (srcLength == 0) {
            srcLength = dataLength - srcOffset;
        }
        if (srcLength > dataLength - srcOffset || srcLength < n ||
            srcLength % n != 0) {
            setGLError(GL_INVALID_VALUE);
            return;
        }
        const std::vector<GLfloat> floats(values.begin(), values.end());
        /* count specifies the number of sets. */
        (gl()->*uniformNfv)(location.value()->location(), srcLength / n,
                            floats.data() + srcOffset);
    } else {
        STARFISH_ASSERT_NOT_REACHED();
    }
}

void WebGLRenderingContext::uniform1fv(Optional<WebGLUniformLocation*> location,
                                       Float32List v)
{
    implementUniformNfv(1, &GL::uniform1fv, location, v, 0, 0);
}

void WebGLRenderingContext::uniform2fv(Optional<WebGLUniformLocation*> location,
                                       Float32List v)
{
    implementUniformNfv(2, &GL::uniform2fv, location, v, 0, 0);
}

void WebGLRenderingContext::uniform3fv(Optional<WebGLUniformLocation*> location,
                                       Float32List v)
{
    implementUniformNfv(3, &GL::uniform3fv, location, v, 0, 0);
}

void WebGLRenderingContext::uniform4fv(Optional<WebGLUniformLocation*> location,
                                       Float32List v)
{
    implementUniformNfv(4, &GL::uniform4fv, location, v, 0, 0);
}

void WebGLRenderingContext::implementUniformNiv(
    size_t n, void (GL::*uniformNiv)(GLint, GLsizei, const GLint*),
    Optional<WebGLUniformLocation*> location, Int32List data,
    unsigned long long srcOffset, GLuint srcLength)
{
    ENTER_CONTEXT_SCOPE();
    /* location is nullable. */
    if (!location) {
        return;
    }
    if (!isFromCurrentProgram(location.value())) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }
    if (data.isInt32ArrayValue()) {
        const ScriptInt32Array values = data.getInt32ArrayValue();
        const size_t dataLength = values->arrayLength();
        if (srcOffset >= dataLength) {
            setGLError(GL_INVALID_VALUE);
            return;
        }
        if (srcLength == 0) {
            srcLength = dataLength - srcOffset;
        }
        if (srcLength > dataLength - srcOffset || srcLength < n ||
            srcLength % n != 0) {
            setGLError(GL_INVALID_VALUE);
            return;
        }
        /* count specifies the number of sets. */
        (gl()->*uniformNiv)(
            location.value()->location(), srcLength / n,
            reinterpret_cast<const GLint*>(values->rawBuffer()) + srcOffset);
    } else if (data.isSequenceOfGLintValue()) {
        const GCAtomicVector<int32_t> values = data.getSequenceOfGLintValue();
        const size_t dataLength = values.size();
        if (srcOffset >= dataLength) {
            setGLError(GL_INVALID_VALUE);
            return;
        }
        if (srcLength == 0) {
            srcLength = dataLength - srcOffset;
        }
        if (srcLength > dataLength - srcOffset || srcLength < n ||
            srcLength % n != 0) {
            setGLError(GL_INVALID_VALUE);
            return;
        }
        /* count specifies the number of sets. */
        (gl()->*uniformNiv)(location.value()->location(), srcLength / n,
                            values.data() + srcOffset);
    } else {
        STARFISH_ASSERT_NOT_REACHED();
    }
}

void WebGLRenderingContext::uniform1iv(Optional<WebGLUniformLocation*> location,
                                       Int32List v)
{
    implementUniformNiv(1, &GL::uniform1iv, location, v, 0, 0);
}

void WebGLRenderingContext::uniform2iv(Optional<WebGLUniformLocation*> location,
                                       Int32List v)
{
    implementUniformNiv(2, &GL::uniform2iv, location, v, 0, 0);
}

void WebGLRenderingContext::uniform3iv(Optional<WebGLUniformLocation*> location,
                                       Int32List v)
{
    implementUniformNiv(3, &GL::uniform3iv, location, v, 0, 0);
}

void WebGLRenderingContext::uniform4iv(Optional<WebGLUniformLocation*> location,
                                       Int32List v)
{
    implementUniformNiv(4, &GL::uniform4iv, location, v, 0, 0);
}

void WebGLRenderingContext::implementUniformMatrixMxNfv(
    size_t m, size_t n,
    void (GL::*uniformMatrixMxNfv)(GLint, GLsizei, GLboolean, const GLfloat*),
    Optional<WebGLUniformLocation*> location, GLboolean transpose,
    Float32List data, unsigned long long srcOffset, GLuint srcLength)
{
    ENTER_CONTEXT_SCOPE();
    /* location is nullable. */
    if (!location.hasValue()) {
        return;
    }
    if (!isFromCurrentProgram(location.value())) {
        setGLError(GL_INVALID_OPERATION);
        return;
    }
    if (data.isFloat32ArrayValue()) {
        const ScriptFloat32Array values = data.getFloat32ArrayValue();
        const size_t dataLength = values->arrayLength();
        if (srcOffset >= dataLength) {
            setGLError(GL_INVALID_VALUE);
            return;
        }
        if (srcLength == 0) {
            srcLength = dataLength - srcOffset;
        }
        if (srcLength > dataLength - srcOffset || srcLength < (m * n) ||
            srcLength % (m * n) != 0) {
            setGLError(GL_INVALID_VALUE);
            return;
        }
        /* count specifies the number of matrices. */
        (gl()->*uniformMatrixMxNfv)(
            location.value()->location(), srcLength / (m * n), transpose,
            reinterpret_cast<const GLfloat*>(values->rawBuffer()) + srcOffset);
    } else if (data.isSequenceOfGLfloatValue()) {
        const GCAtomicVector<double> values = data.getSequenceOfGLfloatValue();
        const size_t dataLength = values.size();
        if (srcOffset >= dataLength) {
            setGLError(GL_INVALID_VALUE);
            return;
        }
        if (srcLength == 0) {
            srcLength = dataLength - srcOffset;
        }
        if (srcLength > dataLength - srcOffset || srcLength < (m * n) ||
            srcLength % (m * n) != 0) {
            setGLError(GL_INVALID_VALUE);
            return;
        }
        const std::vector<GLfloat> floats(values.begin(), values.end());
        /* count specifies the number of matrices. */
        (gl()->*uniformMatrixMxNfv)(location.value()->location(),
                                    srcLength / (m * n), transpose,
                                    floats.data() + srcOffset);
    } else {
        STARFISH_ASSERT_NOT_REACHED();
    }
}

void WebGLRenderingContext::uniformMatrix2fv(
    Optional<WebGLUniformLocation*> uniform, GLboolean transpose,
    Float32List value)
{
    implementUniformMatrixMxNfv(2, 2, &GL::uniformMatrix2fv, uniform, transpose,
                                value, 0, 0);
}

void WebGLRenderingContext::uniformMatrix3fv(
    Optional<WebGLUniformLocation*> uniform, GLboolean transpose,
    Float32List value)
{
    implementUniformMatrixMxNfv(3, 3, &GL::uniformMatrix3fv, uniform, transpose,
                                value, 0, 0);
}

void WebGLRenderingContext::uniformMatrix4fv(
    Optional<WebGLUniformLocation*> uniform, GLboolean transpose,
    Float32List value)
{
    implementUniformMatrixMxNfv(4, 4, &GL::uniformMatrix4fv, uniform, transpose,
                                value, 0, 0);
}

void WebGLRenderingContext::setGLError(GLenum code, const char* message)
{
    m_GLErrors.insert(code);
    if (message) {
        TRACE(WEBGL, "Error(%s): %s", glValueString(code), message);
    }
}

/*
Note: Use hasGLError() to internally check for GL errors. When `glGetError` is
called, the code returned is cleared inside it. If we use `glGetError` directly,
users would not be able to get error code properly. So, we first store the code
from `glGetError`, and then use it. The error code stored will be cleared when
users call gl.getError().
*/
bool WebGLRenderingContext::hasGLError()
{
    return hasNewGLError() || (!m_GLErrors.empty());
}

bool WebGLRenderingContext::hasNewGLError()
{
    bool found = false;
    // GL may retain multiple error flags. Preserve all of them so earlier
    // errors cannot make a later successful state change appear to fail.
    for (GLenum code = m_gl->getError(); code != GL_NO_ERROR;
         code = m_gl->getError()) {
        TRACE(WEBGL, "Error:", glValueString(code));
        setGLError(code);
        found = true;
    }
    return found;
}

bool WebGLRenderingContext::executeInContextScope(
    std::function<void()> callback)
{
    ENTER_CONTEXT_SCOPE(false);
    callback();
    return true;
}

WebGLRenderingContextState* WebGLRenderingContext::getState()
{
    return m_state;
}

bool WebGLRenderingContext::checkAttribOrUniformName(String* name)
{
    // If the passed name is longer than the restriction defined in Maximum
    // Uniform and Attribute Location Lengths, generates an INVALID_VALUE error
    // and returns -1
    if (name->length() > kMaximumUniformAndAttributeLocationLengths) {
        setGLError(GL_INVALID_VALUE);
        return false;
    }

    // Returns -1 if name starts with one of the reserved WebGL prefixes per
    // GLSL Constructs.
    if (name->startsWith("webgl_") || name->startsWith("_webgl_")) {
        return false;
    }

    // TODO?: See Characters Outside the GLSL Source Character Set for
    // additional validation performed by WebGL implementations. WebGL
    // implementations generally must ensure that the shader source sent to a
    // GLSL driver only contains ASCII for safety.
    return true;
}

bool WebGLRenderingContext::isFromCurrentContext(WebGLObject* object)
{
    STARFISH_ASSERT(object != nullptr);

    return object->context() == this;
}

bool WebGLRenderingContext::isBoundCubeMapTexture(GLenum target)
{
    if (target > GL_TEXTURE_BINDING_CUBE_MAP &&
        target < GL_MAX_CUBE_MAP_TEXTURE_SIZE) {
        if (boundTexture(GL_TEXTURE_CUBE_MAP)) {
            return true;
        }
    }
    return false;
}

bool WebGLRenderingContext::isFromCurrentProgram(WebGLUniformLocation* location)
{
    // Consider caching this program id when useProgram is called.
    GLint program = getCurrentProgram();
    if (program == 0) {
        // no program object is active.
        return false;
    }

    if (location->program()->context() != this ||
        location->program()->glObject() != static_cast<GLuint>(program)) {
        // If program were generated by a different WebGLRenderingContext than
        // this one, and location were generated by a different program.
        return false;
    }
    return true;
}

bool WebGLRenderingContext::isExtensionEnabled(const char* name)
{
    const auto& iter = m_enabledExtensions.find(name);
    if (iter != m_enabledExtensions.end()) {
        return true;
    }
    return false;
}

bool WebGLRenderingContext::isDefaultFramebufferBound()
{
    return !m_state->hasWebGLFramebuffer();
}

GLuint WebGLRenderingContext::getCurrentFBO()
{
    return m_state->hasWebGLFramebuffer()
               ? m_state->webGLFramebuffer()->glObject()
               : m_framebufferTexture->fbo();
}

GLint WebGLRenderingContext::getCurrentProgram()
{
    GLint program = 0;
    m_gl->getIntegerv(GL_CURRENT_PROGRAM, &program);
    return program;
}

void WebGLRenderingContext::completePendingJobs()
{
    /*
        +---------+--------------+----------------------+---------------------+
        | Buffer  | Clear value  | Minimum size         | Defined by default? |
        +---------+--------------+----------------------+---------------------+
        | Color   | (0, 0, 0, 0) | 8 bits per component | yes                 |
        | Depth   | 1.0          | 16 bit integer       | yes                 |
        | Stencil | 0            | 8 bits               | no                  |
        +---------+--------------+----------------------+---------------------+

        By default, after compositing the contents of the drawing buffer shall
        be cleared to their default values, as shown in the table above. This
        default behavior can be changed by setting the `preserveDrawingBuffer`
        attribute of the WebGLContextAttributes object.
    */

    if (m_hasPendingJobsBetweenFrames) {
        // If `preserveDrawingBuffer` is true, the contents of the drawing
        // buffer shall be preserved until the author either clears or
        // overwrites them.
        if (!m_attributes.preserveDrawingBuffer()) {
            uint32_t mask = GL_COLOR_BUFFER_BIT;

            // NOTE: If a bit of m_pendingClearMask is 1, it means that users
            // have already set a value corresponding to that bit. Therefore, we
            // will keep the value set by users instead of the default value.

            if (!(m_pendingClearMask & GL_COLOR_BUFFER_BIT)) {
                m_gl->clearColor(0, 0, 0, 0);
            }

            if (m_attributes.depth()) {
                if (!(m_pendingClearMask & GL_DEPTH_BUFFER_BIT)) {
                    m_gl->clearDepthf(1.0);
                }
                mask |= GL_DEPTH_BUFFER_BIT;
            }

            if (m_attributes.stencil()) {
                if (!(m_pendingClearMask & GL_STENCIL_BUFFER_BIT)) {
                    m_gl->clearStencil(0);
                }
                mask |= GL_STENCIL_BUFFER_BIT;
            }

            if (mask != 0) {
                m_gl->clear(mask);
            }
        }
        m_hasPendingJobsBetweenFrames = false;
    }
}

void WebGLRenderingContext::setPendingClearMask(uint32_t mask)
{
    m_pendingClearMask |= mask;
}

GL* WebGLRenderingContext::gl()
{
    return m_gl;
}

} // namespace Starfish

#endif
