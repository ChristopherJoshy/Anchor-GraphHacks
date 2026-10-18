export type Json = null | boolean | number | string | Json[] | { [key: string]: Json }
export type RecordValue = Record<string, unknown>

export interface Point {
  lat: number
  lng: number
  label: string
  id?: string
}

export interface Arc {
  startLat: number
  startLng: number
  endLat: number
  endLng: number
  label: string
}
