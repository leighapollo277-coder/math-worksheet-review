import os
import fitz  # PyMuPDF

def extract_pdf_pages(pdf_path, output_dir, dpi=150):
    """
    Extract each page of a PDF file as a high-resolution PNG image.
    
    Args:
        pdf_path (str): Path to the input PDF file.
        output_dir (str): Directory where PNG images will be saved.
        dpi (int): Dots per inch (resolution) for rendering the pages.
        
    Returns:
        list: List of absolute file paths to the generated PNG images.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
    os.makedirs(output_dir, exist_ok=True)
    
    # Open the PDF document
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"Opened PDF: {pdf_path} ({total_pages} pages)")
    
    generated_files = []
    
    for page_idx in range(total_pages):
        page = doc.load_page(page_idx)
        # Higher DPI yields clearer text/crops
        pix = page.get_pixmap(dpi=dpi)
        
        page_num = page_idx + 1
        filename = f"page_{page_num:02d}.png"
        dest_path = os.path.join(output_dir, filename)
        
        pix.save(dest_path)
        generated_files.append(dest_path)
        print(f"  Extracted page {page_num}/{total_pages} -> {filename}")
        
    doc.close()
    return generated_files
