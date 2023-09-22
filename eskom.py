import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import datetime
import os
import pytz
from tkcalendar import Calendar

# Constants
HISTORY_FILE = 'subscription_history.json'
NOTIFICATIONS = [55, 15, 5]
API_ENDPOINT = "https://eskom-calendar-api.shuttleapp.rs/outages/"
BASE_URL = "https://eskom-calendar-api.shuttleapp.rs"
SETTINGS_FILE = 'preferences.json'


class LoadsheddingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Loadshedding App")

        # Initialize tkinter StringVar for theme
        self.theme_var = tk.StringVar()

        # First, load settings
        self.load_settings()

        # Then, setup UI
        self.setup_ui()

        # Load history if exists
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as file:
                self.history = json.load(file)
        else:
            self.history = []

        # Initialize the GUI components first
        self.theme_var.set(self.settings["theme"])
        self.notif_time_slider.set(self.settings["notification_time"])
        self.apply_theme()

        # Initialize areas
        self.populate_areas_dropdown()
        self.update_subscribed_area_list()

        # Start checking for notifications
        self.check_for_notifications()
        self.root.after(60000, self.check_for_notifications)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as file:
                self.settings = json.load(file)
        else:
            self.settings = {
                "theme": "light",
                "notification_time": 15  # default to 15 minutes
            }

    def save_settings(self):
        with open(SETTINGS_FILE, 'w') as file:
            json.dump(self.settings, file)

    def apply_theme(self):
        if self.settings["theme"] == "dark":
            self.root.configure(bg="gray12")
        else:
            self.root.configure(bg="white")

    def on_theme_change(self):
        self.settings["theme"] = self.theme_var.get()
        self.save_settings()
        self.apply_theme()

    def on_notification_time_change(self, value):
        self.settings["notification_time"] = int(float(value))
        self.save_settings()

        # Load history if exists
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as file:
                self.history = json.load(file)
        else:
            self.history = []

    def setup_ui(self):
        # Tabbed Layout
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        self.status_frame = ttk.Frame(self.notebook)
        self.subscription_frame = ttk.Frame(self.notebook)
        self.history_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.status_frame, text="Current Status")
        self.notebook.add(self.subscription_frame, text="Subscription")
        self.notebook.add(self.history_frame, text="History")

        # Initialize missing GUI components
        self.calendar_label = ttk.Label(
            self.status_frame, text="Calendar Events:")
        self.calendar_label.pack(pady=10)

        # Assuming you want a Text widget for calendar_display
        self.calendar_display = tk.Text(self.status_frame, height=10, width=50)
        self.calendar_display.pack(pady=10)

        # Load history if exists
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as file:
                self.history = json.load(file)
        else:
            self.history = []

        # Styling
        style = ttk.Style()
        style.configure("TFrame", background="#E0E0E0")
        style.configure("TNotebook", tabposition="nw", font=('Arial', 10))
        style.configure("TNotebook.Tab", padding=(10, 5),
                        background="#D0D0D0", foreground="#000")

        # Status Tab - Reuse the code for fetching and displaying loadshedding details
        self.loadshedding_update_button = ttk.Button(
            self.status_frame, text="Update Status", command=self.update_calendar)
        self.loadshedding_update_button.pack(pady=10)

        # Subscription Tab
        self.subscription_label = ttk.Label(
            self.subscription_frame, text="Subscribe to an area:", font=("Arial", 12))
        self.subscription_label.pack(pady=20)

        self.subscription_dropdown = ttk.Combobox(self.subscription_frame)
        self.subscription_dropdown.pack(pady=10)

        self.subscribe_button = ttk.Button(
            self.subscription_frame, text="Subscribe")
        self.subscribe_button.pack(pady=20)

        # Now configure the subscribe_button's command
        self.subscribe_button.config(command=self.subscribe)

        # History Tab - Reuse the code for showing subscription history
        self.subscribed_areas_listbox = tk.Listbox(
            self.history_frame, height=5, cursor="hand2")
        self.subscribed_areas_listbox.pack(pady=10, fill="both", expand=True)
        self.subscribed_areas_listbox.bind(
            "<ButtonRelease-1>", self.show_subscribed_data)

        # Fetch areas for dropdown - Reuse the code
        self.populate_areas_dropdown()

        # Load history - Reuse the code
        self.load_subscription_history()

        # Treeview for Loadshedding details
        columns = ("Start Time", "End Time", "Stage")
        self.loadshedding_tree = ttk.Treeview(
            self.status_frame, columns=columns, show="headings")
        self.loadshedding_tree.heading("Start Time", text="Start Time")
        self.loadshedding_tree.heading("End Time", text="End Time")
        self.loadshedding_tree.heading("Stage", text="Stage")
        self.loadshedding_tree.pack(pady=20, padx=10, fill="both", expand=True)

        # Add Settings Frame to Notebook
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        self.setup_settings_ui()

        self.theme_var.set(self.settings["theme"])
        self.notif_time_slider.set(self.settings["notification_time"])

        self.apply_theme()

        # In the setup_settings_ui function:
        self.dark_mode_radio.config(command=self.on_theme_change)
        self.light_mode_radio.config(command=self.on_theme_change)
        self.notif_time_slider.config(command=self.on_notification_time_change)

    # Restored the name for this method
    def display_data_for_date(self, selected_date):
        if self.history:
            last_subscribed_area = self.history[-1]["area"]
            events = self.fetch_data_from_api(last_subscribed_area)
            for event in events:
                self.loadshedding_tree.insert("", "end", values=(
                    event['start'], event['finish'], event['stage']))

    # Corrected the method call here
    def on_date_select(self, event):
        selected_date = self.cal.get_date()
        self.display_data_for_date(selected_date)

    def update_calendar(self):
        if self.history:
            last_subscribed_area = self.history[-1]["area"]
            events = self.fetch_data_from_api(last_subscribed_area)
            events_text = "\n".join(
                [f"{event.get('start', 'N/A')} to {event.get('finish', event.get('finsh', 'N/A'))} - Stage {event.get('stage', 'N/A')}" for event in events])
            self.calendar_label.config(text=events_text)
            print(events)

    # NEW method to load subscription history into the listbox
    def load_subscription_history(self):
        # Load history if exists
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as file:
                self.history = json.load(file)
                # Populate the listbox with areas from history
                for entry in self.history:
                    self.subscribed_areas_listbox.insert(tk.END, entry["area"])
        else:
            self.history = []

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
                formatted_date = datetime.datetime.fromisoformat(
                    start_date).strftime('%d %b, %Y %H:%M:%S')
                self.calendar_display.insert(
                    tk.END, f"{formatted_date} - Stage {stage} Outage\n")
            except KeyError:
                print("Unexpected data format:", event)

    def subscribe(self):
        area = self.subscription_dropdown.get()
        if area:
            # Save to history
            self.history.append(
                {"area": area, "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
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
        selected_area = self.subscribed_areas_listbox.get(
            self.subscribed_areas_listbox.curselection())
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
        filtered_data = [
            event for event in data if filter_date in event['start']]
        return filtered_data

    def check_for_notifications(self):
        # Get the upcoming events for the last subscribed area (if any)
        if self.history:
            last_subscribed_area = self.history[-1]["area"]
            events = self.fetch_data_from_api(last_subscribed_area)

            # For each event, check if we should notify the user
            for event in events:
                start_time = datetime.datetime.fromisoformat(event['start'])
                # or whichever timezone you want
                local_tz = pytz.timezone('Africa/Johannesburg')
                current_time = datetime.datetime.now(local_tz)
                # Calculate time difference in minutes
                time_difference = (
                    start_time - current_time).total_seconds() / 60

                # If the time difference matches our notification times, show a notification
                if int(time_difference) == self.settings["notification_time"]:
                    self.notify(
                        f"Load shedding will start in {int(time_difference)} minutes!")

            # Call this function again after a minute to recheck
            self.root.after(60000, self.check_for_notifications)

    def notify(self, message):
        messagebox.showinfo("Notification", message)

    def setup_settings_ui(self):
        # Display Preferences Section
        display_pref_label = ttk.Label(
            self.settings_frame, text="Display Preferences", font=("Arial", 12))
        display_pref_label.grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 0))

        # Create the radio buttons and slider first
        self.dark_mode_radio = ttk.Radiobutton(
            self.settings_frame, text="Dark Mode", variable=self.theme_var, value="dark")
        self.light_mode_radio = ttk.Radiobutton(
            self.settings_frame, text="Light Mode", variable=self.theme_var, value="light")
        self.dark_mode_radio.grid(row=1, column=0, sticky="w", padx=20)
        self.light_mode_radio.grid(row=2, column=0, sticky="w", padx=20)

        # Notification Preferences Section
        notif_pref_label = ttk.Label(
            self.settings_frame, text="Notification Preferences", font=("Arial", 12))
        notif_pref_label.grid(row=3, column=0, sticky="w",
                              padx=10, pady=(10, 0))

        self.notif_time_slider = ttk.Scale(
            self.settings_frame, from_=5, to_=60, orient=tk.HORIZONTAL, length=200)
        self.notif_time_slider.set(15)
        self.notif_time_slider.grid(row=4, column=0, sticky="w", padx=20)

        self.dark_mode_radio.config(command=self.on_theme_change)
        self.light_mode_radio.config(command=self.on_theme_change)
        self.notif_time_slider.config(command=self.on_notification_time_change)

        # Credits Section
        credits_label = ttk.Label(
            self.settings_frame, text="Credits", font=("Arial", 12))
        credits_label.grid(row=6, column=0, sticky="w", padx=10, pady=(10, 0))
        credits_content = ttk.Label(
            self.settings_frame, text="Developed by [Your Name]. Libraries: OpenAI, Requests, etc.")
        credits_content.grid(row=7, column=0, sticky="w", padx=20)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x400")
    app = LoadsheddingApp(root)
    root.mainloop()
