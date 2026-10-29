import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from modules.preprocessing import preprocess_text
from modules.risk_scoring import CognitiveRiskScorer
from modules.astroturfing import AstroturfingDetector
from modules.ingestion import extract_clean_posts
import pandas as pd

def main():
    print("Testing Preprocessing...")
    sample_text = "VIRALKAN SEKARANG JUGA!! https://t.co/xyz @someone rezim antek asing ini bgtu parah membodohi rakyat 😡"
    cleaned = preprocess_text(sample_text)
    print("Cleaned:", cleaned)

    print("\nTesting Risk Scoring...")
    scorer = CognitiveRiskScorer()
    risk = scorer.analyze_text(sample_text)
    print(f"Risk Score: {risk['overall_risk_score']}% | Category: {risk['risk_category']}")
    print("Dimensions:", risk['dimensions'])

    print("\nTesting Astroturfing Detection...")
    csv_path = os.path.join(os.path.dirname(__file__), "data", "sample_posts.csv")
    df = pd.read_csv(csv_path)
    posts = extract_clean_posts(df, "text")
    detector = AstroturfingDetector()
    sim_matrix, _ = detector.fit_transform_similarity(posts)
    metrics = detector.calculate_coordination_metrics(sim_matrix, threshold=0.65)
    pairs = detector.find_suspicious_pairs(sim_matrix, posts, threshold=0.65)
    print(f"Total Posts: {metrics['total_posts']} | Suspect Pairs: {len(pairs)} | Amplification: {metrics['amplification_ratio']}%")

    print("\nALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
