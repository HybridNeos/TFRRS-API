class EventSwitcher(object):
    def parseEventMark(self, eventType, mark):
        method = getattr(self, eventType, lambda: "Invalid event")
        return method(mark)

    def SP(self, mark):
        return mark if mark.isalpha() else mark.split(" ")[0]

    def DT(self, mark):
        return mark if mark.isalpha() else mark.split(" ")[0]

    def HT(self, mark):
        return mark if mark.isalpha() else mark.split(" ")[0]

    def WT(self, mark):
        return mark if mark.isalpha() else mark.split(" ")[0]
