import unittest
import os
from parsons import GoogleSlides

# Test Slides: https://docs.google.com/presentation/d/19I-kicyaJV53KoPNwt77KJL10fHzWFdZ_c2mW4XJaxc
slides_id = "19I-kicyaJV53KoPNwt77KJL10fHzWFdZ_c2mW4XJaxc"

class TestGoogleSlides(unittest.TestCase):
    def setUp(self):

        self.gs = GoogleSlides()

        # we're going to grab our Test Slides and drop all slides beyond #1 & 2
        presentation = self.gs.get_presentation(slides_id)
        self.presentation_id = presentation["presentationId"]
        for i in range(len(presentation["slides"])):
            if (i + 1) > 2:
                self.gs.delete_slide(slides_id, i + 1)

    def test_get_presentation(self):
        p = self.gs.get_presentation(slides_id)
        self.assertEqual(9144000, p["pageSize"]["width"]["magnitude"])

    def test_get_slide(self):
        s = self.gs.get_slide(slides_id, 2)
        self.assertEqual("g26d1b1fa556_2_0", s["objectId"])

    def test_duplicate_slide(self):
        # duplicating slide #2 to create 3 slides
        self.gs.duplicate_slide(slides_id, 2)
        p = self.gs.get_presentation(slides_id)
        self.assertEqual(3, len(p["slides"]))

    def test_replace_slide_text(self):
        presentation_id = slides_id
        slide_number = 3
        original_text = "Replace Text"
        replace_text = "Parsons is Fun"
        self.gs.replace_slide_text(
            presentation_id, slide_number, original_text, replace_text
        )

        s = self.gs.get_slide(presentation_id, slide_number)
        content = s["pageElements"][0]["shape"]["text"]["textElements"][1]["textRun"][
            "content"
        ]
        self.assertTrue(True, "Parsons is Fun" in content)

    def test_get_slide_images(self):
        presentation_id = slides_id
        slide_number = 2
        img = self.gs.get_slide_images(presentation_id, slide_number)
        height = img[0]["size"]["height"]["magnitude"]
        self.assertEqual(7825, height)

    def test_replace_slide_image(self):
        presentation_id = slides_id
        img = self.gs.get_slide_images(presentation_id, 2)
        image_obj = img[0]
        new_image_url = "https://media.tenor.com/yxJYCVXImqYAAAAM/westwing-josh.gif"

        self.gs.replace_slide_image(presentation_id, 3, image_obj, new_image_url)
        img = self.gs.get_slide_images(presentation_id, 3)
        self.assertTrue(True, img[0]["image"]["sourceUrl"] == new_image_url)
