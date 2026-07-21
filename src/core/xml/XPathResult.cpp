/*
 * Copyright (c) 2026-present Samsung Electronics Co., Ltd
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

#include "StarfishConfig.h"
#include "Starfish.h"
#include "core/xml/XPathResult.h"
#include "core/dom/DOMException.h"

namespace Starfish {

XPathResult* XPathResult::createNumber(Document* document, double value)
{
    XPathResult* result = new XPathResult(document, NUMBER_TYPE);
    result->m_numberValue = value;
    return result;
}

XPathResult* XPathResult::createString(Document* document, String* value)
{
    XPathResult* result = new XPathResult(document, STRING_TYPE);
    result->m_stringValue = value;
    return result;
}

XPathResult* XPathResult::createBoolean(Document* document, bool value)
{
    XPathResult* result = new XPathResult(document, BOOLEAN_TYPE);
    result->m_booleanValue = value;
    return result;
}

XPathResult* XPathResult::createNodeSet(Document* document, uint16_t resultType,
                                        const GCVector<Node*>& nodes)
{
    STARFISH_ASSERT(resultType >= UNORDERED_NODE_ITERATOR_TYPE &&
                    resultType <= FIRST_ORDERED_NODE_TYPE);
    XPathResult* result = new XPathResult(document, resultType);
    result->m_nodes = nodes;
    return result;
}

void XPathResult::throwTypeMismatchIfNot(uint16_t expectedKind)
{
    if (m_resultType != expectedKind) {
        throw new DOMException(
            m_executionContext, DOMException::TYPE_MISMATCH_ERR,
            "The result type of the XPathResult does not match the "
            "requested value accessor.");
    }
}

double XPathResult::numberValue()
{
    throwTypeMismatchIfNot(NUMBER_TYPE);
    return m_numberValue;
}

String* XPathResult::stringValue()
{
    throwTypeMismatchIfNot(STRING_TYPE);
    STARFISH_ASSERT(m_stringValue != nullptr);
    return m_stringValue;
}

bool XPathResult::booleanValue()
{
    throwTypeMismatchIfNot(BOOLEAN_TYPE);
    return m_booleanValue;
}

Optional<Node*> XPathResult::singleNodeValue()
{
    if (m_resultType != ANY_UNORDERED_NODE_TYPE &&
        m_resultType != FIRST_ORDERED_NODE_TYPE) {
        throw new DOMException(
            m_executionContext, DOMException::TYPE_MISMATCH_ERR,
            "The result type of the XPathResult is not a single node.");
    }
    if (m_nodes.empty()) {
        return nullptr;
    }
    return m_nodes.front();
}

uint32_t XPathResult::snapshotLength()
{
    if (m_resultType != UNORDERED_NODE_SNAPSHOT_TYPE &&
        m_resultType != ORDERED_NODE_SNAPSHOT_TYPE) {
        throw new DOMException(
            m_executionContext, DOMException::TYPE_MISMATCH_ERR,
            "The result type of the XPathResult is not a snapshot.");
    }
    return m_nodes.size();
}

Optional<Node*> XPathResult::iterateNext()
{
    if (m_resultType != UNORDERED_NODE_ITERATOR_TYPE &&
        m_resultType != ORDERED_NODE_ITERATOR_TYPE) {
        throw new DOMException(
            m_executionContext, DOMException::TYPE_MISMATCH_ERR,
            "The result type of the XPathResult is not an iterator.");
    }
    if (m_iteratorPosition >= m_nodes.size()) {
        return nullptr;
    }
    return m_nodes[m_iteratorPosition++];
}

Optional<Node*> XPathResult::snapshotItem(uint32_t index)
{
    if (m_resultType != UNORDERED_NODE_SNAPSHOT_TYPE &&
        m_resultType != ORDERED_NODE_SNAPSHOT_TYPE) {
        throw new DOMException(
            m_executionContext, DOMException::TYPE_MISMATCH_ERR,
            "The result type of the XPathResult is not a snapshot.");
    }
    if (index >= m_nodes.size()) {
        return nullptr;
    }
    return m_nodes[index];
}
} // namespace Starfish
