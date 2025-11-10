# TODO

## v1.0.0 Release
- [ ] Create GitHub release with notes
- [ ] Test installation via HACS custom repository

## Future Enhancements (v1.1.0+)

### Artist Filter Parameter
Add optional artist filter parameter to improve multi-part query accuracy.

**Current approach (v1.0.0):**
- Combine artist and song into query string: "Yellow Coldplay"
- Relies on Spotify's search ranking algorithm
- Works well via LLM prompt enhancement

**Proposed enhancement (v1.1.0):**
- Add `artist` parameter to `search_spotify` service
- Apply artist filtering to search results
- Example: `search_spotify(query="Yellow", type="track", artist="Coldplay")`

**Benefits:**
- More precise matching when multiple artists have songs with same name
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
