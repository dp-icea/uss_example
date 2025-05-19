from beanie import Document

class Test(Document):
    name: str
    age: int
    email: str

    class Settings:
        name = "test"
