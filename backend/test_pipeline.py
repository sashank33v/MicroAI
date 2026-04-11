import sys
import os
import cv2
import numpy as np
import traceback

# Add backend to path
sys.path.append(os.path.dirname(__file__))

import image_analysis

def create_test_image(path):
    # Create a 512x512 image with some "grains"
    img = np.full((512, 512, 3), 200, dtype=np.uint8) # light gray matrix
    # Draw some "grain boundaries"
    for i in range(10):
        cv2.line(img, (i*50, 0), (i*50 + 20, 512), (50, 50, 50), 2)
        cv2.line(img, (0, i*50), (512, i*50 + 20), (50, 50, 50), 2)
    
    cv2.imwrite(path, img)
    print(f"Created test image at {path}")

def test_analysis(explicit_path=None):
    if explicit_path:
        test_img = explicit_path
        print(f"Testing with provided image: {test_img}")
    else:
        test_img = "test_img.png"
        create_test_image(test_img)
    
    print("Starting analysis...")
    try:
        result = image_analysis.analyze_microstructure(test_img, scale_um_per_px=0.5, material_type="Carbon Steel")
        
        print("\n--- Analysis Success ---")
        print(f"Grain Count: {result['grain_stats']['count']}")
        print(f"ASTM G: {result['grain_stats']['astm_number']}")
        print(f"Confidence: {result['confidence']}%")
        print(f"Phases Detected: {len(result['phases'])}")
        print(f"Defects Detected: {len(result['defects'])}")
        print(f"Processing Time: {result['processing_time']}s")
        
        # Check if AI explanation was generated (either LLM or template)
        if result['ai_explanation']:
            print("\nAI Explanation Generated:")
            print(result['ai_explanation'][:500].encode('ascii', 'replace').decode('ascii') + "...")
        else:
            print("\nError: AI Explanation is empty!")
            
        print("\n--- Image Data Generated ---")
        print(f"Overlay Base64 Length: {len(result['overlay_base64'])}")
        
        return True
    except Exception as e:
        print("\n--- Analysis Failed ---")
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(test_img):
            # os.remove(test_img)
            pass

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    success = test_analysis(path)
    if success:
        print("\n[PASSED] Backend analysis pipeline is stable.")
        sys.exit(0)
    else:
        print("\n[FAILED] Backend analysis pipeline encountered errors.")
        sys.exit(1)
