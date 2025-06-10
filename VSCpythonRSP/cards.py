# cards.py
class Card:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Card({self.name})"
