import os
import argparse
import sys
import shutil
import glob

# Ensure correct workspace paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
import pdf_extractor
import resize_and_preview
import analyze_all
import crop_images
import generate_review

def main():
    parser = argparse.ArgumentParser(description="End-to-End Student Math Worksheet Review Generator")
    parser.add_argument("--pdf", required=True, help="Path to the student worksheet PDF file")
    parser.add_argument("--force", action="store_true", help="Bypass cached AI analysis and run full queries again")
    parser.add_argument("--dpi", type=int, default=150, help="Resolution for PDF page extraction (default: 150)")
    
    args = parser.parse_args()
    
    # 1. Setup Directories
    print("=== Step 1: Initializing output directories ===")
    for d in [config.RAW_PAGES_DIR, config.RESIZED_DIR, config.IMAGES_DIR]:
        if os.path.exists(d):
            print(f"Cleaning previous directory: {os.path.basename(d)}...")
            shutil.rmtree(d)
    config.ensure_dirs()
    
    # Handle force cache bypass
    if args.force:
        print("Bypassing cache (--force). Clearing previous raw analysis JSON files...")
        json_caches = glob.glob(os.path.join(config.CACHE_DIR, "page_*_raw.json"))
        for jc in json_caches:
            try:
                os.remove(jc)
                print(f"  Removed cache file: {os.path.basename(jc)}")
            except Exception as e:
                print(f"  Failed to remove cache {jc}: {e}")
                
    # 2. Extract PDF Pages
    print("\n=== Step 2: Extracting PDF pages ===")
    try:
        pages = pdf_extractor.extract_pdf_pages(args.pdf, config.RAW_PAGES_DIR, dpi=args.dpi)
        print(f"Successfully extracted {len(pages)} pages.")
    except Exception as e:
        print(f"Error during PDF page extraction: {e}")
        sys.exit(1)
        
    # 3. Resize Pages
    print("\n=== Step 3: Resizing extracted pages ===")
    try:
        resized_count = resize_and_preview.resize_images(config.RAW_PAGES_DIR, config.RESIZED_DIR)
        print(f"Successfully processed {resized_count} page images.")
    except Exception as e:
        print(f"Error during image resizing: {e}")
        sys.exit(1)
        
    # 4. Generate Previews
    print("\n=== Step 4: Generating preview gallery ===")
    try:
        resize_and_preview.create_preview_html(config.RESIZED_DIR, config.PREVIEW_PATH)
    except Exception as e:
        print(f"Warning: preview generation failed: {e}")
        
    # 5. Run AI Analysis
    print("\n=== Step 5: Performing Gemini Visual Grading ===")
    try:
        # Runs analysis on all pages detected in RESIZED_DIR
        analyze_all.run_analysis()
    except Exception as e:
        print(f"Error during Gemini visual grading: {e}")
        sys.exit(1)
        
    # 6. Crop Elements
    print("\n=== Step 6: Slicing question and step assets ===")
    try:
        cropped_pages = crop_images.run_cropping()
        print(f"Successfully cropped elements for {cropped_pages} pages.")
    except Exception as e:
        print(f"Error during asset cropping: {e}")
        sys.exit(1)
        
    # 7. Compile Report & Generate Review Portal
    print("\n=== Step 7: Generating glassmorphic review portal ===")
    try:
        success = generate_review.run_generation()
        if success:
            print("\n=======================================================")
            print("Success! The review portal has been successfully generated.")
            print(f"Open: {config.INDEX_PATH} in your browser to inspect student answers.")
            print("=======================================================")
        else:
            print("Error: Portal generation failed.")
            sys.exit(1)
    except Exception as e:
        print(f"Error compiling review portal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
