from django.conf import settings

from .models import Domain


def classify_message(message: str) -> str:
    """
    Very small, dependency-free keyword classifier that guesses which KYK
    domain (Recruitment / Software / AI) a message is really about, so leads
    can be routed even if the visitor picked "Something else" in the form.

    This is intentionally simple — swap in a call to an LLM (e.g. the
    Anthropic API) here if you want a smarter classifier later.
    """
    text = (message or "").lower()
    keywords = settings.KYK_DOMAIN_KEYWORDS

    scores = {domain: 0 for domain in keywords}
    for domain, words in keywords.items():
        for word in words:
            if word in text:
                scores[domain] += 1

    best_domain = max(scores, key=scores.get)
    if scores[best_domain] == 0:
        return Domain.OTHER

    mapping = {
        "recruitment": Domain.RECRUITMENT,
        "software": Domain.SOFTWARE,
        "ai": Domain.AI,
    }
    return mapping[best_domain]
