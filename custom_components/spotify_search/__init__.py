"""Spotify Search Integration for Home Assistant."""
import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "spotify_search"
VALID_SEARCH_TYPES = {"artist", "album", "track", "playlist"}

# Cache Spotify client to avoid repeated lookups
_spotify_cache = {
    "client": None,
    "entity_id": None,
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
            else:
                # For albums, tracks, playlists - use direct search
                results = await client.search(query, [search_type], limit=1)
                items_list = getattr(results, f"{search_type}s", None)
                if items_list and len(items_list) > 0:
                    item = items_list[0]

                    # Defensive attribute checks
                    if not hasattr(item, "uri") or not hasattr(item, "name"):
                        _LOGGER.error("%s result missing required attributes", search_type)
                        return {"error": f"Invalid {search_type} data from Spotify"}

                    uri = item.uri
                    name = item.name
                    _LOGGER.info("Found Spotify %s: %s (%s)", search_type, name, uri)
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
        """Clear Spotify client cache."""
        if _spotify_cache["client"] is not None:
            _LOGGER.info("Manually clearing Spotify client cache")
            _spotify_cache["client"] = None
            _spotify_cache["entity_id"] = None
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
