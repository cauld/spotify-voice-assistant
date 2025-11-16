# Spotify Voice Assistant for Home Assistant

**Voice-controlled Spotify playback using natural language.** Just say "Play Coldplay on the kitchen speaker" and your music starts playing - no complex YAML patterns and no cookie authentication.

## Requirements

Before using this integration, you need:

1. **Home Assistant** - Obviously!
2. **Spotify Premium account** - Required for Spotify Connect API
3. **[Spotify integration](https://www.home-assistant.io/integrations/spotify/)** - Home Assistant's official Spotify integration (provides OAuth authentication)
4. **A conversation agent with function calling support** - Examples: [Extended OpenAI Conversation](https://github.com/jekalmin/extended_openai_conversation) (works with Ollama, OpenAI, LocalAI), OpenAI Conversation, Google Generative AI Conversation
5. **At least one Spotify Connect device** - Any speaker/device that appears in Spotify (see [Compatible Speakers](#compatible-speakers) for examples)

## Why Use This?

**Perfect for you if:**
- You want voice-controlled Spotify without running a full music server
- You use conversation agents with function calling (Extended OpenAI Conversation, OpenAI, Gemini, etc.)
- You want direct Spotify Connect integration with minimal dependencies
- You prefer simple, maintainable code (<120 lines)

**Consider alternatives if:**
- You need multi-provider music aggregation (Spotify + local files + streaming services) → Use Music Assistant
- You want rich UI-based queue management and multi-room features → Use Music Assistant
- You use Home Assistant Assist voice pipeline → Music Assistant has [native voice support](https://github.com/music-assistant/voice-support)
- You need advanced Spotify API features → Use SpotifyPlus

**Use both together:** Many users run Music Assistant for UI/management and this integration for voice control via custom conversation agents.

> **⚠️ Important:** This integration provides the search functionality - your conversation agent's LLM model and hardware determine the actual voice command accuracy and response time. For local voice pipelines, qwen3:4b is a pretty good starting point. See [Performance](#performance) for optimization guidance.

## The Problem

Want to control Spotify with your voice in Home Assistant? You'll quickly hit these issues:

- **Spotcast** requires cookie authentication (`sp_dc`, `sp_key`) which breaks frequently with "serverTime" errors
- **Music Assistant** is a full-featured music server - excellent for complete music management, but requires running a separate server and aggregates multiple providers
- **SpotifyPlus** is feature-rich but complex to set up for simple voice commands
- **Custom Sentences** require rigid YAML patterns - "Play {artist} on {speaker}" instead of natural language
- **Built-in Spotify integration** has no search service for voice assistants to use
- **Standard Spotify search returns wrong artists** - Personalized recommendations instead of exact matches (ask for Coldplay, get Taylor Swift)

## The Solution

A lightweight integration designed specifically for voice assistants with function calling:

✅ **Direct Spotify Connect integration** - No music server required, uses Home Assistant's official Spotify integration
✅ **Natural language from day one** - "Play Coldplay" not "play artist equals Coldplay"
✅ **Zero additional authentication** - Reuses your existing Home Assistant Spotify OAuth
✅ **Exact match artist search** - Finds Coldplay when you ask for Coldplay, not recommendations
✅ **Works with any Spotify Connect device** - WiiM, Sonos, Google Cast, Echo, whatever you have
✅ **Under 120 lines of code** - Simple, maintainable, easy to understand
✅ **Voice assistant ready** - Complete conversation agent examples included

## Comparison with Alternatives

| Feature | Spotify Voice Assistant | Spotcast | Music Assistant | SpotifyPlus |
|---------|------------------------|----------|-----------------|-------------|
| **Primary Focus** | Voice search for conversation agents | Casting | Complete music server | Spotify API wrapper |
| **Architecture** | Direct Spotify Connect | Spotify API | Music server (aggregates providers) | Spotify API |
| **Lines of Code** | <120 | 1000+ | 10,000+ | 5000+ |
| **Authentication** | Reuses HA OAuth | Cookies (breaks often) | Own server auth | Own OAuth flow |
| **Setup Complexity** | 1 YAML line | Cookies + config | Full server install | Complex config |
| **Exact Artist Match** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| **Voice Support** | ✅ Function calling | ⚠️ Manual scripts | ✅ HA Assist integration | ⚠️ Manual scripts |
| **Natural Language** | ✅ Via conversation agent | ❌ Rigid patterns | ✅ Via HA Assist | ❌ Manual calls |
| **External Dependencies** | None | None | Separate server | None |
| **Hardware Support** | Any Spotify Connect | Chromecast focused | Universal | Any Spotify Connect |

## Features

- ✅ **Voice-first design** - Built for natural language from day one
- ✅ **Hardware agnostic** - Works with any Spotify Connect device
- ✅ **Search by type** - Artists, albums, tracks, playlists
- ✅ **Exact match preference** - Finds what you ask for, not recommendations
- ✅ **Complete examples** - Extended OpenAI Conversation config included
- ✅ **Playback control** - Pause, play, skip, volume, shuffle - all via voice
- ✅ **Artist radio mode** - Automatically shuffles when playing artists for dynamic playlists
- ✅ **Zero config authentication** - Leverages existing Spotify integration
- ✅ **Detailed logging** - Debug mode shows exactly what's happening
- ✅ **Service response support** - Returns data to automations/scripts

## Quick Start

Say goodbye to complex configurations. Get voice-controlled music in 3 steps:

### 1. Install Prerequisites

- **Spotify Premium account** (required for Spotify Connect)
- **[Official Spotify integration](https://www.home-assistant.io/integrations/spotify/)** configured in Home Assistant
- **[Extended OpenAI Conversation](https://github.com/jekalmin/extended_openai_conversation)** (or another LLM conversation agent)
- **At least one Spotify Connect device** (see [Compatible Speakers](#compatible-speakers))

### 2. Install This Integration

**Via HACS (Recommended):**
1. HACS > Integrations > ⋮ (menu) > Custom repositories
2. Add: `https://github.com/cauld/spotify-voice-assistant`
3. Category: Integration
4. Install "Spotify Voice Assistant"
5. Restart Home Assistant

**Manual Installation:**
1. Download this repository
2. Copy `custom_components/spotify_search` to your HA `custom_components` folder
3. Restart Home Assistant

Add to `configuration.yaml`:
```yaml
spotify_search:
```

### 3. Configure Extended OpenAI Conversation

Copy these functions to Extended OpenAI Conversation settings:

<details>
<summary>Click to expand function configuration</summary>

```yaml
- spec:
    name: search_spotify
    description: Search Spotify for an artist, album, or track and return the Spotify URI. Use this before playing music to get the URI.
    parameters:
      type: object
      properties:
        query:
          type: string
          description: Artist, album, or track name to search for (e.g., "Coldplay", "Parachutes", "Yellow")
        type:
          type: string
          enum: [artist, album, track]
          description: Type of content to search for
      required:
        - query
        - type
  function:
    type: script
    sequence:
      - service: spotify_search.search
        response_variable: _function_result
        data:
          query: "{{ query }}"
          type: "{{ type }}"

- spec:
    name: play_music
    description: Play music on a Spotify Connect device using a Spotify URI. You must first call search_spotify to get the URI.
    parameters:
      type: object
      properties:
        spotify_uri:
          type: string
          description: Spotify URI from search_spotify (e.g., "spotify:artist:4gzpq5DPGxSnKTe4SA8HAU")
        media_player:
          type: string
          description: Entity ID of Spotify Connect media player (e.g., "media_player.kitchen_speaker")
      required:
        - spotify_uri
        - media_player
  function:
    type: script
    sequence:
      - service: media_player.play_media
        target:
          entity_id: "{{ media_player }}"
        data:
          media_content_id: "{{ spotify_uri }}"
          media_content_type: "music"

- spec:
    name: control_playback
    description: Control music playback (pause, resume, stop, next track, previous track, set volume, shuffle)
    parameters:
      type: object
      properties:
        action:
          type: string
          enum: [pause, play, stop, next_track, previous_track, volume_set, shuffle_on, shuffle_off]
          description: Playback control action
        media_player:
          type: string
          description: Entity ID of media player
        volume_level:
          type: number
          description: Volume level (0-100) for volume_set action only
      required:
        - action
        - media_player
  function:
    type: script
    sequence:
      - if: "{{ action == 'pause' }}"
        then:
          - service: media_player.media_pause
            target:
              entity_id: "{{ media_player }}"
      - if: "{{ action == 'play' }}"
        then:
          - service: media_player.media_play
            target:
              entity_id: "{{ media_player }}"
      - if: "{{ action == 'stop' }}"
        then:
          - service: media_player.media_stop
            target:
              entity_id: "{{ media_player }}"
      - if: "{{ action == 'next_track' }}"
        then:
          - service: media_player.media_next_track
            target:
              entity_id: "{{ media_player }}"
      - if: "{{ action == 'previous_track' }}"
        then:
          - service: media_player.media_previous_track
            target:
              entity_id: "{{ media_player }}"
      - if: "{{ action == 'volume_set' }}"
        then:
          - service: media_player.volume_set
            target:
              entity_id: "{{ media_player }}"
            data:
              volume_level: "{{ volume_level / 100 }}"
      - if: "{{ action == 'shuffle_on' }}"
        then:
          - service: media_player.shuffle_set
            target:
              entity_id: "{{ media_player }}"
            data:
              shuffle: true
      - if: "{{ action == 'shuffle_off' }}"
        then:
          - service: media_player.shuffle_set
            target:
              entity_id: "{{ media_player }}"
            data:
              shuffle: false
```
</details>

Add this to your Extended OpenAI Conversation system prompt:

```
Music Playback:
- When asked to play music, follow this two-step process: 1) Call search_spotify to get the Spotify URI, 2) Call play_music with the URI and media player entity
- Available media players: media_player.kitchen_speaker, media_player.gaming_room_speaker, media_player.office_speaker
- Default speaker: If no speaker is specified, use media_player.kitchen_speaker
- Parse commands like "Play {Artist/Album/Track}" and determine the media type automatically
- IMPORTANT: When playing an artist, always enable shuffle after starting playback by calling control_playback with action: shuffle_on to create a dynamic playlist experience
- For playback control (pause, skip, volume, shuffle), use the control_playback function
```

**Customization tips:**
- **Entity IDs are descriptive** (like `media_player.kitchen_speaker`): Just list the entity IDs as shown above
- **Entity IDs are cryptic** (like `media_player.wiim_12345`): Include friendly names for better LLM understanding:
  ```
  - Available speakers: Kitchen Speaker (media_player.wiim_12345), Gaming Room (media_player.sonos_abc), Office (media_player.cast_xyz)
  ```
- **Default speaker:** Change `media_player.kitchen_speaker` to your preferred default location

### Done! Try It

**Standard Patterns (like intent-based systems):**
- "Play Coldplay on the kitchen speaker"
- "Play the album Parachutes"
- "Play Yellow by Coldplay"
- "Pause the music"
- "Skip to the next track"
- "Set volume to 50%"
- "Shuffle on"

**Natural Language (LLM advantage):**
- "I'm in the mood for some Coldplay"
- "Put on that song Yellow"
- "Start playing Coldplay" (uses default speaker from prompt, automatically shuffles artist)
- "Can you play the Parachutes album?"
- "Play me something by Coldplay"
- "I want to hear some chill music from Coldplay"
- "Play Coldplay but shuffle it"
- "Put on some music from that British band with Chris Martin"

**Conversational Playback Control:**
- "Make it louder" (instead of "Set volume to 70")
- "Turn it down a bit" (instead of "Set volume to 30")
- "Next song please" (instead of "Skip to next track")
- "Stop the music" (instead of "Pause playback")
- "Shuffle this" (instead of "Set shuffle to on")

> **Note:** When no speaker is specified, the LLM will use the default media player defined in your Extended OpenAI Conversation prompt. Add instructions like "If no speaker specified, use media_player.kitchen_speaker" to your system prompt.

## Why Natural Language Matters

Traditional voice assistants require specific sentence patterns:
```
Intent Pattern: "Play [artist] on [speaker]"
✅ Works: "Play Coldplay on kitchen speaker"
❌ Fails: "I want to listen to Coldplay"
❌ Fails: "Put on some Coldplay"
❌ Fails: "Start playing Coldplay in the kitchen"
```

This integration uses LLM-based function calling to understand conversational requests:
```
LLM Understanding: Extracts intent from natural speech
✅ Works: "Play Coldplay on kitchen speaker"
✅ Works: "I want to listen to Coldplay"
✅ Works: "Put on some Coldplay"
✅ Works: "Start playing Coldplay in the kitchen"
✅ Works: "Play me that British band with Chris Martin"
```

The LLM understands **what you mean**, not just **what you say**.

## Compatible Speakers

This integration works with **any Spotify Connect-compatible device**:

### Tested & Verified
- **WiiM Audio Pro** (and all WiiM speakers)
- **Sonos speakers** (all models with Spotify)
- **Google Nest/Home speakers**
- **Amazon Echo with Spotify**

### Should Work (Spotify Connect Compatible)
- **Smart Speakers:**
  - Apple HomePod (with Spotify app)
  - Bose Home Speaker series
  - JBL Link series
  - Harman Kardon Citation series
  - Bang & Olufsen Beosound series

- **Streaming Devices:**
  - Chromecast Audio
  - Roku with Spotify channel
  - Fire TV with Spotify
  - Apple TV with Spotify app

- **AV Receivers:**
  - Denon HEOS-enabled receivers
  - Yamaha MusicCast receivers
  - Marantz NR/SR series
  - Pioneer VSX series with Spotify

- **DIY Solutions:**
  - Raspberry Pi with [Raspotify](https://github.com/dtcooper/raspotify)
  - Raspberry Pi with [Spotifyd](https://github.com/Spotifyd/spotifyd)
  - Any Linux/Mac/Windows computer running Spotify

- **Mobile Devices:**
  - Phones/tablets running Spotify app (for testing)

### Requirements
- **Spotify Premium account** (Spotify Connect requires Premium)
- **Device must show up in Home Assistant** as a `media_player` entity
- **Device must support Spotify Connect** (check manufacturer specs)

**Note:** If your device runs Spotify and shows up in Home Assistant's integrations, it will work with this integration.

## Works Alongside Music Assistant

Music Assistant and this integration serve different purposes and work well together:

### Music Assistant
- **Purpose:** Full-featured music server with rich UI, multi-room audio, queue management
- **Architecture:** Music server that aggregates multiple providers (Spotify, local files, streaming services)
- **Voice support:** [Built-in voice integration](https://github.com/music-assistant/voice-support) works with Home Assistant Assist (with or without LLM enhancement)
- **Best for:** Complete music management solution with visual control

### This Integration (Spotify Voice Assistant)
- **Purpose:** Lightweight Spotify search service for conversation agents with function calling support
- **Architecture:** Direct Spotify Connect integration via Home Assistant's official Spotify integration (no music server required)
- **Works with:** Any conversation agent that supports function calling (Extended OpenAI Conversation, OpenAI Conversation, Google Generative AI Conversation, etc.)
- **Best for:** Adding Spotify voice control without running a full music server

### Using Both Together

Many users run both simultaneously:
- **Music Assistant:** Provides UI for manual control, queue management, and automations (skip voice setup)
- **This integration:** Handles voice control via custom conversation agents
- **They work together:** Music started via voice appears in Music Assistant UI and remains fully controllable there

**Example workflow:** Say "Play Coldplay on office speaker" → music starts → open Music Assistant UI → see what's playing, adjust volume, skip tracks, manage queue.

They don't directly integrate but work together because both control the same Spotify Connect devices independently.

### Choose Your Setup

- **Voice only:** Use this integration alone
- **Voice + rich UI:** Use both (Music Assistant without voice + this integration)
- **Home Assistant Assist voice:** Use Music Assistant's [built-in voice support](https://github.com/music-assistant/voice-support)
- **Custom conversation agent voice:** Use this integration

## How It Works

### The Two-Step Process

**1. Search Spotify**
```
You: "Play Coldplay"
LLM: Calls search_spotify(query="Coldplay", type="artist")
Response: {"uri": "spotify:artist:4gzpq5DPGxSnKTe4SA8HAU", "name": "Coldplay"}
```

**2. Play on Device**
```
LLM: Calls play_music(uri="spotify:artist:...", media_player="media_player.kitchen_speaker")
Result: Music starts playing
```

### Exact Match Artist Search

When searching for artists, this integration uses smart matching to avoid Spotify's personalization issues:

1. Queries Spotify for top 10 artist results
2. Checks each result for exact name match (case-insensitive)
3. Returns exact match if found, otherwise returns first result
4. Logs match type (exact/first) for debugging

**Why this matters:** Standard Spotify search prioritizes personalized recommendations. If you search "Coldplay," you might get Taylor Swift if you listen to her frequently. Our exact matching ensures you get Coldplay when you ask for Coldplay.

### No Additional Authentication

The integration leverages Home Assistant's official Spotify integration:
- Uses existing OAuth tokens
- No cookies to manage (`sp_dc`, `sp_key`)
- No tokens to refresh
- Works as long as your Spotify integration works

### Performance Optimization

The integration includes smart caching for optimal performance:

**First search:** ~1.6-5.6ms (finds and caches Spotify client)
**Subsequent searches:** ~0.1ms (uses cached client)
**Performance gain:** 15-50x faster on repeated searches

**Cache Features:**
- Automatically validates cached client on every call
- Self-invalidates when Spotify integration is reloaded or removed
- Manual cache clearing available via `spotify_search.clear_cache` service

The cache is module-level and process-scoped, so it clears automatically on Home Assistant restart.

## Advanced Usage

### Developer Tools Testing

Test the search service directly:

```yaml
service: spotify_search.search
data:
  query: "Coldplay"
  type: "artist"
```

Response:
```json
{
  "uri": "spotify:artist:4gzpq5DPGxSnKTe4SA8HAU",
  "name": "Coldplay",
  "type": "artist"
}
```

### Use in Automations

```yaml
automation:
  - alias: "Morning Music"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: spotify_search.search
        response_variable: artist_result
        data:
          query: "Chillhop Music"
          type: "artist"
      - service: media_player.play_media
        target:
          entity_id: media_player.kitchen_speaker
        data:
          media_content_id: "{{ artist_result.uri }}"
          media_content_type: "music"
```

### Prompt Optimization for Multi-part Queries

For better accuracy when users provide both song/album AND artist names, enhance your Extended OpenAI Conversation system prompt to combine search terms:

```
Music Query Optimization:
- When user provides both song/album AND artist, combine them into the search query
- Example: "Play Yellow by Coldplay" → search_spotify(query="Yellow Coldplay", type="track")
- Example: "Play Parachutes album by Coldplay" → search_spotify(query="Parachutes Coldplay", type="album")
- The combined query improves search accuracy by providing more context to Spotify
```

This approach leverages Spotify's search algorithm to naturally weight both terms, improving accuracy when multiple artists have songs/albums with the same name.

### Clear Cache Service

If you experience issues after removing or re-adding the Spotify integration, you can manually clear the cached client:

```yaml
service: spotify_search.clear_cache
```

The cache automatically invalidates when the Spotify integration is reloaded, so manual clearing is rarely needed.

### Debug Logging

Enable detailed logging in `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.spotify_search: debug
```

This shows search queries, match types (exact vs. first result), and any errors.

## Troubleshooting

### "No Spotify media player entity found"

**Cause:** Official Spotify integration not configured.

**Solution:**
1. Settings > Integrations > Add Integration
2. Search for "Spotify"
3. Complete OAuth authentication
4. Verify `media_player.spotify_*` entity appears
5. Restart Home Assistant

### "Spotify entity does not have a coordinator"

**Cause:** Spotify integration hasn't fully initialized.

**Solution:** Wait 30 seconds after HA starts, or restart Home Assistant.

### Voice commands not working

**Cause:** Extended OpenAI Conversation functions not configured.

**Solution:**
1. Verify functions are added to Extended OpenAI settings
2. Check system prompt includes music playback instructions
3. Test search service manually in Developer Tools
4. Check Home Assistant logs for errors

### Wrong artist/song playing

**Cause:** Exact match not found in top 10 results.

**Solution:**
- Use more specific query: "Coldplay band" instead of just "Coldplay"
- Check search result in Developer Tools first
- Try searching by track or album if artist search fails

### Music won't play on speaker

**Cause:** Device not Spotify Connect compatible or not in HA.

**Solution:**
1. Verify device supports Spotify Connect (check manufacturer site)
2. Check device shows in Settings > Integrations
3. Test playing Spotify directly to device from Spotify app
4. Verify Spotify Premium account is active

## Performance

The integration itself is highly optimized with client caching (15-50x faster after first search). However, overall voice command response time is dominated by your conversation agent's LLM processing.

### Response Time Breakdown

Typical "Play Coldplay" command:
- **Spotify search:** ~500ms first time, ~10ms cached ✅ Fast
- **LLM processing:** 2-10+ seconds per function call ⚠️ Bottleneck
- **Total:** Depends almost entirely on your LLM

### Optimization Tips

**1. Choose a faster LLM**
- **Slow (2-5 min):** Large models on CPU (qwen3:8b, llama3:8b)
- **Medium (5-15 sec):** Small local models (qwen3:1.8b, phi3:mini)
- **Fast (2-5 sec):** Cloud APIs (OpenAI GPT-4o-mini, Anthropic Claude Haiku)

**2. Reduce exposed devices**

Each device in your conversation agent adds tokens to every LLM call, slowing processing:
- **38 devices:** ~1,600 tokens = slower responses
- **25 devices:** ~1,000 tokens = 20-30% faster

**Safe to remove from Extended OpenAI Conversation:**
- Voice satellite media players (if not directly controlled)
- Unavailable/unused devices
- Status sensors not needed for voice commands

**3. Enable GPU acceleration**

If using Ollama locally, GPU acceleration provides 5-10x speedup over CPU.

### Expected Performance

| Configuration | Response Time |
|---------------|---------------|
| Cloud API (GPT-4o-mini) + 25 devices | 2-5 seconds ✅ |
| Local GPU (qwen3:8b) + 25 devices | 10-30 seconds |
| Local CPU (qwen3:8b) + 38 devices | 2-5 minutes ❌ |

**Bottom line:** This integration adds <1 second overhead. LLM choice determines user experience.

## Roadmap

See [TODO.md](TODO.md) for detailed enhancement proposals and implementation plans.

## Contributing

Contributions welcome! Please submit a Pull Request.

## Support

- **Issues:** [GitHub Issues](https://github.com/cauld/spotify-voice-assistant/issues)
- **Discussions:** [Home Assistant Community](https://community.home-assistant.io/)

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built on [Home Assistant Spotify integration](https://www.home-assistant.io/integrations/spotify/)
- Designed for [Extended OpenAI Conversation](https://github.com/jekalmin/extended_openai_conversation)
- Inspired by the HA community's need for simple voice-controlled music
