

# Hackathon 2026

## 2084

Its like 1984 but you're big brother.

## Overview

This repository contains a lightweight demo/hackathon project that demonstrates an admin panel which collects badge swipe events and simple network sniff (HTTP host/SNI) events, stores them in a local MongoDB instance, and provides a small Flask-based admin UI to view and filter the events.

The project is structured into three main areas:

- admin/server: Backend Flask server that receives and stores events into MongoDB and exposes REST endpoints.
- admin/client: Flask web UI that queries the backend and renders pages for swipes and network sniff events.
- packetSniffer / camera / swipe / logger: Helper scripts and probes used to capture or generate events (sniffers, camera utilities, keylogger script for demo).

This README documents how to run the components locally and what each part does.

## Requirements

- Python 3.11+ (project was developed with modern typing features)
- MongoDB connection and service URLs are configurable via a `.env` file or environment variables. The following keys are supported with defaults shown:

- `SERVER` (default: `http://localhost:6000`) - backend admin server URL
- `CLIENT` (default: `http://localhost:3000`) - client origin allowed by CORS
- `MONGO_URI` (default: `mongodb://localhost:27017/`) - MongoDB connection string
- `DB` (default: `hackathon`) - MongoDB database name used by the app
- Install Python deps: `pip install -r requirements.txt`

## Quick start

1. Start MongoDB on your machine (default port 27017).
2. Run the backend server from `admin/server`:

	python admin/server/server.py

	This starts the backend on port 6000 and exposes the endpoints:
	- POST /api/trackSwipe/  (record a swipe)
	- GET  /api/getSwipes     (retrieve swipes)
	- POST /api/packetSniff/postSniffs  (record sniff)
	- GET  /api/packetSniff/getSniffs   (retrieve sniffs)

3. Run the admin client UI from `admin/client`:

	python admin/client/client.py

	The client runs on port 5000 and provides:
	- / (combined dashboard)
	- /swipes (swipes page)
	- /internet (network sniff page)

## Design notes

- The admin client fetches data from the backend and provides query-parameter based filtering. Imports are written to work when run as a script or package.
- Timestamps are stored as Python `datetime` objects in MongoDB; the client utilities provide tolerant parsing for ISO datetimes, epoch seconds, and strings ending with Z (UTC).

## Files of interest

- `admin/server/routes/*.py` — REST endpoints and MongoDB persistence.
- `admin/client/routes/*.py` — Blueprints used by the client UI.
- `admin/client/utils.py` — Filtering and datetime parsing helpers (well-documented functions).
- `packetSniffer/gemSnifferV3.py` — network sniffing and SNI/host extraction (use carefully; requires appropriate permissions).

## Security and ethics

This project contains tools that can capture network metadata (SNI/HTTP host) and keystrokes. Only run these tools in controlled, consenting environments. Do not deploy or use them to capture data you are not authorized to collect.

## Contributing

If you'd like additional docs (API doc, OpenAPI spec, or developer setup scripts), open an issue or submit a PR.


