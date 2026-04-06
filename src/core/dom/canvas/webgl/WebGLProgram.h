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

    const std::unordered_map<std::string, GLuint>& attribLocationBindings()
        const
    {
        return m_attribLocationBindings;
    }

    bool hasAliasedAttribLocations() const;

    void setLinkFailed(bool linkFailed)
    {
        m_linkFailed = linkFailed;
    }

    bool linkFailed() const
    {
        return m_linkFailed;
    }

private:
    GCVector<WebGLShader*> m_webGLShaders;
    // Map from attribute name to location index set by bindAttribLocation
    std::unordered_map<std::string, GLuint> m_attribLocationBindings;
    // Flag to indicate link status was invalidated due to WebGL constraints
    bool m_linkFailed = false;
};
} // namespace Starfish

#endif
#endif
