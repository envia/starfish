/*
 * Copyright (c) 2023-present Samsung Electronics Co., Ltd
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

#ifndef __StarfishWebGLProgram__
#define __StarfishWebGLProgram__

#if defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)

#include "core/dom/canvas/webgl/WebGLObject.h"
#include <unordered_map>

namespace Starfish {

class WebGLShader;

class WebGLProgram : public WebGLObject {
public:
    WebGLProgram(ScriptBindingInstance* instance,
                 WebGLRenderingContext* context, GLuint object);
    void init(ScriptBindingInstance* instance, void* domObjectPointer) override;
    bool isWebGLProgram() const override;
    void addAttachedShader(WebGLShader* shader);
    void removeDetachedShader(WebGLShader* shader);

    const GCVector<WebGLShader*>& getWebGLShaders() const
    {
        return m_webGLShaders;
    }

    void bindAttribLocation(const std::string& name, GLuint location);
    const std::unordered_map<std::string, GLuint>& getAttribLocationBindings() const
    {
        return m_attribLocationBindings;
    }

    void setWebGLLinkFailed(bool failed) { m_webglLinkFailed = failed; }
    bool webglLinkFailed() const { return m_webglLinkFailed; }

private:
    GCVector<WebGLShader*> m_webGLShaders;
    std::unordered_map<std::string, GLuint> m_attribLocationBindings;
    bool m_webglLinkFailed = false;
};
} // namespace Starfish

#endif
#endif
