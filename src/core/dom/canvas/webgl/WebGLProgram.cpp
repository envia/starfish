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

#if defined(STARFISH_ENABLE_CANVAS) && defined(STARFISH_ENABLE_WEBGL)

#include "StarfishConfig.h"
#include "WebGLProgram.h"
#include "core/dom/canvas/webgl/WebGLRenderingContext.h"
#include "platform/canvas/gl/GL.h"
#include "platform/canvas/gl/IncludeGL.h"

namespace Starfish {

WebGLProgram::WebGLProgram(ScriptBindingInstance* instance,
                           WebGLRenderingContext* context, GLuint object)
    : WebGLObject(instance, context, object)
{
}

void WebGLProgram::addAttachedShader(WebGLShader* shader)
{
    if (std::find(m_webGLShaders.begin(), m_webGLShaders.end(), shader) ==
        m_webGLShaders.end()) {
        m_webGLShaders.push_back(shader);
    }
}

void WebGLProgram::removeDetachedShader(WebGLShader* shader)
{
    auto it = std::find(m_webGLShaders.begin(), m_webGLShaders.end(), shader);
    if (it != m_webGLShaders.end()) {
        m_webGLShaders.erase(it);
    }
}

void WebGLProgram::bindAttribLocation(const std::string& name, GLuint location)
{
    m_attribLocationBindings[name] = location;
}

bool WebGLProgram::hasAliasedAttribLocations() const
{
    if (m_attribLocationBindings.size() < 2) {
        return false;
    }

    // Get the GL interface from the context.
    GL* gl = context()->gl();
    GLuint programObj = glObject();

    // Get the number of active attributes.
    GLint numActiveAttribs = 0;
    gl->getProgramiv(programObj, GL_ACTIVE_ATTRIBUTES, &numActiveAttribs);

    if (numActiveAttribs < 2) {
        return false;
    }

    // Get max attribute name length.
    GLint maxNameLength = 0;
    gl->getProgramiv(programObj, GL_ACTIVE_ATTRIBUTE_MAX_LENGTH,
                     &maxNameLength);

    // Collect locations of active attributes that were bound via
    // bindAttribLocation().
    std::unordered_map<GLuint, std::string> locationToAttribName;
    std::vector<char> nameBuffer(maxNameLength);

    for (GLint i = 0; i < numActiveAttribs; i++) {
        GLint size;
        GLenum type;
        GLsizei length;

        gl->getActiveAttrib(programObj, i, maxNameLength, &length, &size, &type,
                            nameBuffer.data());

        std::string attribName(nameBuffer.data(), length);

        // Check if this attribute was bound via bindAttribLocation().
        auto it = m_attribLocationBindings.find(attribName);
        if (it != m_attribLocationBindings.end()) {
            GLuint location = it->second;

            // Check if this location is already used by another active
            // attribute.
            auto locIt = locationToAttribName.find(location);
            if (locIt != locationToAttribName.end()) {
                // Found aliasing, two active attributes bound to same location.
                return true;
            }
            locationToAttribName[location] = attribName;
        }
    }

    return false;
}

} // namespace Starfish

#endif
