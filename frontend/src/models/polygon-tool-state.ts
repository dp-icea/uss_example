import * as Cesium from "cesium";
import { PolygonVolumeModel } from "./polygon";

export interface PolygonToolState {
  addedRegions: PolygonVolumeModel[];
  draftModel?: PolygonVolumeModel;
  draftEntity?: Cesium.Entity;
  guideEntity?: Cesium.Entity;
  vertices: Cesium.Cartographic[];
  isDrawing: boolean;
  isActive: boolean;
}
