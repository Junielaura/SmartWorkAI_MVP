"""Document classification service for SmartWork AI MVP."""

from __future__ import annotations

from typing import Optional, Dict, Any

# Supported categories for the MVP
CATEGORIES = [
    "rapport",
    "tableau de données",
    "compte rendu",
    "facture",
    "document administratif",
    "autre",
]


def classify_document(text: str, user_category: Optional[str] = None) -> Dict[str, Any]:
    """Classify a document based on its content.
    
    Uses simple keyword matching for the MVP. 
    In a production system, this would use an LLM or ML classifier.
    
    Args:
        text: The document text content
        user_category: User-confirmed category if available
    
    Returns:
        Classification result with category and confidence
    """
    text_lower = text.lower()
    
    # Simple keyword-based classification
    scores = {}
    
    # Rapport keywords
    rapport_keys = ["rapport", "bilan", "summary", "summary report"]
    scores["rapport"] = sum(1 for k in rapport_keys if k in text_lower)
    
    # Tableau de données keywords
    tableau_keys = ["tableau", "data", "dataset", "chiffres", "metrics"]
    scores["tableau de données"] = sum(1 for k in tableau_keys if k in text_lower)
    
    # Compte rendu keywords
    compte_rendu_keys = ["compte rendu", "minutes", "meeting notes", "compte-rendu"]
    scores["compte rendu"] = sum(1 for k in compte_rendu_keys if k in text_lower)
    
    # Facture keywords
    facture_keys = ["facture", "invoice", "paiement", "payment", "total HT", "TVA"]
    scores["facture"] = sum(1 for k in facture_keys if k in text_lower)
    
    # Document administratif
    admin_keys = ["administratif", "convention", "contrat", "procédure", "règlement"]
    scores["document administratif"] = sum(1 for k in admin_keys if k in text_lower)
    
    # Find best category
    best_category = "autre"
    best_score = 0
    
    for category, score in scores.items():
        if score > best_score:
            best_score = score
            best_category = category
    
    # If user provided a category, respect it (override)
    if user_category and user_category in CATEGORIES:
        best_category = user_category
    
    # Calculate confidence
    total_keywords = sum(len(keywords) for keywords in [
        rapport_keys, tableau_keys, compte_rendu_keys, facture_keys, admin_keys
    ])
    confidence = min(best_score / max(total_keywords, 1), 1.0) if best_score > 0 else 0.3
    
    return {
        "category": best_category,
        "confidence": round(confidence, 2),
        "scores": {k: v / max(total_keywords, 1) for k, v in scores.items()},
        "all_categories": CATEGORIES,
    }


def suggest_classification(file_path: str) -> Dict[str, Any]:
    """Suggest a classification by extracting text first then classifying."""
    from app.services.extraction import extract_document
    
    try:
        extracted = extract_document(file_path, "pdf")  # Will adapt format
        if extracted and "text" in extracted:
            return classify_document(extracted["text"])
    except Exception:
        pass
    
    # Fallback: return "autre" with low confidence
    return {
        "category": "autre",
        "confidence": 0.1,
        "scores": {cat: 0.0 for cat in CATEGORIES},
        "all_categories": CATEGORIES,
    }