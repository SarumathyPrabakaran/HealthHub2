from flask import Flask, render_template, request, jsonify
import os, dotenv
import openai

dotenv.load_dotenv()
openai.api_key = os.environ.get('API_KEY')


app = Flask(__name__)


@app.route('/home')
def index():
    return render_template('index.html')



@app.route('/', methods=['POST','GET'])
def get_medical_term_explanation():
    
    if request.method=="POST":
        medical_term = request.form.get('term')
        print(medical_term)
    
        prompt = f"Explain the medical term '{medical_term}' in simple words."

        response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=50  
    )

        explanation = response.choices[0].text.strip()
    
        return jsonify({"explanation": explanation})
    
    return render_template('explain.html')

if __name__ == "__main__":
    app.run(debug=True)
