# MODULO EVENTS

class Event:

    def __init__(self, sender, description, other=None) -> None:
        self.sender = sender
        self.description = description
        self.other = other

    def get_sender(self): return self.sender
    def get_description(self): return self.description
    def get_other(self): return self.other

    def __str__(self) -> str:
        return f"<sender={self.sender}, description={self.description}, other={self.other}>"