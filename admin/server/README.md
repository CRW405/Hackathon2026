# Admin server

Small Flask backend that accepts and stores swipe and sniff events.

How to run:

1. Ensure MongoDB is running locally.
2. Run the server:

   python admin/server/server.py

Endpoints are available on port 6000. Example endpoints:

- `POST /api/trackSwipe/`
- `GET  /api/getSwipes`
- `POST /api/packetSniff/postSniffs`
- `GET  /api/packetSniff/getSniffs`
