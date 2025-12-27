import os
from flask import Flask, render_template_string, request, jsonify
from groq import Groq

app = FastAPI()

# --- CONFIGURATION ---
# Replace 'YOUR_GROQ_API_KEY' with your actual API key
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Companion</title>
    <style>
        body { font-family: sans-serif; text-align: center; background-color: #1a1a1a; color: white; padding: 20px; }
        .face-container {
            margin: 10px auto; width: 280px; height: 280px;
            border: 5px solid #007bff; border-radius: 20px;
            overflow: hidden; background: #222;
        }
        img { width: 100%; height: 100%; object-fit: cover; }
        #chat {
            height: 350px; overflow-y: auto; background: #1e1e1e;
            margin: 15px 0; padding: 15px; border-radius: 10px;
            text-align: left; border: 1px solid #333;
        }
        .input-box { display: flex; gap: 10px; }
        input { flex: 1; padding: 15px; border-radius: 25px; border: none; background: #333; color: white; }
        button { padding: 10px 20px; border-radius: 25px; background: #007bff; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <h2 style="color: #007bff;">AI Companion</h2>
    <div class="face-container">
        <img id="face-img" src="/static/neutral.jpg" onerror="this.src='https://via.placeholder.com/280'">
    </div>
    <div id="chat"></div>
    <div class="input-box">
        <input type="text" id="userInput" placeholder="Type your message...">
        <button onclick="sendToAI()">Send</button>
    </div>

    <script>
        async function sendToAI() {
            let input = document.getElementById('userInput');
            let chat = document.getElementById('chat');
            let face = document.getElementById('face-img');
            let text = input.value;

            if(!text) return;

            chat.innerHTML += "<div><b>You:</b> " + text + "</div>";
            input.value = "";
            chat.scrollTop = chat.scrollHeight;

            try {
                const response = await fetch('/get_response', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();

                if(data.emotion === "HAPPY") {
                    face.src = "/static/happy.jpg";
                } else {
                    face.src = "/static/neutral.jpg";
                }

                chat.innerHTML += "<div style='color:#00d4ff; margin-bottom:10px;'><b>AI:</b> " + data.reply + "</div>";
            } catch (e) {
                chat.innerHTML += "<div style='color:red;'>Error connecting to brain.</div>";
            }
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_PAGE

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        user_message = request.json.get('message')

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a kind AI. You must ALWAYS start your reply with [HAPPY] or [NEUTRAL] based on your mood."},
                {"role": "user", "content": user_message}
            ]
        )

        raw_reply = completion.choices[0].message.content
        emotion = "NEUTRAL"
        if "[HAPPY]" in raw_reply:
            emotion = "HAPPY"

        clean_reply = raw_reply.replace("[HAPPY]", "").replace("[NEUTRAL]", "").strip()
        return jsonify({"reply": clean_reply, "emotion": emotion})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}", "emotion": "NEUTRAL"})
if __name__ == "__main__":
    app.run(debug=True)

