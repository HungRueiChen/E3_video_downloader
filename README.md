# NYCU E3 Video Downloader

## Purpose

The NYCU E3 Video Downloader is a Python-based tool designed to automate the process of logging into the National Yang Ming Chiao Tung University's E3 portal, navigating through course pages, and downloading all available video resources for offline review. This tool aims to facilitate students' access to educational materials by providing a streamlined, automated method for downloading course videos.

## Mechanism

The program leverages Selenium for web automation to perform the following tasks:

1. **Login to NYCU E3 Portal**: Automates the login process by filling in the username and password.
2. **Navigate to Course History**: Redirects to the course history page after a successful login.
3. **Extract Video Links**: Identifies and extracts video links from various sources (Resource, Evercam, and Ewant) on the course pages.
4. **Download Videos**: Downloads the identified videos using `urllib` and `requests`, and saves them to appropriately named folders.

### Key Components

- **Selenium WebDriver**: Used for automating browser interactions.
- **WebDriver Manager**: Manages the browser driver binaries.
- **urllib & requests**: Used for downloading video files.
- **pathlib**: Handles filesystem paths and directory operations.
- **re**: Sanitizes folder and file names.

## Usage

### Prerequisites

Ensure you have the following installed on your system:

- Python 3.x
- Selenium (`pip install selenium`)
- WebDriver Manager (`pip install webdriver-manager`)
- Requests (`pip install requests`)

### Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/nycu-e3-video-downloader.git
   cd nycu-e3-video-downloader
   ```
2. **Set the Destination**:
   - By default, the program creates a folder "videos" under the current directory and creates a subdirectorie under "videos" for each course.
   - To change the destination folder, modify Path object on line 137.
     ```python
     # Create a base directory for the videos
     base_dir = Path("path/to/customized/folder")
     base_dir.mkdir(parents=True, exist_ok=True)
     ```

2. **Run the Script**:
   ```bash
   python main.py
   ```

3. **Follow the Prompts**:
   - Enter your NYCU Student ID when prompted.
   - Enter your password when prompted.

## Example Output

```bash
Enter username (Student ID): 12345678
Enter password:
Downloading videos for course: [學生]【109下】A068大體解剖學 Gross Anatomy
Found 3 videos of type resource
Found 2 videos of type evercam
Found 1 videos of type ewant
Downloaded: videos/[學生]【109下】A068大體解剖學 Gross Anatomy/Meta-Lec-01 (Anatomy),02 (Histology)影片_已轉檔.mp4
...

An error occurred: Message: stale element reference: element is not attached to the page document
```

## Troubleshooting

- **Stale Element Reference**: This error occurs when the DOM updates and the reference to an element is lost. The script handles this by re-locating elements as needed.
- **Login Failures**: Ensure your credentials are correct and that you have a stable internet connection.
- **Video Download Issues**: Ensure the video links are accessible and not restricted by additional authentication or permissions.

## Contribution

Feel free to fork this repository, make improvements, and submit pull requests. Contributions are welcome!

## License
