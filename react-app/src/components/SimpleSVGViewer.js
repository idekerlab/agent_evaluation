import React, { useRef, useEffect, useState } from 'react';

const SimpleSVGViewer = ({ svgString, maxWidth = '100%', maxHeight = '800px' }) => {
  const containerRef = useRef(null);
  const svgRef = useRef(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (svgRef.current) {
      try {
        // Parse the SVG string
        const parser = new DOMParser();
        const doc = parser.parseFromString(svgString, 'image/svg+xml');
        const parsedSvg = doc.documentElement;

        // Check if parsing resulted in an error
        const parserError = doc.querySelector('parsererror');
        if (parserError) {
          throw new Error('Invalid SVG');
        }

        // Clear previous content and append the new SVG
        svgRef.current.innerHTML = '';
        svgRef.current.appendChild(parsedSvg);

        // Adjust SVG attributes
        if (parsedSvg.tagName.toLowerCase() === 'svg') {
          parsedSvg.removeAttribute('width');
          parsedSvg.removeAttribute('height');
          parsedSvg.setAttribute('preserveAspectRatio', 'xMidYMid meet');

          if (!parsedSvg.getAttribute('viewBox')) {
            const bbox = parsedSvg.getBBox();
            parsedSvg.setAttribute('viewBox', `${bbox.x} ${bbox.y} ${bbox.width} ${bbox.height}`);
          }
        } else {
          throw new Error('Root element is not an SVG');
        }

        setError(null);
      } catch (err) {
        console.error('Error rendering SVG:', err);
        setError('Failed to render SVG. Please check the SVG content.');
      }
    }
  }, [svgString]);

  return (
    <div 
      ref={containerRef}
      style={{
        maxWidth: maxWidth,
        maxHeight: maxHeight,
        overflow: 'auto',
        border: '1px solid #ccc',
        borderRadius: '4px',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      {error ? (
        <div style={{ color: 'red', padding: '10px' }}>{error}</div>
      ) : (
        <div ref={svgRef} style={{ width: '90%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }} />
        )}
    </div>
  );
};

export default SimpleSVGViewer;