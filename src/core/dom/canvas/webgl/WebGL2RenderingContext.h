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

#include "core/dom/canvas/webgl/WebGLRenderingContext.h"

typedef struct __GLsync* GLsync;

namespace Starfish {

class Uint32ArrayOrSequenceOfGLuint;

using Uint32List = Uint32ArrayOrSequenceOfGLuint;

class WebGLQuery : public WebGLObject {
public:
    WebGLQuery(ScriptBindingInstance* instance, WebGLRenderingContext* context,
               GLuint object);
    void init(ScriptBindingInstance* instance, void* domObjectPointer) override;
    bool isWebGLQuery() const override;

    bool isActive() const
    {
        return m_isActive;
    }

    void setIsActive(bool active)
    {
        m_isActive = active;
    }

private:
    bool m_isActive = false;
};

class WebGLSampler : public WebGLObject {
public:
    WebGLSampler(ScriptBindingInstance* instance,
                 WebGLRenderingContext* context, GLuint object);
    void init(ScriptBindingInstance* instance, void* domObjectPointer) override;
    bool isWebGLSampler() const override;
};

class WebGLSync : public WebGLObject {
public:
    WebGLSync(ScriptBindingInstance* instance, WebGLRenderingContext* context,
              GLsync object);
    void init(ScriptBindingInstance* instance, void* domObjectPointer) override;
    bool isWebGLSync() const override;

    GLsync glObject() const
    {
        return m_glObject;
    }

private:
    GLsync m_glObject;
};

class WebGLTransformFeedback : public WebGLObject {
public:
    WebGLTransformFeedback(ScriptBindingInstance* instance,
                           WebGLRenderingContext* context, GLuint object);
    void init(ScriptBindingInstance* instance, void* domObjectPointer) override;
    bool isWebGLTransformFeedback() const override;
};

class WebGLVertexArrayObject : public WebGLObject {
public:
    WebGLVertexArrayObject(ScriptBindingInstance* instance,
                           WebGLRenderingContext* context, GLuint object);
    void init(ScriptBindingInstance* instance, void* domObjectPointer) override;
    bool isWebGLVertexArrayObject() const override;

    bool hasEverBound()
    {
        return m_hasEverBound;
    }

    void setHasEverBound()
    {
        m_hasEverBound = true;
    }

private:
    bool m_hasEverBound = false;
};

class WebGL2RenderingContext : public WebGLRenderingContext {
public:
    WebGL2RenderingContext(HTMLCanvasElement* canvasElement);
    ~WebGL2RenderingContext() override;

    DECLARE_SCRIPT_BINDING_REQUIRED_FUNCTIONS(WebGL2RenderingContext);

    // Implement WebGLRenderingContextBase

    Optional<WebGLContextAttributes> getContextAttributes();
    bool isContextLost();

    Optional<GCVector<String*>> getSupportedExtensions();
    Optional<ScriptObject> getExtension(String* name);

    void drawingBufferStorage(GLenum sizedFormat, unsigned long width,
                              unsigned long height);

    void activeTexture(GLenum texture);
    void attachShader(WebGLProgram* program, WebGLShader* shader);
    void bindAttribLocation(WebGLProgram* program, GLuint index, String* name);
    void bindBuffer(GLenum target, Optional<WebGLBuffer*> buffer);
    void bindFramebuffer(GLenum target, Optional<WebGLFramebuffer*> buffer);
    void bindRenderbuffer(GLenum target, Optional<WebGLRenderbuffer*> buffer);
    void bindTexture(GLenum target, Optional<WebGLTexture*> texture);
    void blendColor(GLclampf red, GLclampf green, GLclampf blue,
                    GLclampf alpha);
    void blendEquation(GLenum mode);
    void blendEquationSeparate(GLenum modeRGB, GLenum modeAlpha);
    void blendFunc(GLenum sfactor, GLenum dfactor);
    void blendFuncSeparate(GLenum srcRGB, GLenum dstRGB, GLenum srcAlpha,
                           GLenum dstAlpha);

    GLenum checkFramebufferStatus(GLenum target);
    void clear(uint32_t mask);
    void clearColor(float red, float green, float blue, float alpha);
    void clearDepth(GLclampf depth);
    void clearStencil(GLint s);
    void colorMask(GLboolean red, GLboolean green, GLboolean blue,
                   GLboolean alpha);
    void compileShader(WebGLShader* shader);

    void copyTexImage2D(GLenum target, GLint level, GLenum internalformat,
                        GLint x, GLint y, GLsizei width, GLsizei height,
                        GLint border);
    void copyTexSubImage2D(GLenum target, GLint level, GLint xoffset,
                           GLint yoffset, GLint x, GLint y, GLsizei width,
                           GLsizei height);

    WebGLBuffer* createBuffer();
    WebGLFramebuffer* createFramebuffer();
    WebGLProgram* createProgram();
    WebGLRenderbuffer* createRenderbuffer();
    WebGLShader* createShader(unsigned long type);
    WebGLTexture* createTexture();

    void cullFace(GLenum mode);

    void deleteBuffer(Optional<WebGLBuffer*> buffer);
    void deleteFramebuffer(Optional<WebGLFramebuffer*> framebuffer);
    void deleteProgram(Optional<WebGLProgram*> program);
    void deleteRenderbuffer(Optional<WebGLRenderbuffer*> renderbuffer);
    void deleteShader(Optional<WebGLShader*> shader);
    void deleteTexture(Optional<WebGLTexture*> texture);

    void depthFunc(GLenum func);
    void depthMask(GLboolean flag);
    void depthRange(GLclampf zNear, GLclampf zFar);
    void detachShader(WebGLProgram* program, WebGLShader* shader);
    void disable(GLenum cap);
    void disableVertexAttribArray(GLuint index);
    void drawArrays(GLenum mode, GLint first, GLsizei count);
    void drawElements(GLenum mode, GLsizei count, GLenum type, GLintptr offset);

    void enable(GLenum cap);
    void enableVertexAttribArray(GLuint index);
    void finish();
    void flushWebGL();
    void framebufferRenderbuffer(GLenum target, GLenum attachment,
                                 GLenum renderbuffertarget,
                                 Optional<WebGLRenderbuffer*> renderbuffer);
    void framebufferTexture2D(GLenum target, GLenum attachment,
                              GLenum textarget, Optional<WebGLTexture*> texture,
                              GLint level);
    void frontFace(GLenum mode);

    void generateMipmap(GLenum target);

    WebGLActiveInfo* getActiveAttrib(WebGLProgram* program, GLuint index);
    WebGLActiveInfo* getActiveUniform(WebGLProgram* program, GLuint index);
    Optional<GCVector<WebGLShader*>> getAttachedShaders(WebGLProgram* program);

    GLint getAttribLocation(WebGLProgram* program, String* name);

    ScriptValue getBufferParameter(GLenum target, GLenum pname);
    ScriptValue getParameter(GLenum pname);

    GLenum getError();

    ScriptValue getFramebufferAttachmentParameter(GLenum target,
                                                  GLenum attachment,
                                                  GLenum pname);
    ScriptValue getProgramParameter(WebGLProgram* program, GLenum pname);
    String* getProgramInfoLog(WebGLProgram* program);
    ScriptValue getRenderbufferParameter(GLenum target, GLenum pname);
    ScriptValue getShaderParameter(WebGLShader* shader, GLenum pname);
    WebGLShaderPrecisionFormat* getShaderPrecisionFormat(GLenum shadertype,
                                                         GLenum precisiontype);
    String* getShaderInfoLog(WebGLShader* shader);

    String* getShaderSource(WebGLShader* shader);

    ScriptValue getTexParameter(GLenum target, GLenum pname);

    ScriptValue getUniform(WebGLProgram* program,
                           WebGLUniformLocation* location);

    WebGLUniformLocation* getUniformLocation(WebGLProgram* program,
                                             String* name);

    ScriptValue getVertexAttrib(GLuint index, GLenum pname);

    GLintptr getVertexAttribOffset(GLuint index, GLenum pname);

    void hint(GLenum target, GLenum mode);
    bool isBuffer(Optional<WebGLBuffer*> buffer);
    bool isEnabled(GLenum cap);
    bool isFramebuffer(Optional<WebGLFramebuffer*> framebuffer);
    bool isProgram(Optional<WebGLProgram*> program);
    bool isRenderbuffer(Optional<WebGLRenderbuffer*> renderbuffer);
    bool isShader(Optional<WebGLShader*> shader);
    bool isTexture(Optional<WebGLTexture*> texture);
    void lineWidth(GLfloat width);
    void linkProgram(WebGLProgram* program);
    void pixelStorei(GLenum pname, GLint param);
    void polygonOffset(GLfloat factor, GLfloat units);

    void renderbufferStorage(GLenum target, GLenum internalformat,
                             GLsizei width, GLsizei height);
    void sampleCoverage(GLclampf value, GLboolean invert);
    void scissor(GLint x, GLint y, GLsizei width, GLsizei height);

    void shaderSource(WebGLShader* shader, String* source);

    void stencilFunc(GLenum func, GLint ref, GLuint mask);
    void stencilFuncSeparate(GLenum face, GLenum func, GLint ref, GLuint mask);
    void stencilMask(GLuint mask);
    void stencilMaskSeparate(GLenum face, GLuint mask);
    void stencilOp(GLenum fail, GLenum zfail, GLenum zpass);
    void stencilOpSeparate(GLenum face, GLenum fail, GLenum zfail,
                           GLenum zpass);

    void texParameterf(GLenum target, GLenum pname, GLfloat param);
    void texParameteri(GLenum target, GLenum pname, GLint param);

    void uniform1f(Optional<WebGLUniformLocation*> uniform, GLfloat x);
    void uniform2f(Optional<WebGLUniformLocation*> uniform, GLfloat x,
                   GLfloat y);
    void uniform3f(Optional<WebGLUniformLocation*> uniform, GLfloat x,
                   GLfloat y, GLfloat z);
    void uniform4f(Optional<WebGLUniformLocation*> uniform, GLfloat x,
                   GLfloat y, GLfloat z, GLfloat w);

    void uniform1i(Optional<WebGLUniformLocation*> uniform, GLint x);
    void uniform2i(Optional<WebGLUniformLocation*> uniform, GLint x, GLint y);
    void uniform3i(Optional<WebGLUniformLocation*> uniform, GLint x, GLint y,
                   GLint z);
    void uniform4i(Optional<WebGLUniformLocation*> uniform, GLint x, GLint y,
                   GLint z, GLint w);

    void useProgram(Optional<WebGLProgram*> program);
    void validateProgram(WebGLProgram* program);

    void vertexAttrib1f(GLuint index, GLfloat x);
    void vertexAttrib2f(GLuint index, GLfloat x, GLfloat y);
    void vertexAttrib3f(GLuint index, GLfloat x, GLfloat y, GLfloat z);
    void vertexAttrib4f(GLuint index, GLfloat x, GLfloat y, GLfloat z,
                        GLfloat w);

    void vertexAttrib1fv(GLuint index, Float32List values);
    void vertexAttrib2fv(GLuint index, Float32List values);
    void vertexAttrib3fv(GLuint index, Float32List values);
    void vertexAttrib4fv(GLuint index, Float32List values);

    void vertexAttribPointer(GLuint index, GLint size, GLenum type,
                             GLboolean normalized, GLsizei stride,
                             GLintptr offset);

    void viewport(uint32_t x, uint32_t y, uint32_t width, uint32_t height);

    // Implement WebGL2RenderingContextBase

    /* Buffer objects */
    void copyBufferSubData(GLenum readTarget, GLenum writeTarget,
                           GLintptr readOffset, GLintptr writeOffset,
                           GLsizeiptr size);
    void getBufferSubData(GLenum target, GLintptr srcByteOffset,
                          ScriptArrayBufferView dstBuffer,
                          unsigned long long dstOffset = 0, GLuint length = 0);

    /* Framebuffer objects */
    void blitFramebuffer(GLint srcX0, GLint srcY0, GLint srcX1, GLint srcY1,
                         GLint dstX0, GLint dstY0, GLint dstX1, GLint dstY1,
                         GLbitfield mask, GLenum filter);
    void framebufferTextureLayer(GLenum target, GLenum attachment,
                                 Optional<WebGLTexture*> texture, GLint level,
                                 GLint layer);
    void invalidateFramebuffer(GLenum target,
                               GCAtomicVector<GLenum> attachments);
    void invalidateSubFramebuffer(GLenum target,
                                  GCAtomicVector<GLenum> attachments, GLint x,
                                  GLint y, GLsizei width, GLsizei height);
    void readBuffer(GLenum src);

    /* Renderbuffer objects */
    ScriptValue getInternalformatParameter(GLenum target, GLenum internalformat,
                                           GLenum pname);
    void renderbufferStorageMultisample(GLenum target, GLsizei samples,
                                        GLenum internalformat, GLsizei width,
                                        GLsizei height);

    /* Texture objects */
    void texStorage2D(GLenum target, GLsizei levels, GLenum internalformat,
                      GLsizei width, GLsizei height);
    void texStorage3D(GLenum target, GLsizei levels, GLenum internalformat,
                      GLsizei width, GLsizei height, GLsizei depth);

    void texImage3D(GLenum target, GLint level, GLint internalformat,
                    GLsizei width, GLsizei height, GLsizei depth, GLint border,
                    GLenum format, GLenum type, GLintptr pboOffset);
    void texImage3D(GLenum target, GLint level, GLint internalformat,
                    GLsizei width, GLsizei height, GLsizei depth, GLint border,
                    GLenum format, GLenum type, TexImageSource source);
    void texImage3D(GLenum target, GLint level, GLint internalformat,
                    GLsizei width, GLsizei height, GLsizei depth, GLint border,
                    GLenum format, GLenum type, ScriptArrayBufferView srcData);
    void texImage3D(GLenum target, GLint level, GLint internalformat,
                    GLsizei width, GLsizei height, GLsizei depth, GLint border,
                    GLenum format, GLenum type, ScriptArrayBufferView srcData,
                    unsigned long long srcOffset);

    void texSubImage3D(GLenum target, GLint level, GLint xoffset, GLint yoffset,
                       GLint zoffset, GLsizei width, GLsizei height,
                       GLsizei depth, GLenum format, GLenum type,
                       GLintptr pboOffset);
    void texSubImage3D(GLenum target, GLint level, GLint xoffset, GLint yoffset,
                       GLint zoffset, GLsizei width, GLsizei height,
                       GLsizei depth, GLenum format, GLenum type,
                       TexImageSource source);
    void texSubImage3D(GLenum target, GLint level, GLint xoffset, GLint yoffset,
                       GLint zoffset, GLsizei width, GLsizei height,
                       GLsizei depth, GLenum format, GLenum type,
                       ScriptArrayBufferView srcData,
                       unsigned long long srcOffset = 0);

    void copyTexSubImage3D(GLenum target, GLint level, GLint xoffset,
                           GLint yoffset, GLint zoffset, GLint x, GLint y,
                           GLsizei width, GLsizei height);

    void compressedTexImage3D(GLenum target, GLint level, GLenum internalformat,
                              GLsizei width, GLsizei height, GLsizei depth,
                              GLint border, GLsizei imageSize, GLintptr offset);
    void compressedTexImage3D(GLenum target, GLint level, GLenum internalformat,
                              GLsizei width, GLsizei height, GLsizei depth,
                              GLint border, ScriptArrayBufferView srcData,
                              unsigned long long srcOffset = 0,
                              GLuint srcLengthOverride = 0);

    void compressedTexSubImage3D(GLenum target, GLint level, GLint xoffset,
                                 GLint yoffset, GLint zoffset, GLsizei width,
                                 GLsizei height, GLsizei depth, GLenum format,
                                 GLsizei imageSize, GLintptr offset);
    void compressedTexSubImage3D(GLenum target, GLint level, GLint xoffset,
                                 GLint yoffset, GLint zoffset, GLsizei width,
                                 GLsizei height, GLsizei depth, GLenum format,
                                 ScriptArrayBufferView srcData,
                                 unsigned long long srcOffset = 0,
                                 GLuint srcLengthOverride = 0);

    /* Programs and shaders */
    GLint getFragDataLocation(WebGLProgram* program, String* name);

    /* Uniforms */
    void uniform1ui(Optional<WebGLUniformLocation*> location, GLuint v0);
    void uniform2ui(Optional<WebGLUniformLocation*> location, GLuint v0,
                    GLuint v1);
    void uniform3ui(Optional<WebGLUniformLocation*> location, GLuint v0,
                    GLuint v1, GLuint v2);
    void uniform4ui(Optional<WebGLUniformLocation*> location, GLuint v0,
                    GLuint v1, GLuint v2, GLuint v3);

    void uniform1uiv(Optional<WebGLUniformLocation*> location, Uint32List data,
                     unsigned long long srcOffset = 0, GLuint srcLength = 0);
    void uniform2uiv(Optional<WebGLUniformLocation*> location, Uint32List data,
                     unsigned long long srcOffset = 0, GLuint srcLength = 0);
    void uniform3uiv(Optional<WebGLUniformLocation*> location, Uint32List data,
                     unsigned long long srcOffset = 0, GLuint srcLength = 0);
    void uniform4uiv(Optional<WebGLUniformLocation*> location, Uint32List data,
                     unsigned long long srcOffset = 0, GLuint srcLength = 0);

    void uniformMatrix3x2fv(Optional<WebGLUniformLocation*> location,
                            GLboolean transpose, Float32List data,
                            unsigned long long srcOffset = 0,
                            GLuint srcLength = 0);
    void uniformMatrix4x2fv(Optional<WebGLUniformLocation*> location,
                            GLboolean transpose, Float32List data,
                            unsigned long long srcOffset = 0,
                            GLuint srcLength = 0);

    void uniformMatrix2x3fv(Optional<WebGLUniformLocation*> location,
                            GLboolean transpose, Float32List data,
                            unsigned long long srcOffset = 0,
                            GLuint srcLength = 0);
    void uniformMatrix4x3fv(Optional<WebGLUniformLocation*> location,
                            GLboolean transpose, Float32List data,
                            unsigned long long srcOffset = 0,
                            GLuint srcLength = 0);

    void uniformMatrix2x4fv(Optional<WebGLUniformLocation*> location,
                            GLboolean transpose, Float32List data,
                            unsigned long long srcOffset = 0,
                            GLuint srcLength = 0);
    void uniformMatrix3x4fv(Optional<WebGLUniformLocation*> location,
                            GLboolean transpose, Float32List data,
                            unsigned long long srcOffset = 0,
                            GLuint srcLength = 0);

    /* Vertex attribs */
    void vertexAttribI4i(GLuint index, GLint x, GLint y, GLint z, GLint w);
    void vertexAttribI4iv(GLuint index, Int32List values);
    void vertexAttribI4ui(GLuint index, GLuint x, GLuint y, GLuint z, GLuint w);
    void vertexAttribI4uiv(GLuint index, Uint32List values);
    void vertexAttribIPointer(GLuint index, GLint size, GLenum type,
                              GLsizei stride, GLintptr offset);

    /* Writing to the drawing buffer */
    void vertexAttribDivisor(GLuint index, GLuint divisor);
    void drawArraysInstanced(GLenum mode, GLint first, GLsizei count,
                             GLsizei instanceCount);
    void drawElementsInstanced(GLenum mode, GLsizei count, GLenum type,
                               GLintptr offset, GLsizei instanceCount);
    void drawRangeElements(GLenum mode, GLuint start, GLuint end, GLsizei count,
                           GLenum type, GLintptr offset);

    /* Multiple Render Targets */
    void drawBuffers(GCAtomicVector<GLenum> buffers);

    void clearBufferfv(GLenum buffer, GLint drawbuffer, Float32List values,
                       unsigned long long srcOffset = 0);
    void clearBufferiv(GLenum buffer, GLint drawbuffer, Int32List values,
                       unsigned long long srcOffset = 0);
    void clearBufferuiv(GLenum buffer, GLint drawbuffer, Uint32List values,
                        unsigned long long srcOffset = 0);

    void clearBufferfi(GLenum buffer, GLint drawbuffer, GLfloat depth,
                       GLint stencil);

    /* Query Objects */
    WebGLQuery* createQuery();
    void deleteQuery(Optional<WebGLQuery*> query);
    GLboolean isQuery(Optional<WebGLQuery*> query);
    void beginQuery(GLenum target, WebGLQuery* query);
    void endQuery(GLenum target);
    Optional<WebGLQuery*> getQuery(GLenum target, GLenum pname);
    ScriptValue getQueryParameter(WebGLQuery* query, GLenum pname);

    /* Sampler Objects */
    WebGLSampler* createSampler();
    void deleteSampler(Optional<WebGLSampler*> sampler);
    GLboolean isSampler(Optional<WebGLSampler*> sampler);
    void bindSampler(GLuint unit, Optional<WebGLSampler*> sampler);
    void samplerParameteri(WebGLSampler* sampler, GLenum pname, GLint param);
    void samplerParameterf(WebGLSampler* sampler, GLenum pname, GLfloat param);
    ScriptValue getSamplerParameter(WebGLSampler* sampler, GLenum pname);

    /* Sync objects */
    Optional<WebGLSync*> fenceSync(GLenum condition, GLbitfield flags);
    GLboolean isSync(Optional<WebGLSync*> sync);
    void deleteSync(Optional<WebGLSync*> sync);
    GLenum clientWaitSync(WebGLSync* sync, GLbitfield flags, GLuint64 timeout);
    void waitSync(WebGLSync* sync, GLbitfield flags, GLint64 timeout);
    ScriptValue getSyncParameter(WebGLSync* sync, GLenum pname);

    /* Transform Feedback */
    WebGLTransformFeedback* createTransformFeedback();
    void deleteTransformFeedback(Optional<WebGLTransformFeedback*> tf);
    GLboolean isTransformFeedback(Optional<WebGLTransformFeedback*> tf);
    void bindTransformFeedback(GLenum target,
                               Optional<WebGLTransformFeedback*> tf);
    void beginTransformFeedback(GLenum primitiveMode);
    void endTransformFeedback();
    void transformFeedbackVaryings(WebGLProgram* program,
                                   GCVector<String*> varyings,
                                   GLenum bufferMode);
    Optional<WebGLActiveInfo*> getTransformFeedbackVarying(
        WebGLProgram* program, GLuint index);
    void pauseTransformFeedback();
    void resumeTransformFeedback();

    /* Uniform Buffer Objects and Transform Feedback Buffers */
    void bindBufferBase(GLenum target, GLuint index,
                        Optional<WebGLBuffer*> buffer);
    void bindBufferRange(GLenum target, GLuint index,
                         Optional<WebGLBuffer*> buffer, GLintptr offset,
                         GLsizeiptr size);
    ScriptValue getIndexedParameter(GLenum target, GLuint index);
    Optional<GCAtomicVector<GLuint>> getUniformIndices(
        WebGLProgram* program, GCVector<String*> uniformNames);
    ScriptValue getActiveUniforms(WebGLProgram* program,
                                  GCAtomicVector<GLuint> uniformIndices,
                                  GLenum pname);
    GLuint getUniformBlockIndex(WebGLProgram* program,
                                String* uniformBlockName);
    ScriptValue getActiveUniformBlockParameter(WebGLProgram* program,
                                               GLuint uniformBlockIndex,
                                               GLenum pname);
    Optional<String*> getActiveUniformBlockName(WebGLProgram* program,
                                                GLuint uniformBlockIndex);
    void uniformBlockBinding(WebGLProgram* program, GLuint uniformBlockIndex,
                             GLuint uniformBlockBinding);

    /* Vertex Array Objects */
    WebGLVertexArrayObject* createVertexArray();
    void deleteVertexArray(Optional<WebGLVertexArrayObject*> vertexArray);
    GLboolean isVertexArray(Optional<WebGLVertexArrayObject*> vertexArray);
    void bindVertexArray(Optional<WebGLVertexArrayObject*> array);

    // Implement WebGL2RenderingContextOverloads

    // WebGL1:
    void bufferData(GLenum target, GLsizeiptr size, GLenum usage);
    void bufferData(GLenum target, Optional<AllowSharedBufferSource> srcData,
                    GLenum usage);
    void bufferSubData(GLenum target, GLintptr dstByteOffset,
                       AllowSharedBufferSource srcData);

    // WebGL2:
    void bufferData(GLenum target, ScriptArrayBufferView srcData, GLenum usage,
                    unsigned long long srcOffset, GLuint length = 0);
    void bufferSubData(GLenum target, GLintptr dstByteOffset,
                       ScriptArrayBufferView srcData,
                       unsigned long long srcOffset, GLuint length = 0);

    // WebGL1 legacy entrypoints:
    void texImage2D(GLenum target, GLint level, GLint internalformat,
                    GLsizei width, GLsizei height, GLint border, GLenum format,
                    GLenum type, Optional<ScriptArrayBufferView> pixels);
    void texImage2D(GLenum target, GLint level, GLint internalformat,
                    GLenum format, GLenum type, TexImageSource source);

    void texSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset,
                       GLsizei width, GLsizei height, GLenum format,
                       GLenum type, Optional<ScriptArrayBufferView> pixels);
    void texSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset,
                       GLenum format, GLenum type, TexImageSource source);

    // WebGL2 entrypoints:
    void texImage2D(GLenum target, GLint level, GLint internalformat,
                    GLsizei width, GLsizei height, GLint border, GLenum format,
                    GLenum type, GLintptr pboOffset);
    void texImage2D(GLenum target, GLint level, GLint internalformat,
                    GLsizei width, GLsizei height, GLint border, GLenum format,
                    GLenum type, TexImageSource source);
    void texImage2D(GLenum target, GLint level, GLint internalformat,
                    GLsizei width, GLsizei height, GLint border, GLenum format,
                    GLenum type, ScriptArrayBufferView srcData,
                    unsigned long long srcOffset);

    void texSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset,
                       GLsizei width, GLsizei height, GLenum format,
                       GLenum type, GLintptr pboOffset);
    void texSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset,
                       GLsizei width, GLsizei height, GLenum format,
                       GLenum type, TexImageSource source);
    void texSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset,
                       GLsizei width, GLsizei height, GLenum format,
                       GLenum type, ScriptArrayBufferView srcData,
                       unsigned long long srcOffset);

    void compressedTexImage2D(GLenum target, GLint level, GLenum internalformat,
                              GLsizei width, GLsizei height, GLint border,
                              GLsizei imageSize, GLintptr offset);
    void compressedTexImage2D(GLenum target, GLint level, GLenum internalformat,
                              GLsizei width, GLsizei height, GLint border,
                              ScriptArrayBufferView srcData,
                              unsigned long long srcOffset = 0,
                              GLuint srcLengthOverride = 0);

    void compressedTexSubImage2D(GLenum target, GLint level, GLint xoffset,
                                 GLint yoffset, GLsizei width, GLsizei height,
                                 GLenum format, GLsizei imageSize,
                                 GLintptr offset);
    void compressedTexSubImage2D(GLenum target, GLint level, GLint xoffset,
                                 GLint yoffset, GLsizei width, GLsizei height,
                                 GLenum format, ScriptArrayBufferView srcData,
                                 unsigned long long srcOffset = 0,
                                 GLuint srcLengthOverride = 0);

    void uniform1fv(Optional<WebGLUniformLocation*> location, Float32List data,
                    unsigned long long srcOffset = 0, GLuint srcLength = 0);
    void uniform2fv(Optional<WebGLUniformLocation*> location, Float32List data,
                    unsigned long long srcOffset = 0, GLuint srcLength = 0);
    void uniform3fv(Optional<WebGLUniformLocation*> location, Float32List data,
                    unsigned long long srcOffset = 0, GLuint srcLength = 0);
    void uniform4fv(Optional<WebGLUniformLocation*> location, Float32List data,
                    unsigned long long srcOffset = 0, GLuint srcLength = 0);

    void uniform1iv(Optional<WebGLUniformLocation*> location, Int32List data,
                    unsigned long long srcOffset = 0, GLuint srcLength = 0);
    void uniform2iv(Optional<WebGLUniformLocation*> location, Int32List data,
                    unsigned long long srcOffset = 0, GLuint srcLength = 0);
    void uniform3iv(Optional<WebGLUniformLocation*> location, Int32List data,
                    unsigned long long srcOffset = 0, GLuint srcLength = 0);
    void uniform4iv(Optional<WebGLUniformLocation*> location, Int32List data,
                    unsigned long long srcOffset = 0, GLuint srcLength = 0);

    void uniformMatrix2fv(Optional<WebGLUniformLocation*> location,
                          GLboolean transpose, Float32List data,
                          unsigned long long srcOffset = 0,
                          GLuint srcLength = 0);
    void uniformMatrix3fv(Optional<WebGLUniformLocation*> location,
                          GLboolean transpose, Float32List data,
                          unsigned long long srcOffset = 0,
                          GLuint srcLength = 0);
    void uniformMatrix4fv(Optional<WebGLUniformLocation*> location,
                          GLboolean transpose, Float32List data,
                          unsigned long long srcOffset = 0,
                          GLuint srcLength = 0);

    /* Reading back pixels */
    // WebGL1:
    void readPixels(GLint x, GLint y, GLsizei width, GLsizei height,
                    GLenum format, GLenum type,
                    Optional<ScriptArrayBufferView> dstData);
    // WebGL2:
    void readPixels(GLint x, GLint y, GLsizei width, GLsizei height,
                    GLenum format, GLenum type, GLintptr offset);
    void readPixels(GLint x, GLint y, GLsizei width, GLsizei height,
                    GLenum format, GLenum type, ScriptArrayBufferView dstData,
                    unsigned long long dstOffset);

private:
    std::unordered_map<GLuint, WebGLQuery*> m_queries;
};

} // namespace Starfish

#endif // defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)

#endif // __StarfishWebGL2RenderingContext__
