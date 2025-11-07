from flask import Flask, render_template, request, jsonify
from utils.recommender import recommend_assessments

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        job_desc = request.form['job_desc']
        results = recommend_assessments(job_desc)
        return render_template('results.html', job_desc=job_desc, recommendations=results)
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' field"}), 400
    query = data['query']
    results = recommend_assessments(query)
    return jsonify({"query": query, "recommendations": results}), 200

if __name__ == '__main__':
    app.run(debug=True)
