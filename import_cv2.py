import cv2
import os
import toml
import logging

### Config values setup
config = toml.load('config.toml')
max_size_gb =  config["location"]["max_size_gb"] 
max_size_bytes = max_size_gb * (1024 ** 3)
os.makedirs(config["location"]["output_folder"], exist_ok=True)
frame_value = config["target"]["frame_value"]
log_file_name = config["location"]["log_file"]

### Setup log
logging.basicConfig(
    filename=log_file_name,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Get size of folder
def get_folder_size(folder):
    """
    Return size of folder in bytes

    Args:
    folder (string): Absolute path to folder

    Returns:
    total_size: Size of folder content in bytes
    """
    total_size = 0
    for dirpath, _dirnames_, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

# Main logic
def main():
    """
    The main function, performing caption
    """

    # Initialize video capture
    cap = cv2.VideoCapture(config["target"]["rtsp_url"])

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        exit()

    frame_count = 0
    number = 0
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

    while True:
        # Check the folder size before capturing a new frame
        current_size = get_folder_size(config["location"]["output_folder"])
        if max_size_gb == 0:
            if current_size > max_size_bytes:
                logging.error(f"Error: The folder size has exceeded {max_size_gb} GB. Stopping the program.")
                break
        ret, frame = cap.read()

        if not ret:
          logging.error("Error: Could not read frame.")
          cap = cv2.VideoCapture(config["target"]["rtsp_url"])
          continue

        frame_count += 1

        # Capture every Nth frame
        if frame_count % frame_value == 0:
            # Construct the filename
            filename = os.path.join(config["location"]["output_folder"], f'frame_{number}.jpg')

            # Save the frame as an image
            cv2.imwrite(filename, frame)
            logging.info(f'Saved: {filename}')
            number += 1
    # Release the video capture object
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
