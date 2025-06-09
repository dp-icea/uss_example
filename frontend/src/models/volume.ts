import * as Cesium from "cesium";

export interface VolumeData {
  position: Cesium.Cartesian3;
  radius: number;
  height: number;
}

export interface VolumeRequestPayload {
  volume: {
    outline_circle: {
      center: {
        lng: number;
        lat: number;
      };
      radius: {
        value: number;
        units: string;
      };
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

export interface CylinderToolState {
  groundPoint?: Cesium.Entity;
  groundPosition?: Cesium.Cartesian3;
  height: number;
  radius: number;
  lineFromGroundToHeaven?: Cesium.Entity;
  floatingPoint?: Cesium.Entity;
  floatingLabel?: Cesium.Label;
  cylinder?: Cesium.Entity;
  maxCylinder?: Cesium.Entity;
  wheelAcceleration: number;
  isActive: boolean;
}
