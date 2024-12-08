# Movie Database Project
This project is a desktop application that integrates with an SQL database to provide a robust tool for exploring and managing movie-related information. The application allows users to view detailed movie data, search for movies using advanced filtering options, and create personalized watchlists. It solves the problem of easily accessing, navigating, and organizing movie collections by combining a dynamic graphical user interface (GUI) with advanced database querying.

The goal of this application is to offer an intuitive user experience for navigating movie data, discovering films, organizing them into watchlists, and performing multi-field searches without needing direct database interaction.

---

## Features

- Filter movies using multiple fields like age rating, director name, genres, budget range, runtime, production company, and more.
- The GUI includes five main tabs: “Movies,” “Actors,” “Directors,” “Producers,” and “Awards.”
- Users can create and manage multiple watchlists. Watchlist entries automatically track user ratings, comments, and watchlist timestamps.
- Users can set custom filters or toggle columns to customize the displayed fields.
- Right-click on any name (star name, director, production company) to navigate to its relevant tab or row.
- Users can easily add movies to their personal watchlists directly from the “Movies” tab.
- The system is backed by a dynamic SQL database that syncs changes in real time.
- Log actions such as updates or changes for tracking and debugging purposes.

---

## Tech Stack
The Movie Database Desktop Application leverages the following technologies:

- **Backend**: MySQL for database management and Python for database queries and application logic
- **Frontend**: PyQt5, a Python library for creating user-friendly graphical interfaces
- **Database**: MySQL is used for storing structured movie, actor, director, and user interaction data

---

# Installation

## Prerequisites

Before setting up the application, ensure the following tools and dependencies are installed:

pandas==2.2.3
PyMySQL==1.1.1
PyQt5==5.15.11
PyQt5_sip==12.13.0

### Verify Python
Make sure Python 3.7 or higher is installed:

```bash
python3 --version

```

### Ensure MySQL is installed and running on your system:
```bash
mysql --version
```

### Steps to Install
## 1. Clone the project repository to your local machine: 
```bash
git clone https://github.com/avambaker/cs310_final_project.git
```

## 2. Install the Required Python Dependencies:
```bash
pip install PyQt5
pip install pandas
pip install pymysql
```

## 3. Run the project as a module
At the first run, you will be prompted for your SQL password. If you do not have a password, just press "ok."

Note: The default hostname is 'localhost'. If you need to change it, you can edit the code in src/classes/sql_controller.py. There are three instances of connections, so you will need to change it three times.
