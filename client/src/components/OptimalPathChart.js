import { Line } from 'react-chartjs-2';
import { Chart, LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend } from 'chart.js';

Chart.register(LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend);

const OptimalPathChart = ({
  path,
  length,
  average_slope,
  min_slope,
  max_slope,
  local_average_slope,
  local_min_slope,
  local_max_slope
}) => {  if (!path || !Array.isArray(path) || path.length === 0) return null;

  // Split path into X, Y, Z arrays for plotting
  const xs = path.map(p => p[0]);
  const ys = path.map(p => p[1]);
  const zs = path.map(p => p[2]);

  
  const data = {
    labels: xs.map((_, i) => i), // Use index as label
    datasets: [
      {
        label: 'Elevation (m) along path',
        data: zs,
        fill: false,
        borderColor: 'green',
        tension: 0.1,
        pointRadius: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: true },
      title: { display: true, text: 'Optimal Path Elevation Profile' },
    },
    scales: {
      x: { title: { display: true, text: 'Path Step' } },
      y: { title: { display: true, text: 'Elevation (m)' } },
    },
  };

  return (
    <div
      style={{
        position: 'absolute',
        top: 60,
        right: 40,
        background: 'white',
        padding: '20px',
        zIndex: 2000,
        maxWidth: 900,
        maxHeight: 900,
        width: 800,
        height: 600,
        overflow: 'auto',
        border: '1px solid #ccc',
        boxShadow: '0 4px 16px rgba(0,0,0,0.15)',
      }}
    >
      <Line data={data} options={options} />
      <div style={{ marginTop: 20, fontSize: 16 }}>
        <b>Path Statistics:</b>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          <li><b>Length:</b> {length ? length.toFixed(2) : '/'} m</li>
          <li><b>Average slope (between path points):</b> {average_slope ? average_slope.toFixed(3) : '/'} </li>
          <li><b>Min slope (between path points):</b> {min_slope ? min_slope.toFixed(3) : '/'} </li>
          <li><b>Max slope (between path points):</b> {max_slope ? max_slope.toFixed(3) : '/'} </li>
          <li><b>Local average slope (neighbor steps):</b> {local_average_slope ? local_average_slope.toFixed(3) : '/'} </li>
          <li><b>Local min slope (neighbor steps):</b> {local_min_slope ? local_min_slope.toFixed(3) : '/'} </li>
          <li><b>Local max slope (neighbor steps):</b> {local_max_slope ? local_max_slope.toFixed(3) : '/'} </li>
        </ul>
      </div>
    </div>
  );
};

export default OptimalPathChart;