import os
import glob
import json
from PIL import Image
from config import CACHE_DIR, RESIZED_DIR, IMAGES_DIR

def calculate_crop_box(img_width, img_height, y_start_pct, y_end_pct, padding_pct=3.5):
    """
    Calculate the bounding box for PIL cropping based on vertical percentages.
    Includes vertical padding, enforces minimum height of 8%, and clamps bounds.
    """
    # Enforce minimum height of 8% of page height
    height_pct = y_end_pct - y_start_pct
    if height_pct < 8.0:
        diff = 8.0 - height_pct
        y_start_pct = max(0.0, y_start_pct - diff / 2.0)
        y_end_pct = min(100.0, y_end_pct + diff / 2.0)

    # Calculate pixel values
    y_start = (y_start_pct / 100.0) * img_height
    y_end = (y_end_pct / 100.0) * img_height
    
    # Apply vertical padding
    padding_px = (padding_pct / 100.0) * img_height
    y_start = max(0.0, y_start - padding_px)
    y_end = min(float(img_height), y_end + padding_px)
    
    # Convert to integer coordinates for PIL crop: (left, upper, right, lower)
    return (0, int(round(y_start)), img_width, int(round(y_end)))

def crop_page_assets(page_data, src_img_path, dest_dir, padding_pct=3.5):
    """
    Crop question and step assets for a single page based on page data JSON.
    """
    if not os.path.exists(src_img_path):
        print(f"Source image not found: {src_img_path}")
        return False
        
    os.makedirs(dest_dir, exist_ok=True)
    
    page_num = page_data.get("page")
    page_str = f"page_{page_num:02d}"
    
    with Image.open(src_img_path) as img:
        img_width, img_height = img.size
        
        for q in page_data.get("questions", []):
            q_num = q.get("q_number")
            q_crop = q.get("question_crop")
            
            if q_crop and len(q_crop) == 2:
                box = calculate_crop_box(img_width, img_height, q_crop[0], q_crop[1], padding_pct)
                # Crop and save question
                cropped_q = img.crop(box)
                q_filename = f"{page_str}_{q_num}_question.png"
                cropped_q.save(os.path.join(dest_dir, q_filename))
                print(f"  Cropped question: {q_filename} {box}")
                
            for step in q.get("steps", []):
                step_num = step.get("step_number")
                step_crop = step.get("crop")
                
                if step_crop and len(step_crop) == 2:
                    box = calculate_crop_box(img_width, img_height, step_crop[0], step_crop[1], padding_pct)
                    # Crop and save step
                    cropped_step = img.crop(box)
                    step_filename = f"{page_str}_{q_num}_step_{step_num}.png"
                    cropped_step.save(os.path.join(dest_dir, step_filename))
                    print(f"  Cropped step: {step_filename} {box}")
                    
    return True

def run_cropping(cache_dir=CACHE_DIR, resized_dir=RESIZED_DIR, dest_dir=IMAGES_DIR):
    """Orchestrate cropping of all pages present in cache_dir."""
    json_files = sorted(glob.glob(os.path.join(cache_dir, "page_*_raw.json")))
    if not json_files:
        print(f"No cache analysis files found in {cache_dir}.")
        return 0
        
    print(f"Found {len(json_files)} analysis cache files. Slicing images...")
    
    cropped_pages = 0
    for json_path in json_files:
        try:
            with open(json_path, "r") as f:
                page_data = json.load(f)
                
            page_num = page_data.get("page")
            src_img_name = f"page_{page_num:02d}.png"
            src_img_path = os.path.join(resized_dir, src_img_name)
            
            print(f"Slicing {src_img_name}...")
            if crop_page_assets(page_data, src_img_path, dest_dir):
                cropped_pages += 1
            
        except Exception as e:
            print(f"Error slicing {json_path}: {e}")
            
    return cropped_pages

if __name__ == "__main__":
    run_cropping()
