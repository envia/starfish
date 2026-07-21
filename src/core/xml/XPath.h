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

#ifndef __StarfishXPath__
#define __StarfishXPath__

#include "core/util/String.h"

namespace Starfish {

class Document;
class Node;
class XPathResult;

// Evaluates an XPath 1.0 subset expression against contextNode and returns
// an XPathResult of desiredType (an XPathResult::Type value). Throws
// DOMException* with SYNTAX_ERR on unsupported or malformed expressions and
// TYPE_MISMATCH_ERR when the expression result cannot be converted to
// desiredType.
XPathResult* evaluateXPathExpression(Document* document, String* expression,
                                     Node* contextNode, uint16_t desiredType);
} // namespace Starfish

#endif
