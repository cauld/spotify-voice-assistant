# TODO

Development roadmap and future enhancements for Spotify Voice Assistant.

**Current Version:** v1.0.0

## Completed in v1.0.0

- Exact match search for all content types (artists, albums, tracks, playlists)
- Smart playlist search (user playlists first, then public)
- Queue functionality (play vs queue modes)
- Shuffle controls
- Performance caching (Spotify client + user playlists)
- Clear cache service
- Comprehensive test cases

---

## Future Enhancements

### 1. Podcast Support

Add support for searching and playing podcasts and podcast episodes.

**Current limitation:**
- Integration only supports music content (artists, albums, tracks, playlists)

**Proposed:**
- Add `type="podcast"` for searching podcasts (shows)
- Add `type="episode"` for searching specific podcast episodes
- Support "Play the latest episode of [podcast name]"
- Support "Play [episode name] from [podcast name]"

**Implementation:**
- Use Spotify API search types: `show` and `episode`
- Consider caching user's saved/followed podcasts
- Handle episode-specific logic (latest vs specific episode)
- Update Extended OpenAI function definitions
- Update system prompts with podcast examples
- Add podcast test cases to TEST_CASES.md

**API endpoints:**
- `client.search(query, ["show"])` for podcast search
- `client.search(query, ["episode"])` for episode search
- `client.get_show_episodes(show_id)` for getting episodes

---

### 2. Saved Content Quick Access

Extend saved/favorite content search beyond playlists.

**Currently supported:**
- User playlists via `type="playlist"` (searches user first, then public)

**Proposed additions:**
- `type="saved_tracks"` for liked songs
- `type="saved_albums"` for saved albums
- `type="followed_artists"` for followed artists

**Benefits:**
- "Play from my liked songs"
- "Play from my saved albums"
- Faster access to frequently played content

**Implementation:**
- Use Spotify API: `get_saved_tracks()`, `get_saved_albums()`, `get_followed_artists()`
- Handle pagination for large libraries
- Apply similar caching strategy as user playlists
- Add search/filter capabilities within saved content

---

### 3. Configuration Options

Allow users to configure integration behavior via YAML or UI.

**Proposed options:**
- Number of results to check for exact match (currently hardcoded to 10)
- Cache duration/invalidation behavior
- Default search type when ambiguous
- Logging verbosity level
- Whether to require exact match or allow fuzzy matching

**Implementation:**
- Add config flow for UI-based configuration
- Support YAML configuration in `configuration.yaml`
- Ensure sensible defaults
- Document all options in README

---

### 4. Artist Filter Parameter

Add optional artist parameter for more precise filtering.

**Current approach:**
- LLM strips artist from query per system prompt
- Relies on Spotify's search ranking

**Proposed:**
- Add optional `artist` parameter to `search_spotify` service
- Example: `search_spotify(query="Yellow", type="track", artist="Coldplay")`

**Benefits:**
- More precise matching for common track names (e.g., "Hurt" by NIN vs Johnny Cash)
- Explicit filtering vs relying on search ranking

**Trade-offs:**
- Requires LLM to extract both query and artist separately
- May reduce natural language flexibility
- Current approach works well for most cases

**Implementation:**
- Update `services.yaml` to add optional `artist` parameter
- Apply artist filtering in `__init__.py`
- Update Extended OpenAI function definition
- Maintain backward compatibility

---

### 5. HA Assist Integration

Make integration work with Home Assistant's built-in voice pipeline without requiring Extended OpenAI Conversation.

**Current limitation:**
- Requires Extended OpenAI Conversation (or similar) for function calling

**Proposed:**
- Register as native Home Assistant intent/sentence pattern
- Work directly with Assist voice pipeline

**Trade-offs:**
- Would likely require rigid intent patterns ("Play [artist] on [device]")
- Less flexible than LLM-based approach
- May lose natural language advantage
- Music Assistant already provides this via their voice support

**Consider:**
- Whether this adds value given Music Assistant's HA Assist integration
- Could maintain both approaches (function calling + intent patterns)

---

### 6. Multi-room/Group Playback

Add support for playing on speaker groups or multiple devices simultaneously.

**Current behavior:**
- Plays on single device specified in command

**Proposed:**
- Support speaker groups defined in Home Assistant
- "Play Coldplay on all speakers"
- "Play Coldplay in the downstairs"

**Implementation:**
- Detect speaker groups from media_player entities
- Update LLM prompt to understand group concepts
- Test with various Spotify Connect group configurations

---

### 7. Playback Context Awareness

Add awareness of what's currently playing for smarter commands.

**Examples:**
- "Play more like this" - queue similar artists/tracks
- "Who is this?" - return current track/artist info
- "Add this to my workout playlist" - save current track

**Implementation:**
- Query current playback state from Spotify integration
- Add new service calls for context-aware operations
- Update LLM functions with current playback info

---

## Non-Goals

Things we explicitly won't implement:

1. **Advanced Spotify API features** - Use SpotifyPlus for this
2. **Multi-provider music aggregation** - Use Music Assistant for this
3. **Rich UI/queue management** - Use Music Assistant for this
4. **Cookie-based authentication** - Sticking with OAuth via HA's Spotify integration

---

## Contributing

Have ideas for enhancements? Open an issue or submit a PR on GitHub.
