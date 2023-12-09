import argparse
import time
import requests
import qbittorrentapi
from pythonopensubtitles.opensubtitles import OpenSubtitles
from pythonopensubtitles.utils import File
import os

Web_UI_username = "ifini" # Replace with your qBittorrent Web UI username
Web_UI_password = "David_1709" # Replace with your qBittorrent Web UI password
Download_path = "E:\\Media\\Movies" # Replace this with the path to the destination folder
Default_subtitles = "eng" # Replace this with your preferred language for subtitles
Movie_file = ""
Movie_folder = ""

def search_movies(movie_name):
    # YTS API endpoint for searching movies
    api_endpoint = 'https://yts.mx/api/v2/list_movies.json'
    
    # Set up query parameters
    
    params = {
        'query_term': movie_name,
        'limit': 10,
        'sort_by': 'download_count',
        'order_by': 'desc',
    }
    
    try:
        # Make a GET request to the YTS API
        response = requests.get(api_endpoint, params=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Get the response as JSON
            data = response.json()
            
            # Check if there are movies in the results
            if 'movies' in data['data']:
                movies = data['data']['movies']
                
                # Print the top 10 matching movies
                print("Top 10 Movies:")
                for i, movie in enumerate(movies, start=1):
                    print(f"{i}. {movie['title']} ({movie['year']})")
                
            # Ask the user to choose a movie
                choice = int(input("Enter the number of the movie you want to get the torrent URL for: "))
                
                # Validate the user's choice
                if 1 <= choice <= 10:
                    selected_movie = movies[choice - 1]
                    return selected_movie['id']
                else:
                    print("Invalid choice. Please enter a number between 1 and 10.")
                    return None
            else:
                print("No movies found in the results.")
                return None
        else:
            # Print an error message if the request was not successful
            print(f"Error: {response.status_code} - {response.text}")
            return None
            
    except requests.RequestException as e:
        # Handle any exceptions that may occur during the request
        print(f"Error: {e}")
        return None

def get_torrent_url(movie_id):
    # YTS API endpoint for getting details about a specific movie
    details_endpoint = f'https://yts.mx/api/v2/movie_details.json'
    
    # Set up query parameters
    params = {
        'movie_id': movie_id,
    }
    try:
        # Make a GET request to the endpoint
        response = requests.get(details_endpoint, params=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Get the response as JSON
            data = response.json()
            
            # Get torrent information
            torrents = data['data']['movie']['torrents']
            
            # Print the available torrents for the selected movie
            print("\nAvailable Torrents:")
            for i, torrent in enumerate(torrents, start=1):
                print(f"{i}. Quality: {torrent['quality']}, Seeds: {torrent['seeds']}")
            
            # Ask the user to choose a torrent
            torrent_choice = int(input("Enter the number of the torrent you want the URL for: "))
            
            # Validate the user's torrent choice
            if 1 <= torrent_choice <= len(torrents):
                selected_torrent = torrents[torrent_choice - 1]
                return selected_torrent['url']
            else:
                print("Invalid torrent choice. Please enter a number between 1 and the number of torrents.")
                return None
        else:
            # Print an error message if the request was not successful
            print(f"Error: {response.status_code} - {response.text}")
            return None
 
    except requests.RequestException as e:
        # Handle any exceptions that may occur during the request
        print(f"Error: {e}")
        return None

def add_torrent_to_qbittorrent(torrent_url, download_path):
    # Create Client using the appropriate WebUI configuration
    conn_info = dict(
        host = "localhost",
        port = 8080,
        username = Web_UI_username,
        password = Web_UI_password,
    )
    qbt_client = qbittorrentapi.Client(**conn_info)

    # Test the provided credentials
    try:
        qbt_client.auth_log_in()
    except qbittorrentapi.LoginFailed as e:
        print(e)
    
    # Add the torrent to qBittorrent
    response = qbt_client.torrents_add(urls=torrent_url, save_path=download_path)
    time.sleep(2)

    torrent_list = qbt_client.torrents_info(sort='added_on', reverse=True) #get torrents list by added time
    torrent = torrent_list[0] #get the last torrent added
    global Movie_folder
    Movie_folder = torrent['name']
    torrent_hash = torrent['hash']
    files = qbt_client.torrents_files(torrent_hash)
    if files:
        for file_info in files:
            if file_info['name'].lower().endswith('.mp4'): # If the file has a .mp4 extension, you've found your MP4 file
                global Movie_file 
                Movie_file = os.path.splitext(os.path.basename(file_info['name']))[0]
                print(f"Movie file name: {Movie_file}")
                break
    else:
        print("No files found for the torrent.")

    # Check if the torrent was added successfully
    if response == "Ok.":
        print(f"Torrent added successfully to qBittorrent.")
        
        qbt_client.auth_log_out()
        return True
    else:
        print(f"Failed to add torrent to qBittorrent. Error: {response.get('error', 'Unknown error')}")
        qbt_client.auth_log_out()
        return False
    
#TODO - Put the subtitles in the right folder and rename them
def get_subs(subtitles):
    osubs = OpenSubtitles() # Create the OpenSubtitles object
    print(f"Searching for subtitles for {Movie_file}...")
   
    token = osubs.login("Ifini", "David_1709") # Log in to the OpenSubtitles API
    
    results = osubs.search_subtitles([{'sublanguageid': subtitles, 'query': Movie_file}]) # Search for subtitles

    if results: # Check if subtitles were found
        result = results[0] # Get the first result
        
        download_link = result['ZipDownloadLink'] # Get the subtitle file's download link
       
        sub_file_name = result['SubFileName'] # Get the subtitle file's name
        print(f"Subtitle file name: {sub_file_name}")
        
        # subtitle_path = os.path.join(Download_path, Movie_folder, sub_file_name) # Create the path to save the subtitle file in the movie folder
        # print(f"Download path: {Download_path}")
        # print(f"Movie folder: {Movie_folder}")
        # print(f"Sub file name: {sub_file_name}")
        # print(f"Subtitle path: {subtitle_path}")
       
        response = requests.get(download_link) # Download the subtitle file
        
        if response.status_code == 200:  # Check if the request was successful
            with open(sub_file_name, 'wb') as f:  # Save the subtitle file in the movie folder
                f.write(response.content)
            new_sub_name = Movie_file + subtitles + ".srt"
            os.rename(sub_file_name, new_sub_name)
            print(f"Subtitles downloaded successfully to {new_sub_name}.")
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}") # Print an error message if the request was not successful
            return False
    else:
        print("No subtitles found.")
        return False

#TODO - Check if the movie already exists in the destination folder (using the movie file name)
def movie_exists(torrent_url):
    os.chdir(Download_path)
    for folder in os.listdir():
        if folder == Movie_folder:
            print("Movie already exists in the destination folder.")
            return True
    return False
    

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Movie Downloader')
    parser.add_argument('movie_name', type=str, help='Name of the movie to search for')
    parser.add_argument('--subtitles', type=str, help='Language of subtitles to download')
    args = parser.parse_args()

    # Search for movies and get the selected movie ID
    
    selected_movie_id = search_movies(args.movie_name)
    if selected_movie_id:
        # Get the torrent URL for the selected movie
        torrent_url = get_torrent_url(selected_movie_id)
        
        if torrent_url:
            
            #if movie_exists(torrent_url):
            #    print("Movie already exists in the destination folder.")
            #    exit()
            print(torrent_url)
            # Add the torrent to qBittorrent
            add_torrent_to_qbittorrent(torrent_url, Download_path)
        
            # Get subtitles for the movie
            if args.subtitles:
                Default_subtitles = args.subtitles
            selected_movie_subs = get_subs(Default_subtitles)