from html.parser import HTMLParser

class DepthCounter(HTMLParser):

    def __init__(self, tag):
        self.depth = 0
        self.counting = "NO"
        self.searchTag = tag
        self.indices = [0, 0]
        super().__init__()

    def handle_starttag(self, tag, attrs):
        if (tag == self.searchTag):
            self.depth += 1

            #Begin counting if not started
            if (self.counting == "NO"):
                self.counting = "UP"
                self.indices[0] = self.getpos()[1] + len(tag) + 2

    def handle_endtag(self, tag):
        if (self.counting == "DOWN" and tag == self.searchTag):
            self.depth -= 1

            #End of parsing
            if (self.depth == 0):
                self.indices[1] = self.getpos()[1]

    def handle_data(self, data):
        if (self.depth > 0):
            self.counting = "DOWN"

    def change_tag(self, tag):
        self.searchTag = tag

def textWithinTag(HTML, tag):
    parser = DepthCounter(tag)
    parser.feed(HTML)
    startIndex, endIndex = parser.indices
    parser.close()

    return HTML[startIndex:endIndex]
