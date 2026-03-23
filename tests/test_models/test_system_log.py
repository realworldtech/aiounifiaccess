"""Tests for SystemLog models."""

from aiounifiaccess.models.system_log import LogTopic, SystemLogEntry


class TestLogTopic:
    def test_values(self):
        assert LogTopic.ALL == "all"
        assert LogTopic.DOOR_OPENINGS == "door_openings"


class TestSystemLogEntry:
    def test_parse(self):
        e = SystemLogEntry.model_validate(
            {
                "timestamp": "2024-01-01T00:00:00Z",
                "id": "log1",
                "source": {
                    "event": {"type": "door.unlock", "display_message": "Unlocked"},
                    "actor": {"id": "u1", "display_name": "Admin"},
                    "authentication": {},
                    "target": {"id": "d1", "display_name": "Front Door"},
                },
            }
        )
        assert e.id == "log1"
        assert e.source.event.type == "door.unlock"
        assert e.source.actor.display_name == "Admin"
