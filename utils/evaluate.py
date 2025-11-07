import json
import os
from utils.recommender import recommend_assessments

def load_test_data(filepath='data/test_data.json'):
    """Loads the ground-truth test data."""
    try:
        if not os.path.exists(filepath):
            print(f"Error: {filepath} not found. Ensure test_data.json is created.")
            return []
            
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading test data: {e}")
        return []

def evaluate_precision_at_k(test_data, k=1):
    """
    Calculates Precision@K (e.g., Precision@1) for the recommendation engine.
    Precision@K measures how often the expected assessment is found in the top K results.
    """
    if not test_data:
        return 0.0

    hits = 0
    total_queries = len(test_data)

    print(f"\n--- Running Evaluation (Precision@{k}) ---")
    print(f"Total Test Cases: {total_queries}\n")

    for i, test_case in enumerate(test_data):
        query = test_case['query']
        expected_name = test_case['expected_name']

        # Get recommendations using the recommender function
        recommendations = recommend_assessments(query, top_n=k)

        # Check if the expected name is in the top K
        top_k_names = [r['name'] for r in recommendations]

        is_hit = expected_name in top_k_names
        
        print(f"Query {i+1} / {total_queries}")
        print(f"  Input: '{query}'")
        print(f"  Expected: {expected_name}")
        print(f"  Top@{k}: {top_k_names}")

        if is_hit:
            hits += 1
            print(f"  Result: ✅ HIT")
        else:
            print(f"  Result: ❌ MISS")
        print("-" * 30)


    precision_at_k = hits / total_queries
    
    print("\n==================================")
    print(f"Final Evaluation Summary")
    print("==================================")
    print(f"Hits: {hits} / {total_queries}")
    print(f"Precision@{k}: {precision_at_k:.4f}")
    
    return precision_at_k

if __name__ == "__main__":
    data = load_test_data()
    # Evaluate Precision@1 (Top 1 Recommendation)
    evaluate_precision_at_k(data, k=1)