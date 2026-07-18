from dotenv import load_dotenv
import os

from curve.login import login

load_dotenv()


username = os.getenv("CURVE_LOGIN")
password = os.getenv("CURVE_PASSWORD")

if not username or not password:
    raise ValueError("CURVE_LOGIN and CURVE_PWD must be set in .env file")

if __name__ == '__main__':
    login(username, password)

