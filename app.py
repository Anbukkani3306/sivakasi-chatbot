from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import google.generativeai as genai
import PyPDF2
import os

# 🧠 SET YOUR GOOGLE API KEY
genai.configure(api_key="AIzaSyDJ9py0J71gaSFaQLUVf8p_iKaiaze88cI")

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Use a secure, random key in production!

# -------------------------------
# Load and chunk the PDF content
# -------------------------------
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    return text

def chunk_text(text, chunk_size=1500):
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

# -------------------------------
# Gemini response generation
# -------------------------------
def generate_gemini_response(question, chunks):
    context = "\n\n".join(chunks[:3])
    prompt = f"""You are a smart chatbot answering based on this text from a PDF:\n\n{context}\n\nNow answer this question:\n{question}"""

    model = genai.GenerativeModel("models/gemini-1.5-flash")
    chat = model.start_chat()
    response = chat.send_message(prompt)
    return response.text.strip()

# -------------------------------
# Load PDF once when app starts
# -------------------------------
PDF_PATH = "sivakasi_chatbot_info.pdf"
pdf_text = extract_text_from_pdf(PDF_PATH)
pdf_chunks = chunk_text(pdf_text)

# -------------------------------
# Routes
# -------------------------------
@app.route("/")
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    if not session.get("logged_in"):
        return jsonify({"response": "You must be logged in to chat."})
    user_message = request.form["message"]
    reply = generate_gemini_response(user_message, pdf_chunks)
    return jsonify({"response": reply})

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # 🔒 Hardcoded credentials - change for real app
        if username == "admin" and password == "pass123":
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

#if __name__ == "__main__":
 #   app.run(debug=True)
 