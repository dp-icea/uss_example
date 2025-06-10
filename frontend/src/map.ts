import * as Cesium from "cesium";
import { CylinderTool } from "./tools/cylinder-tool";
import { PolygonTool } from "./tools/polygon-tool";
import { USSService } from "./services/uss.service";

export class Map {
  private viewer: Cesium.Viewer;
  private cylinderTool: CylinderTool;
  private polygonTool: PolygonTool;
  private ussService: USSService;
  private activeTool: "cylinder" | "polygon" = "cylinder";

  constructor(container: string) {
    // Set Ion access token if available
    if (process.env.ION_KEY) {
      Cesium.Ion.defaultAccessToken = process.env.ION_KEY;
    }

    // Initialize the Cesium Viewer
    this.viewer = new Cesium.Viewer(container, {
      terrain: Cesium.Terrain.fromWorldTerrain(),
      selectionIndicator: false,
      infoBox: false,
      animation: false,
      timeline: false,
      homeButton: false,
      fullscreenButton: false,
      navigationHelpButton: false,
      vrButton: false,
    });

    // Remove credit container
    this.viewer.cesiumWidget.creditContainer.remove();

    // Initialize services and tools
    this.ussService = new USSService();
    this.cylinderTool = new CylinderTool(this.viewer, this.ussService);
    this.polygonTool = new PolygonTool(this.viewer, this.ussService);

    this.initializeMap();
    this.setupVolumeRequestForm();
    this.setupToolSelection();
  }

  private async initializeMap(): Promise<void> {
    // Add OSM buildings
    const osmBuildingsTileset = await Cesium.createOsmBuildingsAsync();
    this.viewer.scene.primitives.add(osmBuildingsTileset);

    // Configure camera controls
    this.viewer.scene.screenSpaceCameraController.zoomEventTypes = [
      Cesium.CameraEventType.RIGHT_DRAG,
      Cesium.CameraEventType.WHEEL,
      Cesium.CameraEventType.PINCH,
    ];

    // Set initial camera position
    this.viewer.camera.lookAt(
      Cesium.Cartesian3.fromDegrees(-45.873938, -23.212619, 200.0),
      new Cesium.Cartesian3(800.0, 800.0, 800.0),
    );
    this.viewer.camera.lookAtTransform(Cesium.Matrix4.IDENTITY);
  }

  private setupToolSelection(): void {
    const toolRadios = document.querySelectorAll('input[name="drawingTool"]');

    toolRadios.forEach((radio) => {
      radio.addEventListener("change", (event) => {
        const target = event.target as HTMLInputElement;
        if (target.checked) {
          this.switchTool(target.value as "cylinder" | "polygon");
        }
      });
    });

    // Initialize with cylinder tool active
    this.switchTool("cylinder");
  }

  private switchTool(tool: "cylinder" | "polygon"): void {
    // Deactivate current tool
    if (this.activeTool === "cylinder") {
      this.cylinderTool.deactivate?.();
    } else {
      this.polygonTool.deactivate();
    }

    // Activate new tool
    this.activeTool = tool;
    if (tool === "cylinder") {
      this.cylinderTool.activate?.();
    } else {
      this.polygonTool.activate();
    }
  }

  private setupVolumeRequestForm(): void {
    const volumeRequestForm = document.getElementById(
      "volumeRequestForm",
    ) as HTMLFormElement;

    if (volumeRequestForm) {
      volumeRequestForm.addEventListener("submit", async (event: Event) => {
        event.preventDefault();

        const startTimeInput = document.getElementById(
          "startTime",
        ) as HTMLInputElement;
        const endTimeInput = document.getElementById(
          "endTime",
        ) as HTMLInputElement;

        if (startTimeInput && endTimeInput) {
          const startTime = startTimeInput.value;
          const endTime = endTimeInput.value;

          // Validate that end time is after start time
          if (new Date(startTime) >= new Date(endTime)) {
            alert("End time must be after start time");
            return;
          }

          await this.handleVolumeRequest(startTime, endTime);
        }
      });
    }
  }

  private async handleVolumeRequest(
    startTime: string,
    endTime: string,
  ): Promise<void> {
    const submitButton = document.querySelector(
      '#volumeRequestForm button[type="submit"]',
    ) as HTMLButtonElement;

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = "Requesting...";

      try {
        if (this.activeTool === "cylinder") {
          await this.cylinderTool.submitVolumeRequest(startTime, endTime);
        } else {
          await this.polygonTool.submitVolumeRequest(startTime, endTime);
        }
        console.log("Volume request submitted successfully");
      } catch (error) {
        console.error("Error submitting volume request:", error);
      } finally {
        setTimeout(() => {
          submitButton.disabled = false;
          submitButton.textContent = "Request";
        }, 2000);
      }
    }
  }

  getViewer(): Cesium.Viewer {
    return this.viewer;
  }

  getCylinderTool(): CylinderTool {
    return this.cylinderTool;
  }

  getPolygonTool(): PolygonTool {
    return this.polygonTool;
  }

  destroy(): void {
    this.cylinderTool.destroy();
    this.polygonTool.destroy();
    this.viewer.destroy();
  }
}
