import unittest
import os
import sys

# Add current dir to path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crop_images import calculate_crop_box
from generate_review import generate_html_content

class TestMathReviewGenerator(unittest.TestCase):

    def test_calculate_crop_box_valid(self):
        """Test crop calculations with standard bounds and padding."""
        width = 1000
        height = 1000
        y_start_pct = 10.0
        y_end_pct = 20.0
        padding_pct = 1.0
        
        # Expected:
        # y_start = 10% * 1000 = 100px. y_start - (1% * 1000) = 100 - 10 = 90px
        # y_end = 20% * 1000 = 200px. y_end + (1% * 1000) = 200 + 10 = 210px
        # Return format: (0, y_start, width, y_end)
        box = calculate_crop_box(width, height, y_start_pct, y_end_pct, padding_pct)
        self.assertEqual(box, (0, 90, 1000, 210))

    def test_calculate_crop_box_clamps_boundaries(self):
        """Test that crop box bounds never exceed the image coordinates."""
        width = 1000
        height = 1000
        
        # Extreme upper edge
        box_top = calculate_crop_box(width, height, 0.5, 5.0, padding_pct=1.0)
        self.assertEqual(box_top[1], 0)  # Should clamp to 0 instead of -5
        
        # Extreme lower edge
        box_bottom = calculate_crop_box(width, height, 95.0, 99.5, padding_pct=1.0)
        self.assertEqual(box_bottom[3], 1000)  # Should clamp to 1000 instead of 1005

    def test_html_generator_stats(self):
        """Test that generated HTML contains required styling and structures."""
        sample_pages_data = [
            {
                "page": 1,
                "questions": [
                    {
                        "q_number": "Q1",
                        "topic": "Volume computation",
                        "question_crop": [5.0, 15.0],
                        "steps": [
                            {
                                "step_number": 1,
                                "crop": [15.0, 25.0],
                                "is_correct": True,
                                "student_written_text": "5 * 5 = 25",
                                "feedback": ""
                            },
                            {
                                "step_number": 2,
                                "crop": [25.0, 35.0],
                                "is_correct": False,
                                "student_written_text": "25 * 3 = 85",
                                "feedback": "Calculation should be $25 \\times 3 = 75$."
                            }
                        ]
                    }
                ]
            }
        ]
        
        html_str = generate_html_content(sample_pages_data)
        
        # Verify KaTeX imports are included
        self.assertIn("katex.min.css", html_str)
        self.assertIn("katex.min.js", html_str)
        self.assertIn("renderMathInElement", html_str)
        
        # Verify structure
        self.assertIn("Volume computation", html_str)
        self.assertIn("Q1", html_str)
        self.assertIn("Step 1", html_str)
        self.assertIn("Step 2", html_str)
        self.assertIn("Error Detected", html_str)
        self.assertIn("Calculation should be", html_str)

if __name__ == "__main__":
    unittest.main()
