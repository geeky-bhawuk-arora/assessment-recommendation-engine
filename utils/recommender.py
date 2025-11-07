from sentence_transformers import SentenceTransformer, util
import json
import os

model = SentenceTransformer('all-MiniLM-L6-v2')

def load_assessments():
    path = os.path.join('data', 'assessments.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def recommend_assessments(input_text, top_n=10):
    assessments = load_assessments()
    input_emb = model.encode(input_text, convert_to_tensor=True)

    scores = []
    for a in assessments:
        text = f"{a['name']} {a.get('description', '')}"
        emb = model.encode(text, convert_to_tensor=True)
        score = float(util.cos_sim(input_emb, emb))
        scores.append((a, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    top = scores[:top_n]
    return [
        {
            "name": a["name"],
            "url": a["url"],
            "score": round(s, 3)
        } for a, s in top
    ]
