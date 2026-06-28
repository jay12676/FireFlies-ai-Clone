from app.services import generator
from app.services.parser import ParsedSegment

SAMPLE = [
    ParsedSegment("Alice", 0, 4000, "Welcome to the sprint planning meeting for the payments project."),
    ParsedSegment("Bob", 4000, 8000, "I will finish the payments API integration by Friday."),
    ParsedSegment("Alice", 8000, 12000, "We need to review the payments dashboard design this week."),
    ParsedSegment("Carol", 12000, 16000, "Let's schedule a follow up about the payments rollout."),
    ParsedSegment("Bob", 16000, 20000, "The payments testing should cover edge cases thoroughly."),
]


def test_summary_is_nonempty():
    overview = generator.generate_summary(SAMPLE)
    assert overview
    assert len(overview.split()) >= 4


def test_action_items_detected_with_assignee_and_due():
    items = generator.extract_action_items(SAMPLE)
    texts = " ".join(i.text.lower() for i in items)
    assert "i will finish the payments api" in texts
    friday = [i for i in items if "friday" in i.due_date.lower()]
    assert friday and friday[0].assignee == "Bob"


def test_topics_nonempty_and_ordered():
    topics = generator.extract_topics(SAMPLE)
    assert topics
    starts = [t.start_ms for t in topics]
    assert starts == sorted(starts)
    # "payments" is the dominant keyword and should surface as a topic.
    assert any("payment" in t.title.lower() for t in topics)


def test_deterministic():
    a = generator.generate_all(SAMPLE)
    b = generator.generate_all(SAMPLE)
    assert a.overview == b.overview
    assert [i.text for i in a.action_items] == [i.text for i in b.action_items]
