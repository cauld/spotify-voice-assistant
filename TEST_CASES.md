# Voice Command Test Cases

Test suite for validating Spotify Voice Assistant behavior with natural language queries.

## How to Use This

1. Say each command to your voice assistant
2. Note the actual response and whether it worked correctly
3. Use results to identify areas for improvement

## Test Categories

### 1. Basic Artist Queries

**Test 1.1: Simple artist request**
- **Command:** "Play Coldplay"
- **Expected:** Searches for artist "Coldplay", plays on default speaker
- **Result:**
- **Pass/Fail:**

**Test 1.2: Artist with speaker specified**
- **Command:** "Play Coldplay on the kitchen speaker"
- **Expected:** Searches for artist "Coldplay", plays on kitchen speaker
- **Result:**
- **Pass/Fail:**

**Test 1.3: Natural language artist request**
- **Command:** "I'm in the mood for some Coldplay"
- **Expected:** Searches for artist "Coldplay", plays on default speaker
- **Result:**
- **Pass/Fail:**

**Test 1.4: Artist with contextual description**
- **Command:** "Play that British band with Chris Martin"
- **Expected:** LLM interprets as Coldplay, searches and plays
- **Result:**
- **Pass/Fail:**

---

### 2. Album Queries

**Test 2.1: Specific album**
- **Command:** "Play the album Parachutes"
- **Expected:** Searches for album "Parachutes", plays on default speaker
- **Result:**
- **Pass/Fail:**

**Test 2.2: Album with artist (combined query)**
- **Command:** "Play Parachutes by Coldplay"
- **Expected:** Searches for album "Parachutes Coldplay", plays correct album
- **Result:**
- **Pass/Fail:**

**Test 2.3: Natural language album request**
- **Command:** "Can you play the Parachutes album?"
- **Expected:** Searches for album "Parachutes", plays on default speaker
- **Result:**
- **Pass/Fail:**

**Test 2.4: Album with speaker**
- **Command:** "Play the album Parachutes on the gaming room speaker"
- **Expected:** Searches for album "Parachutes", plays on gaming room speaker
- **Result:**
- **Pass/Fail:**

**Test 2.5: Album exact match**
- **Command:** "Play Parachutes"
- **Expected:** Searches albums with limit=10, returns exact match for "Parachutes" (not "Parachutes Deluxe Edition")
- **Result:**
- **Pass/Fail:**

---

### 3. Track Queries

**Test 3.1: Specific track**
- **Command:** "Play Yellow"
- **Expected:** Searches for track "Yellow", plays on default speaker
- **Result:**
- **Pass/Fail:**

**Test 3.2: Track with artist (combined query)**
- **Command:** "Play Yellow by Coldplay"
- **Expected:** Searches for track "Yellow Coldplay", plays correct track
- **Result:**
- **Pass/Fail:**

**Test 3.3: Track with speaker**
- **Command:** "Play the song Yellow on the office speaker"
- **Expected:** Searches for track "Yellow", plays on office speaker
- **Result:**
- **Pass/Fail:**

**Test 3.4: Natural language track request**
- **Command:** "Put on that song Yellow"
- **Expected:** Searches for track "Yellow", plays on default speaker
- **Result:**
- **Pass/Fail:**

**Test 3.5: Track exact match**
- **Command:** "Play Yellow"
- **Expected:** Searches tracks with limit=10, returns exact match for "Yellow" (prioritizes exact name over similar songs)
- **Result:**
- **Pass/Fail:**

---

### 4. Ambiguous Track Names (Edge Cases)

**Test 4.1: Common track name (no artist)**
- **Command:** "Play Hurt"
- **Expected:** Searches for track "Hurt", returns most popular (likely Johnny Cash or Nine Inch Nails)
- **Result:**
- **Pass/Fail:**

**Test 4.2: Common track name with artist**
- **Command:** "Play Hurt by Nine Inch Nails"
- **Expected:** Searches for track "Hurt Nine Inch Nails", returns correct version
- **Result:**
- **Pass/Fail:**

**Test 4.3: Common track name with different artist**
- **Command:** "Play Hurt by Johnny Cash"
- **Expected:** Searches for track "Hurt Johnny Cash", returns Cash cover version
- **Result:**
- **Pass/Fail:**

---

### 5. Exact Match Testing (All Content Types)

**Test 5.1: Exact artist name**
- **Command:** "Play Coldplay"
- **Expected:** Returns exact match for artist "Coldplay" (not similar/recommended artists)
- **Result:**
- **Pass/Fail:**

**Test 5.2: Similar artist name**
- **Command:** "Play Cold War Kids"
- **Expected:** Returns exact match for "Cold War Kids" (not "Coldplay" despite similarity)
- **Result:**
- **Pass/Fail:**

**Test 5.3: Artist with common name**
- **Command:** "Play The Band"
- **Expected:** Returns exact match for artist "The Band" (not generic band recommendations)
- **Result:**
- **Pass/Fail:**

**Test 5.4: Album exact match verification**
- **Command:** "Play A Rush of Blood to the Head"
- **Expected:** Returns exact match for album name, not "Deluxe" or "Remastered" versions
- **Result:**
- **Pass/Fail:**

**Test 5.5: Track exact match verification**
- **Command:** "Play Fix You"
- **Expected:** Returns exact match for track "Fix You" from top 10 results
- **Result:**
- **Pass/Fail:**

---

### 6. Playlist Queries

**Test 6.1: Public playlist - exact match**
- **Command:** "Play Today's Top Hits"
- **Expected:** Searches public playlists, returns exact match for "Today's Top Hits"
- **Result:**
- **Pass/Fail:**

**Test 6.2: Public playlist - common name**
- **Command:** "Play Chill Vibes"
- **Expected:** Searches public playlists with limit=10, prefers exact "Chill Vibes" match over "Chill Vibes Mix"
- **Result:**
- **Pass/Fail:**

**Test 6.3: User playlist - exact match**
- **Command:** "Play my workout playlist"
- **Expected:** Searches only user's saved playlists, finds exact match for "workout"
- **Result:**
- **Pass/Fail:**

**Test 6.4: User playlist - partial match**
- **Command:** "Play my running music"
- **Expected:** If no exact "running music" match, finds partial match like "Running Music 2024"
- **Result:**
- **Pass/Fail:**

**Test 6.5: User playlist - not found**
- **Command:** "Play my xyz123 playlist"
- **Expected:** Returns error "No playlist matching 'xyz123' found in your library"
- **Result:**
- **Pass/Fail:**

**Test 6.6: Playlist vs user playlist distinction**
- **Command 1:** "Play RapCaviar"
- **Expected 1:** Uses type=playlist, searches all public playlists
- **Command 2:** "Play my RapCaviar"
- **Expected 2:** Uses type=user_playlist, searches only user's saved playlists (assuming user has saved RapCaviar)
- **Result:**
- **Pass/Fail:**

---

### 7. Playback Control

**Test 7.1: Pause**
- **Command:** "Pause the music"
- **Expected:** Pauses current playback on active speaker
- **Result:**
- **Pass/Fail:**

**Test 7.2: Resume**
- **Command:** "Resume"
- **Expected:** Resumes playback on active speaker
- **Result:**
- **Pass/Fail:**

**Test 7.3: Next track**
- **Command:** "Skip to the next track"
- **Expected:** Advances to next track
- **Result:**
- **Pass/Fail:**

**Test 7.4: Previous track**
- **Command:** "Go back to the previous song"
- **Expected:** Returns to previous track
- **Result:**
- **Pass/Fail:**

**Test 7.5: Volume up (natural language)**
- **Command:** "Make it louder"
- **Expected:** Increases volume (LLM interprets as volume_set with higher level)
- **Result:**
- **Pass/Fail:**

**Test 7.6: Volume specific**
- **Command:** "Set volume to 50 percent"
- **Expected:** Sets volume to 50%
- **Result:**
- **Pass/Fail:**

**Test 7.7: Stop**
- **Command:** "Stop the music"
- **Expected:** Stops playback
- **Result:**
- **Pass/Fail:**

---

### 8. Multi-Speaker Scenarios

**Test 8.1: Different speaker each time**
- **Commands:**
  - "Play Coldplay on the kitchen speaker"
  - "Play Radiohead on the gaming room speaker"
  - "Play Muse on the office speaker"
- **Expected:** Each plays on the specified speaker
- **Result:**
- **Pass/Fail:**

**Test 8.2: No speaker specified (uses default)**
- **Command:** "Play Coldplay"
- **Expected:** Plays on default speaker from system prompt
- **Result:**
- **Pass/Fail:**

---

### 9. Error Handling

**Test 9.1: Non-existent artist**
- **Command:** "Play XYZ123NotARealBand"
- **Expected:** Returns no results or best guess, handles gracefully
- **Result:**
- **Pass/Fail:**

**Test 9.2: Typo in artist name**
- **Command:** "Play Cold Play" (with space)
- **Expected:** Spotify's fuzzy search finds "Coldplay"
- **Result:**
- **Pass/Fail:**

**Test 9.3: Invalid speaker**
- **Command:** "Play Coldplay on the bedroom speaker" (if bedroom speaker doesn't exist)
- **Expected:** Error or fallback behavior
- **Result:**
- **Pass/Fail:**

---

### 10. Natural Language Variations

**Test 10.1: Informal request**
- **Command:** "Put on some Coldplay"
- **Expected:** Searches for artist "Coldplay", plays on default speaker
- **Result:**
- **Pass/Fail:**

**Test 10.2: Question format**
- **Command:** "Can you play Coldplay?"
- **Expected:** Searches for artist "Coldplay", plays on default speaker
- **Result:**
- **Pass/Fail:**

**Test 10.3: Context-heavy request**
- **Command:** "I want to listen to Coldplay right now"
- **Expected:** Searches for artist "Coldplay", plays on default speaker
- **Result:**
- **Pass/Fail:**

**Test 10.4: Mood-based request**
- **Command:** "Play something chill from Coldplay"
- **Expected:** Searches for artist "Coldplay", plays on default speaker
- **Result:**
- **Pass/Fail:**

---

## Results Summary

**Total Tests:** 40
**Passed:** _____
**Failed:** _____
**Pass Rate:** _____%

### Common Failure Patterns
(Document patterns that emerge from testing)

### Recommendations for Improvement
(Based on test results, list specific enhancements needed)
