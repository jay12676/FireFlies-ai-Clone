from app.services.parser import parse_transcript


def test_txt_with_timestamps_and_speakers():
    content = "[00:05] Alice: Hello team.\n[00:10] Bob: Hi Alice, ready to start?"
    segs = parse_transcript(content, "notes.txt")
    assert len(segs) == 2
    assert segs[0].speaker == "Alice"
    assert segs[0].start_ms == 5000
    assert segs[1].speaker == "Bob"
    assert segs[1].start_ms == 10000


def test_txt_without_timestamps_synthesizes():
    content = "Alice: First line.\nBob: Second line."
    segs = parse_transcript(content, "notes.txt")
    assert segs[0].start_ms == 0
    assert segs[1].start_ms == segs[0].end_ms  # sequential
    assert segs[1].start_ms > 0


def test_txt_continuation_keeps_last_speaker():
    content = "Alice: Line one.\nStill Alice talking."
    segs = parse_transcript(content, "notes.txt")
    assert len(segs) == 2
    assert segs[1].speaker == "Alice"


def test_vtt_parsing():
    content = (
        "WEBVTT\n\n"
        "00:00:01.000 --> 00:00:04.000\n<v Alice>Welcome everyone.\n\n"
        "00:00:05.000 --> 00:00:08.000\nBob: Thanks for joining.\n"
    )
    segs = parse_transcript(content, "rec.vtt")
    assert len(segs) == 2
    assert segs[0].speaker == "Alice"
    assert segs[0].start_ms == 1000
    assert segs[1].speaker == "Bob"
    assert segs[1].text == "Thanks for joining."


def test_json_with_ms():
    content = '[{"speaker":"Alice","start_ms":0,"end_ms":3000,"text":"Hi"},'\
              '{"speaker":"Bob","start_ms":3000,"end_ms":6000,"text":"Hello there"}]'
    segs = parse_transcript(content, "data.json")
    assert len(segs) == 2
    assert segs[1].speaker == "Bob"
    assert segs[1].start_ms == 3000


def test_json_with_seconds():
    content = '[{"speaker":"Alice","start":0,"end":3,"text":"Hi everyone"}]'
    segs = parse_transcript(content, "data.json")
    assert segs[0].start_ms == 0
    assert segs[0].end_ms == 3000
