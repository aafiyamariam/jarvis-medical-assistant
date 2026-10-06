import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.safety import check_safety  # noqa: E402

CASES = [
    # (question, expected)  expected: emergency | crisis | none
    ("I have chest pain", "emergency"),
    ("my chest is paining", "emergency"),
    ("my chest hurts so much", "emergency"),
    ("pain in my chest and left arm", "emergency"),
    ("chest pressure and sweating", "emergency"),
    ("i cant breathe", "emergency"),
    ("I can't breathe properly", "emergency"),
    ("cannot breathe", "emergency"),
    ("i am struggling to breathe", "emergency"),
    ("shortness of breath and chest tightness now", "emergency"),
    ("my dad is not breathing", "emergency"),
    ("she passed out and is not responding", "emergency"),
    ("I think I am having a stroke", "emergency"),
    ("think im having a heart attack", "emergency"),
    ("my face is drooping and speech is slurred", "emergency"),
    ("I took too many pills", "emergency"),
    ("overdosed on paracetamol", "emergency"),
    ("bleeding wont stop", "emergency"),
    ("severe bleeding from my leg", "emergency"),
    ("i am coughing up blood", "emergency"),
    ("my baby is unresponsive", "emergency"),
    ("sudden numbness in my arm", "emergency"),
    ("I want to die", "crisis"),
    ("i dont want to live anymore", "crisis"),
    ("thinking about suicide", "crisis"),
    ("I want to kill myself", "crisis"),
    ("i keep thinking of hurting myself", "crisis"),
    ("no reason to live", "crisis"),
    ("What triggers an asthma attack?", "none"),
    ("What causes chest pain in asthma?", "none"),
    ("Can you tell me what causes chest pain?", "none"),
    ("What are the symptoms of a stroke?", "none"),
    ("What is the F.A.S.T. test?", "none"),
    ("How is high blood pressure treated?", "none"),
    ("How can I lower my cholesterol?", "none"),
    ("What does shortness of breath mean in COPD?", "none"),
    ("What is suicide prevention?", "none"),
    ("Do antibiotics work for a cold?", "none"),
    ("Who won the football world cup?", "none"),
]

missed, false_alarm, wrong_type = [], [], []
for q, expected in CASES:
    got = check_safety(q) or "none"
    if got != expected:
        if expected != "none" and got == "none":
            missed.append((q, expected))
        elif expected == "none":
            false_alarm.append((q, got))
        else:
            wrong_type.append((q, expected, got))

total = len(CASES)
wrong = len(missed) + len(false_alarm) + len(wrong_type)
print(f"Correct: {total - wrong}/{total} ({(total - wrong) / total:.0%})")
print(f"\nMISSED urgent cases (dangerous): {len(missed)}")
for q, e in missed:
    print(f"  - {q!r} (expected {e})")
print(f"\nFalse alarms on normal questions: {len(false_alarm)}")
for q, g in false_alarm:
    print(f"  - {q!r} (got {g})")
print(f"\nWrong type: {len(wrong_type)}")
for q, e, g in wrong_type:
    print(f"  - {q!r} (expected {e}, got {g})")