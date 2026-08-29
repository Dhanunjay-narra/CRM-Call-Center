from app.modules.calls.ivr_engine import IVRMenuNode

def test_ivr_routing():
    menu = IVRMenuNode("Press 1 for Sales, 2 for Support", {"1": "SALES_QUEUE", "2": "SUPPORT_QUEUE"})
    assert menu.process_dtmf_input("1") == "SALES_QUEUE"
    assert menu.process_dtmf_input("9") == "DEFAULT_AGENT_QUEUE"
