# Task: IPC Pattern Discovery for CPP

## Context
You are a static analysis expert. The code2spec parser has identified the following call expressions
from 40 cpp source files that do NOT match any known IPC patterns.

Your task is to identify which of these calls represent IPC (Inter-Process Communication) mechanisms
and categorize them appropriately.

## Known IPC Mechanisms
The parser already knows these IPC mechanisms:
- socket, grpc, message_queue, pipe, shared_memory, signal
- binder, dbus, broadcast_receiver (Android)
- named_pipe, wcf (Windows)
- rmi (Java), xpc (macOS)
- http_client, subprocess
- app_control, message_port (Tizen)

## Unmatched Call Expressions
(375 calls that don't match static patterns)

  - ALLOCA
  - CAST_LOG_IF_ALLOWED
  - CAST_RECV_LOG_IF_ALLOWED
  - CAST_SEND_LOG_IF_ALLOWED
  - CSTR
  - DataStateString
  - EventInit
  - GC_REGISTER_FINALIZER_NO_ORDER
  - GetSystemTimeAsFileTime
  - LayoutRect
  - RTCRtpSendParameters
  - RTCStateToScriptValue
  - ResizeObserverOptions
  - SOURCEBUFFER_LOG
  - STARFISH_ASSERT
  - STARFISH_LOG_DEBUG
  - STARFISH_LOG_ERROR
  - STARFISH_LOG_INFO
  - STARFISH_LOG_WARN
  - STARFISH_RELEASE_ASSERT
  - STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE
  - STARFISH_UNIMPLEMENTED
  - STARFISH_UNSUPPORTED
  - StringView
  - _tzset
  - abortInternal
  - activeAudioSourceBuffer
  - activeAudioStreamIndex
  - activeSourceBuffers
  - activeVideoSourceBuffer
  - activeVideoStreamIndex
  - addTrack
  - aliveSender
  - anySourceBufferInUpdatingState
  - appURL
  - appendBuffer
  - args
  - arrayBufferByteSize
  - arrayBufferRawData
  - arrayBufferViewByteSize
  - arrayBufferViewRawData
  - arrayObj
  - attachedMediaElement
  - audioTrack
  - audioTracks
  - backend
  - backendReceivers
  - backendSender
  - backendSenders
  - backendTransceiver
  - box
  - buf
  - buffer
  - bufferAppend
  - c
  - callScriptFunction
  - callback
  - candidate
  - canvas
  - clearPacketAccessCache
  - client
  - clientAddr
  - codecs
  - codedFrameEviction
  - compositor
  - config
  - configuration
  - constraints
  - createScriptString
  - createScriptValue
  - curStreams
  - currentDirection
  - currentDirectionStr
  - data
  - dataChannel
  - dataChannelDict
  - dataStr
  - decreaseUsedBufferSize
  - demuxer
  - demuxerClient
  - des
  - description
  - direction
  - dispose
  - doRun
  - document
  - drawFps
  - dumpHTTPHeaders
  - element
  - encoding
  - endOfStream
  - endOfStreamInternal
  - error
  - errorDetail
  - eventInit
  - events
  - exception
  - executionContext
  - existingTransceiver
  - fclose

## Your Task
For each call that represents IPC communication:
1. Identify the IPC mechanism type (use existing types or propose new ones)
2. Provide a brief rationale for your classification
3. Suggest the direction (incoming/outgoing/bidirectional)

## Output Format
You MUST output in the following YAML format:

```yaml
language: "cpp"
ipc_patterns:
  - call_name: "SomeClass.SomeMethod"
    ipc_mechanism: "binder"  # or propose new like "content_provider"
    direction: "outgoing"  # incoming/outgoing/bidirectional
    rationale: "This is an Android Binder call for cross-process communication"
```

## Rules
1. Only identify calls that are truly IPC (cross-process communication)
2. Regular function calls within the same process should NOT be marked as IPC
3. If you identify a new IPC mechanism not in the known list, explain why it's needed
4. Be conservative - when in doubt, don't classify as IPC
