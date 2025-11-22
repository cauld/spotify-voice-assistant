"""Spotify Voice Assistant Search Integration for Home Assistant."""
import logging
import re
import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "spotify_voice_assistant"
VALID_SEARCH_TYPES = {"artist", "album", "track", "playlist"}

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)

# Cache Spotify client to avoid repeated lookups
_spotify_cache = {
    "client": None,
    "entity_id": None,
    "user_playlists": None,
}


def clean_query(query: str, search_type: str) -> str:
    """Remove common command words to improve search accuracy."""
    query = query.lower().strip()

    # Remove "play" from the start of any query
    if query.startswith("play "):
        query = query[5:]

    # Remove type-specific filler words
    if search_type == "artist":
        # Remove "artist" prefix if LLM included it
        query = query.replace("artist ", "").replace(
            "group ", "").replace("band ", "")
    elif search_type == "album":
        # Remove "album" prefix
        query = query.replace("album ", "")
    elif search_type == "track":
        # Remove "song" or "track" prefix
        query = query.replace("song ", "").replace("track ", "")

    return " ".join(query.split()).strip()


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Spotify Voice Assistant Search component."""

    async def get_spotify_client():
        """Get Spotify client with caching and validation."""
        if _spotify_cache["client"] is not None:
            if _spotify_cache["entity_id"] in hass.states.async_entity_ids():
                _LOGGER.debug("Using cached Spotify client")
                return _spotify_cache["client"]
            else:
                _LOGGER.info(
                    "Cached Spotify entity no longer exists, invalidating cache")
                _spotify_cache["client"] = None
                _spotify_cache["entity_id"] = None
                _spotify_cache["user_playlists"] = None

        _LOGGER.debug("Cache miss, performing Spotify entity lookup")

        spotify_entity_id = None
        for state in hass.states.async_all("media_player"):
            if "spotify" in state.entity_id.lower():
                spotify_entity_id = state.entity_id
                break

        if not spotify_entity_id:
            _LOGGER.error("No Spotify media player entity found")
            raise LookupError("Spotify not configured")

        entity_component = hass.data.get(
            "entity_components", {}).get("media_player")
        if not entity_component:
            raise LookupError("Media player component not available")

        spotify_entity = None
        for entity in entity_component.entities:
            if entity.entity_id == spotify_entity_id:
                spotify_entity = entity
                break

        if not spotify_entity:
            raise LookupError("Spotify entity not available")

        if not hasattr(spotify_entity, "coordinator"):
            raise AttributeError("Spotify coordinator not available")

        coordinator = spotify_entity.coordinator
        if not hasattr(coordinator, "client"):
            raise AttributeError("Spotify client not available")

        client = coordinator.client
        _spotify_cache["client"] = client
        _spotify_cache["entity_id"] = spotify_entity_id
        _LOGGER.info("Cached Spotify client for entity: %s", spotify_entity_id)

        return client

    async def search_spotify(call: ServiceCall):
        """Search Spotify and return the first result's URI."""
        raw_query = call.data.get("query")
        search_type = call.data.get("type", "artist")

        if not raw_query:
            _LOGGER.error("No query provided to spotify_voice_assistant")
            return {"error": "No query provided"}

        if search_type not in VALID_SEARCH_TYPES:
            return {"error": f"Invalid type. Must be one of: {', '.join(VALID_SEARCH_TYPES)}"}

        # --- UPDATE: Clean the query before sending to Spotify ---
        query = clean_query(raw_query, search_type)
        _LOGGER.info("Searching Spotify (%s) for cleaned query: '%s' (raw: '%s')",
                     search_type, query, raw_query)

        try:
            client = await get_spotify_client()
        except (LookupError, AttributeError) as err:
            _LOGGER.error("Failed to get Spotify client: %s", err)
            return {"error": str(err)}

        try:
            if search_type == "artist":
                results = await client.search(query, ["artist"], limit=10)
                items_list = results.artists
                if items_list and len(items_list) > 0:
                    exact_match = None
                    query_lower = query.lower()
                    for artist in items_list:
                        if hasattr(artist, "name") and artist.name.lower() == query_lower:
                            exact_match = artist
                            break

                    selected_artist = exact_match if exact_match else items_list[0]

                    if not hasattr(selected_artist, "uri"):
                        return {"error": "Invalid artist data from Spotify"}

                    uri = selected_artist.uri
                    name = selected_artist.name
                    match_type = "exact match" if exact_match else "first result"
                    result = {"uri": uri, "name": name, "type": "artist"}
                    _LOGGER.info("✅ SEARCH RESULT (%s): %s",
                                 match_type, result)
                    return result
                else:
                    error_result = {"error": f"No artist found for: {query}"}
                    _LOGGER.error("❌ SEARCH ERROR: %s", error_result)
                    return error_result

            elif search_type == "playlist":
                # Cleaning is already handled by clean_query logic above,
                # but we keep the specific 'playlist' word removal for safety
                query_cleaned = query.lower().replace(
                    "playlist", "").replace("playlists", "").strip()

                # 1. Search User Library
                try:
                    if _spotify_cache["user_playlists"] is None:
                        user_playlists_response = await client.get_playlists_for_current_user()
                        if user_playlists_response and hasattr(user_playlists_response, "items"):
                            _spotify_cache["user_playlists"] = user_playlists_response.items
                        else:
                            _spotify_cache["user_playlists"] = []

                    user_playlists = _spotify_cache["user_playlists"]

                    # Exact match in library
                    for playlist in user_playlists:
                        if hasattr(playlist, "name") and playlist.name.lower() == query_cleaned:
                            result = {"uri": playlist.uri,
                                      "name": playlist.name, "type": "playlist"}
                            _LOGGER.info(
                                "✅ SEARCH RESULT (user library - exact match): %s", result)
                            return result

                    # Partial match in library
                    for playlist in user_playlists:
                        if hasattr(playlist, "name") and query_cleaned in playlist.name.lower():
                            result = {"uri": playlist.uri,
                                      "name": playlist.name, "type": "playlist"}
                            _LOGGER.info(
                                "✅ SEARCH RESULT (user library - partial match): %s", result)
                            return result

                except Exception as err:
                    _LOGGER.warning("Error searching user playlists: %s", err)

                # 2. Fallback to Public Search
                results = await client.search(query_cleaned, ["playlist"], limit=10)
                items_list = results.playlists
                if items_list and len(items_list) > 0:
                    selected_playlist = items_list[0]
                    result = {"uri": selected_playlist.uri,
                              "name": selected_playlist.name, "type": "playlist"}
                    _LOGGER.info(
                        "✅ SEARCH RESULT (public playlist - first result): %s", result)
                    return result
                else:
                    error_result = {"error": f"No playlist found for: {query}"}
                    _LOGGER.error("❌ SEARCH ERROR: %s", error_result)
                    return error_result

            else:
                # Handle Album and Track
                results = await client.search(query, [search_type], limit=10)
                items_list = getattr(results, f"{search_type}s", None)

                if items_list and len(items_list) > 0:
                    exact_match = None
                    query_lower = query.lower()
                    for item in items_list:
                        if hasattr(item, "name") and item.name.lower() == query_lower:
                            exact_match = item
                            break

                    # Fallback logic for Albums
                    if not exact_match and search_type == "album" and len(query.split()) >= 2:
                        _LOGGER.info(
                            "No exact album match for '%s', trying track search", query)
                        try:
                            track_results = await client.search(query, ["track"], limit=10)
                            track_items = getattr(
                                track_results, "tracks", None)
                            if track_items and len(track_items) > 0:
                                first_track = track_items[0]
                                result = {"uri": first_track.uri,
                                          "name": first_track.name, "type": "track"}
                                _LOGGER.info(
                                    "✅ SEARCH RESULT (album→track fallback): %s", result)
                                return result
                        except Exception:
                            pass

                    selected_item = exact_match if exact_match else items_list[0]
                    match_type = "exact match" if exact_match else "first result"
                    result = {"uri": selected_item.uri,
                              "name": selected_item.name, "type": search_type}
                    _LOGGER.info("✅ SEARCH RESULT (%s - %s): %s",
                                 search_type, match_type, result)
                    return result
                else:
                    error_result = {
                        "error": f"No {search_type} found for: {query}"}
                    _LOGGER.error("❌ SEARCH ERROR: %s", error_result)
                    return error_result

        except Exception as err:
            _LOGGER.exception("Unexpected error searching Spotify")
            return {"error": "Search failed"}

    async def clear_cache(call: ServiceCall):
        """Clear Spotify client and user playlists cache."""
        if _spotify_cache["client"] is not None or _spotify_cache["user_playlists"] is not None:
            _spotify_cache["client"] = None
            _spotify_cache["entity_id"] = None
            _spotify_cache["user_playlists"] = None
            return {"success": True, "message": "Cache cleared"}
        else:
            return {"success": False, "message": "Cache was already empty"}

    hass.services.async_register(
        DOMAIN, "search", search_spotify, supports_response="only"
    )
    hass.services.async_register(
        DOMAIN, "clear_cache", clear_cache, supports_response="only"
    )
    return True
