import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Read Spotify API credentials from environment variables
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

# Authenticate with Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope="playlist-modify-public"))

# Get user input for favorite artist, genre, and sample song
fav_artist = input("Enter your favorite artist: ")
genre = input("Enter your favorite genre: ")
sample_song = input("Enter a sample song: ")
playlist_length = int(input("Enter the desired playlist length (number of tracks): "))
popularity = int(input("Enter the desired popularity of tracks (0-100): "))

# Search for top tracks of favorite artist
results = sp.search(q=fav_artist, type="artist")
artist_id = results["artists"]["items"][0]["id"]
top_tracks = sp.artist_top_tracks(artist_id, country="US")["tracks"] # Get top tracks in US because Algerian Spotify is trash
track_ids = [track["id"] for track in top_tracks if track["popularity"] >= popularity] # Only add tracks with popularity >= 10

# Search for similar songs based on sample song
sample_results = sp.search(q=sample_song, type="track")
if sample_results["tracks"]["total"] == 0:
    print(f"No tracks found for '{sample_song}'")
else:
    sample_track_id = sample_results["tracks"]["items"][0]["id"]
    similar_tracks = sp.recommendations(seed_tracks=[sample_track_id], limit=10)["tracks"]
    similar_ids = [track["id"] for track in similar_tracks if track["popularity"] >= popularity] # Only add tracks with popularity >= 10

# Get similar artists and their top tracks
related_artists = sp.artist_related_artists(artist_id)["artists"]
related_tracks = []
for artist in related_artists:
    related_tracks.extend(sp.artist_top_tracks(artist["id"], country="US")["tracks"]) # Get top tracks in US because Algerian Spotify is trash
related_ids = [track["id"] for track in related_tracks if track["popularity"] >= popularity] # Only add tracks with popularity >= 10

# Combine track IDs and remove duplicates
playlist_ids = list(set(track_ids[:20] + similar_ids + related_ids))

# Create a new playlist and add tracks to it in batches of 100
playlist_name = input("Enter a name for your playlist: ")
playlist_description = f"Recommended playlist based on {fav_artist}, {genre}, and {sample_song}"
playlist = sp.user_playlist_create(user=sp.me()["id"], name=playlist_name, public=True, description=playlist_description)
num_tracks_added = 0
for i in range(0, len(playlist_ids), 100):
    if num_tracks_added >= playlist_length:
        break
    num_tracks_to_add = min(playlist_length - num_tracks_added, 100)
    sp.playlist_add_items(playlist_id=playlist["id"], items=playlist_ids[i:i+num_tracks_to_add])
    num_tracks_added += num_tracks_to_add

print(f"Playlist '{playlist_name}' created successfully!")
print(f"Playlist URL: {playlist['external_urls']['spotify']}")
print(f"Number of tracks added: {len(playlist_ids)}")
print(f"Number of tracks skipped: {num_tracks_added - len(playlist_ids)}")
