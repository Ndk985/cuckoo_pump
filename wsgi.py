import os
print("DATABASE_URL =", os.getenv("DATABASE_URL"))   # <-- добавьте

from cp_app import app

if __name__ == "__main__":
    app.run()
