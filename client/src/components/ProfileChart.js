import { Line } from 'react-chartjs-2';
import { Chart, LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend } from 'chart.js';

Chart.register(LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend);

const ProfileChart = ({ profile }) => {
  if (!profile || !profile.distances || !profile.elevations) return null;

  const data = {
    labels: profile.distances.map(d => d.toFixed(2)),
    datasets: [
      {
        label: 'Elevation (m)',
        data: profile.elevations,
        fill: false,
        borderColor: 'blue',
        tension: 0.1,
        pointRadius: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: true },
      title: { display: true, text: 'Terrain Profile' },
    },
    scales: {
      x: { title: { display: true, text: 'Distance (m)' } },
      y: { title: { display: true, text: 'Elevation (m)' } },
    },
  };

return (
    <div
        style={{
        position: 'absolute',
        top: 40,
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

export default ProfileChart;