import os
import glob
import json
from config import WORKSPACE_DIR, CACHE_DIR, REPORT_PATH, INDEX_PATH

def load_all_data(cache_dir, compiled_path):
    """
    Load analysis data from cache files or compiled report.
    Returns a sorted list of page analysis dictionaries.
    """
    pages_data = []
    
    # Try reading the compiled path first
    if os.path.exists(compiled_path):
        try:
            with open(compiled_path, "r") as f:
                data = json.load(f)
                # If structure is {"page_01": {...}, "page_02": {...}}
                if isinstance(data, dict):
                    sorted_keys = sorted(data.keys())
                    for k in sorted_keys:
                        pages_data.append(data[k])
                    return pages_data
        except Exception as e:
            print(f"Error loading compiled report: {e}. Falling back to cache files...")
            
    # Fallback to reading raw files in cache_dir
    json_files = sorted(glob.glob(os.path.join(cache_dir, "page_*_raw.json")))
    for path in json_files:
        try:
            with open(path, "r") as f:
                page_data = json.load(f)
                pages_data.append(page_data)
        except Exception as e:
            print(f"Error reading {path}: {e}")
            
    return pages_data

def clean_latex_escapes(text):
    if not isinstance(text, str):
        return text
    # Replace control character representations of LaTeX backslash sequences
    text = text.replace('\x0c', '\\f')
    return text

def generate_html_content(pages_data, workspace_dir=WORKSPACE_DIR):
    """
    Generate the HTML string based on pages data.
    """
    # Compute stats
    total_questions = 0
    total_steps = 0
    total_errors = 0
    
    sidebar_links = []
    main_feed = []
    
    for page_data in pages_data:
        page_num = page_data.get("page")
        page_str = f"page_{page_num:02d}"
        
        page_questions_html = []
        
        for q in page_data.get("questions", []):
            total_questions += 1
            q_num = q.get("q_number")
            topic = q.get("topic", "Math Question")
            q_id = f"{page_str}_{q_num}"
            
            # Check correctness of question steps
            has_error = False
            steps_html = []
            
            for step in q.get("steps", []):
                total_steps += 1
                step_num = step.get("step_number")
                is_correct = step.get("is_correct", True)
                written_text = clean_latex_escapes(step.get("student_written_text", ""))
                feedback = clean_latex_escapes(step.get("feedback", ""))
                
                step_img_name = f"{page_str}_{q_num}_step_{step_num}.png"
                step_img_path = f"images/{step_img_name}"
                
                # Check if step image exists to prevent broken images
                step_img_exists = os.path.exists(os.path.join(workspace_dir, step_img_path))
                step_alt_text = step.get("step_alt", f"Step {step_num} solution").replace('"', '&quot;')
                img_tag = f'<img src="{step_img_path}" alt="{step_alt_text}" class="step-image">' if step_img_exists else f'<div class="no-image">Step {step_num} Crop Image Not Found</div>'
                
                if not is_correct:
                    total_errors += 1
                    has_error = True
                    badge = '<span class="badge error-badge">⚠️ Error Detected</span>'
                    feedback_card = f"""
                    <div class="feedback-card">
                        <div class="feedback-header">
                            <svg class="warning-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                            <span>Teacher / AI Grading Feedback</span>
                        </div>
                        <div class="feedback-body">
                            {feedback}
                        </div>
                    </div>
                    """
                else:
                    badge = '<span class="badge success-badge">✓ Correct</span>'
                    if feedback.strip():
                        feedback_card = f"""
                        <div class="feedback-card info-card">
                            <div class="feedback-header">
                                <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                <span>HKDSE Exam Tips & Suggestions</span>
                            </div>
                            <div class="feedback-body">
                                {feedback}
                            </div>
                        </div>
                        """
                    else:
                        feedback_card = ""
                    
                steps_html.append(f"""
                <div class="step-container">
                    <div class="step-header">
                        <h4>Step {step_num}</h4>
                        {badge}
                    </div>
                    <div class="step-body">
                        {img_tag}
                        {feedback_card}
                    </div>
                </div>
                """)
                
            # Question Crop
            q_img_name = f"{page_str}_{q_num}_question.png"
            q_img_path = f"images/{q_img_name}"
            q_img_exists = os.path.exists(os.path.join(workspace_dir, q_img_path))
            q_alt_text = q.get("question_alt", f"Diagram/text for {topic}").replace('"', '&quot;')
            q_img_tag = f'<img src="{q_img_path}" alt="{q_alt_text}" class="question-image">' if q_img_exists else f'<div class="no-image">Question Text Crop Not Found</div>'
            
            q_status_class = "error-card" if has_error else "success-card"
            sidebar_status_class = "sidebar-error" if has_error else "sidebar-success"
            sidebar_status_badge = "⚠️" if has_error else "✓"
            
            sidebar_links.append(f"""
            <a href="#{q_id}" class="sidebar-item {sidebar_status_class}">
                <div class="sidebar-item-info">
                    <span class="sidebar-q-num">Page {page_num} - {q_num}</span>
                    <span class="sidebar-topic">{topic}</span>
                </div>
                <span class="sidebar-badge">{sidebar_status_badge}</span>
            </a>
            """)
            
            joined_steps = "\n".join(steps_html)
            page_questions_html.append(f"""
            <div id="{q_id}" class="question-card glass-card {q_status_class}">
                <div class="question-header">
                    <h2>{q_num} <span class="topic-label">{topic}</span></h2>
                    <span class="page-badge">Page {page_num}</span>
                </div>
                <div class="question-content">
                    {q_img_tag}
                    <div class="steps-section">
                        <h3>Student Working Steps</h3>
                        {joined_steps}
                    </div>
                </div>
            </div>
            """)
            
        page_questions_joined = "\n".join(page_questions_html)
        main_feed.append(f"""
        <section class="page-section">
            <h2 class="section-title">Page {page_num} Worksheets</h2>
            {page_questions_joined}
        </section>
        """)

    # Statistics Calculation
    accuracy = int((total_questions - total_errors) / total_questions * 100) if total_questions > 0 else 100
    
    # Append Student Performance Diagnostics summary to sidebar
    sidebar_links.append("""
    <a href="#student-summary" class="sidebar-item sidebar-summary-link" style="margin-top: 16px; border-top: 1px solid var(--border-color); padding-top: 20px;">
        <div class="sidebar-item-info">
            <span class="sidebar-q-num" style="color: #a5b4fc;">📊 Diagnostics Summary</span>
            <span class="sidebar-topic">Weaknesses & Focus Areas</span>
        </div>
        <span class="sidebar-badge" style="color: #a5b4fc;">★</span>
    </a>
    """)
    
    # Append Student Performance Diagnostics card to main feed
    main_feed.append("""
    <section class="page-section" id="student-summary">
        <h2 class="section-title">HKDSE Performance Diagnostics</h2>
        <div class="question-card glass-card student-summary-card">
            <div class="question-header">
                <h2>
                    <svg class="summary-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                    </svg>
                    Student Performance Diagnostics & Revision Guide
                </h2>
                <span class="page-badge">HKDSE Compulsory Part</span>
            </div>
            
            <div class="summary-content">
                <div class="summary-section">
                    <h3 class="summary-subtitle text-error">⚠️ Identified Weaknesses</h3>
                    <ul class="summary-list">
                        <li><strong>Frequent Omission of Geometric Reasons:</strong> The candidate understands circle geometry theorems and carries out calculations correctly, but consistently omits the geometric reasons in parentheses. In the HKDSE exam, this leads to a direct loss of "Reason Marks" (typically 1 mark per reason in Section A). Specific instances:
                            <ul>
                                <li>Page 1 (Q8b): Proved chords perpendicular using Pythagoras' theorem but omitted the reason <code>(converse of Pythagoras' Theorem)</code>.</li>
                                <li>Page 2 (Q13a &amp; b): Applied <code>(opp. ∠s, cyclic quad.)</code>, <code>(∠ in semi-circle)</code>, and <code>(∠ at centre twice ∠ at circum.)</code> without writing down any justifications.</li>
                                <li>Page 3 (Q7): Set up the cyclic quadrilateral equation without stating <code>(opp. ∠s, cyclic quad.)</code>.</li>
                            </ul>
                        </li>
                        <li><strong>Redundant Working Steps:</strong> The student spends valuable exam time writing down complete multi-line similarity proofs (e.g. Page 1, Q8a proving similarity by AAA) when the question command is only "Write down", which only requires stating the similarity statement itself (e.g., $\\triangle ABE \\sim \\triangle DCE$) without proof.</li>
                        <li><strong>Notation Ambiguity (Chord vs. Arc):</strong> In Page 2 (Q13b), the candidate uses the notation $BC$ to refer to the arc length when calculating the sector perimeter. In standard HKDSE notation, $BC$ represents the straight-line chord length, whereas the arc should be denoted as $\\overset{\\frown}{BC}$ or "arc BC". This ambiguity could lead to marks deduction.</li>
                    </ul>
                </div>
                
                <div class="summary-section">
                    <h3 class="summary-subtitle text-success">🎯 Revision Topics & Focusing Areas</h3>
                    <ul class="summary-list">
                        <li><strong>HKEAA Standard Geometric Reasons:</strong>
                            <ul>
                                <li>Thoroughly revise and memorize the list of HKEAA-approved geometric reasons and their official abbreviations (e.g. <code>(opp. ∠s, cyclic quad.)</code>, <code>(∠ in semi-circle)</code>, <code>(converse of Pythagoras' Theorem)</code>, <code>(angles in same segment)</code>, <code>(alt. ∠s, BC // OD)</code>).</li>
                                <li>Establish a habit of writing a matching reason in parentheses immediately after every geometric statement.</li>
                            </ul>
                        </li>
                        <li><strong>Exam Command Verb Recognition:</strong>
                            <ul>
                                <li>Understand what HKEAA command verbs imply to manage time effectively: <strong>"Write down"</strong> means state the answer directly with 0 steps; <strong>"Find / Calculate"</strong> requires calculation working; <strong>"Explain / Prove"</strong> requires full working alongside geometric reasons.</li>
                            </ul>
                        </li>
                        <li><strong>Formal Geometric Notation:</strong>
                            <ul>
                                <li>Differentiate chord lengths from arc lengths using standard notation ($\\overset{\\frown}{BC}$ or $\\text{arc } BC$) and ensure triangles are named in the correct order of corresponding vertices (e.g., $\\triangle ABE \\sim \\triangle DCE$).</li>
                            </ul>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </section>
    """)
    
    sidebar_links_joined = "\n".join(sidebar_links)
    main_feed_joined = "\n".join(main_feed)
    
    # Assembly
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DSE Circle Geometry Grader — AI-Powered HKDSE Answer Review</title>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- KaTeX for Beautiful Math Equations -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body, {{
        delimiters: [
            {{left: '$$', right: '$$', display: true}},
            {{left: '$', right: '$', display: false}}
        ]
    }});"></script>

    <style>
        :root {{
            --bg-base: #0b0f19;
            --bg-surface: rgba(17, 24, 39, 0.7);
            --bg-card-err: rgba(239, 68, 68, 0.05);
            --bg-card-ok: rgba(16, 185, 129, 0.03);
            --border-color: rgba(255, 255, 255, 0.08);
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --primary: #6366f1;
            --success: #10b981;
            --error: #ef4444;
            --error-light: rgba(239, 68, 68, 0.15);
            --success-light: rgba(16, 185, 129, 0.15);
            --font-outfit: 'Outfit', sans-serif;
            --font-inter: 'Inter', sans-serif;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background: radial-gradient(circle at top right, #1e1b4b 0%, var(--bg-base) 60%);
            color: var(--text-primary);
            font-family: var(--font-inter);
            min-height: 100vh;
            display: flex;
            overflow-x: hidden;
        }}

        /* App Layout */
        .sidebar {{
            width: 340px;
            height: 100vh;
            position: fixed;
            left: 0;
            top: 0;
            background: rgba(11, 15, 25, 0.85);
            backdrop-filter: blur(20px);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            z-index: 100;
        }}

        .sidebar-header {{
            padding: 24px;
            border-bottom: 1px solid var(--border-color);
        }}

        .sidebar-header h1 {{
            font-family: var(--font-outfit);
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.5px;
            background: linear-gradient(to right, #a5b4fc, #6366f1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .sidebar-header p {{
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 4px;
        }}

        .sidebar-menu {{
            flex-grow: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .sidebar-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 16px;
            border-radius: 12px;
            text-decoration: none;
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid transparent;
            transition: all 0.2s ease;
        }}

        .sidebar-item:hover {{
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(255, 255, 255, 0.05);
            transform: translateX(4px);
        }}

        .sidebar-item-info {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}

        .sidebar-q-num {{
            font-family: var(--font-outfit);
            font-size: 14px;
            font-weight: 600;
        }}

        .sidebar-topic {{
            font-size: 11px;
            color: var(--text-secondary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 220px;
        }}

        .sidebar-badge {{
            font-size: 14px;
            font-weight: bold;
        }}

        .sidebar-success .sidebar-badge {{
            color: var(--success);
        }}

        .sidebar-error .sidebar-badge {{
            color: var(--error);
        }}

        .sidebar-error {{
            background: rgba(239, 68, 68, 0.03);
            border-left: 3px solid var(--error);
        }}

        .main-content {{
            margin-left: 340px;
            flex-grow: 1;
            padding: 40px 60px;
            max-width: 1200px;
            min-height: 100vh;
        }}

        /* Dashboard Banner */
        .dashboard-header {{
            margin-bottom: 40px;
        }}

        .dashboard-title {{
            font-family: var(--font-outfit);
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 24px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }}

        .stat-card {{
            background: var(--bg-surface);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 20px 24px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .stat-label {{
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
        }}

        .stat-value {{
            font-family: var(--font-outfit);
            font-size: 36px;
            font-weight: 700;
        }}

        .stat-card:nth-child(2) .stat-value {{
            color: var(--error);
        }}

        .stat-card:nth-child(3) .stat-value {{
            color: var(--success);
        }}

        /* Question Feed */
        .page-section {{
            margin-bottom: 60px;
        }}

        .section-title {{
            font-family: var(--font-outfit);
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 24px;
            color: var(--text-secondary);
            border-left: 4px solid var(--primary);
            padding-left: 12px;
        }}

        .glass-card {{
            background: var(--bg-surface);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 32px;
            margin-bottom: 40px;
            box-shadow: 0 10px 40px -10px rgba(0,0,0,0.5);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .glass-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(99, 102, 241, 0.25);
            box-shadow: 0 20px 45px -12px rgba(0,0,0,0.6);
        }}

        .error-card {{
            border-top: 4px solid var(--error);
            background: linear-gradient(to bottom, var(--bg-card-err), var(--bg-surface));
        }}

        .success-card {{
            border-top: 4px solid var(--success);
            background: linear-gradient(to bottom, var(--bg-card-ok), var(--bg-surface));
        }}

        .question-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
        }}

        .question-header h2 {{
            font-family: var(--font-outfit);
            font-size: 24px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .topic-label {{
            font-size: 14px;
            font-weight: 500;
            color: var(--text-secondary);
            background: rgba(255, 255, 255, 0.05);
            padding: 4px 12px;
            border-radius: 20px;
        }}

        .page-badge {{
            font-size: 12px;
            font-weight: 600;
            background: rgba(99, 102, 241, 0.15);
            color: #a5b4fc;
            padding: 4px 10px;
            border-radius: 8px;
        }}

        /* Images and Display */
        .question-image {{
            max-width: 100%;
            height: auto;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            margin-bottom: 32px;
            display: block;
        }}

        .no-image {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px dashed var(--border-color);
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            font-size: 14px;
            color: var(--text-secondary);
            margin-bottom: 24px;
        }}

        .steps-section h3 {{
            font-family: var(--font-outfit);
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
            color: var(--text-secondary);
        }}

        .step-container {{
            background: rgba(255, 255, 255, 0.015);
            border: 1px solid rgba(255, 255, 255, 0.04);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 24px;
        }}

        .step-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }}

        .step-header h4 {{
            font-family: var(--font-outfit);
            font-size: 15px;
            font-weight: 600;
        }}

        .badge {{
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 20px;
        }}

        .success-badge {{
            background: var(--success-light);
            color: #34d399;
        }}

        .error-badge {{
            background: var(--error-light);
            color: #f87171;
        }}

        .step-image {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }}

        /* Feedback cards */
        .feedback-card {{
            background: rgba(239, 68, 68, 0.06);
            border: 1px solid rgba(239, 68, 68, 0.15);
            border-radius: 12px;
            padding: 16px;
            margin-top: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .feedback-card.info-card {{
            background: rgba(59, 130, 246, 0.06);
            border: 1px solid rgba(59, 130, 246, 0.15);
        }}

        .feedback-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: #f87171;
            font-weight: 600;
            font-size: 13px;
        }}

        .feedback-card.info-card .feedback-header {{
            color: #60a5fa;
        }}

        .warning-icon, .info-icon {{
            width: 16px;
            height: 16px;
        }}

        .feedback-body {{
            font-size: 13px;
            line-height: 1.6;
            color: #fca5a5;
        }}

        .feedback-card.info-card .feedback-body {{
            color: #93c5fd;
        }}

        /* Summary Card Styling */
        .student-summary-card {{
            border-top: 4px solid var(--primary) !important;
            background: linear-gradient(to bottom, rgba(99, 102, 241, 0.05), var(--bg-surface)) !important;
        }}

        .summary-icon {{
            color: #818cf8;
        }}

        .summary-content {{
            display: flex;
            flex-direction: column;
            gap: 32px;
            margin-top: 24px;
        }}

        .summary-subtitle {{
            font-family: var(--font-outfit);
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .text-error {{
            color: #f87171;
        }}

        .text-success {{
            color: #34d399;
        }}

        .summary-list {{
            list-style-type: none;
            padding-left: 0;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .summary-list > li {{
            position: relative;
            padding-left: 20px;
            font-size: 14px;
            line-height: 1.6;
            color: var(--text-primary);
        }}

        .summary-list > li::before {{
            content: "•";
            position: absolute;
            left: 0;
            top: 0;
            color: var(--primary);
            font-size: 18px;
            line-height: 1;
        }}

        .summary-list ul {{
            list-style-type: none;
            padding-left: 0;
            margin-top: 8px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .summary-list ul li {{
            position: relative;
            padding-left: 16px;
            font-size: 13px;
            color: var(--text-secondary);
        }}

        .summary-list ul li::before {{
            content: "└";
            position: absolute;
            left: 0;
            top: -2px;
            color: rgba(255, 255, 255, 0.15);
        }}

        /* Responsive styling */
        @media (max-width: 1024px) {{
            body {{
                flex-direction: column;
            }}

            .sidebar {{
                width: 100%;
                height: auto;
                position: static;
                border-right: none;
                border-bottom: 1px solid var(--border-color);
            }}

            .sidebar-menu {{
                max-height: 240px;
            }}

            .main-content {{
                margin-left: 0;
                padding: 30px 20px;
            }}

            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>

    <!-- Sidebar Navigation -->
    <aside class="sidebar">
        <div class="sidebar-header">
            <h1>Math Review Grading</h1>
            <p>Worksheet Question Layout & Analysis</p>
        </div>
        <div class="sidebar-menu">
            {sidebar_links_joined}
        </div>
    </aside>

    <!-- Main Workspace -->
    <main class="main-content">
        <header class="dashboard-header">
            <h1 class="dashboard-title">DSE Circle Geometry Grader</h1>
            
            <!-- Dashboard Stats -->
            <div class="stats-grid">
                <div class="stat-card">
                    <span class="stat-label">Reviewed Problems</span>
                    <span class="stat-value">{total_questions}</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label">Revisions Needed</span>
                    <span class="stat-value">{total_errors}</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label">Concept Mastery</span>
                    <span class="stat-value">{accuracy}%</span>
                </div>
            </div>
        </header>

        <!-- Dynamic Worksheet Reviews -->
        {main_feed_joined}
    </main>

</body>
</html>
"""
    return html_template

def run_generation(cache_dir=CACHE_DIR, compiled_path=REPORT_PATH, dest_path=INDEX_PATH, workspace_dir=WORKSPACE_DIR):
    print("Loading data...")
    pages_data = load_all_data(cache_dir, compiled_path)
    
    if not pages_data:
        print("No analysis data loaded.")
        return False
        
    print(f"Loaded grading data for {len(pages_data)} pages. Generating HTML...")
    html_content = generate_html_content(pages_data, workspace_dir=workspace_dir)
    
    with open(dest_path, "w") as f:
        f.write(html_content)
        
    print(f"Successfully generated review portal at: {dest_path}")
    return True

def main():
    run_generation()

if __name__ == "__main__":
    main()
