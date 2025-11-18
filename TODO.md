# TODO

Development roadmap and enhancement proposals for Spotify Voice Assistant.

## Future Enhancements

### 1. Artist Filter Parameter
Add optional artist filter parameter to improve multi-part query accuracy.

**Current approach (v1.0.0):**
- Combine artist and song into query string: "Yellow Coldplay"
- Relies on Spotify's search ranking algorithm
- Works well via LLM prompt enhancement

**Proposed enhancement:**
- Add `artist` parameter to `search_spotify` service
- Apply artist filtering to search results
- Example: `search_spotify(query="Yellow", type="track", artist="Coldplay")`

**Benefits:**
- More precise matching when multiple artists have songs with same name (e.g., "Hurt" by Nine Inch Nails vs Johnny Cash)
- Explicit artist filtering vs relying on search ranking
- Better handling of edge cases

**Implementation notes:**
- Update `services.yaml` to add `artist` parameter (optional)
- Update `search_spotify` function in `__init__.py` to apply artist filtering
- Update function definition in Extended OpenAI Conversation
- Consider backward compatibility - make parameter optional
- Update documentation and examples

**Trade-offs:**
- Requires more specific parameter extraction from LLM
- May reduce flexibility of natural language queries
- Current combined query approach already works well for most cases

---

### 2. ~~Extend Exact Name Matching to Albums and Tracks~~ ✅ COMPLETED (v1.0.0)
~~Apply the same "exact match" logic currently used for artists to albums and tracks.~~

**Status:** Implemented in v1.0.0
- All search types (artist, album, track, playlist) now use exact name matching
- Searches use limit=10 and check for exact matches before falling back to first result
- Consistent behavior across all content types
- Logs indicate match type (exact/first/partial) for debugging

**Also implemented:**
- Playlist exact matching with same logic
- User playlist search with exact and partial matching
- Caching for user playlists to improve performance

---

### 3. Configuration Options
Allow users to configure integration behavior via Home Assistant UI or YAML.

**Proposed configurable options:**
- Number of results to check for exact match (currently hardcoded to 10)
- Whether to require exact match or allow fuzzy matching
- Default search type (artist/album/track) when not specified
- Cache duration/behavior
- Logging verbosity

**Current behavior:**
- All behavior is hardcoded in the integration

**Benefits:**
- Users can tune behavior for their specific needs without modifying code
- Easier troubleshooting with configurable logging
- Flexibility for different use cases

**Implementation notes:**
- Add config flow for UI-based configuration
- Support YAML configuration in `configuration.yaml`
- Ensure sensible defaults
- Document all options in README

---

### 4. Integration with HA Assist
Make the integration work with Home Assistant's built-in voice pipeline (Assist) without requiring Extended OpenAI Conversation.

**Current behavior:**
- Requires Extended OpenAI Conversation (or similar) to provide function calling interface

**Proposed enhancement:**
- Register as a native Home Assistant intent/sentence pattern
- Allow Assist to use it directly via standard voice pipeline

**Benefits:**
- Users who want to use HA's default voice pipeline (Whisper → built-in LLM → actions) could use this integration
- Lower barrier to entry for non-technical users

**Trade-offs:**
- Would likely still require intent patterns like "Play [artist] on [device]"
- Less flexible than LLM-based approach
- May lose natural language advantage

**Implementation notes:**
- Register intent handlers via Home Assistant's conversation integration
- Define sentence patterns for common use cases
- Consider maintaining both approaches (function calling + intent patterns)

---

### 5. Saved/Favorite Content Quick Access
Add ability to search/play from user's Spotify saved content (liked songs, saved albums, followed artists).

**Status:** Partially implemented in v1.0.0
- ✅ User playlists: `type="user_playlist"` searches only saved playlists
- ✅ Caching implemented for user playlist data
- ⏳ Future: Saved tracks, albums, and followed artists

**Implemented in v1.0.0:**
- Voice commands like "Play my workout playlist" now work
- Searches only user's saved playlists (not all of Spotify)
- Exact and partial matching for user playlists
- Performance-optimized with caching

**Still to implement:**
- `type="saved_tracks"` for liked songs
- `type="saved_albums"` for saved albums
- `type="followed_artists"` for followed artists

**Implementation notes:**
- Use Spotify API endpoints: `get_saved_tracks()`, `get_saved_albums()`
- Handle pagination for large libraries
- Apply similar caching strategy as user playlists
