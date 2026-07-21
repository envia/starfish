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

// XPath 1.0 subset parser and evaluator. Namespaces and variable references
// are not supported; unsupported syntax raises SYNTAX_ERR.

#include "StarfishConfig.h"
#include "Starfish.h"
#include "core/xml/XPath.h"
#include "core/xml/XPathResult.h"
#include "core/dom/Document.h"
#include "core/dom/Element.h"
#include "core/dom/Attr.h"
#include "core/dom/CharacterData.h"
#include "core/dom/DOMException.h"

#include <cmath>
#include <map>

namespace Starfish {
namespace XPathImpl {

    static bool isAsciiDigit(char c)
    {
        return c >= '0' && c <= '9';
    }

    static bool isAsciiAlpha(char c)
    {
        return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
    }

    static bool isAsciiSpace(char c)
    {
        return c == ' ' || c == '\t' || c == '\n' || c == '\r';
    }

    static void throwSyntaxError(Document* document, const char* message)
    {
        throw new DOMException(document->executionContext(),
                               DOMException::SYNTAX_ERR, message);
    }

    // ---------------------------------------------------------------- values

    struct Value : public gc {
        enum Kind { NodeSetKind, BooleanKind, NumberKind, StringKind };
        Kind kind{ BooleanKind };
        GCVector<Node*> nodes;
        bool boolean{ false };
        double number{ 0 };
        String* string{ nullptr };

        static Value* makeBoolean(bool b)
        {
            Value* v = new Value();
            v->kind = BooleanKind;
            v->boolean = b;
            return v;
        }
        static Value* makeNumber(double d)
        {
            Value* v = new Value();
            v->kind = NumberKind;
            v->number = d;
            return v;
        }
        static Value* makeString(String* s)
        {
            Value* v = new Value();
            v->kind = StringKind;
            v->string = s;
            return v;
        }
        static Value* makeNodeSet()
        {
            Value* v = new Value();
            v->kind = NodeSetKind;
            return v;
        }
    };

    static String* stringValueOfNode(Node* node)
    {
        if (node->nodeType() == Node::DOCUMENT_NODE) {
            Element* rootElement = node->asDocument()->documentElement();
            if (!rootElement) {
                return String::emptyString;
            }
            node = rootElement;
        }
        if (node->isAttr()) {
            return node->asAttr()->value();
        }
        auto text = node->textContent();
        if (text.hasValue()) {
            return text.getValue();
        }
        return String::emptyString;
    }

    static double stringToNumber(String* string)
    {
        auto utf8 = string->trim()->toUTF8NonGCString();
        if (utf8.length() == 0) {
            return std::numeric_limits<double>::quiet_NaN();
        }
        char* end = nullptr;
        double result = strtod(utf8.data(), &end);
        if (end != utf8.data() + utf8.length()) {
            return std::numeric_limits<double>::quiet_NaN();
        }
        return result;
    }

    static String* numberToString(double number)
    {
        if (std::isnan(number)) {
            return String::createASCIIString("NaN");
        }
        if (std::isinf(number)) {
            if (number > 0) {
                return String::createASCIIString("Infinity");
            }
            return String::createASCIIString("-Infinity");
        }
        if (number == std::trunc(number) && std::abs(number) < 1e17) {
            char buffer[32];
            snprintf(buffer, sizeof(buffer), "%lld",
                     static_cast<long long>(number));
            return String::fromUTF8(buffer, strlen(buffer));
        }
        char buffer[40];
        snprintf(buffer, sizeof(buffer), "%.17g", number);
        return String::fromUTF8(buffer, strlen(buffer));
    }

    static String* valueToString(Value* value)
    {
        switch (value->kind) {
        case Value::NodeSetKind:
            if (value->nodes.empty()) {
                return String::emptyString;
            }
            return stringValueOfNode(value->nodes.front());
        case Value::BooleanKind:
            if (value->boolean) {
                return String::createASCIIString("true");
            }
            return String::createASCIIString("false");
        case Value::NumberKind:
            return numberToString(value->number);
        case Value::StringKind:
            return value->string;
        }
        STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE();
    }

    static double valueToNumber(Value* value)
    {
        switch (value->kind) {
        case Value::NodeSetKind:
        case Value::StringKind:
            return stringToNumber(valueToString(value));
        case Value::BooleanKind:
            return value->boolean ? 1 : 0;
        case Value::NumberKind:
            return value->number;
        }
        STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE();
    }

    static bool valueToBoolean(Value* value)
    {
        switch (value->kind) {
        case Value::NodeSetKind:
            return !value->nodes.empty();
        case Value::BooleanKind:
            return value->boolean;
        case Value::NumberKind:
            return value->number != 0 && !std::isnan(value->number);
        case Value::StringKind:
            return value->string->length() != 0;
        }
        STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE();
    }

    // ---------------------------------------------------------------- tokens

    enum class TokenType {
        End,
        Slash,
        DoubleSlash,
        LBracket,
        RBracket,
        LParen,
        RParen,
        At,
        Comma,
        Pipe,
        Dot,
        DotDot,
        DoubleColon,
        Star,
        Plus,
        Minus,
        Equal,
        NotEqual,
        Less,
        LessEqual,
        Greater,
        GreaterEqual,
        Dollar,
        Number,
        Literal,
        Name,
    };

    struct Token {
        TokenType type{ TokenType::End };
        std::string name;   // Name
        std::string string; // Literal
        double number{ 0 }; // Number
    };

    class Tokenizer {
    public:
        Tokenizer(Document* document, const std::string& source)
            : m_document(document)
            , m_source(source)
        {
        }

        Token next()
        {
            skipWhitespace();
            Token token;
            if (m_position >= m_source.size()) {
                token.type = TokenType::End;
                return token;
            }
            char c = m_source[m_position];
            switch (c) {
            case '/':
                m_position++;
                if (peek() == '/') {
                    m_position++;
                    token.type = TokenType::DoubleSlash;
                } else {
                    token.type = TokenType::Slash;
                }
                return token;
            case '[':
                m_position++;
                token.type = TokenType::LBracket;
                return token;
            case ']':
                m_position++;
                token.type = TokenType::RBracket;
                return token;
            case '(':
                m_position++;
                token.type = TokenType::LParen;
                return token;
            case ')':
                m_position++;
                token.type = TokenType::RParen;
                return token;
            case '@':
                m_position++;
                token.type = TokenType::At;
                return token;
            case ',':
                m_position++;
                token.type = TokenType::Comma;
                return token;
            case '|':
                m_position++;
                token.type = TokenType::Pipe;
                return token;
            case '$':
                m_position++;
                token.type = TokenType::Dollar;
                return token;
            case '*':
                m_position++;
                token.type = TokenType::Star;
                return token;
            case '+':
                m_position++;
                token.type = TokenType::Plus;
                return token;
            case '-':
                m_position++;
                token.type = TokenType::Minus;
                return token;
            case '=':
                m_position++;
                token.type = TokenType::Equal;
                return token;
            case '!':
                m_position++;
                if (peek() != '=') {
                    throwSyntaxError(m_document,
                                     "Unexpected '!' in expression.");
                }
                m_position++;
                token.type = TokenType::NotEqual;
                return token;
            case '<':
                m_position++;
                if (peek() == '=') {
                    m_position++;
                    token.type = TokenType::LessEqual;
                } else {
                    token.type = TokenType::Less;
                }
                return token;
            case '>':
                m_position++;
                if (peek() == '=') {
                    m_position++;
                    token.type = TokenType::GreaterEqual;
                } else {
                    token.type = TokenType::Greater;
                }
                return token;
            case ':':
                m_position++;
                if (peek() != ':') {
                    throwSyntaxError(m_document,
                                     "Namespace prefixes are not supported.");
                }
                m_position++;
                token.type = TokenType::DoubleColon;
                return token;
            case '.':
                if (m_position + 1 < m_source.size() &&
                    isAsciiDigit(m_source[m_position + 1])) {
                    return lexNumber();
                }
                m_position++;
                if (peek() == '.') {
                    m_position++;
                    token.type = TokenType::DotDot;
                } else {
                    token.type = TokenType::Dot;
                }
                return token;
            case '"':
            case '\'': {
                m_position++;
                size_t end = m_source.find(c, m_position);
                if (end == std::string::npos) {
                    throwSyntaxError(m_document,
                                     "Unterminated string literal.");
                }
                token.type = TokenType::Literal;
                token.string = m_source.substr(m_position, end - m_position);
                m_position = end + 1;
                return token;
            }
            default:
                break;
            }
            if (isAsciiDigit(c)) {
                return lexNumber();
            }
            if (isNameStartChar(c)) {
                size_t start = m_position;
                while (m_position < m_source.size() &&
                       isNameChar(m_source[m_position])) {
                    m_position++;
                }
                token.type = TokenType::Name;
                token.name = m_source.substr(start, m_position - start);
                return token;
            }
            throwSyntaxError(m_document, "Unexpected character in expression.");
            STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE();
        }

    private:
        char peek() const
        {
            return m_position < m_source.size() ? m_source[m_position] : '\0';
        }

        void skipWhitespace()
        {
            while (m_position < m_source.size() &&
                   isAsciiSpace(m_source[m_position])) {
                m_position++;
            }
        }

        static bool isNameStartChar(char c)
        {
            return isAsciiAlpha(c) || c == '_' ||
                   static_cast<unsigned char>(c) >= 0x80;
        }

        static bool isNameChar(char c)
        {
            return isNameStartChar(c) || isAsciiDigit(c) || c == '-' ||
                   c == '.';
        }

        Token lexNumber()
        {
            size_t start = m_position;
            while (m_position < m_source.size() &&
                   (isAsciiDigit(m_source[m_position]) ||
                    m_source[m_position] == '.')) {
                m_position++;
            }
            Token token;
            token.type = TokenType::Number;
            token.number = strtod(
                m_source.substr(start, m_position - start).c_str(), nullptr);
            return token;
        }

        Document* m_document;
        const std::string& m_source;
        size_t m_position{ 0 };
    };

    // ---------------------------------------------------------------- AST

    enum class Axis {
        Child,
        Descendant,
        DescendantOrSelf,
        Self,
        Parent,
        Ancestor,
        AncestorOrSelf,
        Attribute,
        FollowingSibling,
        PrecedingSibling,
        Following,
        Preceding,
    };

    enum class NodeTest {
        Name,
        AnyName,
        Text,
        Comment,
        AnyNode,
        ProcessingInstruction,
    };

    struct Expression;

    struct Step : public gc {
        Axis axis{ Axis::Child };
        NodeTest test{ NodeTest::AnyNode };
        String* name{ nullptr };      // NodeTest::Name, original case
        String* nameLower{ nullptr }; // NodeTest::Name, lowercase for HTML
        GCVector<Expression*> predicates;
    };

    struct Expression : public gc {
        enum Op {
            Or,
            And,
            Equal,
            NotEqual,
            Less,
            LessEqual,
            Greater,
            GreaterEqual,
            Plus,
            Minus,
            Multiply,
            Divide,
            Modulo,
            Union,
            Negate,
            NumberLiteral,
            StringLiteral,
            FunctionCall,
            Path,
        };
        Op op{ Op::Path };

        // binary / unary operators
        Expression* left{ nullptr };
        Expression* right{ nullptr };

        // literals
        double numberValue{ 0 };
        String* stringValue{ nullptr };

        // function call
        String* functionName{ nullptr };
        GCVector<Expression*> arguments;

        // path
        bool absolute{ false };
        Expression* filter{ nullptr }; // path rooted at a primary expression
        GCVector<Step*> steps;
    };

    // ---------------------------------------------------------------- parser

    class Parser {
    public:
        Parser(Document* document, const std::string& source)
            : m_document(document)
            , m_tokenizer(document, source)
        {
            advance();
        }

        Expression* parse()
        {
            Expression* result = parseOrExpr();
            if (m_token.type != TokenType::End) {
                throwSyntaxError(m_document,
                                 "Unexpected token at end of expression.");
            }
            return result;
        }

    private:
        void advance()
        {
            m_token = m_tokenizer.next();
        }

        void expect(TokenType type, const char* message)
        {
            if (m_token.type != type) {
                throwSyntaxError(m_document, message);
            }
            advance();
        }

        bool isNameToken(const char* name) const
        {
            return m_token.type == TokenType::Name && m_token.name == name;
        }

        static Expression* makeBinary(Expression::Op op, Expression* left,
                                      Expression* right)
        {
            Expression* result = new Expression();
            result->op = op;
            result->left = left;
            result->right = right;
            return result;
        }

        Expression* parseOrExpr()
        {
            Expression* left = parseAndExpr();
            while (isNameToken("or")) {
                advance();
                left = makeBinary(Expression::Or, left, parseAndExpr());
            }
            return left;
        }

        Expression* parseAndExpr()
        {
            Expression* left = parseEqualityExpr();
            while (isNameToken("and")) {
                advance();
                left = makeBinary(Expression::And, left, parseEqualityExpr());
            }
            return left;
        }

        Expression* parseEqualityExpr()
        {
            Expression* left = parseRelationalExpr();
            while (m_token.type == TokenType::Equal ||
                   m_token.type == TokenType::NotEqual) {
                Expression::Op op = m_token.type == TokenType::Equal
                                        ? Expression::Equal
                                        : Expression::NotEqual;
                advance();
                left = makeBinary(op, left, parseRelationalExpr());
            }
            return left;
        }

        Expression* parseRelationalExpr()
        {
            Expression* left = parseAdditiveExpr();
            while (true) {
                Expression::Op op;
                if (m_token.type == TokenType::Less) {
                    op = Expression::Less;
                } else if (m_token.type == TokenType::LessEqual) {
                    op = Expression::LessEqual;
                } else if (m_token.type == TokenType::Greater) {
                    op = Expression::Greater;
                } else if (m_token.type == TokenType::GreaterEqual) {
                    op = Expression::GreaterEqual;
                } else {
                    return left;
                }
                advance();
                left = makeBinary(op, left, parseAdditiveExpr());
            }
        }

        Expression* parseAdditiveExpr()
        {
            Expression* left = parseMultiplicativeExpr();
            while (m_token.type == TokenType::Plus ||
                   m_token.type == TokenType::Minus) {
                Expression::Op op = m_token.type == TokenType::Plus
                                        ? Expression::Plus
                                        : Expression::Minus;
                advance();
                left = makeBinary(op, left, parseMultiplicativeExpr());
            }
            return left;
        }

        Expression* parseMultiplicativeExpr()
        {
            Expression* left = parseUnaryExpr();
            while (true) {
                Expression::Op op;
                if (m_token.type == TokenType::Star) {
                    op = Expression::Multiply;
                } else if (isNameToken("div")) {
                    op = Expression::Divide;
                } else if (isNameToken("mod")) {
                    op = Expression::Modulo;
                } else {
                    return left;
                }
                advance();
                left = makeBinary(op, left, parseUnaryExpr());
            }
        }

        Expression* parseUnaryExpr()
        {
            if (m_token.type == TokenType::Minus) {
                advance();
                Expression* result = new Expression();
                result->op = Expression::Negate;
                result->left = parseUnaryExpr();
                return result;
            }
            return parseUnionExpr();
        }

        Expression* parseUnionExpr()
        {
            Expression* left = parsePathExpr();
            while (m_token.type == TokenType::Pipe) {
                advance();
                left = makeBinary(Expression::Union, left, parsePathExpr());
            }
            return left;
        }

        bool tokenStartsStep() const
        {
            switch (m_token.type) {
            case TokenType::Dot:
            case TokenType::DotDot:
            case TokenType::At:
            case TokenType::Star:
                return true;
            case TokenType::Name:
                return true;
            default:
                return false;
            }
        }

        Expression* parsePathExpr()
        {
            Expression* path = new Expression();
            path->op = Expression::Path;

            if (m_token.type == TokenType::Slash ||
                m_token.type == TokenType::DoubleSlash) {
                path->absolute = true;
                if (m_token.type == TokenType::DoubleSlash) {
                    Step* step = new Step();
                    step->axis = Axis::DescendantOrSelf;
                    step->test = NodeTest::AnyNode;
                    path->steps.push_back(step);
                }
                advance();
                if (!tokenStartsStep()) {
                    if (path->steps.empty()) {
                        // bare "/"
                        return path;
                    }
                    throwSyntaxError(m_document, "Expected step after '//'.");
                }
                parseRelativePath(path);
                return path;
            }

            // FilterExpr: primary expression, optionally followed by predicates
            // and a relative path.
            if (m_token.type == TokenType::Literal ||
                m_token.type == TokenType::Number ||
                m_token.type == TokenType::LParen ||
                m_token.type == TokenType::Dollar ||
                lookaheadIsFunctionCall()) {
                Expression* primary = parsePrimaryExpr();
                if (m_token.type != TokenType::Slash &&
                    m_token.type != TokenType::DoubleSlash &&
                    m_token.type != TokenType::LBracket) {
                    return primary;
                }
                path->filter = primary;
                if (m_token.type == TokenType::LBracket) {
                    // predicates over a primary result require node-sets; treat
                    // as a filter step over the self axis
                    Step* step = new Step();
                    step->axis = Axis::Self;
                    step->test = NodeTest::AnyNode;
                    parsePredicates(step);
                    path->steps.push_back(step);
                }
                if (m_token.type == TokenType::Slash ||
                    m_token.type == TokenType::DoubleSlash) {
                    if (m_token.type == TokenType::DoubleSlash) {
                        Step* step = new Step();
                        step->axis = Axis::DescendantOrSelf;
                        step->test = NodeTest::AnyNode;
                        path->steps.push_back(step);
                    }
                    advance();
                    parseRelativePath(path);
                }
                return path;
            }

            if (!tokenStartsStep()) {
                throwSyntaxError(m_document, "Expected expression.");
            }
            parseRelativePath(path);
            return path;
        }

        // A Name token may start either a function call or a location path;
        // parseNameStart() disambiguates after consuming the name.
        bool lookaheadIsFunctionCall() const
        {
            return m_token.type == TokenType::Name;
        }

        Expression* parsePrimaryExpr()
        {
            switch (m_token.type) {
            case TokenType::Literal: {
                Expression* result = new Expression();
                result->op = Expression::StringLiteral;
                result->stringValue = String::fromUTF8(m_token.string.data(),
                                                       m_token.string.size());
                advance();
                return result;
            }
            case TokenType::Number: {
                Expression* result = new Expression();
                result->op = Expression::NumberLiteral;
                result->numberValue = m_token.number;
                advance();
                return result;
            }
            case TokenType::LParen: {
                advance();
                Expression* result = parseOrExpr();
                expect(TokenType::RParen, "Expected ')' in expression.");
                return result;
            }
            case TokenType::Dollar:
                throwSyntaxError(m_document,
                                 "Variable references are not supported.");
                break;
            case TokenType::Name:
                // Either a function call or a location path starting with a
                // name; resolved by parseNameStart().
                return parseNameStart();
            default:
                break;
            }
            throwSyntaxError(m_document, "Expected expression.");
            STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE();
        }

        // Handles an expression starting with a Name token: a function call if
        // followed by '(', otherwise a relative location path.
        Expression* parseNameStart()
        {
            std::string name = m_token.name;
            advance();
            if (m_token.type == TokenType::LParen && name != "text" &&
                name != "node" && name != "comment" &&
                name != "processing-instruction") {
                advance();
                Expression* result = new Expression();
                result->op = Expression::FunctionCall;
                result->functionName =
                    String::fromUTF8(name.data(), name.size());
                if (m_token.type != TokenType::RParen) {
                    while (true) {
                        result->arguments.push_back(parseOrExpr());
                        if (m_token.type != TokenType::Comma) {
                            break;
                        }
                        advance();
                    }
                }
                expect(TokenType::RParen,
                       "Expected ')' after function arguments.");
                return result;
            }

            // location path starting with this name
            Expression* path = new Expression();
            path->op = Expression::Path;
            Step* step = parseStepWithParsedName(name);
            path->steps.push_back(step);
            while (m_token.type == TokenType::Slash ||
                   m_token.type == TokenType::DoubleSlash) {
                if (m_token.type == TokenType::DoubleSlash) {
                    Step* descendant = new Step();
                    descendant->axis = Axis::DescendantOrSelf;
                    descendant->test = NodeTest::AnyNode;
                    path->steps.push_back(descendant);
                }
                advance();
                path->steps.push_back(parseStep());
            }
            return path;
        }

        void parseRelativePath(Expression* path)
        {
            path->steps.push_back(parseStep());
            while (m_token.type == TokenType::Slash ||
                   m_token.type == TokenType::DoubleSlash) {
                if (m_token.type == TokenType::DoubleSlash) {
                    Step* step = new Step();
                    step->axis = Axis::DescendantOrSelf;
                    step->test = NodeTest::AnyNode;
                    path->steps.push_back(step);
                }
                advance();
                path->steps.push_back(parseStep());
            }
        }

        Step* parseStep()
        {
            if (m_token.type == TokenType::Dot) {
                advance();
                Step* step = new Step();
                step->axis = Axis::Self;
                step->test = NodeTest::AnyNode;
                return step;
            }
            if (m_token.type == TokenType::DotDot) {
                advance();
                Step* step = new Step();
                step->axis = Axis::Parent;
                step->test = NodeTest::AnyNode;
                return step;
            }
            if (m_token.type == TokenType::At) {
                advance();
                Step* step = new Step();
                step->axis = Axis::Attribute;
                parseNodeTest(step);
                parsePredicates(step);
                return step;
            }
            if (m_token.type == TokenType::Star) {
                advance();
                Step* step = new Step();
                step->axis = Axis::Child;
                step->test = NodeTest::AnyName;
                parsePredicates(step);
                return step;
            }
            if (m_token.type == TokenType::Name) {
                std::string name = m_token.name;
                advance();
                return parseStepWithParsedName(name);
            }
            throwSyntaxError(m_document, "Expected location step.");
            STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE();
        }

        // The step's leading name has already been consumed. Handles axis
        // specifiers ("name::..."), node-type tests ("text()") and name tests.
        Step* parseStepWithParsedName(const std::string& name)
        {
            Step* step = new Step();
            std::string testName = name;
            if (m_token.type == TokenType::DoubleColon) {
                step->axis = axisFromName(name);
                advance();
                if (m_token.type == TokenType::Star) {
                    advance();
                    step->test = NodeTest::AnyName;
                    parsePredicates(step);
                    return step;
                }
                if (m_token.type == TokenType::At) {
                    throwSyntaxError(m_document, "Unexpected '@' after axis.");
                }
                if (m_token.type != TokenType::Name) {
                    throwSyntaxError(m_document,
                                     "Expected node test after axis.");
                }
                testName = m_token.name;
                advance();
            } else {
                step->axis = Axis::Child;
            }

            if (m_token.type == TokenType::LParen) {
                advance();
                if (testName == "text") {
                    step->test = NodeTest::Text;
                } else if (testName == "node") {
                    step->test = NodeTest::AnyNode;
                } else if (testName == "comment") {
                    step->test = NodeTest::Comment;
                } else if (testName == "processing-instruction") {
                    step->test = NodeTest::ProcessingInstruction;
                    if (m_token.type == TokenType::Literal) {
                        advance();
                    }
                } else {
                    throwSyntaxError(m_document, "Unknown node type test.");
                }
                expect(TokenType::RParen, "Expected ')' in node type test.");
            } else {
                step->test = NodeTest::Name;
                step->name = String::fromUTF8(testName.data(), testName.size());
                step->nameLower = step->name->toLower();
            }
            parsePredicates(step);
            return step;
        }

        void parseNodeTest(Step* step)
        {
            if (m_token.type == TokenType::Star) {
                advance();
                step->test = NodeTest::AnyName;
                return;
            }
            if (m_token.type != TokenType::Name) {
                throwSyntaxError(m_document,
                                 "Expected attribute name after '@'.");
            }
            step->test = NodeTest::Name;
            step->name =
                String::fromUTF8(m_token.name.data(), m_token.name.size());
            step->nameLower = step->name->toLower();
            advance();
        }

        void parsePredicates(Step* step)
        {
            while (m_token.type == TokenType::LBracket) {
                advance();
                step->predicates.push_back(parseOrExpr());
                expect(TokenType::RBracket, "Expected ']' after predicate.");
            }
        }

        Axis axisFromName(const std::string& name)
        {
            if (name == "child") {
                return Axis::Child;
            }
            if (name == "descendant") {
                return Axis::Descendant;
            }
            if (name == "descendant-or-self") {
                return Axis::DescendantOrSelf;
            }
            if (name == "self") {
                return Axis::Self;
            }
            if (name == "parent") {
                return Axis::Parent;
            }
            if (name == "ancestor") {
                return Axis::Ancestor;
            }
            if (name == "ancestor-or-self") {
                return Axis::AncestorOrSelf;
            }
            if (name == "attribute") {
                return Axis::Attribute;
            }
            if (name == "following-sibling") {
                return Axis::FollowingSibling;
            }
            if (name == "preceding-sibling") {
                return Axis::PrecedingSibling;
            }
            if (name == "following") {
                return Axis::Following;
            }
            if (name == "preceding") {
                return Axis::Preceding;
            }
            throwSyntaxError(m_document, "Unsupported axis name.");
            STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE();
        }

        Document* m_document;
        Tokenizer m_tokenizer;
        Token m_token;
    };

    // ----------------------------------------------------------------
    // evaluator

    struct EvaluationContext {
        Node* node;
        size_t position; // 1-based
        size_t size;
    };

    class Evaluator {
    public:
        Evaluator(Document* document)
            : m_document(document)
        {
        }

        Value* evaluate(Expression* expression,
                        const EvaluationContext& context)
        {
            switch (expression->op) {
            case Expression::Or: {
                Value* left = evaluate(expression->left, context);
                if (valueToBoolean(left)) {
                    return Value::makeBoolean(true);
                }
                return Value::makeBoolean(
                    valueToBoolean(evaluate(expression->right, context)));
            }
            case Expression::And: {
                Value* left = evaluate(expression->left, context);
                if (!valueToBoolean(left)) {
                    return Value::makeBoolean(false);
                }
                return Value::makeBoolean(
                    valueToBoolean(evaluate(expression->right, context)));
            }
            case Expression::Equal:
            case Expression::NotEqual:
                return evaluateEquality(expression, context);
            case Expression::Less:
            case Expression::LessEqual:
            case Expression::Greater:
            case Expression::GreaterEqual:
                return evaluateRelational(expression, context);
            case Expression::Plus:
            case Expression::Minus:
            case Expression::Multiply:
            case Expression::Divide:
            case Expression::Modulo: {
                double left =
                    valueToNumber(evaluate(expression->left, context));
                double right =
                    valueToNumber(evaluate(expression->right, context));
                switch (expression->op) {
                case Expression::Plus:
                    return Value::makeNumber(left + right);
                case Expression::Minus:
                    return Value::makeNumber(left - right);
                case Expression::Multiply:
                    return Value::makeNumber(left * right);
                case Expression::Divide:
                    return Value::makeNumber(left / right);
                default:
                    return Value::makeNumber(std::fmod(left, right));
                }
            }
            case Expression::Union: {
                Value* left = evaluate(expression->left, context);
                Value* right = evaluate(expression->right, context);
                if (left->kind != Value::NodeSetKind ||
                    right->kind != Value::NodeSetKind) {
                    throwSyntaxError(m_document,
                                     "Union operands must be node-sets.");
                }
                Value* result = Value::makeNodeSet();
                for (size_t i = 0; i < left->nodes.size(); i++) {
                    appendUnique(result->nodes, left->nodes[i]);
                }
                for (size_t i = 0; i < right->nodes.size(); i++) {
                    appendUnique(result->nodes, right->nodes[i]);
                }
                sortInDocumentOrder(result->nodes);
                return result;
            }
            case Expression::Negate:
                return Value::makeNumber(
                    -valueToNumber(evaluate(expression->left, context)));
            case Expression::NumberLiteral:
                return Value::makeNumber(expression->numberValue);
            case Expression::StringLiteral:
                return Value::makeString(expression->stringValue);
            case Expression::FunctionCall:
                return evaluateFunction(expression, context);
            case Expression::Path:
                return evaluatePath(expression, context);
            }
            STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE();
        }

        void sortInDocumentOrder(GCVector<Node*>& nodes)
        {
            if (nodes.size() < 2) {
                return;
            }
            std::map<Node*, std::vector<size_t>> keys;
            for (size_t i = 0; i < nodes.size(); i++) {
                keys[nodes[i]] = documentOrderKey(nodes[i]);
            }
            // GCVector has no random-access sort support; copy out, sort, copy
            // back.
            std::vector<Node*> copied;
            copied.reserve(nodes.size());
            for (size_t i = 0; i < nodes.size(); i++) {
                copied.push_back(nodes[i]);
            }
            std::stable_sort(
                copied.begin(), copied.end(),
                [&keys](Node* a, Node* b) { return keys[a] < keys[b]; });
            for (size_t i = 0; i < copied.size(); i++) {
                nodes[i] = copied[i];
            }
        }

    private:
        static void appendUnique(GCVector<Node*>& nodes, Node* node)
        {
            for (size_t i = 0; i < nodes.size(); i++) {
                if (nodes[i] == node) {
                    return;
                }
            }
            nodes.push_back(node);
        }

        std::vector<size_t> documentOrderKey(Node* node)
        {
            std::vector<size_t> key;
            Node* current = node;
            if (current->isAttr()) {
                Attr* attr = current->asAttr();
                Element* owner = attr->ownerElement();
                if (owner) {
                    key.push_back(indexOfAttribute(owner, attr));
                    // attributes come right after their element but before its
                    // children; SIZE_MAX cannot be used since children compare
                    // greater; use a two-level key: element key + {0,
                    // attrIndex} vs element key + {1, childIndex}
                    key.push_back(0);
                    current = owner;
                }
            }
            while (current) {
                Node* parent = current->parentNode();
                if (parent) {
                    size_t index = 0;
                    for (Node* sibling = parent->firstChild(); sibling;
                         sibling = sibling->nextSibling()) {
                        if (sibling == current) {
                            break;
                        }
                        index++;
                    }
                    key.push_back(index + 1);
                }
                current = parent;
            }
            std::reverse(key.begin(), key.end());
            return key;
        }

        static size_t indexOfAttribute(Element* element, Attr* attr)
        {
            GCVector<String*> names = element->getAttributeNames();
            for (size_t i = 0; i < names.size(); i++) {
                if (names[i]->equals(attr->name())) {
                    return i;
                }
            }
            return 0;
        }

        Value* evaluateEquality(Expression* expression,
                                const EvaluationContext& context)
        {
            Value* left = evaluate(expression->left, context);
            Value* right = evaluate(expression->right, context);
            bool equal;
            if (left->kind == Value::NodeSetKind ||
                right->kind == Value::NodeSetKind) {
                equal = nodeSetComparison(left, right,
                                          expression->op == Expression::Equal);
                return Value::makeBoolean(equal);
            }
            if (left->kind == Value::BooleanKind ||
                right->kind == Value::BooleanKind) {
                equal = valueToBoolean(left) == valueToBoolean(right);
            } else if (left->kind == Value::NumberKind ||
                       right->kind == Value::NumberKind) {
                equal = valueToNumber(left) == valueToNumber(right);
            } else {
                equal = valueToString(left)->equals(valueToString(right));
            }
            if (expression->op == Expression::NotEqual) {
                equal = !equal;
            }
            return Value::makeBoolean(equal);
        }

        // Existential comparison when at least one side is a node-set. Returns
        // the raw comparison result; for Equal op pass wantEqual=true, for
        // NotEqual pass wantEqual=false.
        bool nodeSetComparison(Value* left, Value* right, bool wantEqual)
        {
            auto stringsOf = [](Value* value, GCVector<String*>& out) {
                if (value->kind == Value::NodeSetKind) {
                    for (size_t i = 0; i < value->nodes.size(); i++) {
                        out.push_back(stringValueOfNode(value->nodes[i]));
                    }
                } else {
                    out.push_back(valueToString(value));
                }
            };
            if (left->kind != Value::NodeSetKind ||
                right->kind != Value::NodeSetKind) {
                // node-set vs primitive
                Value* nodeSet =
                    left->kind == Value::NodeSetKind ? left : right;
                Value* primitive =
                    left->kind == Value::NodeSetKind ? right : left;
                if (primitive->kind == Value::BooleanKind) {
                    return (valueToBoolean(nodeSet) == primitive->boolean) ==
                           wantEqual;
                }
                for (size_t i = 0; i < nodeSet->nodes.size(); i++) {
                    String* nodeString = stringValueOfNode(nodeSet->nodes[i]);
                    bool eq;
                    if (primitive->kind == Value::NumberKind) {
                        eq = stringToNumber(nodeString) == primitive->number;
                    } else {
                        eq = nodeString->equals(valueToString(primitive));
                    }
                    if (eq == wantEqual) {
                        return true;
                    }
                }
                return false;
            }
            GCVector<String*> leftStrings, rightStrings;
            stringsOf(left, leftStrings);
            stringsOf(right, rightStrings);
            for (size_t i = 0; i < leftStrings.size(); i++) {
                for (size_t j = 0; j < rightStrings.size(); j++) {
                    bool eq = leftStrings[i]->equals(rightStrings[j]);
                    if (eq == wantEqual) {
                        return true;
                    }
                }
            }
            return false;
        }

        Value* evaluateRelational(Expression* expression,
                                  const EvaluationContext& context)
        {
            double left = valueToNumber(evaluate(expression->left, context));
            double right = valueToNumber(evaluate(expression->right, context));
            bool result;
            switch (expression->op) {
            case Expression::Less:
                result = left < right;
                break;
            case Expression::LessEqual:
                result = left <= right;
                break;
            case Expression::Greater:
                result = left > right;
                break;
            default:
                result = left >= right;
                break;
            }
            return Value::makeBoolean(result);
        }

        Value* evaluatePath(Expression* expression,
                            const EvaluationContext& context)
        {
            GCVector<Node*> current;
            if (expression->filter) {
                Value* start = evaluate(expression->filter, context);
                if (expression->steps.empty()) {
                    return start;
                }
                if (start->kind != Value::NodeSetKind) {
                    throwSyntaxError(
                        m_document,
                        "Filter expression must evaluate to a node-set.");
                }
                current = start->nodes;
            } else if (expression->absolute) {
                current.push_back(m_document);
            } else {
                current.push_back(context.node);
            }

            for (size_t i = 0; i < expression->steps.size(); i++) {
                Step* step = expression->steps[i];
                GCVector<Node*> next;
                for (size_t j = 0; j < current.size(); j++) {
                    GCVector<Node*> matched;
                    nodesForStep(step, current[j], matched);
                    applyPredicates(step, matched);
                    for (size_t k = 0; k < matched.size(); k++) {
                        appendUnique(next, matched[k]);
                    }
                }
                current = next;
            }

            Value* result = Value::makeNodeSet();
            result->nodes = current;
            return result;
        }

        void applyPredicates(Step* step, GCVector<Node*>& nodes)
        {
            for (size_t p = 0; p < step->predicates.size(); p++) {
                Expression* predicate = step->predicates[p];
                GCVector<Node*> kept;
                for (size_t i = 0; i < nodes.size(); i++) {
                    EvaluationContext context{ nodes[i], i + 1, nodes.size() };
                    Value* value = evaluate(predicate, context);
                    bool keep;
                    if (value->kind == Value::NumberKind) {
                        keep = value->number ==
                               static_cast<double>(context.position);
                    } else {
                        keep = valueToBoolean(value);
                    }
                    if (keep) {
                        kept.push_back(nodes[i]);
                    }
                }
                nodes = kept;
            }
        }

        bool nodeMatchesTest(Step* step, Node* node)
        {
            switch (step->test) {
            case NodeTest::AnyNode:
                return true;
            case NodeTest::Text:
                return node->nodeType() == Node::TEXT_NODE ||
                       node->nodeType() == Node::CDATA_SECTION_NODE;
            case NodeTest::Comment:
                return node->nodeType() == Node::COMMENT_NODE;
            case NodeTest::ProcessingInstruction:
                return node->nodeType() == Node::PROCESSING_INSTRUCTION_NODE;
            case NodeTest::AnyName:
                if (step->axis == Axis::Attribute) {
                    return node->isAttr();
                }
                return node->nodeType() == Node::ELEMENT_NODE;
            case NodeTest::Name: {
                if (step->axis == Axis::Attribute) {
                    if (!node->isAttr()) {
                        return false;
                    }
                    return node->asAttr()->name()->equals(step->name);
                }
                if (node->nodeType() != Node::ELEMENT_NODE) {
                    return false;
                }
                String* localName = node->localName();
                if (m_document->isXMLDocument()) {
                    return localName->equals(step->name);
                }
                // HTML documents: element names are lower-cased; match name
                // tests case-insensitively as browsers do.
                return localName->equalsIgnoreCase(step->nameLower);
            }
            }
            return false;
        }

        void collectDescendants(Node* node, Step* step, GCVector<Node*>& out)
        {
            for (Node* child = node->firstChild(); child;
                 child = child->nextSibling()) {
                if (nodeMatchesTest(step, child)) {
                    out.push_back(child);
                }
                collectDescendants(child, step, out);
            }
        }

        void collectAttributes(Node* node, Step* step, GCVector<Node*>& out)
        {
            if (node->nodeType() != Node::ELEMENT_NODE) {
                return;
            }
            Element* element = node->asElement();
            if (step->test == NodeTest::Name) {
                Attr* attr = element->getAttributeNode(step->name);
                if (attr) {
                    out.push_back(attr);
                }
                return;
            }
            GCVector<String*> names = element->getAttributeNames();
            for (size_t i = 0; i < names.size(); i++) {
                Attr* attr = element->getAttributeNode(names[i]);
                if (attr && nodeMatchesTest(step, attr)) {
                    out.push_back(attr);
                }
            }
        }

        void nodesForStep(Step* step, Node* context, GCVector<Node*>& out)
        {
            Node* base = context;
            if (base->isAttr()) {
                // Only the ancestor-ish and self axes make sense from an
                // attribute node.
                if (step->axis != Axis::Parent &&
                    step->axis != Axis::Ancestor &&
                    step->axis != Axis::AncestorOrSelf &&
                    step->axis != Axis::Self) {
                    return;
                }
                Element* owner = base->asAttr()->ownerElement();
                switch (step->axis) {
                case Axis::Self:
                    if (nodeMatchesTest(step, base)) {
                        out.push_back(base);
                    }
                    return;
                case Axis::Parent:
                    if (owner && nodeMatchesTest(step, owner)) {
                        out.push_back(owner);
                    }
                    return;
                default:
                    for (Node* ancestor = owner; ancestor;
                         ancestor = ancestor->parentNode()) {
                        if (nodeMatchesTest(step, ancestor)) {
                            out.push_back(ancestor);
                        }
                    }
                    return;
                }
            }
            switch (step->axis) {
            case Axis::Child:
                for (Node* child = base->firstChild(); child;
                     child = child->nextSibling()) {
                    if (nodeMatchesTest(step, child)) {
                        out.push_back(child);
                    }
                }
                return;
            case Axis::Descendant:
                collectDescendants(base, step, out);
                return;
            case Axis::DescendantOrSelf:
                if (nodeMatchesTest(step, base)) {
                    out.push_back(base);
                }
                collectDescendants(base, step, out);
                return;
            case Axis::Self:
                if (nodeMatchesTest(step, base)) {
                    out.push_back(base);
                }
                return;
            case Axis::Parent: {
                Node* parent = base->parentNode();
                if (parent && nodeMatchesTest(step, parent)) {
                    out.push_back(parent);
                }
                return;
            }
            case Axis::Ancestor:
                for (Node* ancestor = base->parentNode(); ancestor;
                     ancestor = ancestor->parentNode()) {
                    if (nodeMatchesTest(step, ancestor)) {
                        out.push_back(ancestor);
                    }
                }
                return;
            case Axis::AncestorOrSelf:
                for (Node* ancestor = base; ancestor;
                     ancestor = ancestor->parentNode()) {
                    if (nodeMatchesTest(step, ancestor)) {
                        out.push_back(ancestor);
                    }
                }
                return;
            case Axis::Attribute:
                collectAttributes(base, step, out);
                return;
            case Axis::FollowingSibling:
                for (Node* sibling = base->nextSibling(); sibling;
                     sibling = sibling->nextSibling()) {
                    if (nodeMatchesTest(step, sibling)) {
                        out.push_back(sibling);
                    }
                }
                return;
            case Axis::PrecedingSibling:
                for (Node* sibling = base->previousSibling(); sibling;
                     sibling = sibling->previousSibling()) {
                    if (nodeMatchesTest(step, sibling)) {
                        out.push_back(sibling);
                    }
                }
                return;
            case Axis::Following: {
                // all nodes after base in document order, excluding descendants
                Node* current = base;
                while (current) {
                    Node* sibling = current->nextSibling();
                    while (!sibling && current->parentNode()) {
                        current = current->parentNode();
                        sibling = current->nextSibling();
                    }
                    if (!sibling) {
                        return;
                    }
                    for (Node* n = sibling; n; n = n->nextSibling()) {
                        if (nodeMatchesTest(step, n)) {
                            out.push_back(n);
                        }
                        collectDescendants(n, step, out);
                    }
                    current = current->parentNode();
                    if (!current) {
                        return;
                    }
                }
                return;
            }
            case Axis::Preceding: {
                // all nodes before base in document order, excluding ancestors,
                // in reverse document order
                GCVector<Node*> ancestors;
                for (Node* ancestor = base; ancestor;
                     ancestor = ancestor->parentNode()) {
                    ancestors.push_back(ancestor);
                }
                GCVector<Node*> all;
                collectPrecedingInDocOrder(m_document, base, ancestors, all);
                for (size_t i = all.size(); i > 0; i--) {
                    out.push_back(all[i - 1]);
                }
                return;
            }
            }
        }

        // Preorder walk that stops at `stop`, collecting matching nodes that
        // are not in `excluded`.
        bool collectPrecedingInDocOrder(Node* node, Node* stop,
                                        const GCVector<Node*>& excluded,
                                        GCVector<Node*>& out)
        {
            if (node == stop) {
                return true;
            }
            bool isExcluded = false;
            for (size_t i = 0; i < excluded.size(); i++) {
                if (excluded[i] == node) {
                    isExcluded = true;
                    break;
                }
            }
            if (!isExcluded && node != m_document) {
                out.push_back(node);
            }
            for (Node* child = node->firstChild(); child;
                 child = child->nextSibling()) {
                if (collectPrecedingInDocOrder(child, stop, excluded, out)) {
                    return true;
                }
            }
            return false;
        }

        Value* evaluateFunction(Expression* expression,
                                const EvaluationContext& context)
        {
            String* name = expression->functionName;
            size_t argc = expression->arguments.size();
            auto arg = [&](size_t index) -> Value* {
                return evaluate(expression->arguments[index], context);
            };
            auto argAsString = [&](size_t index) -> String* {
                return valueToString(arg(index));
            };
            auto contextString = [&]() -> String* {
                return stringValueOfNode(context.node);
            };

            if (name->equals("last")) {
                return Value::makeNumber(static_cast<double>(context.size));
            }
            if (name->equals("position")) {
                return Value::makeNumber(static_cast<double>(context.position));
            }
            if (name->equals("count")) {
                if (argc != 1) {
                    throwSyntaxError(m_document,
                                     "count() requires one argument.");
                }
                Value* value = arg(0);
                if (value->kind != Value::NodeSetKind) {
                    throwSyntaxError(m_document,
                                     "count() requires a node-set argument.");
                }
                return Value::makeNumber(
                    static_cast<double>(value->nodes.size()));
            }
            if (name->equals("local-name") || name->equals("name")) {
                Node* target = context.node;
                if (argc >= 1) {
                    Value* value = arg(0);
                    if (value->kind != Value::NodeSetKind) {
                        throwSyntaxError(
                            m_document, "name() requires a node-set argument.");
                    }
                    if (value->nodes.empty()) {
                        return Value::makeString(String::emptyString);
                    }
                    target = value->nodes.front();
                }
                if (target->isAttr()) {
                    return Value::makeString(target->asAttr()->name());
                }
                if (target->nodeType() == Node::ELEMENT_NODE) {
                    return Value::makeString(target->localName());
                }
                return Value::makeString(String::emptyString);
            }
            if (name->equals("string")) {
                return Value::makeString(argc >= 1 ? argAsString(0)
                                                   : contextString());
            }
            if (name->equals("number")) {
                if (argc >= 1) {
                    return Value::makeNumber(valueToNumber(arg(0)));
                }
                return Value::makeNumber(stringToNumber(contextString()));
            }
            if (name->equals("boolean")) {
                if (argc != 1) {
                    throwSyntaxError(m_document,
                                     "boolean() requires one argument.");
                }
                return Value::makeBoolean(valueToBoolean(arg(0)));
            }
            if (name->equals("not")) {
                if (argc != 1) {
                    throwSyntaxError(m_document,
                                     "not() requires one argument.");
                }
                return Value::makeBoolean(!valueToBoolean(arg(0)));
            }
            if (name->equals("true")) {
                return Value::makeBoolean(true);
            }
            if (name->equals("false")) {
                return Value::makeBoolean(false);
            }
            if (name->equals("concat")) {
                String* result = String::emptyString;
                for (size_t i = 0; i < argc; i++) {
                    result = result->concat(argAsString(i));
                }
                return Value::makeString(result);
            }
            if (name->equals("starts-with")) {
                if (argc != 2) {
                    throwSyntaxError(m_document,
                                     "starts-with() requires two arguments.");
                }
                String* haystack = argAsString(0);
                String* needle = argAsString(1);
                return Value::makeBoolean(haystack->startsWith(needle));
            }
            if (name->equals("contains")) {
                if (argc != 2) {
                    throwSyntaxError(m_document,
                                     "contains() requires two arguments.");
                }
                String* haystack = argAsString(0);
                String* needle = argAsString(1);
                return Value::makeBoolean(haystack->contains(needle));
            }
            if (name->equals("string-length")) {
                String* value = argc >= 1 ? argAsString(0) : contextString();
                return Value::makeNumber(static_cast<double>(value->length()));
            }
            if (name->equals("normalize-space")) {
                String* value = argc >= 1 ? argAsString(0) : contextString();
                auto utf8 = value->toUTF8NonGCString();
                std::string normalized;
                bool pendingSpace = false;
                for (size_t i = 0; i < utf8.length(); i++) {
                    char c = utf8[i];
                    if (c == ' ' || c == '\t' || c == '\n' || c == '\r') {
                        if (!normalized.empty()) {
                            pendingSpace = true;
                        }
                        continue;
                    }
                    if (pendingSpace) {
                        normalized += ' ';
                        pendingSpace = false;
                    }
                    normalized += c;
                }
                return Value::makeString(
                    String::fromUTF8(normalized.data(), normalized.size()));
            }
            if (name->equals("substring-before") ||
                name->equals("substring-after")) {
                if (argc != 2) {
                    throwSyntaxError(
                        m_document,
                        "substring-before()/substring-after() require two "
                        "arguments.");
                }
                String* haystack = argAsString(0);
                String* needle = argAsString(1);
                size_t index = haystack->find(needle);
                if (index == SIZE_MAX) {
                    return Value::makeString(String::emptyString);
                }
                if (name->equals("substring-before")) {
                    return Value::makeString(haystack->substring(0, index));
                }
                size_t start = index + needle->length();
                return Value::makeString(
                    haystack->substring(start, haystack->length() - start));
            }
            if (name->equals("substring")) {
                if (argc < 2) {
                    throwSyntaxError(m_document,
                                     "substring() requires two or three "
                                     "arguments.");
                }
                String* value = argAsString(0);
                double start = std::round(valueToNumber(arg(1)));
                double end = argc >= 3
                                 ? start + std::round(valueToNumber(arg(2)))
                                 : std::numeric_limits<double>::infinity();
                if (std::isnan(start) || std::isnan(end) || end <= 1 ||
                    start > static_cast<double>(value->length())) {
                    return Value::makeString(String::emptyString);
                }
                size_t from = start < 1 ? 0 : static_cast<size_t>(start) - 1;
                size_t to = end > static_cast<double>(value->length()) + 1
                                ? value->length()
                                : static_cast<size_t>(end) - 1;
                if (to <= from) {
                    return Value::makeString(String::emptyString);
                }
                return Value::makeString(value->substring(from, to - from));
            }
            if (name->equals("ceiling")) {
                if (argc != 1) {
                    throwSyntaxError(m_document,
                                     "ceiling() requires one argument.");
                }
                return Value::makeNumber(std::ceil(valueToNumber(arg(0))));
            }
            if (name->equals("floor")) {
                if (argc != 1) {
                    throwSyntaxError(m_document,
                                     "floor() requires one argument.");
                }
                return Value::makeNumber(std::floor(valueToNumber(arg(0))));
            }
            if (name->equals("round")) {
                if (argc != 1) {
                    throwSyntaxError(m_document,
                                     "round() requires one argument.");
                }
                return Value::makeNumber(std::round(valueToNumber(arg(0))));
            }
            if (name->equals("sum")) {
                if (argc != 1) {
                    throwSyntaxError(m_document,
                                     "sum() requires one argument.");
                }
                Value* value = arg(0);
                if (value->kind != Value::NodeSetKind) {
                    throwSyntaxError(m_document,
                                     "sum() requires a node-set argument.");
                }
                double sum = 0;
                for (size_t i = 0; i < value->nodes.size(); i++) {
                    sum += stringToNumber(stringValueOfNode(value->nodes[i]));
                }
                return Value::makeNumber(sum);
            }
            throwSyntaxError(m_document, "Unsupported XPath function.");
            STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE();
        }

        Document* m_document;
    };
} // namespace XPathImpl

XPathResult* evaluateXPathExpression(Document* document, String* expression,
                                     Node* contextNode, uint16_t desiredType)
{
    using namespace XPathImpl;

    if (desiredType > XPathResult::FIRST_ORDERED_NODE_TYPE) {
        throw new DOMException(document->executionContext(),
                               DOMException::NOT_SUPPORTED_ERR,
                               "Invalid XPathResult type requested.");
    }

    auto utf8 = expression->toUTF8NonGCString();
    std::string source(utf8.data(), utf8.length());
    Parser parser(document, source);
    Expression* parsed = parser.parse();

    Evaluator evaluator(document);
    EvaluationContext context{ contextNode ? contextNode : document, 1, 1 };
    Value* value = evaluator.evaluate(parsed, context);

    uint16_t type = desiredType;
    if (type == XPathResult::ANY_TYPE) {
        switch (value->kind) {
        case Value::NodeSetKind:
            type = XPathResult::UNORDERED_NODE_ITERATOR_TYPE;
            break;
        case Value::BooleanKind:
            type = XPathResult::BOOLEAN_TYPE;
            break;
        case Value::NumberKind:
            type = XPathResult::NUMBER_TYPE;
            break;
        case Value::StringKind:
            type = XPathResult::STRING_TYPE;
            break;
        }
    }

    switch (type) {
    case XPathResult::NUMBER_TYPE:
        return XPathResult::createNumber(document, valueToNumber(value));
    case XPathResult::STRING_TYPE:
        return XPathResult::createString(document, valueToString(value));
    case XPathResult::BOOLEAN_TYPE:
        return XPathResult::createBoolean(document, valueToBoolean(value));
    default:
        break;
    }

    if (value->kind != Value::NodeSetKind) {
        throw new DOMException(
            document->executionContext(), DOMException::TYPE_MISMATCH_ERR,
            "The expression cannot be converted to the requested "
            "XPathResult type.");
    }

    if (type == XPathResult::ORDERED_NODE_ITERATOR_TYPE ||
        type == XPathResult::ORDERED_NODE_SNAPSHOT_TYPE ||
        type == XPathResult::FIRST_ORDERED_NODE_TYPE) {
        evaluator.sortInDocumentOrder(value->nodes);
    }
    if (type == XPathResult::FIRST_ORDERED_NODE_TYPE &&
        value->nodes.size() > 1) {
        GCVector<Node*> first;
        first.push_back(value->nodes.front());
        return XPathResult::createNodeSet(document, type, first);
    }
    return XPathResult::createNodeSet(document, type, value->nodes);
}
} // namespace Starfish
