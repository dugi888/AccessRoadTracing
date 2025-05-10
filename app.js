  // Create grid data with random elevations (0-100m)
        const gridSize = 40;
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