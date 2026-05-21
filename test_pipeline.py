import os
import json
import unittest
import shutil
import tempfile
from PIL import Image
import fitz  # PyMuPDF

import config
import pdf_extractor
import resize_and_preview
import analyze_all
import crop_images
import generate_review

class MockPromptRunner:
    def __init__(self, response_text):
        self.response_text = response_text
        self.calls = []

    def run(self, prompt):
        self.calls.append(prompt)
        return self.response_text

class TestPipeline(unittest.TestCase):
    def setUp(self):
        # Create a temp directory for sandbox testing
        self.test_dir = tempfile.mkdtemp()
        
        # Setup subdirectory paths
        self.raw_dir = os.path.join(self.test_dir, "raw_pages")
        self.resized_dir = os.path.join(self.test_dir, "resized")
        self.cache_dir = os.path.join(self.test_dir, "analysis_cache")
        self.images_dir = os.path.join(self.test_dir, "images")
        
        os.makedirs(self.raw_dir)
        os.makedirs(self.resized_dir)
        os.makedirs(self.cache_dir)
        os.makedirs(self.images_dir)
        
        # Paths
        self.report_path = os.path.join(self.test_dir, "analysis_report.json")
        self.index_path = os.path.join(self.test_dir, "index.html")

    def tearDown(self):
        # Remove temp directory sandbox
        shutil.rmtree(self.test_dir)

    def test_pdf_extraction(self):
        # Create a 2-page dummy PDF using PyMuPDF
        pdf_path = os.path.join(self.test_dir, "dummy.pdf")
        doc = fitz.open()
        doc.new_page(width=595, height=842) # A4 dimensions
        doc.new_page(width=595, height=842)
        doc.save(pdf_path)
        doc.close()
        
        # Run extraction
        generated_files = pdf_extractor.extract_pdf_pages(pdf_path, self.raw_dir, dpi=72)
        
        self.assertEqual(len(generated_files), 2)
        self.assertTrue(os.path.exists(os.path.join(self.raw_dir, "page_01.png")))
        self.assertTrue(os.path.exists(os.path.join(self.raw_dir, "page_02.png")))

    def test_image_resizing(self):
        # Create a large dummy image
        img_path = os.path.join(self.raw_dir, "page_01.png")
        img = Image.new("RGB", (2000, 1600), color="white")
        img.save(img_path)
        
        # Run resizing
        resize_and_preview.resize_images(self.raw_dir, self.resized_dir, target_width=1000)
        
        resized_path = os.path.join(self.resized_dir, "page_01.png")
        self.assertTrue(os.path.exists(resized_path))
        with Image.open(resized_path) as resized_img:
            self.assertEqual(resized_img.size, (1000, 800))

    def test_analysis_with_mock_runner(self):
        # Setup resized page image
        img_path = os.path.join(self.resized_dir, "page_01.png")
        img = Image.new("RGB", (1000, 1000), color="white")
        img.save(img_path)
        
        mock_json_response = """
        {
          "page": 1,
          "questions": [
            {
              "q_number": "Q1",
              "topic": "Angles",
              "question_crop": [10, 30],
              "steps": [
                {
                  "step_number": 1,
                  "crop": [35, 60],
                  "is_correct": true,
                  "student_written_text": "x = 45",
                  "feedback": ""
                }
              ]
            }
          ]
        }
        """
        runner = MockPromptRunner(mock_json_response)
        
        # Analyze page
        data = analyze_all.analyze_page(1, runner=runner, cache_dir=self.cache_dir, resized_dir=self.resized_dir)
        
        self.assertIsNotNone(data)
        self.assertEqual(data["page"], 1)
        self.assertEqual(len(data["questions"]), 1)
        self.assertEqual(data["questions"][0]["q_number"], "Q1")
        
        # Verify cache file creation
        self.assertTrue(os.path.exists(os.path.join(self.cache_dir, "page_01_raw.json")))

    def test_cropping_assets(self):
        # Create image
        img_path = os.path.join(self.resized_dir, "page_01.png")
        img = Image.new("RGB", (1000, 1000), color="blue")
        img.save(img_path)
        
        page_data = {
            "page": 1,
            "questions": [
                {
                    "q_number": "Q1",
                    "question_crop": [10, 30],
                    "steps": [
                        {
                            "step_number": 1,
                            "crop": [40, 70]
                        }
                    ]
                }
            ]
        }
        
        # Crop elements
        success = crop_images.crop_page_assets(page_data, img_path, self.images_dir)
        self.assertTrue(success)
        
        # Verify files generated
        self.assertTrue(os.path.exists(os.path.join(self.images_dir, "page_01_Q1_question.png")))
        self.assertTrue(os.path.exists(os.path.join(self.images_dir, "page_01_Q1_step_1.png")))

    def test_html_generation(self):
        pages_data = [
            {
                "page": 1,
                "questions": [
                    {
                        "q_number": "Q1",
                        "topic": "Geometry",
                        "question_crop": [10, 30],
                        "steps": [
                            {
                                "step_number": 1,
                                "crop": [40, 70],
                                "is_correct": False,
                                "feedback": "Needs improvement"
                            }
                        ]
                    }
                ]
            }
        ]
        
        # Write compile JSON
        with open(self.report_path, "w") as f:
            json.dump({"page_01": pages_data[0]}, f)
            
        # Run generator
        success = generate_review.run_generation(
            cache_dir=self.cache_dir,
            compiled_path=self.report_path,
            dest_path=self.index_path,
            workspace_dir=self.test_dir
        )
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.index_path))
        
        # Check that KaTeX and generated content exist in HTML file
        with open(self.index_path, "r") as f:
            html = f.read()
            self.assertIn("KaTeX", html)
            self.assertIn("Geometry", html)
            self.assertIn("Needs improvement", html)

if __name__ == "__main__":
    unittest.main()
