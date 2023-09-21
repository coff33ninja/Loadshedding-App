## Loadshedding App Setup Guide

# Description:
The Loadshedding App is designed to function as a desktop widget, providing users with a convenient view of loadshedding schedules on their computer's desktop. The app leverages data from the EskomCalendar API. While the core concept of a desktop widget was envisioned by the creator, the data is sourced from an external API, ensuring real-time updates and accurate schedules.

# Pre-requisites:

- Administrative privileges on the machine.
- An active internet connection.

# Steps:

1. Navigate to the directory containing the setup batch file (setup.bat).
2. Right-click on setup.bat and select "Run as administrator". This ensures all commands execute with the necessary privileges.
3. The batch file will execute a series of commands to install necessary dependencies and launch the Loadshedding App (eskom.py).
4. Once the app is launched, follow the on-screen instructions to use the Loadshedding App.
5.  The batch file will pause at the end to show any messages or errors. Review them to ensure everything went smoothly.

# Commands executed by the batch file:

winget install python
pip install requests ics
pip install pytz
pip install tkcalendar
python eskom.py
pause

NB: Rerun setup.bat to be used as a launcher

## API Details:

# EskomCalendar API:

- Base URL: https://eskom-calendar-api.shuttleapp.rs
- Description: This API provides real-time loadshedding schedules based on regions. Data is sourced from the official EskomCalendar.

# Attribution:

Data is provided by the EskomCalendar API. Users are encouraged to always refer to official channels for critical decisions. The Loadshedding App and its creators are not affiliated with Eskom, and the accuracy of the data is dependent on the aforementioned API.

# Troubleshooting:

- If you encounter issues with Winget, ensure you have the latest version of the Windows App Installer.
- Ensure that Python is correctly added to your system's PATH.
- If you face any package installation issues, ensure you have an active internet connection and try again.
