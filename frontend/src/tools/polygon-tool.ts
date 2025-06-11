import * as Cesium from "cesium";
import { PolygonToolState } from "../models/polygon-tool-state";
import {
  PolygonVolumeModel,
  PolygonVolumeState,
  PolygonVolumeStateColors,
  PolygonVolumeRequestPayload,
  PolygonVolumeSchema,
} from "../models/polygon";
import { USSService } from "../services/uss.service";

const DEFAULT_HEIGHT = 50.0;
const MAX_HEIGHT = 120.0;

export class PolygonTool {
  private apiService: USSService;
  private viewer: Cesium.Viewer;
  private handler: Cesium.ScreenSpaceEventHandler;
  private annotations: Cesium.LabelCollection;
  private floatingHeightLabel?: Cesium.Label;
  // TODO: Implement later
  private floatingAreaLabel?: Cesium.Label;
  private state: PolygonToolState;

  constructor(viewer: Cesium.Viewer, apiService: USSService) {
    this.viewer = viewer;
    this.apiService = apiService;
    this.handler = new Cesium.ScreenSpaceEventHandler(viewer.canvas);
    this.annotations = viewer.scene.primitives.add(
      new Cesium.LabelCollection(),
    );

    this.state = {
      addedRegions: [],
      isDrawingBase: false,
      isActive: false,
    };

    this.setupEventHandlers();
  }

  private setupEventHandlers(): void {
    // Left click handler
    this.handler.setInputAction(
      (event: Cesium.ScreenSpaceEventHandler.PositionedEvent) => {
        this.handleLeftClick(event);
      },
      Cesium.ScreenSpaceEventType.LEFT_CLICK,
    );

    // Right click handler to finish base polygon
    this.handler.setInputAction(
      (event: Cesium.ScreenSpaceEventHandler.PositionedEvent) => {
        this.handleRightClick(event);
      },
      Cesium.ScreenSpaceEventType.RIGHT_CLICK,
    );

    // Mouse move handler for dynamic polygon
    this.handler.setInputAction(
      (event: Cesium.ScreenSpaceEventHandler.MotionEvent) => {
        this.handleMouseMove(event);
      },
      Cesium.ScreenSpaceEventType.MOUSE_MOVE,
    );
  }

  private handleLeftClick(
    event: Cesium.ScreenSpaceEventHandler.PositionedEvent,
  ): void {
    if (!this.state.isActive) return;

    // Start drawing the base of the polygon
    if (!this.state.draftModel) {
      this.startBasePolygonCreation(event);
    } else if (this.state.isDrawingBase) {
      this.updateBasePolygonCreation(event);
    } else {
      this.finishPolygonCreation(event);
    }
  }

  private startBasePolygonCreation(
    event: Cesium.ScreenSpaceEventHandler.PositionedEvent,
  ): void {
    const ray = this.viewer.camera.getPickRay(event.position);
    const groundPosition = this.viewer.scene.globe.pick(ray, this.viewer.scene);

    if (!Cesium.defined(groundPosition)) {
      return;
    }

    this.state.draftModel = {
      base: [],
      height: DEFAULT_HEIGHT,
      state: PolygonVolumeState.DRAFT,
    };

    this.state.draftModel.base.push(
      Cesium.Cartographic.fromCartesian(groundPosition),
    );

    this.state.isDrawingBase = true;
  }

  private updateBasePolygonCreation(
    event: Cesium.ScreenSpaceEventHandler.PositionedEvent,
  ): void {
    const ray = this.viewer.camera.getPickRay(event.position);
    const groundPosition = this.viewer.scene.globe.pick(ray, this.viewer.scene);

    if (!Cesium.defined(groundPosition)) {
      return;
    }

    const cartographic = Cesium.Cartographic.fromCartesian(groundPosition);
    this.state.draftModel.base.push(cartographic);

    if (this.state.draftEntity) {
      this.viewer.entities.remove(this.state.draftEntity);
    }

    const vertices = this.state.draftModel.base.slice();
    vertices.push(cartographic);

    this.state.draftEntity = this.viewer.entities.add({
      polygon: {
        hierarchy: new Cesium.PolygonHierarchy(
          vertices.map((vertex) => Cesium.Cartographic.toCartesian(vertex)),
        ),
        material:
          PolygonVolumeStateColors[PolygonVolumeState.DRAFT].withAlpha(0.5),
      },
    });
  }

  private finishPolygonCreation(
    event: Cesium.ScreenSpaceEventHandler.PositionedEvent,
  ): void {
    if (!this.state.isActive) return;

    if (!this.state.draftModel) {
      console.error("finishPolygonCreation called without draftModel");
      return;
    }

    if (this.state.draftModel.base.length < 3) {
      console.error("Not enough points in the base of the polygon");
      return;
    }

    this.state.draftModel.entity = this.state.draftEntity;
    this.state.addedRegions.push(this.state.draftModel);

    this.viewer.entities.remove(this.state.guideEntity);
    this.state.isDrawingBase = false;
    this.state.draftModel = undefined;

    if (this.state.draftEntity) {
      this.state.draftEntity = undefined;
    }
  }

  private handleRightClick(
    event: Cesium.ScreenSpaceEventHandler.PositionedEvent,
  ): void {
    if (!this.state.isActive || !this.state.isDrawingBase) return;

    if (!this.state.draftModel || this.state.draftModel.base.length < 3) {
      this.showErrorMessage(
        this.state.draftModel,
        "At least 3 points are required to form a polygon.",
      );
      return;
    }

    this.state.isDrawingBase = false;

    if (this.state.draftEntity) {
      this.viewer.entities.remove(this.state.draftEntity);
    }

    console.log(this.state.draftModel.base);
    this.state.draftEntity = this.viewer.entities.add({
      polygon: {
        hierarchy: new Cesium.PolygonHierarchy(
          this.state.draftModel.base.map((vertex) =>
            Cesium.Cartographic.toCartesian(vertex),
          ),
        ),
        material:
          PolygonVolumeStateColors[PolygonVolumeState.DRAFT].withAlpha(0.5),
        height: this.getMinHeight(this.state.draftModel.base),
        extrudedHeight:
          this.getMinHeight(this.state.draftModel.base) +
          this.state.draftModel.height,
        outline: true,
        outlineColor: Cesium.Color.BLACK,
        outlineWidth: 5,
      },
    });

    this.state.guideEntity = this.viewer.entities.add({
      polygon: {
        hierarchy: new Cesium.PolygonHierarchy(
          this.state.draftModel.base.map((vertex) =>
            Cesium.Cartographic.toCartesian(vertex),
          ),
        ),
        material: Cesium.Color.GREY.withAlpha(0.01),
        height: this.getMinHeight(this.state.draftModel.base),
        extrudedHeight:
          this.getMinHeight(this.state.draftModel.base) + MAX_HEIGHT,
      },
    });
    console.log("Guide Entity created:", this.state.guideEntity);
  }

  private getMinHeight(vertices: Cesium.Cartographic[]): number {
    if (!vertices || vertices.length === 0) {
      return 0;
    }

    return vertices.reduce((min, vertex) => {
      return Math.min(min, vertex.height);
    }, Infinity);
  }

  private handleHeightChange(
    event: Cesium.ScreenSpaceEventHandler.MotionEvent,
  ): void {
    if (!this.state.isActive || this.state.isDrawingBase) return;

    if (!this.state.draftModel || !this.state.guideEntity) {
      return;
    }

    const hitEntity = this.viewer.scene.pick(event.endPosition);
    if (
      !Cesium.defined(hitEntity) ||
      (hitEntity.id !== this.state.guideEntity &&
        hitEntity.id !== this.state.draftEntity)
    ) {
      return;
    }

    const hitPosition = this.viewer.scene.pickPosition(event.endPosition);
    if (!Cesium.defined(hitPosition)) {
      return;
    }

    const hitCartographicPosition =
      Cesium.Cartographic.fromCartesian(hitPosition);
    const minHeight = this.getMinHeight(this.state.draftModel.base);

    this.state.draftModel.height = hitCartographicPosition.height - minHeight;
    const heightText = `${this.state.draftModel.height.toFixed(2)} m`;

    // Update label
    if (this.floatingHeightLabel)
      this.annotations.remove(this.floatingHeightLabel);
    this.floatingHeightLabel = this.annotations.add({
      position: hitPosition,
      text: heightText,
      showBackground: true,
      font: "14px monospace",
      horizontalOrigin: Cesium.HorizontalOrigin.LEFT,
      verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
      disableDepthTestDistance: Number.POSITIVE_INFINITY,
    });

    if (this.state.draftEntity)
      this.viewer.entities.remove(this.state.draftEntity);
    this.state.draftEntity = this.viewer.entities.add({
      polygon: {
        hierarchy: new Cesium.PolygonHierarchy(
          this.state.draftModel.base.map((vertex) =>
            Cesium.Cartographic.toCartesian(vertex),
          ),
        ),
        height: this.getMinHeight(this.state.draftModel.base),
        extrudedHeight:
          this.getMinHeight(this.state.draftModel.base) +
          this.state.draftModel.height,
        material:
          PolygonVolumeStateColors[PolygonVolumeState.DRAFT].withAlpha(0.5),
        outline: true,
        outlineColor: Cesium.Color.BLACK,
      },
    });
  }

  private handleBaseChange(
    event: Cesium.ScreenSpaceEventHandler.MotionEvent,
  ): void {
    const ray = this.viewer.camera.getPickRay(event.endPosition);
    const groundPosition = this.viewer.scene.globe.pick(ray, this.viewer.scene);

    if (!Cesium.defined(groundPosition)) {
      return;
    }

    const cartographic = Cesium.Cartographic.fromCartesian(groundPosition);

    const vertices = this.state.draftModel.base.slice();
    vertices.push(cartographic);

    if (this.state.draftEntity) {
      this.viewer.entities.remove(this.state.draftEntity);
    }

    this.state.draftEntity = this.viewer.entities.add({
      polygon: {
        hierarchy: new Cesium.PolygonHierarchy(
          vertices.map((vertex) => Cesium.Cartographic.toCartesian(vertex)),
        ),
        material:
          PolygonVolumeStateColors[PolygonVolumeState.DRAFT].withAlpha(0.5),
        outline: true,
        outlineColor: Cesium.Color.BLACK,
      },
    });
  }

  private handleMouseMove(
    event: Cesium.ScreenSpaceEventHandler.MotionEvent,
  ): void {
    if (!this.state.isActive) return;

    if (!this.state.draftModel) return;

    if (this.state.isDrawingBase) {
      this.handleBaseChange(event);
    } else {
      this.handleHeightChange(event);
    }
  }

  private showErrorMessage(model: PolygonVolumeModel, message: string): void {
    if (model.base.length === 0) return;

    const centerPosition = this.calculatePolygonCenter(model.base);
    const errorLabel = this.annotations.add({
      position: Cesium.Cartographic.toCartesian(centerPosition),
      text: `ERROR: ${message}`,
      showBackground: true,
      backgroundColor: Cesium.Color.RED.withAlpha(0.8),
      fillColor: Cesium.Color.WHITE,
      font: "16px monospace",
      horizontalOrigin: Cesium.HorizontalOrigin.CENTER,
      verticalOrigin: Cesium.VerticalOrigin.TOP,
      disableDepthTestDistance: Number.POSITIVE_INFINITY,
      pixelOffset: new Cesium.Cartesian2(0, -50),
    });

    setTimeout(() => {
      this.annotations.remove(errorLabel);
    }, 5000);
  }

  private calculatePolygonCenter(
    vertices: Cesium.Cartographic[],
  ): Cesium.Cartographic {
    let totalLat = 0;
    let totalLon = 0;
    let totalHeight = 0;

    for (const vertex of vertices) {
      totalLat += vertex.latitude;
      totalLon += vertex.longitude;
      totalHeight += vertex.height;
    }

    return new Cesium.Cartographic(
      totalLon / vertices.length,
      totalLat / vertices.length,
      totalHeight / vertices.length,
    );
  }

  async submitVolumeRequest(startTime: string, endTime: string): Promise<void> {
    console.info("Trying to submit volume request...");

    if (this.state.addedRegions.length === 0) {
      throw new Error("No polygon regions available to submit.");
    }

    const modelIndex = this.state.addedRegions.findIndex(
      (model) => model.state === PolygonVolumeState.DRAFT,
    );
    if (modelIndex === -1) {
      throw new Error("No draft model available to submit.");
    }

    const model = this.state.addedRegions[modelIndex];

    const minHeight = this.getMinHeight(model.base);

    const payload: PolygonVolumeRequestPayload = {
      volume: {
        outline_polygon: {
          vertices: model.base.map((vertex) => ({
            lng: vertex.longitude,
            lat: vertex.latitude,
          })),
        },
        altitude_lower: {
          value: minHeight,
          reference: "W84",
          units: "M",
        },
        altitude_upper: {
          value: minHeight + model.height,
          reference: "W84",
          units: "M",
        },
      },
      time_start: {
        value: startTime,
        format: "RFC3339",
      },
      time_end: {
        value: endTime,
        format: "RFC3339",
      },
    };

    try {
      await this.apiService.submitFlightPlan(payload);
      // TODO: Make the polygon green
      model.state = PolygonVolumeState.ACCEPTED;

      this.drawModel(model);
    } catch (error: any) {
      // TODO: Make the polygon red
      model.state = PolygonVolumeState.ERROR;

      this.drawModel(model);

      if (error.response && error.response.status === 409) {
        const errorData = error.response.data;
        let errorMessage =
          "Flight plan conflicts with existing constraints or operational intents";

        if (errorData.detail && errorData.detail.message) {
          errorMessage = errorData.detail.message;
        }

        this.showErrorMessage(model, errorMessage);
        console.error("Conflict error:", errorData);
      } else {
        const errorMessage = error.message || "Unknown error occurred";
        this.showErrorMessage(model, errorMessage);
        console.error("Error submitting volume request:", error);
      }

      throw error;
    }
  }

  public drawModel(model: PolygonVolumeModel): void {
    if (!model.entity) {
      return;
    }

    this.viewer.entities.remove(model.entity);
    model.entity = this.viewer.entities.add({
      polygon: {
        hierarchy: new Cesium.PolygonHierarchy(
          model.base.map((vertex) => Cesium.Cartographic.toCartesian(vertex)),
        ),
        material: PolygonVolumeStateColors[model.state].withAlpha(0.5),
        height: this.getMinHeight(model.base),
        extrudedHeight: this.getMinHeight(model.base) + model.height,
        outline: true,
        outlineColor: Cesium.Color.BLACK,
      },
    });
  }

  public drawConflictRegion(region: PolygonVolumeSchema): void {
    const minHeight = region.volume.altitude_lower.value;
    const maxHeight = region.volume.altitude_upper.value;

    const vertices = region.volume.outline_polygon.vertices.map(
      (vertex) => new Cesium.Cartographic(vertex.lng, vertex.lat, minHeight),
    );

    const polygonEntity = this.viewer.entities.add({
      polygon: {
        hierarchy: new Cesium.PolygonHierarchy(
          vertices.map((vertex) => Cesium.Cartographic.toCartesian(vertex)),
        ),
        material: Cesium.Color.GREY.withAlpha(0.5),
        height: minHeight,
        extrudedHeight: maxHeight,
        outline: true,
        outlineColor: Cesium.Color.RED,
      },
    });

    this.state.addedRegions.push({
      base: vertices,
      height: maxHeight - minHeight,
      entity: polygonEntity,
      state: PolygonVolumeState.ERROR,
    });
  }

  activate(): void {
    this.state.isActive = true;
  }

  deactivate(): void {
    this.state.isActive = false;
    this.state.isDrawingBase = false;

    if (this.state.draftEntity) {
      this.viewer.entities.remove(this.state.draftEntity);
      this.state.draftEntity = undefined;
    }

    this.state.draftModel = undefined;
  }

  destroy(): void {
    this.handler.destroy();
  }
}
