import { cp, mkdir } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'

const source = new URL('../node_modules/cesium/Build/Cesium/', import.meta.url)
const target = new URL('../public/cesium/', import.meta.url)
await mkdir(target, { recursive: true })
for (const directory of ['Workers', 'ThirdParty', 'Assets', 'Widgets']) {
  await cp(fileURLToPath(new URL(directory, source)), fileURLToPath(new URL(directory, target)), { recursive: true })
}
console.log('Cesium workers, geographic assets, and widget resources prepared locally.')
