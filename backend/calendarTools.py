# # calendar_tools.py - Updated to use unified auth
# from typing import List
# from phi.tools import Toolkit, tool
# import os

# # Import the unified auth function
# from google_services import get_calendar_service

# class CalendarTools(Toolkit):
#     def __init__(self, service):
#         super().__init__()
#         self.service = service
#         self.register(self.list_events)
#         self.register(self.create_event)
#         self.register(self.delete_event)

#     def list_events(self, calendarId='primary', max_results=10) -> dict:
#         """List upcoming events from Google Calendar"""
#         try:
#             events_result = self.service.events().list(
#                 calendarId=calendarId,
#                 maxResults=max_results,
#                 singleEvents=True,
#                 orderBy='startTime',
#                 timeMin='2025-06-21T00:00:00Z'  # Only get future events
#             ).execute()
#             events = events_result.get('items', [])

#             if not events:
#                 return {"type": "event_list", "content": "No upcoming events found."}

#             output = ""
#             for event in events:
#                 start = event['start'].get('dateTime', event['start'].get('date'))
#                 summary = event.get('summary', 'No Title')
#                 event_id = event.get('id', 'No ID')
#                 output += f"ID: {event_id}\n{start} - {summary}\n\n"
#             return {"type": "event_list", "content": output}
#         except Exception as e:
#             return {"type": "error", "content": f"Error listing events: {str(e)}"}

#     def create_event(self, summary: str, start_datetime: str, end_datetime: str, timezone: str = 'UTC', description: str = None) -> dict:
#         """Create a new event in Google Calendar"""
#         try:
#             event = {
#                 'summary': summary,
#                 'start': {
#                     'dateTime': start_datetime,
#                     'timeZone': timezone,
#                 },
#                 'end': {
#                     'dateTime': end_datetime,
#                     'timeZone': timezone,
#                 },
#             }
            
#             if description:
#                 event['description'] = description
                
#             created_event = self.service.events().insert(calendarId='primary', body=event).execute()
#             return {"type": "confirmation", "content": f"✅ Event created: {created_event.get('htmlLink')}"}
#         except Exception as e:
#             return {"type": "error", "content": f"Error creating event: {str(e)}"}

#     def delete_event(self, event_id: str) -> dict:
#         """Delete an event from Google Calendar"""
#         try:
#             self.service.events().delete(calendarId='primary', eventId=event_id).execute()
#             return {"type": "confirmation", "content": "✅ Event deleted successfully."}
#         except Exception as e:
#             return {"type": "error", "content": f"Error deleting event: {str(e)}"}


# # Test function
# if __name__ == "__main__":
#     try:
#         calendar_service = get_calendar_service()
#         calendar_tools = CalendarTools(service=calendar_service)

#         # List upcoming events
#         print("Listing upcoming events:")
#         result = calendar_tools.list_events(max_results=5)
#         print(result['content'])

#         # Create a test event (Adjust date/time as needed)
#         # print(calendar_tools.create_event(
#         #     summary="Test Meeting",
#         #     start_datetime="2025-06-22T15:00:00",
#         #     end_datetime="2025-06-22T16:00:00",
#         #     timezone="America/New_York",
#         #     description="This is a test event created by the calendar tool"
#         # ))

#         # Delete an event by ID (get ID from list_events output)
#         # print(calendar_tools.delete_event("EVENT_ID_HERE"))

#     except Exception as e:
#         print(f"Error: {e}")
#         print("\nMake sure you have:")
#         print("1. Downloaded credentials.json from Google Cloud Console")
#         print("2. Enabled Google Calendar API")
#         print("3. Set up OAuth 2.0 credentials")


# calendar_tools.py - Fixed version with consistent return types
from typing import List, Dict, Any
from phi.tools import Toolkit, tool
import os
from datetime import datetime, timezone

# Import the unified auth function
from google_services import get_calendar_service

class CalendarTools(Toolkit):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.register(self.list_events)
        self.register(self.create_event)
        self.register(self.delete_event)

    def list_events(self, calendarId: str = 'primary', max_results: int = 10) -> str:
        """
        List upcoming events from Google Calendar
        
        Args:
            calendarId: Calendar ID (default: 'primary')
            max_results: Maximum number of events to return
            
        Returns:
            Formatted string of events
        """
        try:
            # Get current time in ISO format
            now = datetime.now(timezone.utc).isoformat()
            
            events_result = self.service.events().list(
                calendarId=calendarId,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])

            if not events:
                return "📅 No upcoming events found."

            output = "📅 Upcoming Events:\n\n"
            for i, event in enumerate(events, 1):
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'No Title')
                event_id = event.get('id', 'No ID')
                
                # Format the date/time more nicely
                if 'T' in start:
                    # It's a datetime
                    dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%Y-%m-%d %H:%M')
                else:
                    # It's a date
                    formatted_time = start
                
                output += f"{i}. {summary}\n"
                output += f"   Time: {formatted_time}\n"
                output += f"   ID: {event_id}\n\n"
                
            return output
            
        except Exception as e:
            error_msg = f"❌ Error listing events: {str(e)}"
            print(error_msg)  # Also print for debugging
            return error_msg

    def create_event(self, summary: str, start_datetime: str, end_datetime: str, 
                    timezone: str = 'America/Chicago', description: str = None) -> str:
        """
        Create a new event in Google Calendar
        
        Args:
            summary: Event title
            start_datetime: Start time in ISO format (e.g., '2025-06-22T15:00:00')
            end_datetime: End time in ISO format
            timezone: Timezone (default: 'UTC')
            description: Event description (optional)
            
        Returns:
            Confirmation message
        """
        try:
            event = {
                'summary': summary,
                'start': {
                    'dateTime': start_datetime,
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_datetime,
                    'timeZone': timezone,
                },
            }
            
            if description:
                event['description'] = description
                
            created_event = self.service.events().insert(calendarId='primary', body=event).execute()
            
            success_msg = f"✅ Event '{summary}' created successfully!"
            if created_event.get('htmlLink'):
                success_msg += f"\n🔗 Link: {created_event.get('htmlLink')}"
                
            return success_msg
            
        except Exception as e:
            error_msg = f"❌ Error creating event: {str(e)}"
            print(error_msg)  # Also print for debugging
            return error_msg

    def delete_event(self, event_id: str) -> str:
        """
        Delete an event from Google Calendar
        
        Args:
            event_id: The ID of the event to delete
            
        Returns:
            Confirmation message
        """
        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            return f"✅ Event with ID '{event_id}' deleted successfully."
            
        except Exception as e:
            error_msg = f"❌ Error deleting event: {str(e)}"
            print(error_msg)  # Also print for debugging
            return error_msg


# Test function
if __name__ == "__main__":
    try:
        print("Getting calendar service...")
        calendar_service = get_calendar_service()
        print("Calendar service obtained successfully!")
        
        print("Creating calendar tools...")
        calendar_tools = CalendarTools(service=calendar_service)
        print("Calendar tools created successfully!")

        # List upcoming events
        print("Listing upcoming events:")
        result = calendar_tools.list_events(max_results=5)
        print(result)

        # Uncomment to test creating an event
        # print("\nCreating test event...")
        # create_result = calendar_tools.create_event(
        #     summary="Test Meeting",
        #     start_datetime="2025-06-22T15:00:00",
        #     end_datetime="2025-06-22T16:00:00",
        #     timezone="America/New_York",
        #     description="This is a test event created by the calendar tool"
        # )
        # print(create_result)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nMake sure you have:")
        print("1. Downloaded credentials.json from Google Cloud Console")
        print("2. Enabled Google Calendar API")
        print("3. Set up OAuth 2.0 credentials")