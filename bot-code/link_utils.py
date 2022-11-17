import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

try:
    # Obtain the Spotify API tokens from our environment variables
    SPOTIFY_ID = os.environ.get('SPOTIFY_ID')
    SPOTIFY_SECRET = os.environ.get('SPOTIFY_SECRET')
    # Link the tokens with the API wrapper
    sp_api = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_ID, client_secret=SPOTIFY_SECRET))
    api = True
except:
    api = False
    print('Check the client_id and client_secret')

# Small class that will store strings referring to what type of link the program is referring to
class LinkType():
    Spotify = 'Spotify'
    Spotify_Playlist = 'Spotify_Playlist'
    Spotify_Album = 'Spotify_Album'
    YouTube = 'YouTube'
    YouTube_Playlist = 'YouTube_Playlist'
    Unknown = "Unknown"


async def identify_url(url):
    """Identifies the URL based on a few specific traits.
    Uses the LinkType class to obtain the correct string for returning.
    Will only identify links to a YouTube video, YouTube playlist, Spotify
    track, or Spotify playlist. All other links will be identified as Unknown.

    Args:
        url (str): The full URL to be identified

    Returns:
        str: Contains the string from the corresponding variable in the LinkType class
    """    
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
    elif 'https://open.spotify.com/album' in url:
        ret = LinkType.Spotify_Album

    return ret

"""

"""
async def convert_spotify_to_youtube(url):
    """Takes in a url of a Spotify track or playlist, grabs the title and artist of each song, 
    and returns a list of songs that can be searched using youtube_dl 

    Args:
        url (str): Valid URL of a Spotify track or playlist

    Returns:
        list: A list where each element is a song title and the song's artist. Example: "Back in Black by AC/DC"
    """    
    link_type = await identify_url(url)
    songs = []
    if api: # Ensure we do have API access before running
        if link_type == LinkType.Spotify_Playlist:
            # Dictionary from the Spotify API containing all info about the playlist
            data = sp_api.playlist_items(playlist_id=url, fields='items(track.name,track.artists.name)')
            playlist = data['items']
            # Collect each track and artist's name, append it to the list of songs
            for track in playlist:
                song = track['track']['name']
                artist = track['track']['artists'][0]['name']
                songs.append(song + ' by ' + artist)

        elif link_type == LinkType.Spotify:
            # Dictionary from the Spotify API containing all info about the track
            data = sp_api.track(track_id=url)
            # Collect the track and artist's name, append it to the list of songs
            artist = data['artists'][0]['name']
            title = data['name']
            songs.append(title + ' by ' + artist)
        
        elif link_type == LinkType.Spotify_Album:
            # Dictionary from the Spotify API containing all info about the album
            data = sp_api.album_tracks(album_id=url)
            album = data['items']
            # Collect each track and artist's name, append it to the list of songs
            for track in album:
                song = track['name']
                artist = track['artists'][0]['name']
                songs.append(song + ' by ' + artist)        

    return songs

