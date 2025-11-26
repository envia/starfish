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

#ifndef __StarfishWebGLRenderingContext__
#define __StarfishWebGLRenderingContext__

#if defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)

#include "platform/canvas/gl/GLTypes.h"
#include "core/dom/canvas/webgl/WebGLRenderingContextBase.h"
#include "core/dom/canvas/webgl/WebGLRenderingContextBaseMixIn.h"
#include "core/dom/canvas/webgl/WebGLRenderingContextOverloads.h"
#include "core/dom/canvas/webgl/WebGLUtils.h"
#include "core/dom/canvas/webgl/WebGLContextAttributes.h"
#include "core/util/GCDescriptor.h"

#include <unordered_set>
#include <unordered_map>

namespace Starfish {

class WebGLActiveInfo;
class WebGLBuffer;
class WebGLObject;
class WebGLProgram;
class WebGLShader;
class WebGLTexture;
class WebGLFramebuffer;
class WebGLRenderbuffer;
class WebGLUniformLocation;
class WebGLRenderingContextState;
class WebGLShaderPrecisionFormat;
class String;
class Float32ArrayOrSequenceOfGLfloat;
class Int32ArrayOrSequenceOfGLint;
class ArrayBufferOrSharedArrayBufferOrArrayBufferView;
class
    ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement;
class GL;
class TexImageHelper;

using Float32List = Float32ArrayOrSequenceOfGLfloat;
using Int32List = Int32ArrayOrSequenceOfGLint;
using AllowSharedBufferSource = ArrayBufferOrSharedArrayBufferOrArrayBufferView;
using TexImageSource =
    ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement;

using GLErrorSet = std::unordered_set<GLenum>;
using GLTextureMap = std::unordered_map<GLenum, GLuint>;
using GLExtensionMap =
    GCUnorderedMap<std::string, ScriptObject, CaseInsensitiveHash,
                   CaseInsensitiveEqual>;

class WebGLRenderingContext : public WebGLRenderingContextBaseMixIn, public WebGLRenderingContextBase, public WebGLRenderingContextOverloads {
public:
    WebGLRenderingContext(HTMLCanvasElement* canvasElement);
    virtual ~WebGLRenderingContext();

    DECLARE_SCRIPT_BINDING_REQUIRED_FUNCTIONS(WebGLRenderingContext);

    void preInitialize(ScriptValue contextAttributes);

    void initialize() override;
    void flush() override;
    void onResize() override;

    GLsizei drawingBufferWidth() const;
    GLsizei drawingBufferHeight() const;
    String* drawingBufferColorSpace();
    void setDrawingBufferColorSpace(String* value);
    String* unpackColorSpace();
    void setUnpackColorSpace(String* value);

private:
    void handleTexImageWithArrayBufferView(
        GLenum target, GLint level, GLsizei width, GLsizei height,
        GLenum format, GLenum type, Optional<ScriptArrayBufferView> pixels,
        std::function<void(const TexImageHelper*)> updateImage,
        std::function<void(const std::vector<GLubyte>&)> updateBlackImage,
        std::function<void(const std::vector<GLushort>&)>
            updateTwoBytesBlackImage);
    void handleTexImageWithImageSource(
        const GLenum format, const GLenum type, const TexImageSource& source,
        std::function<void(const TexImageHelper*)> updateImage);

public:
    GL* gl();

    BEGIN_IMPLEMENT_NEW_WITH_GC_DESC(WebGLRenderingContext,
                                     WebGLRenderingContextBaseMixIn);
    FILL_GC_POINTER(WebGLRenderingContext, m_state);
    FILL_GC_POINTER(WebGLRenderingContext, m_unpackColorSpace);
    FILL_GC_POINTER(WebGLRenderingContext, m_drawingBufferColorSpace);
    FILL_GC_COLLECTION(WebGLRenderingContext, m_enabledExtensions);
    END_IMPLEMENT_NEW_WITH_GC_DESC();

public:
    // Use setGLError only on WebGLRenderingContext and GLExtensions.
    void setGLError(GLenum code, const char* message = nullptr);
    bool hasGLError();
    void updateGLError();
    bool executeInContextScope(std::function<void()> callback);
    WebGLRenderingContextState* getState();

private:
    bool checkAttribOrUniformName(String* name);
    bool isFromCurrentContext(WebGLObject* object);
    bool isBoundCubeMapTexture(GLenum target);
    bool isFromCurrentProgram(WebGLUniformLocation* uniform);
    bool isExtensionEnabled(const char* requestedName);
    bool isDefaultFramebufferBound();
    GLuint getCurrentFBO();
    GLint getCurrentProgram();
    void completePendingJobs();
    void setPendingClearMask(uint32_t mask);

    bool m_hasPendingJobsBetweenFrames;
    uint32_t m_pendingClearMask;

    GLErrorSet m_GLErrors;
    GLTextureMap m_boundTextures;
    bool m_unpackFlipY;
    bool m_unpackPremultiplyAlpha;
    GLenum m_unpackColorspaceConversion;
    WebGLContextAttributes m_attributes;
    bool m_isContextLost;
    GL* m_gl;

    // The followings are gc managed.
    WebGLRenderingContextState* m_state;
    String* m_unpackColorSpace;
    String* m_drawingBufferColorSpace;
    GLExtensionMap m_enabledExtensions;
};
} // namespace Starfish

#endif
#endif
