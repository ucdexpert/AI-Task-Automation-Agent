"""Test WhatsApp and Calendar Notification Tools"""
import asyncio
from app.tools.whatsapp_tool import WhatsAppTool
from app.tools.calendar_notification_tool import CalendarNotificationTool

async def test_whatsapp():
    print("=" * 60)
    print("Testing WhatsApp Tool")
    print("=" * 60)
    
    whatsapp = WhatsAppTool()
    
    # Test 1: Send text message
    print("\n📱 Test 1: Sending text message...")
    result = await whatsapp.execute(
        operation="send_text",
        message="🚀 WhatsApp integration is working! This is a test message from AI Task Automation Agent."
    )
    
    if result.get("success"):
        print(f"✅ Message sent successfully!")
        print(f"   Message ID: {result.get('message_id')}")
        print(f"   Recipient: {result.get('recipient')}")
    else:
        print(f"❌ Failed: {result.get('message')}")
    
    # Test 2: Send template message
    print("\n📱 Test 2: Sending template message...")
    result = await whatsapp.execute(
        operation="send_template",
        template_name="hello_world",
        template_language="en_US"
    )
    
    if result.get("success"):
        print(f"✅ Template sent successfully!")
        print(f"   Message ID: {result.get('message_id')}")
    else:
        print(f"❌ Failed: {result.get('message')}")

async def test_calendar_notification():
    print("\n" + "=" * 60)
    print("Testing Calendar Notification Tool")
    print("=" * 60)
    
    notif = CalendarNotificationTool()
    
    # Test 1: Event created notification
    print("\n📅 Test 1: Event created notification...")
    result = await notif.execute(
        event_summary="Team Meeting - Project Review",
        event_start="2026-04-15 at 10:00 AM",
        event_end="2026-04-15 at 11:00 AM",
        notification_type="event_created"
    )
    
    if result.get("success"):
        print(f"✅ Notification sent!")
        print(f"   Message ID: {result.get('message_id')}")
    else:
        print(f"❌ Failed: {result.get('message')}")
    
    # Test 2: Event reminder
    print("\n📅 Test 2: Event reminder notification...")
    result = await notif.execute(
        event_summary="Doctor Appointment",
        event_start="2026-04-16 at 3:00 PM",
        notification_type="event_reminder"
    )
    
    if result.get("success"):
        print(f"✅ Reminder sent!")
        print(f"   Message ID: {result.get('message_id')}")
    else:
        print(f"❌ Failed: {result.get('message')}")

async def main():
    try:
        await test_whatsapp()
        await test_calendar_notification()
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
