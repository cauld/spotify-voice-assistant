"""Spotify Search Integration for Home Assistant."""
import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "spotify_search"
VALID_SEARCH_TYPES = {"artist", "album", "track", "playlist", "user_playlist"}

# Cache Spotify client to avoid repeated lookups
_spotify_cache = {
    "client": None,
    "entity_id": None,
    "user_playlists": None,
}


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Spotify Search component."""

    async def get_spotify_client():
        """Get Spotify client with caching and validation."""
        # Validate cache if it exists
        if _spotify_cache["client"] is not None:
            # Fast check: Does entity still exist?
            if _spotify_cache["entity_id"] in hass.states.async_entity_ids():
                _LOGGER.debug("Using cached Spotify client")
                return _spotify_cache["client"]
            else:
                _LOGGER.info("Cached Spotify entity no longer exists, invalidating cache")
                _spotify_cache["client"] = None
                _spotify_cache["entity_id"] = None

        # Cache miss or invalidated - do full lookup
        _LOGGER.debug("Cache miss, performing Spotify entity lookup")

        # Try to find the Spotify media player entity
        spotify_entity_id = None
        for state in hass.states.async_all("media_player"):
            if "spotify" in state.entity_id.lower():
                spotify_entity_id = state.entity_id
                break

        if not spotify_entity_id:
            _LOGGER.error("No Spotify media player entity found")
            raise LookupError("Spotify not configured")

        _LOGGER.debug("Found Spotify entity: %s", spotify_entity_id)

        # Get the Spotify integration's data through entity platform
        entity_component = hass.data.get("entity_components", {}).get("media_player")
        if not entity_component:
            _LOGGER.error("Media player component not found")
            raise LookupError("Media player component not available")

        # Find the Spotify entity object
        spotify_entity = None
        for entity in entity_component.entities:
            if entity.entity_id == spotify_entity_id:
                spotify_entity = entity
                break

        if not spotify_entity:
            _LOGGER.error("Spotify entity %s not found in entities", spotify_entity_id)
            raise LookupError("Spotify entity not available")

        # Access the Spotify client from the coordinator
        if not hasattr(spotify_entity, "coordinator"):
            _LOGGER.error("Spotify entity does not have a coordinator")
            raise AttributeError("Spotify coordinator not available")

        coordinator = spotify_entity.coordinator

        if not hasattr(coordinator, "client"):
            _LOGGER.error("Spotify coordinator does not have a client attribute")
            raise AttributeError("Spotify client not available")

        client = coordinator.client
        _LOGGER.debug("Spotify client type: %s", type(client).__name__)

        # Cache for future calls
        _spotify_cache["client"] = client
        _spotify_cache["entity_id"] = spotify_entity_id
        _LOGGER.info("Cached Spotify client for entity: %s", spotify_entity_id)

        return client

    async def search_spotify(call: ServiceCall):
        """Search Spotify and return the first result's URI."""
        query = call.data.get("query")
        search_type = call.data.get("type", "artist")

        if not query:
            _LOGGER.error("No query provided to spotify_search")
            return {"error": "No query provided"}

        # Validate search type
        if search_type not in VALID_SEARCH_TYPES:
            _LOGGER.error("Invalid search type: %s", search_type)
            return {"error": f"Invalid type. Must be one of: {', '.join(VALID_SEARCH_TYPES)}"}

        try:
            client = await get_spotify_client()
        except (LookupError, AttributeError) as err:
            _LOGGER.error("Failed to get Spotify client: %s", err)
            return {"error": str(err)}

        try:
            # Search Spotify using the integration's client (async method)
            # SpotifyClient.search signature: search(query: str, types: list[SearchType], *, limit: int = 48)
            if search_type == "artist":
                # For artists, search using the artist type directly to get better matches
                _LOGGER.debug("Searching for artist: %s", query)
                results = await client.search(query, ["artist"], limit=10)
                items_list = results.artists
                if items_list and len(items_list) > 0:
                    # Check if any artist name matches exactly (case-insensitive)
                    exact_match = None
                    query_lower = query.lower()
                    for artist in items_list:
                        # Defensive attribute check
                        if hasattr(artist, "name") and artist.name.lower() == query_lower:
                            exact_match = artist
                            break

                    # Use exact match if found, otherwise use first result
                    selected_artist = exact_match if exact_match else items_list[0]

                    # Defensive attribute checks
                    if not hasattr(selected_artist, "uri") or not hasattr(selected_artist, "name"):
                        _LOGGER.error("Artist result missing required attributes")
                        return {"error": "Invalid artist data from Spotify"}

                    uri = selected_artist.uri
                    name = selected_artist.name
                    match_type = "exact match" if exact_match else "first result"
                    _LOGGER.info("Found Spotify artist: %s (%s) - %s", name, uri, match_type)
                    return {"uri": uri, "name": name, "type": "artist"}
                else:
                    _LOGGER.warning("No artists found for query: %s", query)
                    return {"error": f"No artist found for: {query}"}
            elif search_type == "playlist":
                # For playlists, search with higher limit and check for exact matches
                _LOGGER.debug("Searching for playlist: %s", query)
                results = await client.search(query, ["playlist"], limit=10)
                items_list = results.playlists
                if items_list and len(items_list) > 0:
                    # Check if any playlist name matches exactly (case-insensitive)
                    exact_match = None
                    query_lower = query.lower()
                    for playlist in items_list:
                        # Defensive attribute check
                        if hasattr(playlist, "name") and playlist.name.lower() == query_lower:
                            exact_match = playlist
                            break

                    # Use exact match if found, otherwise use first result
                    selected_playlist = exact_match if exact_match else items_list[0]

                    # Defensive attribute checks
                    if not hasattr(selected_playlist, "uri") or not hasattr(selected_playlist, "name"):
                        _LOGGER.error("Playlist result missing required attributes")
                        return {"error": "Invalid playlist data from Spotify"}

                    uri = selected_playlist.uri
                    name = selected_playlist.name
                    match_type = "exact match" if exact_match else "first result"
                    _LOGGER.info("Found Spotify playlist: %s (%s) - %s", name, uri, match_type)
                    return {"uri": uri, "name": name, "type": "playlist"}
                else:
                    _LOGGER.warning("No playlists found for query: %s", query)
                    return {"error": f"No playlist found for: {query}"}
            elif search_type == "user_playlist":
                # Search within user's saved playlists
                _LOGGER.debug("Searching user's playlists for: %s", query)
                try:
                    # Get user's playlists (with caching)
                    if _spotify_cache["user_playlists"] is None:
                        _LOGGER.debug("Cache miss, fetching user playlists")
                        user_playlists = await client.get_playlists_for_current_user()
                        _spotify_cache["user_playlists"] = user_playlists
                    else:
                        _LOGGER.debug("Using cached user playlists")
                        user_playlists = _spotify_cache["user_playlists"]

                    if not user_playlists or not hasattr(user_playlists, "items"):
                        _LOGGER.warning("No user playlists found or invalid response")
                        return {"error": "Could not retrieve user playlists"}

                    items_list = user_playlists.items
                    if not items_list or len(items_list) == 0:
                        _LOGGER.warning("User has no saved playlists")
                        return {"error": "No saved playlists found"}

                    # Search for exact match in user's playlists
                    exact_match = None
                    query_lower = query.lower()
                    for playlist in items_list:
                        if hasattr(playlist, "name") and playlist.name.lower() == query_lower:
                            exact_match = playlist
                            break

                    # If no exact match, search for partial match
                    partial_match = None
                    if not exact_match:
                        for playlist in items_list:
                            if hasattr(playlist, "name") and query_lower in playlist.name.lower():
                                partial_match = playlist
                                break

                    selected_playlist = exact_match or partial_match

                    if not selected_playlist:
                        _LOGGER.warning("No matching playlist found in user's library for: %s", query)
                        return {"error": f"No playlist matching '{query}' found in your library"}

                    # Defensive attribute checks
                    if not hasattr(selected_playlist, "uri") or not hasattr(selected_playlist, "name"):
                        _LOGGER.error("User playlist result missing required attributes")
                        return {"error": "Invalid playlist data"}

                    uri = selected_playlist.uri
                    name = selected_playlist.name
                    match_type = "exact match" if exact_match else "partial match"
                    _LOGGER.info("Found user playlist: %s (%s) - %s", name, uri, match_type)
                    return {"uri": uri, "name": name, "type": "playlist"}

                except Exception as err:
                    _LOGGER.error("Error retrieving user playlists: %s", err)
                    return {"error": "Failed to retrieve user playlists"}
            else:
                # For albums, tracks - search with higher limit and check for exact matches
                _LOGGER.debug("Searching for %s: %s", search_type, query)
                results = await client.search(query, [search_type], limit=10)
                items_list = getattr(results, f"{search_type}s", None)
                if items_list and len(items_list) > 0:
                    # Check if any item name matches exactly (case-insensitive)
                    exact_match = None
                    query_lower = query.lower()
                    for item in items_list:
                        # Defensive attribute check
                        if hasattr(item, "name") and item.name.lower() == query_lower:
                            exact_match = item
                            break

                    # Use exact match if found, otherwise use first result
                    selected_item = exact_match if exact_match else items_list[0]

                    # Defensive attribute checks
                    if not hasattr(selected_item, "uri") or not hasattr(selected_item, "name"):
                        _LOGGER.error("%s result missing required attributes", search_type)
                        return {"error": f"Invalid {search_type} data from Spotify"}

                    uri = selected_item.uri
                    name = selected_item.name
                    match_type = "exact match" if exact_match else "first result"
                    _LOGGER.info("Found Spotify %s: %s (%s) - %s", search_type, name, uri, match_type)
                    return {"uri": uri, "name": name, "type": search_type}
                else:
                    _LOGGER.warning("No results found for query: %s", query)
                    return {"error": f"No {search_type} found for: {query}"}

        except AttributeError as err:
            _LOGGER.error("Spotify API returned unexpected data structure: %s", err)
            return {"error": "Unexpected response from Spotify"}
        except Exception as err:
            _LOGGER.exception("Unexpected error searching Spotify")
            return {"error": "Search failed"}

    async def clear_cache(call: ServiceCall):
        """Clear Spotify client and user playlists cache."""
        if _spotify_cache["client"] is not None or _spotify_cache["user_playlists"] is not None:
            _LOGGER.info("Manually clearing Spotify cache")
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
