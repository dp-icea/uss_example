import * as Cesium from "cesium";
import { PolygonToolState } from "../models/polygon-tool-state";
import {
  PolygonVolumeModel,
  PolygonVolumeState,
  PolygonVolumeStateColors,
  PolygonVolumeRequestPayload,
} from "../models/polygon";
import { USSService } from "../services/uss.service";

const DEFAULT_HEIGHT = 50.0;
const MAX_HEIGHT = 120.0;

export class PolygonTool {
  private apiService: USSService;
  private viewer: Cesium.Viewer;
  private handler: Cesium.ScreenSpaceEventHandler;
  private annotations: Cesium.LabelCollection;
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
      vertices: [],
      isDrawing: false,
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

    // Right click handler to finish polygon
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

    const ray = this.viewer.camera.getPickRay(event.position);
    const groundPosition = this.viewer.scene.globe.pick(ray, this.viewer.scene);

    if (!Cesium.defined(groundPosition)) {
      return;
    }

    const cartographic = Cesium.Cartographic.fromCartesian(groundPosition);
    this.state.vertices.push(cartographic);

    if (!this.state.isDrawing) {
      this.startPolygonCreation();
    }

    this.updatePolygon();
  }

  private handleRightClick(
    event: Cesium.ScreenSpaceEventHandler.PositionedEvent,
  ): void {
    if (!this.state.isActive || !this.state.isDrawing) return;

    if (this.state.vertices.length >= 3) {
      this.finishPolygonCreation();
    }
  }

  private handleMouseMove(
    event: Cesium.ScreenSpaceEventHandler.MotionEvent,
  ): void {
    if (!this.state.isActive || !this.state.isDrawing) return;

    const ray = this.viewer.camera.getPickRay(event.endPosition);
    const groundPosition = this.viewer.scene.globe.pick(ray, this.viewer.scene);

    if (!Cesium.defined(groundPosition)) {
      return;
    }

    const cartographic = Cesium.Cartographic.fromCartesian(groundPosition);
    this.updateDynamicPolygon(cartographic);
  }

  private startPolygonCreation(): void {
    this.state.isDrawing = true;
    this.state.draftModel = {
      vertices: [...this.state.vertices],
      minHeight: 0,
      maxHeight: DEFAULT_HEIGHT,
      state: PolygonVolumeState.DRAFT,
    };
  }

  private updatePolygon(): void {
    if (!this.state.draftModel) return;

    this.state.draftModel.vertices = [...this.state.vertices];
    this.createPolygonEntity();
  }

  private updateDynamicPolygon(mousePosition: Cesium.Cartographic): void {
    if (!this.state.draftModel) return;

    const dynamicVertices = [...this.state.vertices, mousePosition];
    this.createPolygonEntity(dynamicVertices);
  }

  private createPolygonEntity(vertices?: Cesium.Cartographic[]): void {
    if (!this.state.draftModel) return;

    const polygonVertices = vertices || this.state.draftModel.vertices;

    if (polygonVertices.length < 2) return;

    // Remove existing entity
    if (this.state.draftEntity) {
      this.viewer.entities.remove(this.state.draftEntity);
    }

    // Convert to Cartesian3 array
    const positions = polygonVertices.map((vertex) =>
      Cesium.Cartographic.toCartesian(vertex),
    );

    this.state.draftEntity = this.viewer.entities.add({
      polygon: {
        hierarchy: positions,
        material:
          PolygonVolumeStateColors[PolygonVolumeState.DRAFT].withAlpha(0.5),
        outline: true,
        outlineColor: Cesium.Color.BLACK,
        extrudedHeight: this.state.draftModel.maxHeight,
        height: this.state.draftModel.minHeight,
      },
    });
  }

  private finishPolygonCreation(): void {
    if (!this.state.draftModel || this.state.vertices.length < 3) {
      return;
    }

    this.state.draftModel.entity = this.state.draftEntity;
    this.state.addedRegions.push(this.state.draftModel);

    // Reset state
    this.state.draftModel = undefined;
    this.state.draftEntity = undefined;
    this.state.vertices = [];
    this.state.isDrawing = false;
  }

  private updatePolygonColor(
    model: PolygonVolumeModel,
    color: Cesium.Color,
  ): void {
    if (!model.entity) return;

    this.viewer.entities.remove(model.entity);

    const positions = model.vertices.map((vertex) =>
      Cesium.Cartographic.toCartesian(vertex),
    );

    model.entity = this.viewer.entities.add({
      polygon: {
        hierarchy: positions,
        material: color.withAlpha(0.5),
        outline: true,
        outlineColor: Cesium.Color.BLACK,
        extrudedHeight: model.maxHeight,
        height: model.minHeight,
      },
    });
  }

  private showErrorMessage(model: PolygonVolumeModel, message: string): void {
    if (model.vertices.length === 0) return;

    const centerPosition = this.calculatePolygonCenter(model.vertices);
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

    const payload: PolygonVolumeRequestPayload = {
      volume: {
        outline_polygon: {
          vertices: model.vertices.map((vertex) => ({
            lng: vertex.longitude,
            lat: vertex.latitude,
          })),
        },
        altitude_lower: {
          value: model.minHeight,
          reference: "W84",
          units: "M",
        },
        altitude_upper: {
          value: model.maxHeight,
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
      this.updatePolygonColor(
        model,
        PolygonVolumeStateColors[PolygonVolumeState.ACCEPTED],
      );
      model.state = PolygonVolumeState.ACCEPTED;
    } catch (error: any) {
      this.updatePolygonColor(
        model,
        PolygonVolumeStateColors[PolygonVolumeState.ERROR],
      );
      model.state = PolygonVolumeState.ERROR;

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

  activate(): void {
    this.state.isActive = true;
  }

  deactivate(): void {
    this.state.isActive = false;
    this.state.isDrawing = false;
    this.state.vertices = [];

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
