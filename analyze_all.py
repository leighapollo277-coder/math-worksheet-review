import os
import subprocess
import json
import time

def analyze_page(page_num):
    cache_dir = "/Users/kenyim/.gemini/antigravity/scratch/math-answer-review/analysis_cache"
    cache_path = os.path.join(cache_dir, f"page_{page_num:02d}_raw.json")
    if os.path.exists(cache_path):
        print(f"Loading cached analysis for Page {page_num}...")
        try:
            with open(cache_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cache for Page {page_num}: {e}. Re-analyzing...")

    image_path = f"/Users/kenyim/.gemini/antigravity/scratch/math-answer-review/resized/page_{page_num:02d}.png"
    if not os.path.exists(image_path):
        print(f"Image {image_path} does not exist!")
        return None

    print(f"Analyzing Page {page_num}...")
    
    prompt = f"""You are a professional math examiner and layout assistant.
Analyze this scanned student math sheet page: {image_path}
Identify:
1. All math questions present on this page (e.g. Q1, Q2, etc.).
2. The student's written steps and final answers for each question.
3. The exact boundaries (vertical coordinates in percentages, 0 to 100) for cropping:
   - The question block itself (excluding student answers).
   - Each individual step written by the student.
4. Carefully grade the student's work step-by-step:
   - Identify the exact step where the student made an error (if any).
   - Write a detailed, friendly explanation of why the step is incorrect.
   - Provide the correct calculation and correct result for that step.

Please return the results in a strict JSON format matching this schema:
{{
  "page": {page_num},
  "questions": [
    {{
      "q_number": "Q6",
      "topic": "Cone curved surface area ratio",
      "question_crop": [y_start_percent, y_end_percent],
      "steps": [
        {{
          "step_number": 1,
          "crop": [y_start_percent, y_end_percent],
          "is_correct": true,
          "student_written_text": "...",
          "feedback": ""
        }},
        {{
          "step_number": 2,
          "crop": [y_start_percent, y_end_percent],
          "is_correct": false,
          "student_written_text": "...",
          "feedback": "Explain why it is wrong and what the correct step should be in clear HTML-friendly math notation using LaTeX like $...$"
        }}
      ]
    }}
  ]
}}

IMPORTANT: Return ONLY the raw JSON object. Do not include markdown code block syntax (like ```json). Ensure that the crop values are realistic y-axis percentages (from 0 to 100) that completely cover the question or step from top to bottom.
"""
    
    try:
        process = subprocess.Popen(
            ["/usr/local/bin/gemini", "--skip-trust", "--prompt", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print(f"Error for Page {page_num}: {stderr}")
            return None
        
        # Clean any markdown block wrap if model outputs it
        res_text = stdout.strip()
        if res_text.startswith("```"):
            lines = res_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            res_text = "\n".join(lines).strip()
            
        try:
            data = json.loads(res_text)
            os.makedirs(cache_dir, exist_ok=True)
            with open(cache_path, "w") as f:
                json.dump(data, f, indent=2)
            return data
        except json.JSONDecodeError:
            print(f"JSON decode error on page {page_num}. Output was:\n{stdout}")
            # Save raw output for debugging
            os.makedirs(cache_dir, exist_ok=True)
            with open(os.path.join(cache_dir, f"page_{page_num:02d}_error.json"), "w") as f:
                f.write(stdout)
            return None
            
    except Exception as e:
        print(f"Exception analyzing Page {page_num}: {e}")
        return None

def main():
    results = {}
    for p in range(1, 14):
        data = analyze_page(p)
        if data:
            results[f"page_{p:02d}"] = data
        else:
            print(f"Failed to analyze Page {p}")
        time.sleep(2) # rate limit buffer
        
    with open("/Users/kenyim/.gemini/antigravity/scratch/math-answer-review/analysis_report.json", "w") as f:
        json.dump(results, f, indent=2)
    print("All pages analyzed. Saved to analysis_report.json")

if __name__ == "__main__":
    main()
