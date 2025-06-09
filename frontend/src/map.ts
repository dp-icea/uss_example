import * as Cesium from "cesium";
import { CylinderTool } from "./tools/cylinder-tool";
import { VolumeApiService } from "./services/volume-api.service";

export class Map {
  private viewer: Cesium.Viewer;
  private cylinderTool: CylinderTool;
  private volumeApiService: VolumeApiService;

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
    this.volumeApiService = new VolumeApiService();
    this.cylinderTool = new CylinderTool(this.viewer, this.volumeApiService);

    this.initializeMap();
    this.setupVolumeRequestForm();
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
      new Cesium.Cartesian3(800.0, 800.0, 800.0)
    );
    this.viewer.camera.lookAtTransform(Cesium.Matrix4.IDENTITY);
  }

  private setupVolumeRequestForm(): void {
    const volumeRequestForm = document.getElementById("volumeRequestForm") as HTMLFormElement;

    if (volumeRequestForm) {
      volumeRequestForm.addEventListener("submit", async (event: Event) => {
        event.preventDefault();

        const startTimeInput = document.getElementById("startTime") as HTMLInputElement;
        const endTimeInput = document.getElementById("endTime") as HTMLInputElement;

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

  private async handleVolumeRequest(startTime: string, endTime: string): Promise<void> {
    const submitButton = document.querySelector('#volumeRequestForm button[type="submit"]') as HTMLButtonElement;

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = "Requesting...";

      try {
        await this.cylinderTool.submitVolumeRequest(startTime, endTime);
        console.log("Volume request submitted successfully");
        alert(`Request submitted for period: ${startTime} to ${endTime}`);
      } catch (error) {
        console.error("Error submitting volume request:", error);
        alert("Error submitting request. Please try again.");
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

  destroy(): void {
    this.cylinderTool.destroy();
    this.viewer.destroy();
  }
}
