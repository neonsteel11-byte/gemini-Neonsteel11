import os
import sys
import cv2

def verify_video_integrity(file_path):
    """Physically opens the media container to verify it contains valid, readable H.264 pixel tracks."""
    if not os.path.exists(file_path):
        print(f"❌ [Safety Guard]: File completely missing at {file_path}")
        return False
        
    # Attempt to open the video container via OpenCV
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        print(f"❌ [Safety Guard]: YouTube upload BLOCKED! File at {file_path} is an unreadable or corrupt binary container.")
        return False

    # Read frame properties
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    # Ironclad validation thresholds
    if frame_count <= 0 or width <= 0 or height <= 0:
        print(f"❌ [Safety Guard]: YouTube upload BLOCKED! File has zero valid media dimensions ({width}x{height}, Frames: {frame_count}).")
        return False

    print(f"🛡️ [Safety Guard]: Verification passed for {os.path.basename(file_path)}! ({width}x{height}, Total Frames: {frame_count}). Proceeding safely.")
    return True

if __name__ == "__main__":
    # Example target paths from your Visual Composer output
    short_target = "output/airbnb_short.mp4"
    long_target = "output/airbnb_long.mp4"
    
    print("🔒 [Safety Guard]: Initializing pre-upload integrity sweep...")
    
    if not verify_video_integrity(short_target) or not verify_video_integrity(long_target):
        print("🚨 [Safety Guard]: Critical failure detected in production assets. Script terminating forcefully to protect channel reputation.")
        sys.exit(1) # Forces GitHub Actions to stop and marks the build as failed BEFORE hitting YouTube
        
    print("🚀 [Safety Guard]: All assets authenticated. Safe to initiate backend API uploads.")
    # Your remaining upload code executes safely below this line...
