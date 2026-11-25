# Smart Courier Planner Website

This package adds a dark browser interface and local account system to the Smart Courier Planner algorithms. The website runs on your computer and uses Python's standard library; no third-party Python packages are needed.

## Start

1. Install Python 3.9 or newer.
2. Open this folder in VS Code or a terminal.
3. Run `python server.py`.
4. Open `http://127.0.0.1:8000` in a browser.

## Use

Create an account with an email address and a password of at least 8 characters, then sign in. Choose the included sample, paste a scenario as JSON, or generate a random scenario. The planner displays trips, parcel loading order, road paths, route distances, distance savings, and bin-packing statistics. Sign out from the top-right of the planner.

Accounts are saved in `users.json` beside `server.py`. Passwords are stored as salted PBKDF2 hashes. Login sessions last 12 hours and are held in memory, so restarting the server signs everyone out. This built-in account system is intended for a local capstone demonstration and is not configured for public internet hosting.

Scenario JSON uses `depot`, `vehicle_capacity`, `edges` as `[nodeA, nodeB, distance]` arrays, and `parcels` with `id`, `dest`, `weight`, `priority`, and `deadline` fields. The included `data/sample.json` is a working example.

The original CLI remains available through `python main.py`.
