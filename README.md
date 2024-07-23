# NYCU E3 Video Downloader

## Purpose

The NYCU E3 Video Downloader is a Python-based tool designed to automate the process of logging into the National Yang Ming Chiao Tung University's E3 portal, navigating through course pages, and downloading all available video resources for offline review. This tool aims to facilitate students' access to educational materials by providing a streamlined, automated method for downloading course videos.

## Mechanism

The program leverages Selenium for web automation to perform the following tasks:

1. **Login to NYCU E3 Portal**: Automates the login process by filling in the username and password.
2. **Navigate to Course History**: Redirects to the course history page after a successful login.
3. **Extract Video Links**: Identifies and extracts video links from various sources (Html, Mpeg, Evercam, and Ewant) on the course pages.
4. **Download Videos**: Downloads the identified videos using `urllib` and `requests`, and saves them to appropriately named folders.

## Features

This program includes the following features:

- **Duplication Detection**: Duplicated file names are appended with suffix "_n" to prevent overwriting videos of the same file name.
- **Existing File Detection**: The program automatically skips existing videos in the destination folder to save time during a re-run.

## Prerequisites

Ensure you have the following installed on your system:

- Python 3.x
- Selenium (`pip install selenium`)
- WebDriver Manager (`pip install webdriver-manager`)
- Requests (`pip install requests`)

## Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/nycu-e3-video-downloader.git
   cd nycu-e3-video-downloader
   ```
2. **Set the Destination**:
   - By default, the program creates a folder "videos" under the current directory and creates a subdirectory under "videos" for each course.
   - To change the destination folder, modify Path object on line 148.
     ```python
     # Create a base directory for the videos
     base_dir = Path("path/to/customized/folder")
     base_dir.mkdir(parents=True, exist_ok=True)
     ```

3. **Run the Script**:
   ```bash
   python main.py
   ```

4. **Follow the Prompts**:
   - Enter your NYCU Student ID when prompted.
   - Enter your password when prompted.

## Example Output

```bash
Enter username (Student ID): 10701000
Enter password:
[學生]【109下】A068大體解剖學 Gross Anatomy
Found 3 videos of type html
Found 0 videos of type mpeg
Found 2 videos of type evercam
Found 1 videos of type ewant
Duplicated file name, renaming 授課影片 to 授課影片_1
Status code = 200, Downloading: https://e3.nycu.edu.tw/pluginfile.php/1397477/mod_ewantvideo/videos/0/media.mp4
...

```

## Troubleshooting

- **Disconnected**: This error can occur when the screen is turned off. Please ensure your device does not enter sleep mode during execution.
- **Stale Element Reference**: This error occurs when the DOM updates and the reference to an element is lost. The script handles this by re-locating elements as needed.
- **Login Failures**: Ensure your credentials are correct and that you have a stable internet connection.
- **Video Download Issues**: Ensure the video links are accessible and not restricted by additional authentication or permissions.

## Caution

- Make sure your storage is large enough, as all videos may occupy up to 250G.
- Certain video webpages trigger the browser to download videos automatically to your system's default "Download" folder. NYCU E3 Video Downloader skips these videos without prompting, so please check your "Download" folder and move these videos (especially 精神科學, 實驗外科) to destination folder manually.
- Expired authentication can raise a runtime error and force the program to terminate. If this happens, please re-run the main.py to log in again.

## Contribution

Feel free to fork this repository, make improvements, and submit pull requests. Contributions are welcome!

## License
