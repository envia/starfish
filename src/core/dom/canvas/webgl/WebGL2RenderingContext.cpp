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
#include "core/dom/canvas/webgl/WebGL2RenderingContext.h"
#include "core/dom/ExecutionContext.h"
#include "binding/generated/ArrayBufferOrSharedArrayBufferOrArrayBufferViewUnion.h"
#include "binding/generated/ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElementUnion.h"

#include "platform/canvas/gl/IncludeGL.h"
#include "platform/canvas/gl/GL.h"

#include <EscargotPublic.h>

namespace Starfish {

WebGL2RenderingContext::WebGL2RenderingContext(HTMLCanvasElement* canvasElement)
    : WebGLRenderingContext(canvasElement)
{
    // INDIGO_TODO
}

WebGL2RenderingContext::~WebGL2RenderingContext()
{
}

ScriptBindingInstance* WebGL2RenderingContext::scriptBindingInstance()
{
    return executionContext()->scriptBindingInstance();
}

ScriptValue WebGL2RenderingContext::getParameter(GLenum pname)
{
    // INDIGO_TODO
    //ENTER_CONTEXT_SCOPE(scriptNull());

    switch (pname) {
    // INDIGO_TODO
    case GL_READ_BUFFER:
    case GL_UNPACK_ROW_LENGTH:
    case GL_UNPACK_SKIP_ROWS:
    case GL_UNPACK_SKIP_PIXELS:
    case GL_PACK_ROW_LENGTH:
    case GL_PACK_SKIP_ROWS:
    case GL_PACK_SKIP_PIXELS:
    case GL_COLOR:
    case GL_DEPTH:
    case GL_STENCIL:
    case GL_RED:
    case GL_RGB8:
    case GL_RGB10_A2:
    case GL_TEXTURE_BINDING_3D:
    case GL_UNPACK_SKIP_IMAGES:
    case GL_UNPACK_IMAGE_HEIGHT:
    case GL_TEXTURE_3D:
    case GL_TEXTURE_WRAP_R:
        STARFISH_UNSUPPORTED("pname: 0x%04X(%s)", pname, __PRETTY_FUNCTION__);
        return scriptNull();
    case GL_MAX_3D_TEXTURE_SIZE: {
        std::vector<int> values(1);
        m_gl->getIntegerv(pname, &values[0]);
        STARFISH_LOG_WARN("INDIGO_TEMP: MAX_3D_TEXTURE_SIZE=%d", values[0]);
        return Escargot::ValueRef::create(values[0]);
    }
    case GL_UNSIGNED_INT_2_10_10_10_REV:
    case GL_MAX_ELEMENTS_VERTICES:
    case GL_MAX_ELEMENTS_INDICES:
    case GL_TEXTURE_MIN_LOD:
    case GL_TEXTURE_MAX_LOD:
    case GL_TEXTURE_BASE_LEVEL:
    case GL_TEXTURE_MAX_LEVEL:
    case GL_MIN:
    case GL_MAX:
    case GL_DEPTH_COMPONENT24:
    case GL_MAX_TEXTURE_LOD_BIAS:
    case GL_TEXTURE_COMPARE_MODE:
    case GL_TEXTURE_COMPARE_FUNC:
    case GL_CURRENT_QUERY:
    case GL_QUERY_RESULT:
    case GL_QUERY_RESULT_AVAILABLE:
    case GL_STREAM_READ:
    case GL_STREAM_COPY:
    case GL_STATIC_READ:
    case GL_STATIC_COPY:
    case GL_DYNAMIC_READ:
    case GL_DYNAMIC_COPY:
        STARFISH_UNSUPPORTED("pname: 0x%04X(%s)", pname, __PRETTY_FUNCTION__);
        return scriptNull();
    case GL_MAX_DRAW_BUFFERS: {
        std::vector<int> values(1);
        m_gl->getIntegerv(pname, &values[0]);
        STARFISH_LOG_WARN("INDIGO_TEMP: MAX_DRAW_BUFFERS=%d", values[0]);
        return Escargot::ValueRef::create(values[0]);
    }
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
    case GL_MAX_FRAGMENT_UNIFORM_COMPONENTS:
    case GL_MAX_VERTEX_UNIFORM_COMPONENTS:
    case GL_SAMPLER_3D:
    case GL_SAMPLER_2D_SHADOW:
    case GL_FRAGMENT_SHADER_DERIVATIVE_HINT:
    case GL_PIXEL_PACK_BUFFER:
    case GL_PIXEL_UNPACK_BUFFER:
    case GL_PIXEL_PACK_BUFFER_BINDING:
    case GL_PIXEL_UNPACK_BUFFER_BINDING:
    case GL_FLOAT_MAT2x3:
    case GL_FLOAT_MAT2x4:
    case GL_FLOAT_MAT3x2:
    case GL_FLOAT_MAT3x4:
    case GL_FLOAT_MAT4x2:
    case GL_FLOAT_MAT4x3:
    case GL_SRGB:
    case GL_SRGB8:
    case GL_SRGB8_ALPHA8:
    case GL_COMPARE_REF_TO_TEXTURE:
    case GL_RGBA32F:
    case GL_RGB32F:
    case GL_RGBA16F:
    case GL_RGB16F:
    case GL_VERTEX_ATTRIB_ARRAY_INTEGER:
    case GL_MAX_ARRAY_TEXTURE_LAYERS:
    case GL_MIN_PROGRAM_TEXEL_OFFSET:
    case GL_MAX_PROGRAM_TEXEL_OFFSET:
    case GL_MAX_VARYING_COMPONENTS:
    case GL_TEXTURE_2D_ARRAY:
    case GL_TEXTURE_BINDING_2D_ARRAY:
    case GL_R11F_G11F_B10F:
    case GL_UNSIGNED_INT_10F_11F_11F_REV:
    case GL_RGB9_E5:
    case GL_UNSIGNED_INT_5_9_9_9_REV:
    case GL_TRANSFORM_FEEDBACK_BUFFER_MODE:
    case GL_MAX_TRANSFORM_FEEDBACK_SEPARATE_COMPONENTS:
    case GL_TRANSFORM_FEEDBACK_VARYINGS:
    case GL_TRANSFORM_FEEDBACK_BUFFER_START:
    case GL_TRANSFORM_FEEDBACK_BUFFER_SIZE:
    case GL_TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN:
    case GL_RASTERIZER_DISCARD:
    case GL_MAX_TRANSFORM_FEEDBACK_INTERLEAVED_COMPONENTS:
    case GL_MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS:
    case GL_INTERLEAVED_ATTRIBS:
    case GL_SEPARATE_ATTRIBS:
    case GL_TRANSFORM_FEEDBACK_BUFFER:
    case GL_TRANSFORM_FEEDBACK_BUFFER_BINDING:
    case GL_RGBA32UI:
    case GL_RGB32UI:
    case GL_RGBA16UI:
    case GL_RGB16UI:
    case GL_RGBA8UI:
    case GL_RGB8UI:
    case GL_RGBA32I:
    case GL_RGB32I:
    case GL_RGBA16I:
    case GL_RGB16I:
    case GL_RGBA8I:
    case GL_RGB8I:
    case GL_RED_INTEGER:
    case GL_RGB_INTEGER:
    case GL_RGBA_INTEGER:
    case GL_SAMPLER_2D_ARRAY:
    case GL_SAMPLER_2D_ARRAY_SHADOW:
    case GL_SAMPLER_CUBE_SHADOW:
    case GL_UNSIGNED_INT_VEC2:
    case GL_UNSIGNED_INT_VEC3:
    case GL_UNSIGNED_INT_VEC4:
    case GL_INT_SAMPLER_2D:
    case GL_INT_SAMPLER_3D:
    case GL_INT_SAMPLER_CUBE:
    case GL_INT_SAMPLER_2D_ARRAY:
    case GL_UNSIGNED_INT_SAMPLER_2D:
    case GL_UNSIGNED_INT_SAMPLER_3D:
    case GL_UNSIGNED_INT_SAMPLER_CUBE:
    case GL_UNSIGNED_INT_SAMPLER_2D_ARRAY:
    case GL_DEPTH_COMPONENT32F:
    case GL_DEPTH32F_STENCIL8:
    case GL_FLOAT_32_UNSIGNED_INT_24_8_REV:
    case GL_FRAMEBUFFER_ATTACHMENT_COLOR_ENCODING:
    case GL_FRAMEBUFFER_ATTACHMENT_COMPONENT_TYPE:
    case GL_FRAMEBUFFER_ATTACHMENT_RED_SIZE:
    case GL_FRAMEBUFFER_ATTACHMENT_GREEN_SIZE:
    case GL_FRAMEBUFFER_ATTACHMENT_BLUE_SIZE:
    case GL_FRAMEBUFFER_ATTACHMENT_ALPHA_SIZE:
    case GL_FRAMEBUFFER_ATTACHMENT_DEPTH_SIZE:
    case GL_FRAMEBUFFER_ATTACHMENT_STENCIL_SIZE:
    case GL_FRAMEBUFFER_DEFAULT:
    case GL_UNSIGNED_INT_24_8:
    case GL_DEPTH24_STENCIL8:
    case GL_UNSIGNED_NORMALIZED:
    //case GL_DRAW_FRAMEBUFFER_BINDING: /* Same as GL_FRAMEBUFFER_BINDING */
    case GL_READ_FRAMEBUFFER:
    case GL_DRAW_FRAMEBUFFER:
    case GL_READ_FRAMEBUFFER_BINDING:
    case GL_RENDERBUFFER_SAMPLES:
    case GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_LAYER:
        STARFISH_UNSUPPORTED("pname: 0x%04X(%s)", pname, __PRETTY_FUNCTION__);
        return scriptNull();
    case GL_MAX_COLOR_ATTACHMENTS: {
        std::vector<int> values(1);
        m_gl->getIntegerv(pname, &values[0]);
        STARFISH_LOG_WARN("INDIGO_TEMP: MAX_COLOR_ATTACHMENTS=%d", values[0]);
        return Escargot::ValueRef::create(values[0]);
    }
    case GL_COLOR_ATTACHMENT1:
    case GL_COLOR_ATTACHMENT2:
    case GL_COLOR_ATTACHMENT3:
    case GL_COLOR_ATTACHMENT4:
    case GL_COLOR_ATTACHMENT5:
    case GL_COLOR_ATTACHMENT6:
    case GL_COLOR_ATTACHMENT7:
    case GL_COLOR_ATTACHMENT8:
    case GL_COLOR_ATTACHMENT9:
    case GL_COLOR_ATTACHMENT10:
    case GL_COLOR_ATTACHMENT11:
    case GL_COLOR_ATTACHMENT12:
    case GL_COLOR_ATTACHMENT13:
    case GL_COLOR_ATTACHMENT14:
    case GL_COLOR_ATTACHMENT15:
    case GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE:
    //case GL_MAX_SAMPLES: /* INDIGO_TODO: GL_MAX_SAMPLES (1) */
    case GL_HALF_FLOAT:
    case GL_RG:
    case GL_RG_INTEGER:
    case GL_R8:
    case GL_RG8:
    case GL_R16F:
    case GL_R32F:
    case GL_RG16F:
    case GL_RG32F:
    case GL_R8I:
    case GL_R8UI:
    case GL_R16I:
    case GL_R16UI:
    case GL_R32I:
    case GL_R32UI:
    case GL_RG8I:
    case GL_RG8UI:
    case GL_RG16I:
    case GL_RG16UI:
    case GL_RG32I:
    case GL_RG32UI:
    //case GL_VERTEX_ARRAY_BINDING: /* INDIGO_TODO: GL_VERTEX_ARRAY_BINDING (1) */
    case GL_R8_SNORM:
    case GL_RG8_SNORM:
    case GL_RGB8_SNORM:
    case GL_RGBA8_SNORM:
    case GL_SIGNED_NORMALIZED:
    //case GL_COPY_READ_BUFFER: /* Same as GL_COPY_READ_BUFFER_BINDING */
    //case GL_COPY_WRITE_BUFFER: /* Same as GL_COPY_WRITE_BUFFER_BINDING */
    case GL_COPY_READ_BUFFER_BINDING: /* Same as GL_COPY_READ_BUFFER */
    case GL_COPY_WRITE_BUFFER_BINDING: /* Same as GL_COPY_WRITE_BUFFER */
    case GL_UNIFORM_BUFFER:
    case GL_UNIFORM_BUFFER_BINDING:
    case GL_UNIFORM_BUFFER_START:
    case GL_UNIFORM_BUFFER_SIZE:
        STARFISH_UNSUPPORTED("pname: 0x%04X(%s)", pname, __PRETTY_FUNCTION__);
        return scriptNull();
    case GL_MAX_VERTEX_UNIFORM_BLOCKS: {
        std::vector<int> values(1);
        m_gl->getIntegerv(pname, &values[0]);
        STARFISH_LOG_WARN("INDIGO_TEMP: MAX_VERTEX_UNIFORM_BLOCKS=%d", values[0]);
        return Escargot::ValueRef::create(values[0]);
    }
    case GL_MAX_FRAGMENT_UNIFORM_BLOCKS:
        STARFISH_UNSUPPORTED("pname: 0x%04X(%s)", pname, __PRETTY_FUNCTION__);
        return scriptNull();
    case GL_MAX_COMBINED_UNIFORM_BLOCKS: {
        std::vector<int> values(1);
        m_gl->getIntegerv(pname, &values[0]);
        STARFISH_LOG_WARN("INDIGO_TEMP: MAX_COMBINED_UNIFORM_BLOCKS=%d", values[0]);
        return Escargot::ValueRef::create(values[0]);
    }
    case GL_MAX_UNIFORM_BUFFER_BINDINGS: {
        std::vector<int> values(1);
        m_gl->getIntegerv(pname, &values[0]);
        STARFISH_LOG_WARN("INDIGO_TEMP: MAX_UNIFORM_BUFFER_BINDINGS=%d", values[0]);
        return Escargot::ValueRef::create(values[0]);
    }
    case GL_MAX_UNIFORM_BLOCK_SIZE:
    case GL_MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS:
    case GL_MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS:
    case GL_UNIFORM_BUFFER_OFFSET_ALIGNMENT:
    case GL_ACTIVE_UNIFORM_BLOCKS:
    case GL_UNIFORM_TYPE:
    case GL_UNIFORM_SIZE:
    case GL_UNIFORM_BLOCK_INDEX:
    case GL_UNIFORM_OFFSET:
    case GL_UNIFORM_ARRAY_STRIDE:
    case GL_UNIFORM_MATRIX_STRIDE:
    case GL_UNIFORM_IS_ROW_MAJOR:
    case GL_UNIFORM_BLOCK_BINDING:
    case GL_UNIFORM_BLOCK_DATA_SIZE:
    case GL_UNIFORM_BLOCK_ACTIVE_UNIFORMS:
    case GL_UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES:
    case GL_UNIFORM_BLOCK_REFERENCED_BY_VERTEX_SHADER:
    case GL_UNIFORM_BLOCK_REFERENCED_BY_FRAGMENT_SHADER:
    case GL_INVALID_INDEX:
    case GL_MAX_VERTEX_OUTPUT_COMPONENTS:
        STARFISH_UNSUPPORTED("pname: 0x%04X(%s)", pname, __PRETTY_FUNCTION__);
        return scriptNull();
    case GL_MAX_FRAGMENT_INPUT_COMPONENTS: {
        std::vector<int> values(1);
        m_gl->getIntegerv(pname, &values[0]);
        STARFISH_LOG_WARN("INDIGO_TEMP: MAX_FRAGMENT_INPUT_COMPONENTS=%d", values[0]);
        return Escargot::ValueRef::create(values[0]);
    }
    case GL_MAX_SERVER_WAIT_TIMEOUT:
    case GL_OBJECT_TYPE:
    case GL_SYNC_CONDITION:
    case GL_SYNC_STATUS:
    case GL_SYNC_FLAGS:
    case GL_SYNC_FENCE:
    case GL_SYNC_GPU_COMMANDS_COMPLETE:
    case GL_UNSIGNALED:
    case GL_SIGNALED:
    case GL_ALREADY_SIGNALED:
    case GL_TIMEOUT_EXPIRED:
    case GL_CONDITION_SATISFIED:
    case GL_WAIT_FAILED:
    case GL_SYNC_FLUSH_COMMANDS_BIT:
    case GL_VERTEX_ATTRIB_ARRAY_DIVISOR:
    case GL_ANY_SAMPLES_PASSED:
    case GL_ANY_SAMPLES_PASSED_CONSERVATIVE:
    case GL_SAMPLER_BINDING:
    case GL_RGB10_A2UI:
    case GL_INT_2_10_10_10_REV:
    case GL_TRANSFORM_FEEDBACK:
    case GL_TRANSFORM_FEEDBACK_PAUSED:
    case GL_TRANSFORM_FEEDBACK_ACTIVE:
    case GL_TRANSFORM_FEEDBACK_BINDING:
    case GL_TEXTURE_IMMUTABLE_FORMAT:
    case GL_MAX_ELEMENT_INDEX:
    case GL_TEXTURE_IMMUTABLE_LEVELS:
        STARFISH_UNSUPPORTED("pname: 0x%04X(%s)", pname, __PRETTY_FUNCTION__);
        return scriptNull();
    }
    return WebGLRenderingContext::getParameter(pname);
}

// WebGLRenderingContextOverloads

void WebGL2RenderingContext::bufferData(GLenum target, GLsizeiptr size,
                                       GLenum usage)
{
    // INDIGO_TODO
    //ENTER_CONTEXT_SCOPE();

    WebGLRenderingContext::bufferData(target, size, usage);
}

void WebGL2RenderingContext::bufferData(GLenum target,
                                       Optional<AllowSharedBufferSource> data,
                                       GLenum usage)
{
    // INDIGO_TODO
    //ENTER_CONTEXT_SCOPE();

    WebGLRenderingContext::bufferData(target, data, usage);
}

void WebGL2RenderingContext::bufferData(GLenum target, ScriptArrayBufferView srcData, GLenum usage, unsigned long long srcOffset, GLuint length)
{
    // INDIGO_TODO
    //ENTER_CONTEXT_SCOPE();

    // INDIGO_TODO
    STARFISH_UNIMPLEMENTED("INDIGO_WebGL2RenderingContext::bufferData");
}

void WebGL2RenderingContext::texImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&, uint64_t&)
{
    // INDIGO_TODO
    //ENTER_CONTEXT_SCOPE();

    // INDIGO_TODO
    STARFISH_UNIMPLEMENTED("INDIGO_WebGL2RenderingContext::texImage2D");
}

void WebGL2RenderingContext::texImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, ImageBitmapOrImageDataOrHTMLImageElementOrHTMLCanvasElementOrHTMLVideoElement&)
{
    // INDIGO_TODO
    //ENTER_CONTEXT_SCOPE();

    // INDIGO_TODO
    STARFISH_UNIMPLEMENTED("INDIGO_WebGL2RenderingContext::texImage2D");
}

void WebGL2RenderingContext::texImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, int64_t&)
{
    // INDIGO_TODO
    //ENTER_CONTEXT_SCOPE();

    // INDIGO_TODO
    STARFISH_UNIMPLEMENTED("INDIGO_WebGL2RenderingContext::texImage2D");
}

void WebGL2RenderingContext::texImage2D(uint32_t&, int32_t&, int32_t&, int32_t&, int32_t&, int32_t&, uint32_t&, uint32_t&, Escargot::ArrayBufferViewRef*&)
{
    // INDIGO_TODO
    //ENTER_CONTEXT_SCOPE();

    // INDIGO_TODO
    STARFISH_UNIMPLEMENTED("INDIGO_WebGL2RenderingContext::texImage2D");
}

void WebGL2RenderingContext::texImage2D(GLenum target, GLint level,
                                        GLint internalFormat, GLenum format,
                                        GLenum type, TexImageSource source)
{
    // INDIGO_TODO
    //ENTER_CONTEXT_SCOPE();

    WebGLRenderingContext::texImage2D(target, level, internalFormat, format,
                                      type, source);
}

} // namespace Starfish

#endif // defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)
