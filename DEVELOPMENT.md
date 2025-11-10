# Development Guide

## Development Setup

This repository is set up for active development while being used in a running Home Assistant instance.

### Recommended Setup: Symlink Development

For active development, symlink this repository into Home Assistant's `custom_components` directory:

```bash
# Remove existing installation (if using HACS version)
rm -rf /path/to/homeassistant/config/custom_components/spotify_search

# Create symlink to your development repo
ln -s /path/to/your/spotify-voice-assistant/custom_components/spotify_search \
      /path/to/homeassistant/config/custom_components/spotify_search
```

**Benefits:**
- ✅ Edit files in your development repository
- ✅ Changes immediately affect running Home Assistant (after restart)
- ✅ Develop, test, and commit from one location
- ✅ No file duplication or sync issues

### Development Workflow

1. **Make Changes**
   ```bash
   cd /path/to/your/spotify-voice-assistant
   # Edit files in custom_components/spotify_search/
   ```

2. **Test Changes**
   ```bash
   # Restart Home Assistant
   docker restart homeassistant

   # Watch logs
   docker logs -f homeassistant | grep spotify_search
   ```

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```

4. **Create Release** (when ready)
   - Update version in `manifest.json`
   - Push changes
   - Create new GitHub release (e.g., v1.1.0)
   - HACS will auto-detect and notify users

### Switching to HACS Version (Future)

When you want to use the HACS version instead of development:

```bash
# Remove symlink
rm /path/to/homeassistant/config/custom_components/spotify_search

# Install via HACS
# HACS > Integrations > Spotify Voice Assistant > Install

# Restart Home Assistant
```

### Switching Back to Development

```bash
# Remove HACS version
rm -rf /path/to/homeassistant/config/custom_components/spotify_search

# Recreate symlink
ln -s /path/to/your/spotify-voice-assistant/custom_components/spotify_search \
      /path/to/homeassistant/config/custom_components/spotify_search

# Restart Home Assistant
# Method varies by installation type (Docker, Core, Supervised, etc.)
```

## Testing Checklist

Before each release:

- [ ] Test artist search with exact match (e.g., "Coldplay")
- [ ] Test artist search with first result fallback
- [ ] Test album search
- [ ] Test track search
- [ ] Test via voice commands
- [ ] Test via Developer Tools
- [ ] Check debug logs for errors
- [ ] Verify version in manifest.json is updated
- [ ] Update README if features changed

## File Structure

```
spotify-voice-assistant/
├── custom_components/
│   └── spotify_search/
│       ├── __init__.py          # Main integration code
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

### Common Debug Commands

```bash
# Watch integration logs in real-time (Docker example)
docker logs -f homeassistant 2>&1 | grep spotify_search

# Check if integration loaded
# Look for "Setting up spotify_search" in Home Assistant logs

# Verify symlink (if using symlink development)
ls -la /path/to/homeassistant/config/custom_components/spotify_search

# Check manifest version
cat custom_components/spotify_search/manifest.json | grep version
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

## Version Numbering

Follow semantic versioning:
- **v1.0.x** - Bug fixes only
- **v1.x.0** - New features (playlist support, config options, etc.)
- **v2.0.0** - Breaking changes (API changes, config changes, etc.)

## Contributing to Your Own Repo

When making improvements:

1. Create a feature branch (optional for solo development)
2. Make changes and test thoroughly
3. Update version in manifest.json
4. Commit with descriptive message
5. Push to main branch
6. Create GitHub release
7. HACS users will be notified automatically

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
