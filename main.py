import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope="playlist-modify-public user-top-read"
    )
)

# -----------------------------
# Mood rules (metadata-based)
# -----------------------------
MOODS = {
    "happy": {"popularity": (60, 100), "explicit": False},
    "sad": {"popularity": (0, 50), "explicit": False},
    "chill": {"popularity": (30, 70), "explicit": False},
    "energetic": {"popularity": (70, 100), "explicit": True}
}

print("Choose a mood:", ", ".join(MOODS.keys()))
mood = input("Mood: ").strip().lower()

if mood not in MOODS:
    raise ValueError("Invalid mood")

rules = MOODS[mood]

# -----------------------------
# Spotify user
# -----------------------------
user = sp.current_user()
user_id = user["id"]
print("Logged in as:", user["display_name"])

# -----------------------------
# Create playlist
# -----------------------------
playlist = sp.user_playlist_create(
    user=user_id,
    name=f"{mood.capitalize()} Album 🎧",
    public=True,
    description=f"Auto-generated {mood} album"
)
playlist_id = playlist["id"]

# -----------------------------
# Fetch top tracks
# -----------------------------
top_tracks = sp.current_user_top_tracks(
    limit=50,
    time_range="short_term"
)

scored_tracks = []

for idx, track in enumerate(top_tracks["items"]):
    score = 0
    popularity = track["popularity"]
    explicit = track["explicit"]

    # --- Mood-specific scoring ---
    if mood == "happy":
        score += popularity * 1.2
        score += (50 - idx)  # favor recent/top-ranked

    elif mood == "sad":
        score += (100 - popularity) * 1.1
        score += idx  # favor deeper cuts

    elif mood == "chill":
        score += popularity
        if not explicit:
            score += 15

    elif mood == "energetic":
        score += popularity * 1.3
        if explicit:
            score += 20

    scored_tracks.append((score, track["uri"]))

# Sort and select
scored_tracks.sort(reverse=True, key=lambda x: x[0])
album_tracks = [uri for _, uri in scored_tracks[:12]]



# Limit album size
album_tracks = album_tracks[:12]

# -----------------------------
# Add tracks
# -----------------------------
if album_tracks:
    sp.playlist_add_items(playlist_id, album_tracks)
    print("🎶 Mood album created successfully!")
else:
    print("⚠️ No tracks matched this mood. Try another mood.")



