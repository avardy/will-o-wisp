import cv2
import numpy as np
import time
from scipy import interpolate

def capture_and_preprocess(cap, cfg, homography=None, max_retries=3, retry_delay=0.1):
    """
    Capture and preprocess an image from the camera with retry logic.
    
    Args:
        cap: OpenCV VideoCapture object
        cfg: Configuration object with camera settings
        homography: Optional homography matrix for perspective correction
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delay: Delay between retries in seconds (default: 0.1)
    
    Returns:
        tuple: (gray_image, warped_image) or (None, None) if all retries fail
    """
    for attempt in range(max_retries + 1):  # +1 to include the initial attempt
        ret, image = cap.read()
        
        # Check if capture was successful and image is valid
        if ret and image is not None and image.size > 0:
            break  # Success, exit retry loop
        
        if attempt < max_retries:
            error_msg = 'Cannot read video'
            if not ret:
                error_msg = 'Camera read failed (ret=False)'
            elif image is None:
                error_msg = 'Camera returned None image'
            elif image.size == 0:
                error_msg = 'Camera returned empty image'
                
            print(f'{error_msg} (attempt {attempt + 1}/{max_retries + 1}). Retrying in {retry_delay}s...')
            time.sleep(retry_delay)
            
            # Optionally try to reinitialize the camera connection
            if attempt > 0:  # Only after first failure
                try:
                    # Try to grab and release a frame to clear the buffer
                    cap.grab()
                except:
                    pass
        else:
            print(f'Failed to read video after {max_retries + 1} attempts.')
            return None, None
        
    # At this point, we have successfully captured an image
    h, w = image.shape[:2]
    if w != cfg.input_width or h != cfg.input_height:
        if not capture_and_preprocess.warned:
            print("cv2 is ignoring the specified width/height. Resizing...")
            capture_and_preprocess.warned = True
        image = cv2.resize(image, (cfg.input_width, cfg.input_height))

    # Undistort the raw image.
    undistorted = image
    if homography is not None:
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(cfg.calib_K, cfg.calib_D, (w,h), 1, (w,h))
        undistorted = cv2.undistort(image, cfg.calib_K, cfg.calib_D, None, newcameramtx)

    # Warp the raw image.
    warped_image = None
    if homography is not None:
        warped_image = cv2.warpPerspective(undistorted, homography, (cfg.output_width, cfg.output_height))

        return cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY), warped_image
    else:

        return cv2.cvtColor(undistorted, cv2.COLOR_BGR2GRAY), None

# An attribute to the above function just so that we display the resize warning
# only once.
capture_and_preprocess.warned = False

def interpolate_missing_values(image, image_with_zeros_for_missing):
    # https://stackoverflow.com/questions/37662180/interpolate-missing-values-2d-python/39596856#39596856
    mask = image_with_zeros_for_missing == 0

    h, w = image.shape[:2]
    xx, yy = np.meshgrid(np.arange(w), np.arange(h))

    known_x = xx[~mask]
    known_y = yy[~mask]
    known_v = image[~mask]
    missing_x = xx[mask]
    missing_y = yy[mask]

    interp_values = interpolate.griddata(
        (known_x, known_y), known_v, (missing_x, missing_y),
        method='linear', fill_value=0
    )

    interp_image = image.copy()
    interp_image[missing_y, missing_x] = interp_values

    return interp_image