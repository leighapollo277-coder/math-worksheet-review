import os
import json
import sys

def validate():
    report_path = "analysis_report.json"
    if not os.path.exists(report_path):
        print(f"Report file {report_path} not found. Skipping validation.")
        return 0

    with open(report_path, "r") as f:
        try:
            report_data = json.load(f)
        except Exception as e:
            print(f"Error reading report JSON: {e}")
            return 1

    circle_keywords = ["circle", "chord", "arc", "diameter", "tangent", "cyclic", "circumference", "subtended", "semicircle"]
    non_circle_topics = ["algebra", "percentage", "hemisphere", "cone", "rectangle", "frustum", "parallelogram", "triangle"]

    mismatch_found = False

    for page_key, page_data in report_data.items():
        questions = page_data.get("questions", [])
        for q in questions:
            topic = q.get("topic", "").lower()
            q_num = q.get("q_number", "Unknown")
            q_alt = q.get("question_alt", "").lower()
            
            # Combine student feedback or written steps to inspect
            feedback_text = ""
            for step in q.get("steps", []):
                feedback_text += " " + step.get("feedback", "").lower()
                feedback_text += " " + step.get("student_written_text", "").lower()

            # Check: If the topic belongs to non-circle math but the diagram description contains circle keywords
            is_non_circle_topic = any(k in topic for k in non_circle_topics)
            has_circle_diagram = any(k in q_alt for k in circle_keywords) or any(k in feedback_text for k in circle_keywords)

            # Exception: if topic explicitly contains circle, it is a circle topic
            if "circle" in topic:
                is_non_circle_topic = False

            if is_non_circle_topic and has_circle_diagram:
                print(f"[MISMATCH] Page: {page_key}, Question: {q_num}")
                print(f"  Topic: '{q.get('topic')}'")
                print(f"  Alt Text: '{q.get('question_alt')}'")
                print(f"  Visual features indicate circle geometry, mismatching the non-circle topic.")
                mismatch_found = True

    if mismatch_found:
        print("Validation FAILED: Visual-semantic mismatches were detected.")
        return 1
    else:
        print("Validation PASSED: All topics match visual descriptions.")
        return 0

if __name__ == "__main__":
    sys.exit(validate())
