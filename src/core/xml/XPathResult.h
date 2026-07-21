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

#ifndef __StarfishXPathResult__
#define __StarfishXPathResult__

#include "binding/ScriptWrappable.h"
#include "core/dom/Document.h"

namespace Starfish {

class XPathResult final : public ScriptWrappable {
public:
    enum Type : uint16_t {
        ANY_TYPE = 0,
        NUMBER_TYPE = 1,
        STRING_TYPE = 2,
        BOOLEAN_TYPE = 3,
        UNORDERED_NODE_ITERATOR_TYPE = 4,
        ORDERED_NODE_ITERATOR_TYPE = 5,
        UNORDERED_NODE_SNAPSHOT_TYPE = 6,
        ORDERED_NODE_SNAPSHOT_TYPE = 7,
        ANY_UNORDERED_NODE_TYPE = 8,
        FIRST_ORDERED_NODE_TYPE = 9,
    };

    static XPathResult* createNumber(Document* document, double value);
    static XPathResult* createString(Document* document, String* value);
    static XPathResult* createBoolean(Document* document, bool value);
    static XPathResult* createNodeSet(Document* document, uint16_t resultType,
                                      const GCVector<Node*>& nodes);

    uint32_t resultType()
    {
        return m_resultType;
    }

    double numberValue();
    String* stringValue();
    bool booleanValue();
    Optional<Node*> singleNodeValue();

    bool invalidIteratorState()
    {
        // Document mutation tracking is not implemented; iterators are never
        // invalidated.
        return false;
    }

    uint32_t snapshotLength();
    Optional<Node*> iterateNext();
    Optional<Node*> snapshotItem(uint32_t index);

    virtual ScriptBindingInstance* scriptBindingInstance() override
    {
        return m_scriptBindingInstance;
    }

    virtual void init(ScriptBindingInstance* instance,
                      void* domObjectPointer) override;
    virtual bool isXPathResult() const override;

private:
    XPathResult(Document* document, uint16_t resultType)
        : ScriptWrappable(this)
        , m_scriptBindingInstance(document->scriptBindingInstance())
        , m_executionContext(document->executionContext())
        , m_resultType(resultType)
    {
    }

    void throwTypeMismatchIfNot(uint16_t expectedKind);

    ScriptBindingInstance* m_scriptBindingInstance;
    ExecutionContext* m_executionContext;
    uint16_t m_resultType;
    double m_numberValue{ 0 };
    String* m_stringValue{ nullptr };
    bool m_booleanValue{ false };
    GCVector<Node*> m_nodes;
    size_t m_iteratorPosition{ 0 };
};
} // namespace Starfish

#endif
