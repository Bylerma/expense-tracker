from datetime import datetime

class Expense:
    def __init__(self, id=None, amount=0, category="", description="", date=None):
        self.id = id
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date if date else datetime.now()
    
    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date.strftime("%Y-%m-%d")
        }