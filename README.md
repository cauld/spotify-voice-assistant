<div align="center" style="background-color: rgb(35, 35, 37);">
  <img src="images/banner.png" alt="Spotify Voice Assistant Banner" width="100%">
</div>

# Spotify Voice Assistant (SVA) for Home Assistant

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

**Consider alternatives if:**
- You need multi-provider music aggregation (Spotify + local files + streaming services) → Use Music Assistant
- You want rich UI-based queue management and multi-room features → Use Music Assistant
- You use Home Assistant Assist voice pipeline → Music Assistant has [native voice support](https://github.com/music-assistant/voice-support)
- You need advanced Spotify API features → Use SpotifyPlus

> **Important:** This integration provides the search functionality - your conversation agent's LLM model and hardware determine the actual voice command accuracy and response time. For local voice pipelines, qwen3:4b is a good starting point. See [Performance](#performance) for optimization guidance.

## Key Features

- **Natural language voice control** - "Play Coldplay" not "play artist equals Coldplay"
- **Zero additional authentication** - Reuses your existing Home Assistant Spotify OAuth
- **Exact match search** - Finds Coldplay when you ask for Coldplay, not recommendations
- **Works with any Spotify Connect device** - WiiM, Sonos, Google Cast, Echo, whatever you have
- **Lightweight and simple** - Direct Spotify Connect integration, no music server required
- **Complete examples included** - Function calling config for Extended OpenAI Conversation

## Comparison with Alternatives

| Feature | Spotify Voice Assistant | Spotcast | Music Assistant | SpotifyPlus |
|---------|------------------------|----------|-----------------|-------------|
| **Primary Focus** | Voice search for conversation agents | Casting | Complete music server | Spotify API wrapper |
| **Architecture** | Direct Spotify Connect | Spotify API | Music server (aggregates providers) | Spotify API |
| **Complexity** | Minimal | Moderate | High | High |
| **Authentication** | Reuses HA OAuth | Cookies (breaks often) | Own server auth | Own OAuth flow |
| **Setup Complexity** | 1 YAML line | Cookies + config | Full server install | Complex config |
| **Exact Artist Match** | Yes | No | Yes | Yes |
| **Voice Support** | Function calling | Manual scripts | HA Assist integration | Manual scripts |
| **Natural Language** | Via conversation agent | Rigid patterns | Via HA Assist | Manual calls |
| **External Dependencies** | None | None | Separate server | None |
| **Hardware Support** | Any Spotify Connect | Chromecast focused | Universal | Any Spotify Connect |

## Features

- **Voice-first design** - Built for natural language from day one
- **Hardware agnostic** - Works with any Spotify Connect device
- **Search by type** - Artists, albums, tracks, and playlists
- **Exact match preference** - Finds what you ask for across all content types, not recommendations
- **Smart playlist search** - Checks your personal playlists first, then falls back to public Spotify playlists
- **Complete examples** - Extended OpenAI Conversation config included
- **Playback control** - Pause, play, skip, volume, shuffle - all via voice
- **Play and queue modes** - Replace current playback or add to queue seamlessly
- **Artist radio mode** - Automatically shuffles when playing artists for dynamic playlists
- **Zero config authentication** - Leverages existing Spotify integration
- **Detailed logging** - Debug mode shows exactly what's happening
- **Service response support** - Returns data to automations/scripts

## Quick Start

Say goodbye to complex configurations. Get voice-controlled music in 3 steps:

### 1. Install Prerequisites

- **Spotify Premium account** (required for Spotify Connect)
- **[Official Spotify integration](https://www.home-assistant.io/integrations/spotify/)** configured in Home Assistant
- **[Extended OpenAI Conversation](https://github.com/jekalmin/extended_openai_conversation)** (or another LLM conversation agent)
- **At least one Spotify Connect device** (see [Compatible Speakers](#compatible-speakers))

### 2. Install This Integration

**Via HACS (Recommended):**

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Chad+Auld&repository=https%3A%2F%2Fgithub.com%2Fcauld%2Fspotify-voice-assistant&category=integration)

Or manually:
1. HACS > Integrations > ⋮ (menu) > Custom repositories
2. Add: `https://github.com/cauld/spotify-voice-assistant`
3. Category: Integration
4. Install "Spotify Voice Assistant"
5. Restart Home Assistant

**Manual Installation:**
1. Download this repository
2. Copy `custom_components/spotify_voice_assistant` to your HA `custom_components` folder
3. Restart Home Assistant

Add to `configuration.yaml`:
```yaml
spotify_voice_assistant:
```

### 3. Configure Extended OpenAI Conversation

**Add Functions:**

Copy the function configuration from [`examples/extended_openai_functions.yaml`](examples/extended_openai_functions.yaml) to your Extended OpenAI Conversation settings.

This includes:
- `search_spotify` - Search for music and get Spotify URIs
- `play_music` - Play music immediately (replaces current playback)
- `queue_music` - Add music to queue (doesn't interrupt playback)
- `control_playback` - Pause, play, skip, volume, shuffle controls

**Add System Prompt:**

Copy the music playback rules from [`examples/system_prompt.txt`](examples/system_prompt.txt) to your Extended OpenAI Conversation system prompt.

Key behaviors configured:
- Play vs Queue command detection
- Automatic query cleaning (strips "play", "queue", location words)
- Smart type detection (artist/album/track/playlist)
- No confirmation prompts for immediate playback

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
- "Play the song Dark Side of the Moon by Pink Floyd"
- "Play Today's Top Hits"
- "Play my workout playlist"
- "Queue Wish You Were Here"
- "Add the album Dark Side of the Moon to queue"
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
- "Play my chill vibes playlist"
- "Put on my running music"
- "Queue up some Pink Floyd for later"
- "Add Comfortably Numb to the queue"

**Conversational Playback Control:**
- "Make it louder" (instead of "Set volume to 70")
- "Turn it down a bit" (instead of "Set volume to 30")
- "Next song please" (instead of "Skip to next track")
- "Stop the music" (instead of "Pause playback")
- "Shuffle this" (instead of "Set shuffle to on")

> **Note:** When no speaker is specified, the LLM will use the default media player defined in your Extended OpenAI Conversation prompt. Add instructions like "If no speaker specified, use media_player.kitchen_speaker" to your system prompt.

## Why Natural Language Matters

Traditional voice assistants require exact patterns like "Play [artist] on [speaker]". LLM-based function calling understands conversational requests: "I want to listen to Coldplay", "Put on some Coldplay", or even "Play me that British band with Chris Martin" all work naturally.

## Compatible Speakers

Works with **any Spotify Connect-compatible device** that appears in Home Assistant as a `media_player` entity.

**Requirements:**
- Spotify Premium account (required for Spotify Connect)
- Device appears in Home Assistant's Spotify integration
- Device supports Spotify Connect

**Tested devices:** WiiM speakers, Sonos, Google Nest/Home, Amazon Echo

**Should work:** Any smart speaker, AV receiver, streaming device, or computer with Spotify Connect support. This includes HomePod, Chromecast, Fire TV, Raspberry Pi with [Raspotify](https://github.com/dtcooper/raspotify), and more.


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

### Exact Match Search

This integration uses smart matching across all content types to avoid Spotify's personalization issues:

1. Queries Spotify for top 10 results (instead of just 1)
2. Checks each result for exact name match (case-insensitive)
3. Returns exact match if found, otherwise returns first result
4. Logs match type (exact/first/partial) for debugging

**Applies to:** Artists, albums, tracks, and playlists

**Why this matters:** Standard Spotify search prioritizes personalized recommendations. If you search "Coldplay," you might get Taylor Swift if you listen to her frequently. Our exact matching ensures you get Coldplay when you ask for Coldplay.

### Smart Playlist Search

Playlist searches automatically check your personal playlists first, then fall back to public Spotify playlists:

1. Cleans the query (removes "playlist" and "playlists" from search terms)
2. Searches your saved Spotify playlists for exact match
3. If no exact match, searches your playlists for partial match
4. If still not found, searches public Spotify playlists
5. Returns exact match from public results if found, otherwise first result

**Examples:**
- "Play my workout playlist" → Checks your saved playlists first
- "Play vibes" → Finds your "Vibes" playlist if you have one, otherwise searches public playlists
- "Play Today's Top Hits" → Checks your playlists first, then finds public playlist

### No Additional Authentication

The integration leverages Home Assistant's official Spotify integration:
- Uses existing OAuth tokens
- No cookies to manage (`sp_dc`, `sp_key`)
- No tokens to refresh
- Works as long as your Spotify integration works

### Performance Optimization

The integration uses smart caching to speed up repeated searches. The Spotify client and user playlists are cached automatically. Cache clears on Home Assistant restart or can be cleared manually via the `spotify_voice_assistant.clear_cache` service.

## Advanced Usage

### Search Types

The integration supports five search types:

| Type | Description | Example Query | Use Case |
|------|-------------|---------------|----------|
| `artist` | Search all Spotify artists | "Coldplay" | Play an artist's music |
| `album` | Search all Spotify albums | "Parachutes" | Play a specific album |
| `track` | Search all Spotify tracks | "Yellow" | Play a specific song |
| `playlist` | Search all public Spotify playlists | "Today's Top Hits" | Play curated or public playlists |
| `user_playlist` | Search only your saved playlists | "workout" | Play your personal playlists |

**Key difference:**
- `playlist` - Searches all of Spotify's public playlists
- `user_playlist` - Searches only playlists you've saved/created

### Developer Tools Testing

Test the search service directly:

```yaml
service: spotify_voice_assistant.search
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

Test user playlist search:

```yaml
service: spotify_voice_assistant.search
data:
  query: "workout"
  type: "user_playlist"
```

Response:
```json
{
  "uri": "spotify:playlist:37i9dQZF1DX76Wlfdnj7AP",
  "name": "Workout Beats",
  "type": "playlist"
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
      - service: spotify_voice_assistant.search
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

### Clear Cache Service

If you experience issues or want to refresh cached data (e.g., after adding new playlists to your Spotify library), you can manually clear the cache:

```yaml
service: spotify_voice_assistant.clear_cache
```

This clears:
- Cached Spotify client reference
- Cached user playlist data

**When to use:**
- After adding/removing playlists in Spotify (to refresh user_playlist searches)
- After removing or re-adding the Spotify integration
- If experiencing unexpected search results

The cache automatically invalidates when the Spotify integration is reloaded, so manual clearing is rarely needed.

### Debug Logging

Enable detailed logging in `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.spotify_voice_assistant: debug
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
- **Medium (5-15 sec):** Small local models (qwen3:4b, qwen3:1.8b)
- **Fast (2-5 sec):** Cloud APIs (OpenAI GPT-4o-mini, Anthropic Claude Haiku)

**2. Reduce exposed devices**

Avoid exposing unnecessary devices to your voice assistant. Each device in your conversation agent adds tokens to every LLM call, slowing processing:
- **38 devices:** ~1,600 tokens = slower responses
- **25 devices:** ~1,000 tokens = 20-30% faster

**Safe to remove from Extended OpenAI Conversation:**
- Voice satellite media players (if not directly controlled)
- Unavailable/unused devices
- Status sensors not needed for voice commands

**3. Enable GPU acceleration**

If using Ollama locally, GPU acceleration provides 5-10x speedup over CPU.
If using Docker, remember, [GPU support isn't enabled by default](https://docs.docker.com/compose/how-tos/gpu-support/).

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
