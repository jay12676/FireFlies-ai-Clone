from app import models


def test_cascade_delete_removes_children(db_session):
    m = models.Meeting(title="Test")
    m.participants.append(models.Participant(name="Alice"))
    m.segments.append(models.TranscriptSegment(text="hello", order_index=0))
    m.summary = models.Summary(overview="overview")
    m.topics.append(models.KeyTopic(title="Intro", start_ms=0, order_index=0))
    m.action_items.append(models.ActionItem(text="do thing", order_index=0))
    db_session.add(m)
    db_session.commit()

    mid = m.id
    assert db_session.query(models.TranscriptSegment).filter_by(meeting_id=mid).count() == 1

    db_session.delete(m)
    db_session.commit()

    assert db_session.query(models.TranscriptSegment).filter_by(meeting_id=mid).count() == 0
    assert db_session.query(models.Summary).filter_by(meeting_id=mid).count() == 0
    assert db_session.query(models.ActionItem).filter_by(meeting_id=mid).count() == 0
    assert db_session.query(models.KeyTopic).filter_by(meeting_id=mid).count() == 0
