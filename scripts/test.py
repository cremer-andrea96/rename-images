from PIL import Image, ExifTags
import os

def get_date_taken(image_path):
    """
    Extracts the 'DateTimeOriginal' from a JPG image's EXIF metadata.
    Returns the date as a string or None if not available.
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")

    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if not exif_data:
                return None  # No EXIF metadata found

            # Map EXIF tag IDs to names
            exif = {
                ExifTags.TAGS.get(tag_id, tag_id): value
                for tag_id, value in exif_data.items()
            }

            return exif.get("DateTimeOriginal")  # Format: 'YYYY:MM:DD HH:MM:SS'
    except Exception as e:
        print(f"Error reading EXIF data: {e}")
        return None


# Example usage
if __name__ == "__main__":
    folder = "C:\\Users\\andre\\Documents\\Repos\\rename-images\\Examples"  # Replace with your JPG file path

    for path in os.listdir(folder):
        full_path = os.path.join(folder, path)
        if os.path.isfile(full_path) and path.endswith(".jpg"):
            date_taken = get_date_taken(full_path)
            if date_taken:
                print(f"file: {path} -- Date taken: {date_taken}")
            else:
                print("Date taken metadata not found.")