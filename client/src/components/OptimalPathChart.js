import { Line } from 'react-chartjs-2';
import { Chart, LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend } from 'chart.js';

Chart.register(LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend);

const OptimalPathChart = ({ path }) => {
  if (!path || !Array.isArray(path) || path.length === 0) return null;

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
        maxHeight: 600,
        width: 800,
        height: 500,
        overflow: 'auto',
        border: '1px solid #ccc',
        boxShadow: '0 4px 16px rgba(0,0,0,0.15)',
      }}
    >
      <Line data={data} options={options} />
    </div>
  );
};

export default OptimalPathChart;