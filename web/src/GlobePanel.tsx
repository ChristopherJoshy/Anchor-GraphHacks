import Globe from 'react-globe.gl'
import { useMemo } from 'react'
import { arcsFrom, pointsFrom } from './data'

export function GlobePanel({ network }: { network: unknown }) {
  const points = useMemo(() => pointsFrom(network), [network])
  const arcs = useMemo(() => arcsFrom(network), [network])
  return <div className="globe-stage" aria-label="Network location globe">
    {points.length ? <Globe
      width={600}
      height={360}
      backgroundColor="rgba(0,0,0,0)"
      globeImageUrl="https://unpkg.com/three-globe/example/img/earth-night.jpg"
      bumpImageUrl="https://unpkg.com/three-globe/example/img/earth-topology.png"
      pointsData={points}
      pointLat="lat"
      pointLng="lng"
      pointColor={() => '#62e2bd'}
      pointAltitude={0.018}
      pointRadius={0.42}
      pointLabel="label"
      arcsData={arcs}
      arcStartLat="startLat"
      arcStartLng="startLng"
      arcEndLat="endLat"
      arcEndLng="endLng"
      arcColor={() => ['#44dec0', '#ef725c']}
      arcStroke={0.4}
      arcDashLength={0.35}
      arcDashGap={0.18}
      arcDashAnimateTime={2400}
      atmosphereColor="#268f83"
      atmosphereAltitude={0.13}
      enablePointerInteraction
    /> : <div className="globe-empty"><span className="globe-orbit" aria-hidden="true"><i /></span><b>Location coordinates unavailable</b><span>The network response did not include displayable coordinates.</span></div>}
    <div className="globe-legend"><span><i className="legend-dot" />Entities</span><span><i className="legend-line" />Relationships with mapped endpoints</span></div>
  </div>
}
