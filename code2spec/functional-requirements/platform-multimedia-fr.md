# Functional Requirements — platform-multimedia

> **Relevant source files**
> - [`MediaPlayer.h`](src:src/platform/multimedia/MediaPlayer.h)
> - [`StreamInfo.h`](src:src/platform/multimedia/StreamInfo.h)
> - [`DemuxerSource.h`](src:src/platform/multimedia/DemuxerSource.h)

## Given Factors

- Compile-time gated by `STARFISH_ENABLE_MULTIMEDIA`
- Multiple platform backends (Linux, Tizen, TV, WebRTC)
- Media codecs: AAC, MP3, Vorbis, Opus, H.264, HEVC, VP9, AV1

## Overview

The multimedia module provides media playback infrastructure including player state management, stream demuxing, codec handling, and WebRTC support.

## Functional Requirements

### FR-MM-001: Media Playback
The system shall manage media playback with states: NONE, PLAYING, PAUSED, END.
- **Source:** [`MediaPlayer.h`](src:src/platform/multimedia/MediaPlayer.h#L67)

### FR-MM-002: Seek Management
The system shall manage seek operations with states: NO_SEEK, SEEKING, WAITING.
- **Source:** [`MediaPlayer.h`](src:src/platform/multimedia/MediaPlayer.h#L73)

### FR-MM-003: Stream Type Detection
The system shall identify stream types: Unknown, Audio, Video, Subtitle.
- **Source:** [`StreamInfo.h`](src:src/platform/multimedia/StreamInfo.h#L52)

### FR-MM-004: Codec Support
The system shall support audio codecs (AAC, MP3, Vorbis, Opus) and video codecs (H.264, HEVC, VP9, AV1).
- **Source:** [`StreamInfo.h`](src:src/platform/multimedia/StreamInfo.h#L59)

### FR-MM-005: Audio Sample Formats
The system shall handle audio sample formats: U8, S16, S32, FLT, DBL, and planar variants.
- **Source:** [`StreamInfo.h`](src:src/platform/multimedia/StreamInfo.h#L73)

### FR-MM-006: Demuxer Seek
The system shall support seek operations with whences: Set, Current, End, LookSize.
- **Source:** [`DemuxerSource.h`](src:src/platform/multimedia/DemuxerSource.h#L26)

## Dependencies

- core-engine, platform-canvas, libcurl

## Code Factors

- C++, LGPL v2.1, compile-time gated

## Quality

- Error logging always enabled (`PLAYER_LOGE`)
- Default video dimensions for audio-only streams
