// Create grid data with random elevations (0-100m)
const gridSize = 33;
let elevations = Array(gridSize).fill().map(() => 
    Array(gridSize).fill().map(() => Math.floor(Math.random() * 100))
);

// Create grid UI
const grid = document.getElementById('grid');
for (let i = 0; i < gridSize; i++) {
    for (let j = 0; j < gridSize; j++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.dataset.x = i;
        cell.dataset.y = j;
        cell.textContent = elevations[i][j];
        grid.appendChild(cell);
    }
}

let selectedPoints = [];
let chart = null;

// Grid click handler
grid.addEventListener('click', (e) => {
    if (!e.target.classList.contains('cell')) return;

    const cell = e.target;
    const x = parseInt(cell.dataset.x);
    const y = parseInt(cell.dataset.y);

    // Select/deselect points
    if (selectedPoints.length < 2) {
        cell.classList.add('selected');
        selectedPoints.push({x, y});
    }

    // When two points are selected
    if (selectedPoints.length === 2) {
        const path = getPath(selectedPoints[0], selectedPoints[1]);
        plotElevationProfile(path);
        selectedPoints = [];
        // Clear selection after 1s
        setTimeout(() => {
            document.querySelectorAll('.selected').forEach(c => c.classList.remove('selected'));
        }, 1000);
    }
});

// Bresenham's line algorithm to get path points
function getPath(start, end) {
    const path = [];
    let dx = Math.abs(end.x - start.x);
    let dy = -Math.abs(end.y - start.y);
    let sx = start.x < end.x ? 1 : -1;
    let sy = start.y < end.y ? 1 : -1;
    let err = dx + dy;
    
    let [x, y] = [start.x, start.y];
    
    while (true) {
        path.push({x, y, elevation: elevations[x][y]});
        if (x === end.x && y === end.y) break;
        let e2 = 2 * err;
        if (e2 >= dy) {
            err += dy;
            x += sx;
        }
        if (e2 <= dx) {
            err += dx;
            y += sy;
        }
    }
    return path;
}

// Plot elevation profile using Chart.js
function plotElevationProfile(path) {
    if (chart) chart.destroy();

    const ctx = document.getElementById('elevationChart').getContext('2d');
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: path.map((p, i) => i * 10 + 'm'),
            datasets: [{
                label: 'Elevation Profile',
                data: path.map(p => p.elevation),
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            scales: {
                y: {
                    title: {display: true, text: 'Elevation (m)'}
                },
                x: {
                    title: {display: true, text: 'Distance'}
                }
            }
        }
    });
}

// Diamond-Square Algorithm to generate terrain
function generateTerrain(size, roughness) {
    const grid = Array(size + 1).fill().map(() => Array(size + 1).fill(0));

    // Initialize corners
    grid[0][0] = Math.random() * 100;
    grid[0][size] = Math.random() * 100;
    grid[size][0] = Math.random() * 100;
    grid[size][size] = Math.random() * 100;

    let stepSize = size;
    let scale = roughness;

    while (stepSize > 1) {
        const halfStep = stepSize / 2;

        // Diamond step
        for (let x = 0; x < size; x += stepSize) {
            for (let y = 0; y < size; y += stepSize) {
                const avg = (grid[x][y] +
                             grid[x + stepSize][y] +
                             grid[x][y + stepSize] +
                             grid[x + stepSize][y + stepSize]) / 4;
                grid[x + halfStep][y + halfStep] = avg + (Math.random() * 2 - 1) * scale;
            }
        }

        // Square step
        for (let x = 0; x <= size; x += halfStep) {
            for (let y = (x + halfStep) % stepSize; y <= size; y += stepSize) {
                const avg = (
                    (grid[(x - halfStep + size + 1) % (size + 1)][y] || 0) +
                    (grid[(x + halfStep) % (size + 1)][y] || 0) +
                    (grid[x][(y - halfStep + size + 1) % (size + 1)] || 0) +
                    (grid[x][(y + halfStep) % (size + 1)] || 0)
                ) / 4;
                grid[x][y] = avg + (Math.random() * 2 - 1) * scale;

                // Ensure edges wrap correctly
                if (x === 0) grid[size][y] = grid[x][y];
                if (y === 0) grid[x][size] = grid[x][y];
            }
        }

        stepSize = halfStep;
        scale *= roughness;
    }

    return grid;
}




// Generate terrain and update the grid
const terrain = generateTerrain(gridSize - 1, 1);
elevations = terrain.map(row => row.map(value => Math.max(0, Math.min(100, Math.floor(value)))));


function getColor(elevation) {
    if (elevation < 10) {
        return '#0000FF'; // Deep blue (deep water)
    } else if (elevation < 20) {
        return '#4169E1'; // Royal blue (shallow water)
    } else if (elevation < 30) {
        return '#00FF00'; // Light green (low plains)
    } else if (elevation < 40) {
        return '#32CD32'; // Lime green (plains)
    } else if (elevation < 50) {
        return '#FFD700'; // Gold (low hills)
    } else if (elevation < 60) {
        return '#FFA500'; // Orange (hills)
    } else if (elevation < 70) {
        return '#8B4513'; // Saddle brown (high hills)
    } else if (elevation < 80) {
        return '#A0522D'; // Sienna (mountains)
    } else if (elevation < 90) {
        return '#D2B48C'; // Tan (high mountains)
    } else {
        return '#FFFFFF'; // White (snow caps)
    }
}
// Update grid UI with terrain data
// Update grid UI with terrain data and colors
grid.innerHTML = ''; // Clear existing grid
for (let i = 0; i < gridSize; i++) {
    for (let j = 0; j < gridSize; j++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.dataset.x = i;
        cell.dataset.y = j;
        cell.textContent = elevations[i][j];
        cell.style.backgroundColor = getColor(elevations[i][j]); // Set cell color
        grid.appendChild(cell);
    }
}