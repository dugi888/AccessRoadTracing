import {  useEffect, useRef, useState } from 'react';
import ProfileChart from './ProfileChart';
import OptimalPathChart from './OptimalPathChart';
import PathControls from './PathControls';
import * as THREE from 'three';


const PotreeViewer = () => {
  const containerRef = useRef(null);
  const viewerRef = useRef(null);
  const [selectedPoints, setSelectedPoints] = useState([]);
  const [profileResult, setProfileResult] = useState(null);
  const [optimalPathResult, setOptimalPathResult] = useState(null);

  const [params, setParams] = useState({
  algorithm: "astar",
  max_slope: "100",
  min_elev: "0",
  max_elev: "20000",
  grid_size: "100",
  max_angle: "180",
  max_step: "10000",
  buffer: "10",
});


useEffect(() => {
  if (
    window.Potree &&
    viewerRef.current &&
    optimalPathResult &&
    Array.isArray(optimalPathResult.path) &&
    optimalPathResult.path.length > 1
  ) {
    // Remove previous path if needed
    if (viewerRef.current.optimalPathLine) {
      viewerRef.current.scene.removeMeasurement(viewerRef.current.optimalPathLine);
      viewerRef.current.optimalPathLine = null;
    }

    // Create Potree polyline measurement using measuringTool
    const polyline = viewerRef.current.measuringTool.startInsertion({
      showDistances: false,
      closed: false,
      name: "Optimal Path"
    });
    optimalPathResult.path.forEach(([x, y, z]) => {
      polyline.addMarker(new THREE.Vector3(x, y, z));
    });
    
    polyline.closed = false;
    polyline.name = "Optimal Path";
    viewerRef.current.scene.addMeasurement(polyline);
    viewerRef.current.optimalPathLine = polyline;
    //viewerRef.current.measuringTool.cancelInsertion();
  }
}, [optimalPathResult, viewerRef]);
  useEffect(() => {
    // Create sidebar container
    let sidebar = document.getElementById('potree_sidebar_container');
    if (!sidebar) {
      sidebar = document.createElement('div');
      sidebar.id = 'potree_sidebar_container';
      sidebar.style.width = '300px';
      sidebar.style.height = '100%';
      sidebar.style.zIndex = 1000;
      sidebar.style.pointerEvents = 'auto';
      containerRef.current.appendChild(sidebar);
    }

    // Initialize Potree viewer
    if (window.Potree && !viewerRef.current) {
      const viewer = new window.Potree.Viewer(document.getElementById('potree_render_area'));
      viewerRef.current = viewer;

      viewer.setEDLEnabled(true);
      viewer.setFOV(60);
      viewer.setPointBudget(20_000_000);
      viewer.loadSettingsFromURL();
      viewer.loadGUI(() => {
        viewer.setLanguage('en');
        if (viewer.sidebar) {
          window.$(viewer.sidebar).show();
        }

        // Override measurement addition handler
        const originalAddMeasurement = viewer.scene.addMeasurement.bind(viewer.scene);
        viewer.scene.addMeasurement = function(measurement) {
          originalAddMeasurement(measurement);
          if (measurement.name === "Point") {
            const pointMeasurements = viewer.scene.measurements.filter(m => m.name === "Point");
            
            if (pointMeasurements.length >= 2) {
              setSelectedPoints(
                pointMeasurements
              );
            }
          }
        };
      });

      window.Potree.loadPointCloud('/pointclouds/mountain/ept.json', 'Terrain', e => {
        const pointcloud = e.pointcloud;
        viewer.scene.addPointCloud(pointcloud);
        viewer.setBackground("white"); // Potree's built-in method
        viewer.fitToScreen();
      });
    }
  }, []);


    // Function to send API request
  const sendProfileRequest = async () => {
    if (
      selectedPoints.length >= 2 &&
      selectedPoints[0].points[0]?.position &&
      selectedPoints[1].points[0]?.position
    ) {
      const p1 = selectedPoints[0].points[0].position;
      const p2 = selectedPoints[1].points[0].position;
      // Convert THREE.Vector3 to array [x, y, z]
      const point1 = [p1.x, p1.y, p1.z];
      const point2 = [p2.x, p2.y, p2.z];

      try {
        const response = await fetch('http://localhost:8000/profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ point1, point2 }),
        });
        if (!response.ok) {
          throw new Error(await response.text());
        }
        const data = await response.json();
        setProfileResult(data);
      } catch (err) {
        setProfileResult(null);
        console.error('API error:', err);
        alert('Error fetching profile data. Please try again.');
      }
    } else {
      alert('Please select two points first.');
    }
  };


const sendOptimalPathRequest = async (activeParams) => {
  if (
    selectedPoints.length >= 2 &&
    selectedPoints[0].points[0]?.position &&
    selectedPoints[1].points[0]?.position
  ) {
    const p1 = selectedPoints[0].points[0].position;
    const p2 = selectedPoints[1].points[0].position;
    const point1 = [p1.x, p1.y, p1.z];
    const point2 = [p2.x, p2.y, p2.z];

    const urlParams = new URLSearchParams(activeParams);

    try {
      const response = await fetch(`http://localhost:8000/optimal-path?${urlParams.toString()}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ point1, point2 }),
      });
      if (!response.ok) {
        throw new Error(await response.text());
      }
      const data = await response.json();
      if (!data.path || !Array.isArray(data.path) || data.path.length === 0) {
        alert('No valid path found. Please adjust your parameters.');
        throw new Error('Invalid path data received from server');
      }
      setOptimalPathResult(data);
    } catch (err) {
      setOptimalPathResult(null);
      console.error('API error:', err);
    }
  } else {
    alert('Please select two points first.');
  }
};

  return (
    <div
      ref={containerRef}
      className="potree_container"
      style={{
        position: 'absolute',
        width: '100%',
        height: '100%',
        left: 0,
        top: 0,
      }}
    >
      <div
        id="potree_render_area"
        style={{
          width: '100%',
          height: '100%',
        }}
      />
      
      <PathControls
        onProfileClick={sendProfileRequest}
        onOptimalPathClick={sendOptimalPathRequest}
        params={params}
        setParams={setParams}
        disabled={selectedPoints.length < 2}
      />
      <ProfileChart profile={profileResult} />
      <OptimalPathChart path={optimalPathResult?.path} />
    </div>
  );
};

export default PotreeViewer;