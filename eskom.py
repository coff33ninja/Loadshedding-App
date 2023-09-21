import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import datetime
import os
import pytz
from tkcalendar import Calendar

BASE_URL = "https://eskom-calendar-api.shuttleapp.rs"

# Constants
HISTORY_FILE = 'subscription_history.json'
NOTIFICATIONS = [55, 15, 5]
API_ENDPOINT = "https://eskom-calendar-api.shuttleapp.rs/outages/"

class LoadsheddingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Loadshedding App")

        # Add a Calendar
        self.cal = Calendar(self.root, selectmode='day')
        self.cal.pack(pady=20)
        self.cal.bind("<<CalendarSelected>>", self.on_date_select)

        # GUI Components
        self.setup_ui()

        # Load history if exists
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as file:
                self.history = json.load(file)
        else:
            self.history = []

        # Initialize areas
        self.populate_areas_dropdown()
        self.update_subscribed_area_list()

    def setup_ui(self):
        # Label to display calendar data
        self.calendar_label = ttk.Label(self.root, text="Loadshedding Calendar", font=("Arial", 16))
        self.calendar_label.pack(pady=20)
        
        # Frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10, expand=True, fill="both")

        # Scrollbar
        self.calendar_display_scroll = tk.Scrollbar(self.main_frame, orient="vertical")
        self.calendar_display_scroll.pack(side="right", fill="y")
    
        # Calendar UI - Using Text widget with Scrollbar
        self.calendar_display_scroll = tk.Scrollbar(self.main_frame, orient="vertical")
        self.calendar_display_scroll.pack(side="right", fill="y")
        self.calendar_display = tk.Text(self.main_frame, wrap=tk.NONE, yscrollcommand=self.calendar_display_scroll.set, height=10)
        self.calendar_display.pack(pady=25, padx=15, expand=True, fill="both")
        self.calendar_display_scroll.config(command=self.calendar_display.yview)

        # Subscription Option
        self.subscription_label = ttk.Label(self.root, text="Subscribe to area:")
        self.subscription_label.pack(pady=10)

        self.areas = ["western-cape-stellenbosch", "city-of-cape-town-area-15"]
        self.subscription_dropdown = ttk.Combobox(self.root, values=self.areas)
        self.subscription_dropdown.pack(pady=25)

        self.subscribe_button = ttk.Button(self.root, text="Subscribe", command=self.subscribe)
        self.subscribe_button.pack(pady=10)

        self.subscribed_areas_label = ttk.Label(self.root, text="Subscribed Areas:")
        self.subscribed_areas_label.pack(pady=10)

        self.subscribed_areas_listbox = tk.Listbox(self.root, height=5, cursor="hand2")
        self.subscribed_areas_listbox.pack(pady=10)
        self.subscribed_areas_listbox.bind("<ButtonRelease-1>", self.show_subscribed_data)

        # Update Calendar Button
        self.update_calendar_button = ttk.Button(self.root, text="Update Calendar", command=self.update_calendar)
        self.update_calendar_button.pack(pady=10)

        # Attribution
        self.attribution_label = ttk.Label(self.root, text="Data from EskomCalendar", font=("Arial", 10))
        self.attribution_label.pack(pady=20)

    def on_date_select(self, event):
        selected_date = self.cal.get_date()
        # Use the date to fetch and display load shedding information
        self.display_data_for_date(selected_date)

    def fetch_data_from_api(self, area):
        response = requests.get(API_ENDPOINT + area)
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def populate_areas_dropdown(self):
        areas = self.fetch_areas()
        if areas:
            self.subscription_dropdown["values"] = areas

    def fetch_areas(self, regex=None):
        endpoint = "/list_areas"
        if regex:
            endpoint += f"/{regex}"

        response = requests.get(BASE_URL + endpoint)
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def display_on_calendar(self, data):
        self.calendar_display.delete(1.0, tk.END)
        for event in data:
            try:
                start_date = event['start']  
                stage = event['stage']  
                formatted_date = datetime.datetime.fromisoformat(start_date).strftime('%d %b, %Y %H:%M:%S')
                self.calendar_display.insert(tk.END, f"{formatted_date} - Stage {stage} Outage\n")
            except KeyError:
                print("Unexpected data format:", event)

    def display_data_for_date(self, selected_date):
        if self.history:
            last_subscribed_area = self.history[-1]["area"]
            events = self.fetch_data_from_api(last_subscribed_area, selected_date)
            self.display_on_calendar(events)

    def subscribe(self):
        area = self.subscription_dropdown.get()
        if area:
            # Save to history
            self.history.append({"area": area, "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            with open(HISTORY_FILE, 'w') as file:
                json.dump(self.history, file)

            # Fetch and display data for the selected area
            events = self.fetch_data_from_api(area)
            self.display_on_calendar(events)

            # Update the listbox with the new area
            self.update_subscribed_area_list()

    def update_subscribed_area_list(self):
        # Clear the listbox
        self.subscribed_areas_listbox.delete(0, tk.END)
        
        # Populate the listbox with areas from history
        for entry in self.history:
            self.subscribed_areas_listbox.insert(tk.END, entry["area"])

    def show_subscribed_data(self, event=None):
        selected_area = self.subscribed_areas_listbox.get(self.subscribed_areas_listbox.curselection())
        if selected_area:
            events = self.fetch_data_from_api(selected_area)
            self.display_on_calendar(events)

    def fetch_data_from_api(self, area, filter_date=None):
        response = requests.get(API_ENDPOINT + area)
        if response.status_code != 200:
            return []

        data = response.json()
        if not filter_date:
            return data
    
        # If there's a date filter, we filter the data based on it
        filtered_data = [event for event in data if filter_date in event['start']]
        return filtered_data

    def update_calendar(self):
        # For now, we'll just update the calendar for the last selected area.
        # You may want to handle updating data for multiple areas or change the logic as per your needs.
        if self.history:
            last_subscribed_area = self.history[-1]["area"]
            events = self.fetch_data_from_api(last_subscribed_area)
            events_text = "\n".join([f"{event['start']} to {event['finsh']} - Stage {event['stage']}" for event in events])
            self.calendar_label.config(text=events_text)

    def check_for_notifications(self):
        # Get the upcoming events for the last subscribed area (if any)
        if self.history:
            last_subscribed_area = self.history[-1]["area"]
            events = self.fetch_data_from_api(last_subscribed_area)
        
            # For each event, check if we should notify the user
            for event in events:
                start_time = datetime.datetime.fromisoformat(event['start'])
                local_tz = pytz.timezone('Africa/Johannesburg')  # or whichever timezone you want
                current_time = datetime.datetime.now(local_tz)
                time_difference = (start_time - current_time).total_seconds() / 60  # Calculate time difference in minutes
            
                # If the time difference matches our notification times, show a notification
                if int(time_difference) in NOTIFICATIONS:
                    self.notify(f"Load shedding will start in {int(time_difference)} minutes!")

            # Call this function again after a minute to recheck
            self.root.after(60000, self.check_for_notifications)

    def notify(self, message):
        messagebox.showinfo("Notification", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = LoadsheddingApp(root)
    app.check_for_notifications()  # Start the notification checking loop
    root.mainloop()