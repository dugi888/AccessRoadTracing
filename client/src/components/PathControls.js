import React, { useState } from 'react';
import './PathControls.css';


const paramFields = [
  { name: "max_slope", label: "Max Slope", type: "number", min: "0.00", max: "1.00", step: "0.01" },
  { name: "min_elev", label: "Min Elevation", type: "number" },
  { name: "max_elev", label: "Max Elevation", type: "number" },
  { name: "max_angle", label: "Max Angle", type: "number" },
  { name: "max_step", label: "Max Step", type: "number" },
  { name: "grid_size", label: "Grid Size", type: "number" },
  { name: "buffer", label: "Bounding offset", type: "number" }
];

const PathControls = ({
  onProfileClick,
  onOptimalPathClick,
  params,
  setParams,
  disabled
}) => {
  // Track which params are enabled
  const [enabled, setEnabled] = useState({
    max_slope: false,
    min_elev:  false,
    max_elev:  false,
    max_angle: false,
    max_step:  false,
    grid_size: false,
    buffer: false
  });

  const handleChange = (e) => {
    setParams(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleCheckbox = (e) => {
    const { name, checked } = e.target;
    setEnabled(prev => ({
      ...prev,
      [name]: checked
    }));
  };

  // Compose params to send: only include enabled ones
  const getActiveParams = () => {
    const active = { algorithm: params.algorithm };
    for (const field of paramFields) {
      if (enabled[field.name]) {
        active[field.name] = params[field.name];
      }
    }
    return active;
  };

  // Wrap the click handlers to pass only active params
  const handleOptimalPathClick = () => {
    onOptimalPathClick(getActiveParams());
  };

  return (
  <div className="pathcontrols-container">
    <form className="pathcontrols-form" onSubmit={e => e.preventDefault()}>
      <label>
        Algorithm:
        <select name="algorithm" value={params.algorithm} onChange={handleChange}>
          <option value="astar">A*</option>
          <option value="dijkstra">Dijkstra</option>
          <option value="greedy">Greedy</option>
          <option value="theta_star">Theta*</option>
        </select>
      </label>
     {paramFields.map(field => (
  <label key={field.name} className="pathcontrols-label">
    <input
      type="checkbox"
      name={field.name}
      checked={enabled[field.name]}
      onChange={handleCheckbox}
    />
    {field.label}:
    <input
      type={field.type}
      name={field.name}
      value={params[field.name]}
      onChange={handleChange}
      disabled={!enabled[field.name]}
      min={field.min}
      max={field.max}
      step={field.step}
    />
  </label>
))}
      <div className="pathcontrols-buttons">
        <button type="button" onClick={onProfileClick} disabled={disabled}>
          Get Terrain Profile
        </button>
        <button type="button" onClick={handleOptimalPathClick} disabled={disabled}>
          Get Optimal Path
        </button>
      </div>
    </form>
  </div>
);
};

export default PathControls;