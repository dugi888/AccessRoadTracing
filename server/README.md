# Access Road Tracing Server

This server provides an API for generating terrain profiles and computing optimal paths between two 3D points using various pathfinding algorithms.

## Algorithms Supported

The `/optimal-path` endpoint supports the following algorithms:
- **A\*** (`astar`)
- **Dijkstra** (`dijkstra`)
- **Greedy Best-First Search** (`greedy`)
- **Theta\*** (`theta_star`)

Each algorithm can be selected via the `algorithm` query parameter.

## API Endpoints

### 1. `/profile`

**POST**  
Returns the terrain profile between two 3D points.

**Request Body:**
```json
{
  "point1": [x1, y1, z1],
  "point2": [x2, y2, z2]
}
```

### 2. `/optimal-path`

**POST**  
Finds the optimal path between two 3D points using the selected algorithm.

**Request Body:**
```json
{
  "point1": [x1, y1, z1],
  "point2": [x2, y2, z2]
}
```

**Query Parameters:**
- `algorithm`: `"astar"`, `"dijkstra"`, `"greedy"`, or `"theta_star"` (default: `"astar"`)
- `max_slope`: Maximum allowed slope (default: `100.0`)
- `min_elev`: Minimum elevation (optional)
- `max_elev`: Maximum elevation (optional)
- `grid_size`: Size of the grid (default: `100`)
- `max_step`: Maximum step distance (default: `10000.0`)
- `max_angle`: Maximum allowed angle (default: `180.0`)
- `buffer`: Buffer around the bounding box (default: `10`)

**Example Request:**
```
POST /optimal-path?algorithm=astar&max_slope=30
Content-Type: application/json

{
  "point1": [100, 200, 50],
  "point2": [300, 400, 60]
}
```

**Response:**
```json
{
  "path": [
    [x1, y1, z1],
    [x2, y2, z2],
    ...
  ]
}
```

## Running the Server

To start the server:
```sh
pip install -r requirements.txt
```

```sh
python api.py
```

The server will be available at `http://localhost:8000`.

