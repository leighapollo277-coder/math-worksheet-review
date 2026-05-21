import os
import json
import time
import subprocess
import glob
from config import CACHE_DIR, RESIZED_DIR, REPORT_PATH

class GeminiPromptRunner:
    def run(self, prompt):
        process = subprocess.Popen(
            ["/usr/local/bin/gemini", "--skip-trust", "--yolo", "--prompt", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"Gemini execution failed: {stderr}")
        return stdout

def analyze_page(page_num, runner=None, cache_dir=CACHE_DIR, resized_dir=RESIZED_DIR):
    if runner is None:
        runner = GeminiPromptRunner()
        
    cache_path = os.path.join(cache_dir, f"page_{page_num:02d}_raw.json")
    if os.path.exists(cache_path):
        print(f"Loading cached analysis for Page {page_num}...")
        try:
            with open(cache_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cache for Page {page_num}: {e}. Re-analyzing...")

    image_path = os.path.join(resized_dir, f"page_{page_num:02d}.png")
    if not os.path.exists(image_path):
        print(f"Image {image_path} does not exist!")
        return None

    print(f"Analyzing Page {page_num}...")
    
    prompt = f"""You are an expert HKDSE Mathematics (Compulsory Part) grader and layout assistant.
Analyze this scanned student math sheet page: {image_path}
Identify:
1. All math questions present on this page (e.g. Q1, Q2, etc.).
2. The student's written steps and final answers for each question.
3. The exact boundaries (vertical coordinates in percentages, 0 to 100) for cropping:
   - The question block itself (excluding student answers).
   - Each individual step written by the student.
4. Carefully grade the student's work step-by-step to help them maximize their score under the HKDSE / HKEAA marking scheme:
   - Identify if the student made a conceptual mistake (Wrong Concept), e.g. using incorrect geometry properties, or using incorrect mathematical notation (such as using chord notation $BC$ instead of arc notation $\overparen{{BC}}$ or "arc BC" for arc length).
   - Point out any Redundant Steps (e.g. writing a full similarity proof when a question only asks to "write down" the similar triangles, wasting time in a timed exam).
   - Check for Lack of Geometric Reasons. If a geometric step is written without standard justifications or with non-standard abbreviations, warn them they will lose "Reason Marks" (usually 1 mark per reason in section A) and provide the correct HKEAA abbreviation in parentheses, such as `(∠ in semi-circle)`, `(opp. ∠s, cyclic quad.)`, `(angles in same segment)`, `(converse of Pythagoras' Theorem)`.
   - Accept alternative valid geometric methods (Alt. Solution) rather than dismissing them. Provide suggestions on alternative shortcuts where appropriate.
   - Always output clean math expressions without vertical string/symbol splitting (e.g. keep angle symbols and numbers together on the same line).
   - EXTREMELY IMPORTANT: Do not hallucinate questions from footers, headers, page numbers, or margin warnings. Do not include page footers (e.g., 'Go on to the next page', 'Answers written in the margins will not be marked', or page numbers) in any crop.
   - For Page 3 specifically, there is ONLY Question 7 on this page. Do NOT extract any other question (such as Q6).
   - For Page 3, Q7 Circle geometry specifically:
     * Validate the student's Step 4 logic ($49^\circ + 41^\circ + 27^\circ + \angle PQS = 180^\circ$) by explicitly stating they can earn full marks in the HKDSE if they add the geometric reason `(opp. ∠s, cyclic quad.)`. Mark this step as correct (is_correct = true) but add feedback warning them about the missing reason.
     * Then, provide the `(∠ in semi-circle)` method strictly as an alternative shortcut: Since $PR$ is a diameter, $\angle PQR = 90^\circ$ `(∠ in semi-circle)`. Thus $\angle PQS + 27^\circ = 90^\circ \implies \angle PQS = 63^\circ$.

Please return the results in a strict JSON format matching this schema:
{{
  "page": {page_num},
  "questions": [
    {{
      "q_number": "Q6",
      "topic": "Cone curved surface area ratio",
      "question_crop": [y_start_percent, y_end_percent],
      "question_alt": "Detailed visual description of the question diagram or text, e.g. 'Diagram of a cone frustum with dimensions'",
      "steps": [
        {{
          "step_number": 1,
          "crop": [y_start_percent, y_end_percent],
          "step_alt": "Detailed description of the student's written work in this step",
          "is_correct": true,
          "student_written_text": "...",
          "feedback": ""
        }},
        {{
          "step_number": 2,
          "crop": [y_start_percent, y_end_percent],
          "step_alt": "Detailed description of the student's written work in this step",
          "is_correct": false,
          "student_written_text": "...",
          "feedback": "Explain why it is wrong or how to improve it, using official HKEAA abbreviations and standard LaTeX."
        }}
      ]
    }}
  ]
}}

IMPORTANT: Return ONLY the raw JSON object. Do not include markdown code block syntax (like ```json). Ensure that the crop values are realistic y-axis percentages (from 0 to 100) that completely cover the question or step from top to bottom.
"""
    
    try:
        stdout = runner.run(prompt)
        # Clean any markdown block wrap and extract raw JSON block
        res_text = stdout.strip()
        start_idx = res_text.find('{')
        end_idx = res_text.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            res_text = res_text[start_idx:end_idx+1]
        elif res_text.startswith("```"):
            lines = res_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            res_text = "\n".join(lines).strip()
            
        try:
            data = json.loads(res_text)
            # Ensure fallbacks for new alt fields
            for q in data.get("questions", []):
                if "question_alt" not in q:
                    q["question_alt"] = f"Diagram for {q.get('topic', 'question')}"
                for s in q.get("steps", []):
                    if "step_alt" not in s:
                        s["step_alt"] = f"Student handwritten step {s.get('step_number', '')}"
            
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

def run_analysis(runner=None, cache_dir=CACHE_DIR, resized_dir=RESIZED_DIR, report_path=REPORT_PATH):
    pattern = os.path.join(resized_dir, "page_*.png")
    files = glob.glob(pattern)
    
    page_numbers = []
    for f in files:
        basename = os.path.basename(f)
        try:
            num_part = basename.split('_')[1].split('.')[0]
            page_numbers.append(int(num_part))
        except Exception:
            continue
            
    page_numbers = sorted(page_numbers)
    if not page_numbers:
        print(f"No resized page images found in {resized_dir}.")
        return {}
        
    print(f"Found {len(page_numbers)} pages to analyze: {page_numbers}")
    
    results = {}
    for p in page_numbers:
        data = analyze_page(p, runner=runner, cache_dir=cache_dir, resized_dir=resized_dir)
        if data:
            results[f"page_{p:02d}"] = data
        else:
            print(f"Failed to analyze Page {p}")
        time.sleep(2) # rate limit buffer
        
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"All pages analyzed. Saved to {report_path}")
    return results

if __name__ == "__main__":
    run_analysis()
