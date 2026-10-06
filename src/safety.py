import re

EMERGENCY_MSG = (
    "This may be a medical emergency. Please call your local emergency number "
    "(for example 112 in India and the EU, 911 in the US, 999 in the UK) or go to the "
    "nearest emergency room right away. I can only share general information and "
    "can't help in an emergency."
)
CRISIS_MSG = (
    "I'm really sorry you're feeling this way. You deserve support from a real person. "
    "Please contact a local crisis line or emergency service right now, or reach out "
    "to someone you trust and tell them how you feel."
)
NO_INFO_MSG = "I don't have enough information in my documents to answer that."
URGENT_HINT = (
    "\n\nIf this is urgent or getting worse, please contact a doctor or your local emergency services."
)

_EMERGENCY_RAW = [
    r"\bchest\b.{0,25}\b(pain|pains|paining|painful|hurt|hurts|hurting|tight|tightness|pressure|crushing|squeezing)\b",
    r"\b(pain|pains|paining|pressure|tightness)\b.{0,15}\bchest\b",
    r"\b(cant|cannot|can not|unable to|struggling to|hard to|difficult to)\b.{0,15}\bbreath\w*",
    r"\b(difficulty|trouble|struggling|shortness|short)\b.{0,12}\bbreath\w*",
    r"\b(not breathing|stopped breathing|stops breathing|gasping)\b",
    r"\b(having|getting)\b.{0,15}\b(heart attack|stroke|seizure|anaphylaxis|allergic reaction)\b",
    r"\b(overdose|overdosed|overdosing|took too many|swallowed too many)\b",
    r"\b(unconscious|passed out|unresponsive|not responding|collapsed|wont wake)\b",
    r"\b(severe|heavy|uncontrolled)\b.{0,15}\bbleeding\b",
    r"\bbleeding\b.{0,20}\b(wont stop|not stopping|heavily)\b",
    r"\b(vomiting|coughing|coughed|spitting)\b.{0,10}\bblood\b",
    r"\b(face|arm)\b.{0,20}\b(drooping|droops|numb|numbness)\b",
    r"\bsudden(ly)?\b.{0,30}\b(numb\w*|weak\w*|confus\w*|slurred|vision loss|loss of vision)\b",
    r"\b(slurred|slurring)\b",
    r"\b(poisoned|swallowed poison)\b",
]
_CRISIS_RAW = [
    r"\b(suicide|suicidal|selfharm|self harm)\b",
    r"\b(hurt|hurting|harm|harming|cut|cutting|kill|killing)\s+myself\b",
    r"\b(end|ending|take|taking)\s+my\s+(own\s+)?life\b",
    r"\b(want|wanna|wish)\s+(to\s+)?die\b",
    r"\b(dont|do not)\s+want\s+to\s+(live|be here)\b",
    r"\bbetter off dead\b",
    r"\bno reason to live\b",
]
EMERGENCY_PATTERNS = [re.compile(p) for p in _EMERGENCY_RAW]
CRISIS_PATTERNS = [re.compile(p) for p in _CRISIS_RAW]

_FILLER = re.compile(
    r"^((hey|hi|hello|jarvis|please|can you|could you|tell me|i want to know|i would like to know)\s+)+"
)
_INFO_START = re.compile(r"^(what|why|how|when|which|explain|define|tell me about|causes of|symptoms of)\b")
_FIRST_PERSON = re.compile(
    r"\b(i|im|ive|id|my|me|myself|we|our|he|she|his|her|they|someone|somebody|"
    r"mom|dad|mother|father|wife|husband|son|daughter|child|baby|friend)\b"
)
_URGENT_WORDS = re.compile(
    r"\b(pain\w*|bleed\w*|breath\w*|faint\w*|collaps\w*|chok\w*|seizure\w*|severe|worsening|dizzy|unconscious)\b"
)


def _normalize(text):
    t = text.lower().replace("\u2019", "'").replace("'", "")
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def check_safety(question):
    """Return 'crisis', 'emergency' or None."""
    q = _normalize(question)
    core = _FILLER.sub("", q)
    # general knowledge questions ("what causes chest pain?") are not emergencies
    if _INFO_START.match(core) and not _FIRST_PERSON.search(core):
        return None
    if any(p.search(q) for p in CRISIS_PATTERNS):
        return "crisis"
    if any(p.search(q) for p in EMERGENCY_PATTERNS):
        return "emergency"
    return None


def is_urgent_wording(question):
    return bool(_URGENT_WORDS.search(_normalize(question)))