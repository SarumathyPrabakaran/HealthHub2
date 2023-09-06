from flask import Flask, render_template, request, jsonify

import openai

# Set your OpenAI API key
openai.api_key = ''


app = Flask(__name__)


@app.route('/home')
def index():
    return render_template('index.html')



@app.route('/', methods=['POST','GET'])
def get_medical_term_explanation():
    # Extract the medical term from the POST request
    if request.method=="POST":
        medical_term = request.form.get('term')
        print(medical_term)
    # Define the prompt for GPT-3
        prompt = f"Explain the medical term '{medical_term}' in simple words."

    # Use GPT-3 to generate an explanation
        response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=50  # Adjust as needed
    )

    # Extract and return the explanation from the GPT-3 response
        explanation = response.choices[0].text.strip()
    
        return jsonify({"explanation": explanation})
    
    return render_template('explain.html')
if __name__ == "__main__":
    app.run(debug=True)
