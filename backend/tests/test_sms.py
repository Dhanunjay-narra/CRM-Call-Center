from app.modules.channels.sms_router import SMSGatewayDispatcher

def test_sms_dispatch_routing():
    dispatcher = SMSGatewayDispatcher()
    msg = dispatcher.dispatch_sms("+18005550100", "+14155552671", "Your ticket has been updated.")
    assert msg.status == "DELIVERED"
    assert msg.message_id == "SMS-1"
