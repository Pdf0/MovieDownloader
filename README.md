# Movie Downloader

Movie Downloader is a Python script that allows you to search for movies using the YTS API, select a movie, and add its torrent to qBittorrent for downloading.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/movie-downloader.git
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate 
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Usage

   Run the script by providing the name of the movie you want to search for as a command-line argument:

   ```bash
   python3 movie_downloader.py "Movie Name"
   ```

   Follow the on-screen prompts to choose a movie and add its torrent to qBittorrent.

5. Configuration

   Before running the script, make sure to update the following variables in the script:

   ```python
   Web_UI_username = "your_qBittorrent_Web_UI_username"
   Web_UI_password = "your_qBittorrent_Web_UI_password"
   Download_path = "path/to/destination/directory"
   ```
7. Dependencies

   [requests](https://pypi.org/project/requests/)

   [qbittorrentapi](https://pypi.org/project/qbittorrentapi/)
