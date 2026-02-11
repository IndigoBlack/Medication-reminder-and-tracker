from flask import Flask

# Medication scheduling. Mabe use google calender for this
# Track Whether the user has taken their medicine

app = Flask(__name__)

@app.route("/")
def main():
    ...