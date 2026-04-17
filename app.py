import math
import re
import time
from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = "portfolio-static-key-not-auth-sensitive"

COMMON_PASSWORDS = {
    "123456","password","123456789","12345678","12345","1234567","1234567890",
    "qwerty","abc123","million2","000000","1234","iloveyou","aaron431","password1",
    "qqww1122","123","omgpop","123321","654321","qwertyuiop","qwerty123","1q2w3e4r",
    "666666","987654321","999999","111111","123123","superman","qwe123","11111",
    "sunshine","princess","welcome","shadow","12341234","monkey","dragon","master",
    "letmein","football","michael","baseball","jordan23","starwars","hello","charlie",
    "donald","password2","qwerty1","1111111","1111","mustang","access","batman",
    "trustno1","hunter2","hunter","ranger","robert","thomas","thomas1","george",
    "jessica","andrew","asshole","fuckyou","biteme","cheese","coffee","buster",
    "pepper","ginger","test1234","test","secret","admin","login","pass","passw0rd",
    "123qwe","!@#$%^&*","abc","zxcvbn","qazwsx","asdfgh","zxcvbnm","asdfghjkl",
    "password123","iloveyou1","abc1234","qwert","123654","456789","1234qwer","pass123",
    "mypassword","computer","internet","samsung","nintendo","minecraft","pokemon",
    "whatever","changeme","letmein1","mother","jesus","love","jordan","freedom",
    "flower","cookie","matrix","cowboys","harley","ranger1","thunder","hockey",
    "soccer","baseball1","football1","golfer","eagle","hunter1","yellow","orange",
    "silver","purple","butter","please","hello123","money","system","black","white",
    "green","blue","red","pink","gold","love123","sexy","sex","2000","1000","2020",
    "2021","2022","2023","2024","superman1","batman1","spiderman","ironman","captain",
}


limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)


def password_strength(pw: str) -> dict:
    if not pw:
        return {"score": 0, "label": "Empty", "crack_time": "instant", "bits": 0}

    score = 0
    has_lower = bool(re.search(r"[a-z]", pw))
    has_upper = bool(re.search(r"[A-Z]", pw))
    has_digit = bool(re.search(r"\d", pw))
    has_symbol = bool(re.search(r"[^a-zA-Z0-9]", pw))

    pool = 0
    if has_lower:
        pool += 26
    if has_upper:
        pool += 26
    if has_digit:
        pool += 10
    if has_symbol:
        pool += 32

    if pool == 0:
        pool = 26

    bits = len(pw) * math.log2(pool) if pool > 0 else 0

    # Length scoring
    if len(pw) >= 20:
        score += 35
    elif len(pw) >= 16:
        score += 28
    elif len(pw) >= 12:
        score += 20
    elif len(pw) >= 8:
        score += 10
    else:
        score += 2

    # Character variety
    variety = sum([has_lower, has_upper, has_digit, has_symbol])
    score += [0, 5, 15, 25, 35][variety]

    # Pattern penalties
    if re.search(r"(.)\1{2,}", pw):
        score -= 10
    if re.search(r"(012|123|234|345|456|567|678|789|890|abc|bcd|cde)", pw.lower()):
        score -= 10
    common = ["password", "qwerty", "admin", "login", "letmein", "welcome", "monkey", "dragon"]
    if any(c in pw.lower() for c in common):
        score -= 20

    score = max(0, min(100, score))

    # Crack time label (assumes 10B guesses/sec GPU cluster)
    guesses_per_sec = 10_000_000_000
    combinations = pool ** len(pw) if pool > 0 else 1
    seconds = combinations / (2 * guesses_per_sec)

    if seconds < 1:
        crack_time = "instantly"
    elif seconds < 60:
        crack_time = f"{int(seconds)} seconds"
    elif seconds < 3600:
        crack_time = f"{int(seconds/60)} minutes"
    elif seconds < 86400:
        crack_time = f"{int(seconds/3600)} hours"
    elif seconds < 31536000:
        crack_time = f"{int(seconds/86400)} days"
    elif seconds < 3.154e9:
        crack_time = f"{int(seconds/31536000)} years"
    elif seconds < 3.154e12:
        crack_time = f"{int(seconds/3.154e9)} thousand years"
    elif seconds < 3.154e15:
        crack_time = f"{int(seconds/3.154e12)} million years"
    else:
        crack_time = "billions of years"

    if score >= 80:
        label = "Very Strong"
    elif score >= 60:
        label = "Strong"
    elif score >= 40:
        label = "Fair"
    elif score >= 20:
        label = "Weak"
    else:
        label = "Very Weak"

    is_common = pw.lower() in COMMON_PASSWORDS

    if is_common:
        score = min(score, 10)

    feedback = []
    if is_common:
        feedback.append("This is one of the most commonly used passwords")
    if len(pw) < 12:
        feedback.append("Use at least 12 characters")
    if not has_upper:
        feedback.append("Add uppercase letters")
    if not has_digit:
        feedback.append("Add numbers")
    if not has_symbol:
        feedback.append("Add special characters (!@#$...)")
    if re.search(r"(.)\1{2,}", pw):
        feedback.append("Avoid repeated characters")

    return {
        "score": score,
        "label": label,
        "crack_time": crack_time,
        "bits": round(bits, 1),
        "feedback": feedback,
        "has_lower": has_lower,
        "has_upper": has_upper,
        "has_digit": has_digit,
        "has_symbol": has_symbol,
        "length": len(pw),
        "is_common": is_common,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
@limiter.limit("60 per minute")
def analyze():
    data = request.get_json(silent=True) or {}
    pw = str(data.get("password", ""))[:128]  # cap at 128 chars
    return jsonify(password_strength(pw))


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5051)
