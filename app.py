from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import PyPDF2
import os

# 🧠 SET YOUR GOOGLE API KEY
genai.configure(api_key="AIzaSyDJ9py0J71gaSFaQLUVf8p_iKaiaze88cI")  # ← replace with your key

app = Flask(__name__)

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

    # Use the correct model name and bidirectional chat interface
    model = genai.GenerativeModel("models/gemini-1.5-flash")  # or gemini-1.5-pro or other working variant
    chat = model.start_chat()
    response = chat.send_message(prompt)

    return response.text.strip()


# -------------------------------
# Load PDF once when app starts
# -------------------------------
PDF_PATH = "sivakasi _chatbot_info.pdf"  # ✅ make sure this file is in the same folder
pdf_text = extract_text_from_pdf(PDF_PATH)
pdf_chunks = chunk_text(pdf_text)

# -------------------------------
# Flask Routes
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form["message"]
    reply = generate_gemini_response(user_message, pdf_chunks)
    return jsonify({"response": reply})

if __name__ == "__main__":
    app.run(debug=True)
