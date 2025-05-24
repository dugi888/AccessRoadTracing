import { useEffect, useRef } from 'react';

const PotreeViewer = () => {
  const pointsRef = useRef([]);
  const containerRef = useRef(null);
  const viewerRef = useRef(null); // <-- Store viewer instance

  useEffect(() => {
    // Create sidebar container only if it doesn't exist
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

    // Only initialize Potree viewer once
    if (window.Potree && !viewerRef.current) {
      const viewer = new window.Potree.Viewer(document.getElementById('potree_render_area'));
      viewerRef.current = viewer; // Save instance

      viewer.setEDLEnabled(true);
      viewer.setFOV(60);
      viewer.setPointBudget(1_000_000);
      viewer.loadSettingsFromURL();
      viewer.loadGUI(() => {
        viewer.setLanguage('en');
        if (viewer.sidebar) {
          window.$(viewer.sidebar).show();
        }
      });

      window.Potree.loadPointCloud('/pointclouds/mountain/ept.json', 'Terrain', e => {
        const pointcloud = e.pointcloud;
        viewer.scene.addPointCloud(pointcloud);

        if (window.Potree.PointColorType && window.Potree.PointColorType.ELEVATION) {
          pointcloud.material.pointColorType = window.Potree.PointColorType.ELEVATION;
        } else {
          pointcloud.material.pointColorType = 1;
        }

        viewer.fitToScreen();
      });

      // Add click event listener for picking points
      const handleClick = (event) => {
        const rect = viewer.renderArea.getBoundingClientRect();
        const mouse = {
          x: event.clientX - rect.left,
          y: event.clientY - rect.top
        };

        let pickResult = null;
        if (window.Potree.utils && window.Potree.utils.pick) {
          pickResult = window.Potree.utils.pick(viewer, {
            camera: viewer.scene.getActiveCamera(),
            scene: viewer.scene.pointclouds,
            renderer: viewer.renderer,
            position: [mouse.x, mouse.y]
          });
        }

        if (pickResult && pickResult.position) {
          pointsRef.current.push(pickResult.position);
          if (pointsRef.current.length === 2) {
            console.log('Picked points:', pointsRef.current);
            pointsRef.current = [];
          }
        }
      };

      viewer.renderArea.addEventListener('click', handleClick);

      // Cleanup
      return () => {
        viewer.renderArea.removeEventListener('click', handleClick);
      };
    }
  }, []);

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
    </div>
  );
}

export default PotreeViewer;