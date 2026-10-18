import { useEffect, useRef, useState } from 'react'
import { Compass, Globe2, Layers, Minus, Plus } from 'lucide-react'
import {
  ArcType, Cartesian2, Cartesian3, Color, Credit, DistanceDisplayCondition, Entity,
  ImageryLayer, LabelStyle, Math as CesiumMath, NearFarScalar, PolylineDashMaterialProperty,
  ScreenSpaceEventType, TileMapServiceImageryProvider, UrlTemplateImageryProvider, Viewer,
} from 'cesium'
import 'cesium/Build/Cesium/Widgets/widgets.css'
import type { MapConnection, MapLayer, MapLocation } from './geography'

export interface MapFocus { locationId: string; level: 'region' | 'city'; sequence: number }
interface Props {
  locations: MapLocation[]
  connections: MapConnection[]
  selectedId: string | null
  focus: MapFocus | null
  onSelect: (id: string) => void
  onConnection: (id: string) => void
}

const NASA_TILES = 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpeg'
const palette = { point: '#e7c398', selected: '#ffffff', failure: '#ef8c72', dependencies: '#9bb1c6', transport: '#b5bec2', recovery: '#94c7a5' }
const layerNames: Record<MapLayer, string> = { dependencies: 'Supplier dependencies', transport: 'Transport connections', recovery: 'Recovery allocations' }
const HOME_HEIGHT = 14_000_000

export function EarthExplorer({ locations, connections, selectedId, focus, onSelect, onConnection }: Props) {
  const host = useRef<HTMLDivElement>(null)
  const viewer = useRef<Viewer | null>(null)
  const callbacks = useRef({ onSelect, onConnection })
  callbacks.current = { onSelect, onConnection }
  const imagery = useRef<ImageryLayer | null>(null)
  const [ready, setReady] = useState(false)
  const [failure, setFailure] = useState('')
  const [tileWarning, setTileWarning] = useState('')
  const [basemap, setBasemap] = useState<'earth' | 'streets'>('earth')
  const [layers, setLayers] = useState<Record<MapLayer, boolean>>({ dependencies: true, transport: false, recovery: true })
  const [showLayers, setShowLayers] = useState(false)
  const [height, setHeight] = useState(HOME_HEIGHT)

  useEffect(() => {
    if (!host.current) return
    let instance: Viewer
    try {
      instance = new Viewer(host.current, {
        baseLayer: false, baseLayerPicker: false, animation: false, timeline: false,
        geocoder: false, homeButton: false, navigationHelpButton: false,
        sceneModePicker: false, fullscreenButton: false, infoBox: false,
        selectionIndicator: false, skyBox: false, requestRenderMode: true,
        maximumRenderTimeChange: Infinity, scene3DOnly: true,
      })
    } catch (error) {
      setFailure(`The 3D map could not start. ${error instanceof Error ? error.message : 'WebGL may be unavailable.'} Use the location list to inspect the same network.`)
      return
    }
    viewer.current = instance
    instance.scene.backgroundColor = Color.fromCssColorString('#111b24')
    instance.scene.globe.baseColor = Color.fromCssColorString('#233d4e')
    instance.scene.globe.enableLighting = false
    instance.scene.globe.maximumScreenSpaceError = 2
    instance.scene.screenSpaceCameraController.maximumZoomDistance = 35_000_000
    instance.scene.screenSpaceCameraController.minimumZoomDistance = 500
    if (instance.scene.sun) instance.scene.sun.show = false
    if (instance.scene.moon) instance.scene.moon.show = false
    instance.scene.fog.enabled = false
    instance.targetFrameRate = 40
    instance.imageryLayers.add(ImageryLayer.fromProviderAsync(TileMapServiceImageryProvider.fromUrl('/cesium/Assets/Textures/NaturalEarthII', {
      maximumLevel: 2, credit: new Credit('Natural Earth II · public domain', true),
    })))
    instance.camera.setView({ destination: Cartesian3.fromDegrees(77, 24, HOME_HEIGHT) })
    instance.screenSpaceEventHandler.setInputAction((event: { position: Cartesian2 }) => {
      const picked = instance.scene.pick(event.position)
      if (!(picked?.id instanceof Entity)) return
      const id = String(picked.id.id)
      if (id.startsWith('location:')) callbacks.current.onSelect(id.slice(9))
      if (id.startsWith('connection:')) callbacks.current.onConnection(id.slice(11))
    }, ScreenSpaceEventType.LEFT_CLICK)
    const removeCamera = instance.camera.moveEnd.addEventListener(() => setHeight(instance.camera.positionCartographic.height))
    const observer = new ResizeObserver(() => {
      if (!instance.isDestroyed()) { instance.resize(); instance.scene.requestRender() }
    })
    observer.observe(host.current)
    setReady(true)
    return () => {
      observer.disconnect()
      removeCamera()
      viewer.current = null
      if (!instance.isDestroyed()) instance.destroy()
    }
  }, [])

  useEffect(() => {
    const instance = viewer.current
    if (!ready || !instance) return
    if (imagery.current) instance.imageryLayers.remove(imagery.current)
    setTileWarning('')
    const provider = new UrlTemplateImageryProvider(basemap === 'earth' ? {
      url: NASA_TILES, maximumLevel: 8,
      credit: new Credit('NASA GIBS · Blue Marble composite imagery', true),
    } : {
      url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png', maximumLevel: 19,
      credit: new Credit('© OpenStreetMap contributors', true),
    })
    provider.errorEvent.addEventListener(() => setTileWarning('Some map tiles could not be loaded. Graph records are still available.'))
    imagery.current = instance.imageryLayers.addImageryProvider(provider)
    instance.scene.requestRender()
  }, [ready, basemap])

  useEffect(() => {
    const instance = viewer.current
    if (!instance || !ready) return
    instance.entities.removeAll()
    const indexed = new Map(locations.map(location => [location.id, location]))
    for (const location of locations) {
      const selected = location.id === selectedId
      const color = Color.fromCssColorString(location.affected.length ? palette.failure : selected ? palette.selected : palette.point)
      instance.entities.add({
        id: `location:${location.id}`,
        position: Cartesian3.fromDegrees(location.lng, location.lat, 5000),
        point: { color, pixelSize: selected ? 13 : 9, outlineColor: Color.fromCssColorString('#192831'), outlineWidth: 2 },
        label: { text: location.name, font: '13px IBM Plex Sans, sans-serif', fillColor: color,
          style: LabelStyle.FILL_AND_OUTLINE, outlineColor: Color.fromCssColorString('#15222b'), outlineWidth: 3,
          pixelOffset: new Cartesian2(0, -23), scaleByDistance: new NearFarScalar(1e5, 1, 2e7, 0.85),
          distanceDisplayCondition: new DistanceDisplayCondition(0, selected ? 4e7 : 1.1e7) },
      })
    }
    for (const connection of connections) {
      if (!layers[connection.layer]) continue
      const start = indexed.get(connection.from), end = indexed.get(connection.to)
      if (!start || !end) continue
      const color = Color.fromCssColorString(connection.affected ? palette.failure : palette[connection.layer])
      instance.entities.add({ id: `connection:${connection.id}`,
        polyline: { positions: Cartesian3.fromDegreesArrayHeights([start.lng, start.lat, 35000, end.lng, end.lat, 35000]),
          width: connection.layer === 'recovery' ? 3 : 1.5, arcType: ArcType.GEODESIC,
          material: connection.layer === 'transport' ? new PolylineDashMaterialProperty({ color, dashLength: 14 }) : color.withAlpha(0.8) },
      })
    }
    instance.scene.requestRender()
  }, [ready, locations, connections, selectedId, layers])

  const focusedLocation = focus ? locations.find(row => row.id === focus.locationId) : undefined
  const focusLocationId = focus?.locationId
  const focusLevel = focus?.level
  const focusSequence = focus?.sequence
  const focusLatitude = focusedLocation?.lat
  const focusLongitude = focusedLocation?.lng
  useEffect(() => {
    const instance = viewer.current
    if (!instance || !ready || !focusLocationId || focusLevel === undefined || focusLatitude === undefined || focusLongitude === undefined) return
    if (focusLevel === 'city') setBasemap('streets')
    instance.camera.flyTo({ destination: Cartesian3.fromDegrees(focusLongitude, focusLatitude, focusLevel === 'city' ? 22000 : 2_200_000),
      duration: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 1.4,
      orientation: { heading: 0, pitch: CesiumMath.toRadians(-90), roll: 0 } })
  }, [ready, focusLocationId, focusLevel, focusSequence, focusLatitude, focusLongitude])

  function home() {
    const instance = viewer.current
    if (!instance) return
    setBasemap('earth')
    instance.camera.flyTo({ destination: Cartesian3.fromDegrees(77, 24, HOME_HEIGHT), duration: 1.3,
      orientation: { heading: 0, pitch: -Math.PI / 2, roll: 0 } })
  }

  const cityDetail = basemap === 'streets' && height < 150_000
  const selectedLocation = locations.find(location => location.id === selectedId)
  return <section className={`earth-map ${basemap === 'streets' ? 'street-map' : ''}`} aria-label="Interactive supply network map">
    <div ref={host} className="cesium-host" role="group" aria-label="3D Earth map; use the location list to select records" />
    {!ready && !failure && <div className="map-loading" role="status">Opening the Earth explorer…</div>}
    {failure && <div className="map-failure" role="alert">{failure}</div>}
    <div className="map-heading"><span className="map-overline">{cityDetail ? 'Street context' : 'Connected operations'}</span><h1>{cityDetail ? `${selectedLocation?.name ?? 'Selected'} reference area` : 'Your supply network.'}</h1><p>{cityDetail ? 'City reference only · facility addresses are not shown.' : `${locations.length} geographic references · select a location to explore`}</p></div>
    <div className="map-top-controls">
      <div className="basemap-switch" role="group" aria-label="Base map"><button aria-pressed={basemap === 'earth'} onClick={() => setBasemap('earth')}>Earth</button><button aria-pressed={basemap === 'streets'} onClick={() => setBasemap('streets')}>Street detail</button></div>
      <button className="map-button" aria-expanded={showLayers} onClick={() => setShowLayers(!showLayers)}><Layers size={16} />Layers</button>
      {showLayers && <div className="layers-popover"><strong>Show on map</strong>{(Object.keys(layers) as MapLayer[]).map(key => <label key={key}><input type="checkbox" checked={layers[key]} onChange={() => setLayers(current => ({ ...current, [key]: !current[key] }))} /><span className={`line-key ${key}`} />{layerNames[key]}<small>{connections.filter(row => row.layer === key).length}</small></label>)}<p>Lines connect geographic reference points. They are not live shipment tracks.</p></div>}
    </div>
    <div className="map-navigation" role="group" aria-label="Map navigation"><button className="map-button" onClick={home} aria-label="Show whole Earth"><Globe2 size={18} /></button><button className="map-button" onClick={() => { const camera = viewer.current?.camera; if (camera) { camera.zoomIn(camera.positionCartographic.height * 0.45); viewer.current?.scene.requestRender() } }} aria-label="Zoom in"><Plus size={18} /></button><button className="map-button" onClick={() => { const camera = viewer.current?.camera; if (camera) { camera.zoomOut(camera.positionCartographic.height * 0.65); viewer.current?.scene.requestRender() } }} aria-label="Zoom out"><Minus size={18} /></button><button className="map-button" onClick={() => { viewer.current?.camera.flyTo({ destination: viewer.current.camera.position, orientation: { heading: 0, pitch: -Math.PI / 2, roll: 0 }, duration: 0.6 }) }} aria-label="Reset north"><Compass size={18} /></button></div>
    <div className="map-bottom"><div className="map-legend"><span><i className="location-key" />Reference location</span>{layers.dependencies && <span><i className="dependency-key" />Graph dependency</span>}{layers.transport && <span><i className="transport-key" />Modeled transport</span>}<span><i className="failure-key" />Affected</span>{layers.recovery && connections.some(connection => connection.layer === 'recovery') && <span><i className="recovery-key" />Recovery allocation</span>}</div><span className="map-altitude">{height < 150000 ? 'City reference view' : height < 6e6 ? 'Regional view' : 'Global view'} · {Math.round(height / 1000).toLocaleString()} km altitude</span></div>
    <div className="map-guidance">Drag to explore · scroll to zoom · click a marker for details</div>
    {basemap === 'earth' && height < 200000 && <div className="imagery-note">NASA composite imagery has limited city detail. Select <button onClick={() => setBasemap('streets')}>Street detail</button> for roads and place names.</div>}
    {tileWarning && <div className="imagery-note" role="status">{tileWarning}</div>}
    {ready && !locations.length && <div className="imagery-note" role="status">No graph locations loaded. Refresh the connection to display the network.</div>}
  </section>
}
