from myParser import textWithinTag
import unittest

class TestWithingTag(unittest.TestCase):

    def test_basic(self):
        HTML = "<body>basic test</body>"
        self.assertEqual(textWithinTag(HTML, "body"), "basic test")

    @unittest.expectedFailure
    def test_basicWithDecorator(self):
        HTML = "<body style=\"background-color: blue\">basic test</body>"
        self.assertEqual(textWithinTag(HTML, "body"), "basic test")

    def test_innerTag(self):
        HTML = "<p><span><div>inner test</div></span></p>"
        self.assertEqual(textWithinTag(HTML, "span"), "<div>inner test</div>")

    def test_repeatedTag(self):
        HTML = "<body><div><p><div>repeated test</div></p></div></body>"
        self.assertEqual(textWithinTag(HTML, "div"), "<p><div>repeated test</div></p>")

    @unittest.expectedFailure
    def test_repeatedExtraData(self):
        HTML = "<body><div>extra data <p><div>repeated test</div></p></div></body>"
        self.assertEqual(textWithinTag(HTML, "div"), "<p><div>repeated test</div></p>")

if __name__ == '__main__':
    unittest.main()
