# AccessRoadTracing

This project consists of two main parts: a **server** and a **client**.

---

## Project Structure

```
AccessRoadTracing/
├── server/   # Backend Python code (API, data processing, etc.)
├── client/   # Frontend React app
└── README.md
```

---

## Server

The server contains the backend logic for AccessRoadTracing.

### Setup

1. Navigate to the `server` directory:
    ```sh
    cd server
    ```
2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
3. Start the server:
    ```sh
    py api.py
    ```
4. The server will typically run on [http://localhost:8000](http://localhost:8000) 

---

## Client

The client is a React application for the frontend.

### Setup

1. Navigate to the `client` directory:
    ```sh
    cd client
    ```
2. Install dependencies:
    ```sh
    npm install
    ```
3. Start the development server:
    ```sh
    npm start
    ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser to view the app.

---

## Development Workflow

- Start the **server** first to provide backend APIs.
- Then start the **client** to interact with the frontend.
- Adjust API endpoints in the client as needed to match the server's address and port.

---

## Additional Notes

- See `client/README.md` for more details on the React app.
- See `server/README.md` (if available) for backend-specific documentation.

---
