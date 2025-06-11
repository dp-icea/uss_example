import * as Cesium from "cesium";

export enum PolygonVolumeState {
  DRAFT = "DRAFT",
  ACCEPTED = "ACCEPTED",
  ERROR = "ERROR",
  REQUESTED = "REQUESTED",
}

export const PolygonVolumeStateColors = {
  [PolygonVolumeState.DRAFT]: Cesium.Color.YELLOW,
  [PolygonVolumeState.ACCEPTED]: Cesium.Color.GREEN,
  [PolygonVolumeState.ERROR]: Cesium.Color.RED,
  [PolygonVolumeState.REQUESTED]: Cesium.Color.GREY,
} as const;

export interface PolygonVolumeModel {
  base: Cesium.Cartographic[];
  height: number;
  entity?: Cesium.Entity;
  state: PolygonVolumeState;
}

export interface PolygonVolumeSchema {
  volume: {
    outline_polygon: {
      vertices: Array<{
        lng: number;
        lat: number;
      }>;
    };
    altitude_lower: {
      value: number;
      reference: string;
      units: string;
    };
    altitude_upper: {
      value: number;
      reference: string;
      units: string;
    };
  };
  time_start: {
    value: string;
    format: string;
  };
  time_end: {
    value: string;
    format: string;
  };
}

export interface PolygonVolumeRequestPayload {
  volume: {
    outline_polygon: {
      vertices: Array<{
        lng: number;
        lat: number;
      }>;
    };
    altitude_lower: {
      value: number;
      reference: string;
      units: string;
    };
    altitude_upper: {
      value: number;
      reference: string;
      units: string;
    };
  };
  time_start: {
    value: string;
    format: string;
  };
  time_end: {
    value: string;
    format: string;
  };
}
