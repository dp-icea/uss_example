import * as Cesium from "cesium";
import { VolumeData, CylinderToolState, VolumeRequestPayload } from "../models/volume";
import { VolumeApiService } from "../services/volume-api.service";

export class CylinderTool {
  private viewer: Cesium.Viewer;
  private handler: Cesium.ScreenSpaceEventHandler;
  private annotations: Cesium.LabelCollection;
  private state: CylinderToolState;
  private volumeAdded: VolumeData[] = [];
  private apiService: VolumeApiService;

  constructor(viewer: Cesium.Viewer, apiService: VolumeApiService) {
    this.viewer = viewer;
    this.apiService = apiService;
    this.handler = new Cesium.ScreenSpaceEventHandler(viewer.canvas);
    this.annotations = viewer.scene.primitives.add(new Cesium.LabelCollection());

    this.state = {
      height: 0,
      radius: 50.0,
      wheelAcceleration: 1.0,
      isActive: false,
    };

    this.setupEventHandlers();
  }

  private setupEventHandlers(): void {
    // Remove default double-click behavior
    this.viewer.cesiumWidget.screenSpaceEventHandler.removeInputAction(
      Cesium.ScreenSpaceEventType.LEFT_DOUBLE_CLICK
    );

    // Left click handler
    this.handler.setInputAction((movement: any) => {
      this.handleLeftClick(movement);
    }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

    // Mouse move handler
    this.handler.setInputAction((movement: any) => {
      this.handleMouseMove(movement);
    }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);

    // Wheel handler
    this.handler.setInputAction((movement: any) => {
      this.handleWheel(movement);
    }, Cesium.ScreenSpaceEventType.WHEEL);

    // Right click for height annotations
    this.handler.setInputAction((movement: any) => {
      this.handleRightClick(movement);
    }, Cesium.ScreenSpaceEventType.RIGHT_CLICK);
  }

  private handleLeftClick(movement: any): void {
    if (!Cesium.defined(this.state.groundPoint)) {
      this.startCylinderCreation(movement);
    } else {
      this.finishCylinderCreation();
    }
  }

  private startCylinderCreation(movement: any): void {
    const ray = this.viewer.camera.getPickRay(movement.position);
    const earthPosition = this.viewer.scene.globe.pick(ray, this.viewer.scene);

    if (!Cesium.defined(earthPosition)) {
      return;
    }

    this.state.groundPoint = this.createPoint(earthPosition);
    this.state.floatingPoint = this.createPoint(earthPosition);
    this.state.groundPosition = earthPosition;

    // Create max cylinder (guide)
    this.state.maxCylinder = this.viewer.entities.add({
      position: this.state.groundPosition,
      cylinder: {
        length: 120.0,
        topRadius: this.state.radius + 1.0,
        bottomRadius: this.state.radius + 1.0,
        material: Cesium.Color.YELLOW.withAlpha(0.01),
      },
    });

    // Create main cylinder - changed to YELLOW
    this.state.height = 0;
    this.state.cylinder = this.viewer.entities.add({
      position: this.state.groundPosition,
      cylinder: {
        length: this.state.height,
        topRadius: this.state.radius,
        bottomRadius: this.state.radius,
        material: Cesium.Color.YELLOW.withAlpha(0.5),
        outline: true,
        outlineColor: Cesium.Color.BLACK,
      },
    });

    // Disable zoom on wheel while creating cylinder
    this.viewer.scene.screenSpaceCameraController.zoomEventTypes = [
      Cesium.CameraEventType.RIGHT_DRAG,
      Cesium.CameraEventType.PINCH,
    ];
  }

  private finishCylinderCreation(): void {
    if (this.state.height === undefined) return;

    this.volumeAdded.push({
      position: this.state.groundPosition!,
      radius: this.state.radius,
      height: this.state.height,
    });

    // Clean up temporary entities
    if (this.state.maxCylinder) this.viewer.entities.remove(this.state.maxCylinder);
    if (this.state.groundPoint) this.viewer.entities.remove(this.state.groundPoint);
    if (this.state.floatingPoint) this.viewer.entities.remove(this.state.floatingPoint);
    if (this.state.floatingLabel) this.annotations.remove(this.state.floatingLabel);

    // Reset state
    this.state.radius = 50.0;
    this.state.groundPoint = undefined;
    this.state.floatingPoint = undefined;
    this.state.lineFromGroundToHeaven = undefined;

    // Re-enable zoom on wheel
    this.viewer.scene.screenSpaceCameraController.zoomEventTypes = [
      Cesium.CameraEventType.RIGHT_DRAG,
      Cesium.CameraEventType.WHEEL,
      Cesium.CameraEventType.PINCH,
    ];
  }

  private handleMouseMove(movement: any): void {
    if (!Cesium.defined(this.state.floatingPoint)) return;

    const feature = this.viewer.scene.pick(movement.endPosition);
    if (!Cesium.defined(feature) || feature.id !== this.state.maxCylinder) return;

    const cartesian = this.viewer.scene.pickPosition(movement.endPosition);
    if (!Cesium.defined(cartesian)) return;

    const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
    const groundCartographic = Cesium.Cartographic.fromCartesian(this.state.groundPosition!);
    this.state.height = 2 * (cartographic.height - groundCartographic.height);
    const heightText = `${this.state.height.toFixed(2)} m`;

    // Update label
    if (this.state.floatingLabel) this.annotations.remove(this.state.floatingLabel);
    this.state.floatingLabel = this.annotations.add({
      position: cartesian,
      text: heightText,
      showBackground: true,
      font: "14px monospace",
      horizontalOrigin: Cesium.HorizontalOrigin.LEFT,
      verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
      disableDepthTestDistance: Number.POSITIVE_INFINITY,
    });

    // Update cylinder - keep YELLOW during creation
    if (this.state.cylinder) this.viewer.entities.remove(this.state.cylinder);
    this.state.cylinder = this.viewer.entities.add({
      position: this.state.groundPosition,
      cylinder: {
        length: this.state.height,
        topRadius: this.state.radius,
        bottomRadius: this.state.radius,
        material: Cesium.Color.YELLOW.withAlpha(0.5),
        outline: true,
        outlineColor: Cesium.Color.BLACK,
      },
    });

    // Fix: Use ConstantPositionProperty instead of setValue
    if (this.state.floatingPoint && this.state.floatingPoint.position) {
      this.state.floatingPoint.position = new Cesium.ConstantPositionProperty(cartesian);
    }
  }

  private handleWheel(movement: any): void {
    if (!Cesium.defined(this.state.groundPoint)) return;

    this.state.radius += Math.sign(movement) * this.state.wheelAcceleration;

    // Update max cylinder
    if (this.state.maxCylinder) this.viewer.entities.remove(this.state.maxCylinder);
    this.state.maxCylinder = this.viewer.entities.add({
      position: this.state.groundPosition,
      cylinder: {
        length: 120.0,
        topRadius: this.state.radius + 1.0,
        bottomRadius: this.state.radius + 1.0,
        material: Cesium.Color.YELLOW.withAlpha(0.01),
      },
    });

    // Update main cylinder - keep YELLOW during creation
    if (this.state.cylinder) this.viewer.entities.remove(this.state.cylinder);
    this.state.cylinder = this.viewer.entities.add({
      position: this.state.groundPosition,
      cylinder: {
        length: this.state.height,
        topRadius: this.state.radius,
        bottomRadius: this.state.radius,
        material: Cesium.Color.YELLOW.withAlpha(0.5),
        outline: true,
        outlineColor: Cesium.Color.BLACK,
      },
    });
  }

  private handleRightClick(movement: any): void {
    if (!this.viewer.scene.pickPositionSupported) return;

    const feature = this.viewer.scene.pick(movement.position);
    if (!Cesium.defined(feature)) return;

    const cartesian = this.viewer.scene.pickPosition(movement.position);
    if (!Cesium.defined(cartesian)) return;

    const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
    const height = `${cartographic.height.toFixed(2)} m`;

    this.annotations.add({
      position: cartesian,
      text: height,
      showBackground: true,
      font: "14px monospace",
      horizontalOrigin: Cesium.HorizontalOrigin.LEFT,
      verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
      disableDepthTestDistance: Number.POSITIVE_INFINITY,
    });
  }

  private createPoint(worldPosition: Cesium.Cartesian3): Cesium.Entity {
    return this.viewer.entities.add({
      position: worldPosition,
      point: {
        color: Cesium.Color.RED,
        pixelSize: 10,
      },
    });
  }

  private updateCylinderColor(color: Cesium.Color): void {
    if (this.state.cylinder) {
      this.viewer.entities.remove(this.state.cylinder);
      this.state.cylinder = this.viewer.entities.add({
        position: this.state.groundPosition,
        cylinder: {
          length: this.state.height,
          topRadius: this.state.radius,
          bottomRadius: this.state.radius,
          material: color.withAlpha(0.5),
          outline: true,
          outlineColor: Cesium.Color.BLACK,
        },
      });
    }
  }

  private showErrorMessage(message: string): void {
    // Create a temporary error label
    const errorLabel = this.annotations.add({
      position: this.state.groundPosition!,
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

    // Remove error message after 5 seconds
    setTimeout(() => {
      this.annotations.remove(errorLabel);
    }, 5000);

    // Also show browser alert
    alert(`Error: ${message}`);
  }

  async submitVolumeRequest(startTime: string, endTime: string): Promise<void> {
    if (this.volumeAdded.length === 0) {
      throw new Error('No volume data available');
    }

    const volumeData = this.volumeAdded[this.volumeAdded.length - 1];
    const center = Cesium.Cartographic.fromCartesian(volumeData.position);

    const payload: VolumeRequestPayload = {
      volume: {
        outline_circle: {
          center: {
            lng: Cesium.Math.toDegrees(center.longitude),
            lat: Cesium.Math.toDegrees(center.latitude),
          },
          radius: {
            value: volumeData.radius,
            units: "M",
          },
        },
        altitude_lower: {
          value: center.height,
          reference: "W84",
          units: "M",
        },
        altitude_upper: {
          value: center.height + volumeData.height,
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
      const response = await this.apiService.submitFlightPlan(payload);

      // Check if the response indicates success
      if (response.status === 201 && response.message === "Operational intent created successfully") {
        // Success: Change cylinder to GREEN
        this.updateCylinderColor(Cesium.Color.GREEN);
        console.log("Volume request submitted successfully:", response);
      } else {
        // Unexpected response format
        this.updateCylinderColor(Cesium.Color.RED);
        this.showErrorMessage("Unexpected response format from server");
      }
    } catch (error: any) {
      // Error occurred
      this.updateCylinderColor(Cesium.Color.RED);

      if (error.response && error.response.status === 409) {
        // Conflict error - parse the specific error message
        const errorData = error.response.data;
        let errorMessage = "Flight plan conflicts with existing constraints or operational intents";

        if (errorData.detail && errorData.detail.message) {
          errorMessage = errorData.detail.message;
        }

        this.showErrorMessage(errorMessage);
        console.error("Conflict error:", errorData);
      } else {
        // Other errors
        const errorMessage = error.message || "Unknown error occurred";
        this.showErrorMessage(errorMessage);
        console.error("Error submitting volume request:", error);
      }

      throw error;
    }
  }

  getVolumeData(): VolumeData[] {
    return this.volumeAdded;
  }

  destroy(): void {
    this.handler.destroy();
  }
}
