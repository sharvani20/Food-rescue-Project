import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';

// Fix default leaflet icon paths for Vite build
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom colored SVG pin markers
const createCustomIcon = (color) => {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${color}" width="32" height="32" stroke="#ffffff" stroke-width="1.5"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>`;
  return L.divIcon({
    html: svg,
    className: 'custom-leaflet-pin',
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
  });
};

const icons = {
  DONOR: createCustomIcon('#059669'),     // Emerald Green
  NGO: createCustomIcon('#2563eb'),       // Royal Blue
  DEPOT: createCustomIcon('#4f46e5'),     // Indigo
  PICKUP: createCustomIcon('#d97706'),    // Amber
  DELIVERY: createCustomIcon('#16a34a'),  // Green
  DEFAULT: createCustomIcon('#64748b'),
};

const MapController = ({ center, zoom, markers, polylines }) => {
  const map = useMap();
  useEffect(() => {
    if (markers && markers.length > 0) {
      const validMarkers = markers.filter(m => m.lat && m.lng);
      if (validMarkers.length > 0) {
        const bounds = L.latLngBounds(validMarkers.map(m => [m.lat, m.lng]));
        if (polylines && polylines.length > 0) {
          polylines.forEach(p => {
            if (p.coords && p.coords.length > 0) {
              p.coords.forEach(c => bounds.extend(c));
            }
          });
        }
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 });
        return;
      }
    }
    map.setView(center, zoom);
  }, [markers, polylines, center, zoom, map]);
  return null;
};

export const LeafletMap = ({
  center = [17.7231, 83.3150], // Default center: Visakhapatnam, Andhra Pradesh
  zoom = 13,
  markers = [],
  polylines = [],
  height = '480px'
}) => {
  return (
    <div className="leaflet-map-wrapper" style={{ height }}>
      <MapContainer
        center={center}
        zoom={zoom}
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%' }}
      >
        <MapController center={center} zoom={zoom} markers={markers} polylines={polylines} />

        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Render Markers */}
        {markers.map((m, idx) => {
          const icon = icons[m.type] || icons.DEFAULT;
          return (
            <Marker key={m.id || idx} position={[m.lat, m.lng]} icon={icon}>
              <Popup>
                <div style={{ padding: '4px', maxWidth: '200px' }}>
                  <strong style={{ fontSize: '0.95rem', color: '#0f172a' }}>{m.title}</strong>
                  {m.type && (
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748b', marginTop: '2px' }}>
                      {m.type}
                    </div>
                  )}
                  {m.address && <p style={{ fontSize: '0.8rem', color: '#475569', margin: '4px 0 0 0' }}>{m.address}</p>}
                  {m.notes && <p style={{ fontSize: '0.8rem', fontStyle: 'italic', color: '#059669', margin: '4px 0 0 0' }}>{m.notes}</p>}
                </div>
              </Popup>
            </Marker>
          );
        })}

        {/* Render Polyline Route Paths */}
        {polylines.map((p, idx) => (
          <Polyline
            key={idx}
            positions={p.coords}
            pathOptions={{
              color: p.color || '#4f46e5',
              weight: 5,
              opacity: 0.85,
              dashArray: p.dashed ? '8, 8' : undefined
            }}
          />
        ))}
      </MapContainer>
    </div>
  );
};
