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

#ifndef __StarfishAbortSignal__
#define __StarfishAbortSignal__

#include "core/dom/EventTarget.h"

namespace Starfish {

class AbortSignal : public EventTarget {
public:
    AbortSignal(ExecutionContext* executionContext);

    DECLARE_SCRIPT_BINDING_REQUIRED_FUNCTIONS(AbortSignal)

    virtual ExecutionContext* executionContext() const override;

    bool aborted() const
    {
        return m_aborted;
    }

    // UA-internal: transition this signal to the aborted state and fire the
    // 'abort' event once. Called by AbortController::abort().
    void signalAbort();

#define VIRTUAL
#define OVERRIDE
    DECLARE_EVENT_LISTENER(abort);
#undef VIRTUAL
#undef OVERRIDE

private:
    ExecutionContext* m_executionContext;
    bool m_aborted;
};

} // namespace Starfish

#endif
