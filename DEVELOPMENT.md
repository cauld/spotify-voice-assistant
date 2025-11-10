# Development Guide

## Development Setup

This repository is set up for active development while being used in a running Home Assistant instance.

### Recommended Setup: Docker Bind Mount

For Docker-based Home Assistant installations, use a bind mount to link this repository directly into your container. This is the cleanest approach for active development.

**Add this volume to your Docker run command or docker-compose.yml:**

```bash
# Docker run example
docker run ... \
  -v /path/to/spotify-voice-assistant/custom_components/spotify_search:/config/custom_components/spotify_search:ro \
  ...

# docker-compose.yml example
services:
  homeassistant:
    volumes:
      - /path/to/spotify-voice-assistant/custom_components/spotify_search:/config/custom_components/spotify_search:ro
```

**Benefits:**
- ✅ Edit files in your development repository
- ✅ Changes immediately reflected (after restart/reload)
- ✅ Develop, test, and commit from one location
- ✅ No file duplication or sync issues
- ✅ Read-only mount (`:ro`) protects your source files

**Note:** You'll need to recreate/restart your container after adding the bind mount.

### Alternative: Symlink Development (Non-Docker or Host Config)

If you have direct filesystem access to your Home Assistant config directory:

```bash
# Remove existing installation (if using HACS version)
rm -rf /path/to/homeassistant/config/custom_components/spotify_search

# Create symlink to your development repo
ln -s /path/to/your/spotify-voice-assistant/custom_components/spotify_search \
      /path/to/homeassistant/config/custom_components/spotify_search
```

**Important for Docker:** If using symlinks with Docker, ensure the symlink target path is accessible from inside the container (either mounted or within the config volume).

### When to Restart vs Reload

Understanding when you need to restart Home Assistant vs just reloading the integration:

**Full Restart Required:**
- Python code changes (`__init__.py`)
- Manifest changes (`manifest.json`)
- Adding/removing the integration
- First-time setup

**Reload Integration Only:**
- Service definition changes (`services.yaml`)
- Go to Developer Tools > YAML > Reload "Core Configuration"

**No Action Required:**
- Documentation changes (README.md, DEVELOPMENT.md)
- Git operations (commit, push, tag)

## Development Workflow

### 1. Make Changes

```bash
cd /path/to/your/spotify-voice-assistant
# Edit files in custom_components/spotify_search/
```

### 2. Test Changes

```bash
# For Python code changes - full restart
docker restart homeassistant

# For YAML changes - reload only (faster)
# Use Developer Tools > YAML > Core Configuration

# Watch logs in real-time
docker logs -f homeassistant 2>&1 | grep spotify_search
```

### 3. Commit Changes

```bash
git add .
git commit -m "Description of changes"
git push
```

### 4. Create Release (when ready)

- Update version in `manifest.json`
- Push changes
- Create new GitHub release (e.g., v1.1.0)
- HACS will auto-detect and notify users

## Switching Between Development and HACS

### Switch to HACS Version

When you want to use the stable HACS version instead of development:

**For bind mount setup:**
```bash
# Remove the bind mount from your Docker configuration
# Recreate the container without the bind mount
docker restart homeassistant

# Install via HACS
# HACS > Integrations > Spotify Voice Assistant > Install
# Restart Home Assistant
```

**For symlink setup:**
```bash
# Remove symlink
rm /path/to/homeassistant/config/custom_components/spotify_search

# Install via HACS
# HACS > Integrations > Spotify Voice Assistant > Install
# Restart Home Assistant
```

### Switch Back to Development

**For bind mount setup:**
```bash
# Add the bind mount back to your Docker configuration
# Recreate/restart the container
docker restart homeassistant
```

**For symlink setup:**
```bash
# Remove HACS version
rm -rf /path/to/homeassistant/config/custom_components/spotify_search

# Recreate symlink
ln -s /path/to/your/spotify-voice-assistant/custom_components/spotify_search \
      /path/to/homeassistant/config/custom_components/spotify_search

# Restart Home Assistant
```

## Testing Checklist

Before each release:

- [ ] Test artist search with exact match (e.g., "Coldplay")
- [ ] Test artist search with first result fallback
- [ ] Test album search
- [ ] Test track search
- [ ] Test playlist search
- [ ] Test via voice commands through Extended OpenAI Conversation
- [ ] Test via Developer Tools service call
- [ ] Test clear_cache service
- [ ] Check debug logs for errors
- [ ] Verify caching is working (check debug logs for "Using cached Spotify client")
- [ ] Verify version in manifest.json is updated
- [ ] Update README if features changed

## File Structure

```
spotify-voice-assistant/
├── custom_components/
│   └── spotify_search/
│       ├── __init__.py          # Main integration code (186 lines)
│       ├── manifest.json        # Version and metadata
│       └── services.yaml        # Service definitions
├── examples/                    # User examples
├── README.md                    # Main documentation
├── LICENSE                      # MIT License
├── .gitignore                   # Git ignore patterns
├── DEVELOPMENT.md              # This file
└── GITHUB-SETUP.md             # GitHub setup instructions
```

## Debugging

### Enable Debug Logging

In Home Assistant `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.spotify_search: debug
```

After adding debug logging, restart Home Assistant to apply.

### Common Debug Commands

```bash
# Watch integration logs in real-time (Docker example)
docker logs -f homeassistant 2>&1 | grep spotify_search

# Check if integration loaded successfully
docker logs homeassistant 2>&1 | grep "Setting up spotify_search"

# Verify bind mount or symlink
# For bind mount:
docker inspect homeassistant | grep spotify_search

# For symlink:
ls -la /path/to/homeassistant/config/custom_components/spotify_search

# Check manifest version
cat custom_components/spotify_search/manifest.json | grep version

# Check Python syntax without running
python3 -m py_compile custom_components/spotify_search/__init__.py
```

### Debug Logging Output

When working correctly, you should see:
```
INFO Setting up spotify_search
INFO Setup of domain spotify_search took 0.00 seconds
DEBUG Cache miss, performing Spotify entity lookup
DEBUG Found Spotify entity: media_player.spotify_xxx
DEBUG Spotify client type: SpotifyClient
INFO Cached Spotify client for entity: media_player.spotify_xxx
DEBUG Searching for artist: Coldplay
INFO Found Spotify artist: Coldplay (spotify:artist:4gzpq5DPGxSnKTe4SA8HAU) - exact match
```

Subsequent searches should show:
```
DEBUG Using cached Spotify client  # <-- Caching is working!
```

### Test Service Call

Via Developer Tools > Services:
```yaml
service: spotify_search.search
data:
  query: "Coldplay"
  type: "artist"
```

Expected response:
```json
{
  "uri": "spotify:artist:4gzpq5DPGxSnKTe4SA8HAU",
  "name": "Coldplay",
  "type": "artist"
}
```

### Test Clear Cache Service

```yaml
service: spotify_search.clear_cache
```

Expected response:
```json
{
  "success": true,
  "message": "Cache cleared"
}
```

## Performance Notes

The v1.0.0 release includes client caching that provides 15-50x performance improvement:

- **Without cache:** ~150-500ms per search (full entity lookup)
- **With cache:** ~3-10ms per search (cached client reuse)

Cache automatically invalidates if the Spotify integration is reloaded or removed.

## Version Numbering

Follow semantic versioning:
- **v1.0.x** - Bug fixes only
- **v1.x.0** - New features (config options, additional search types, etc.)
- **v2.0.0** - Breaking changes (API changes, config changes, etc.)

## Release Process

When making improvements:

1. Make changes and test thoroughly with checklist above
2. Update version in `manifest.json`
3. Commit with descriptive message (no AI attribution)
4. Push to main branch
5. Create GitHub release with tag matching manifest version
6. HACS users will be notified automatically

**Example:**
```bash
# Update manifest.json version to 1.1.0
git add custom_components/spotify_search/manifest.json
git commit -m "Add support for podcast search"
git push

# Create release on GitHub
gh release create v1.1.0 --title "v1.1.0 - Podcast Search Support" \
  --notes "Added support for searching Spotify podcasts"
```

## Backup Strategy

Before making major changes, create a backup:

```bash
# Backup your development repository
tar -czf spotify-voice-assistant-backup-$(date +%Y%m%d).tar.gz \
  custom_components/

# Optionally backup your HA configuration
cp /path/to/homeassistant/config/configuration.yaml \
   configuration-backup-$(date +%Y%m%d).yaml
```

## Common Issues

### Integration Not Loading

**Symptom:** No "Setting up spotify_search" in logs

**Check:**
1. Verify bind mount or symlink is correct
2. Check `configuration.yaml` has `spotify_search:` entry
3. Ensure files are readable by HA container user
4. Look for Python syntax errors in logs

**Docker bind mount check:**
```bash
docker inspect homeassistant | grep -A2 spotify_search
```

### Symlink Not Working in Docker

**Symptom:** Integration loads but shows errors about missing files

**Solution:** Symlinks must point to paths accessible from inside the container. Use bind mounts instead (see setup section above).

### Changes Not Reflecting

**Symptom:** Made changes but HA still runs old code

**Solution:**
1. Ensure you're editing the correct files (check bind mount/symlink target)
2. Restart HA after Python code changes
3. Check for cached `.pyc` files in `__pycache__/` and clear if needed
4. Verify bind mount is not read-only when testing (remove `:ro` temporarily)

## Code Quality

### Before Committing

```bash
# Check Python syntax
python3 -m py_compile custom_components/spotify_search/__init__.py

# Check for common issues
grep -n "TODO\|FIXME\|XXX" custom_components/spotify_search/*.py

# Ensure no debug print statements
grep -n "print(" custom_components/spotify_search/*.py
```

### Code Standards

- Use lazy logging: `_LOGGER.debug("Text: %s", var)` not `_LOGGER.debug(f"Text: {var}")`
- Use defensive programming: check attributes with `hasattr()` before accessing
- Validate all user inputs
- Handle specific exceptions before generic ones
- Keep functions focused and under 50 lines when possible
