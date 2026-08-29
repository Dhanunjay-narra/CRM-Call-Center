from app.modules.calls.supervisor import SupervisorManager, SupervisionMode

def test_supervisor_coaching_session():
    mgr = SupervisorManager()
    sess = mgr.attach_supervisor("sup-001", "CALL-101", SupervisionMode.WHISPER)
    assert sess.mode == SupervisionMode.WHISPER
    assert sess.call_id == "CALL-101"
