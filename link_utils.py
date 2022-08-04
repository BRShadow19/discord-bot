import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

try:
    SPOTIFY_ID = os.environ.get('SPOTIFY_ID')
    SPOTIFY_SECRET = os.environ.get('SPOTIFY_SECRET')
    sp_api = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_ID, client_secret=SPOTIFY_SECRET))
    api = True
except:
    api = False
    print('Check the client_id and client_secret')

    
class LinkType():
    Spotify = 'Spotify'
    Spotify_Playlist = 'Spotify_Playlist'
    YouTube = 'YouTube'
    YouTube_Playlist = 'YouTube_Playlist'
    Unknown = "Unknown"


async def identify_url(url):
    ret = LinkType.Unknown
    if 'https://www.youtu' in url or 'https://youtu.be' in url:
        if 'youtube.com/playlist' in url:
            ret = LinkType.YouTube_Playlist
        else:
            ret = LinkType.YouTube
    
    elif 'https://open.spotify.com/track' in url:
        ret =  LinkType.Spotify
    
    elif 'https://open.spotify.com/playlist' in url:
        ret = LinkType.Spotify_Playlist
    
    return ret

"""
Takes in a url of a Spotify track or playlist, grabs the title and artist of each song, 
and returns a list of songs that can be searched using youtube_dl 
"""
async def convert_spotify_to_youtube(url):
    link_type = await identify_url(url)
    songs = []
    if api:
        if link_type == "Spotify_Playlist":
            data = sp_api.playlist_items(playlist_id=url, fields='items(track.name,track.artists.name)')
            playlist = data['items']
            for track in playlist:
                song = track['track']['name']
                artist = track['track']['artists'][0]['name']
                songs.append(song + ' by ' + artist)
        elif link_type == "Spotify":
            data = sp_api.track(track_id=url)
            artist = data['artists'][0]['name']
            title = data['name']
            songs.append(title + ' by ' + artist)
    return songs

