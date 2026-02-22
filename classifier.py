def classify(text):
    text = text.lower()

    if "ai" in text or "machine learning" in text:
        return "Artificial Intelligence"
    elif "law" in text:
        return "Law"
    elif "bio" in text or "medical" in text:
        return "Biomedical"
    else:
        return "Engineering"