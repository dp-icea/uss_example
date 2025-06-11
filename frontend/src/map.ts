import * as Cesium from "cesium";
import {
  CylinderVolumeRequestPayload,
  CylinderVolumeSchema,
} from "./models/volume";
import { CylinderTool } from "./tools/cylinder-tool";
import { PolygonTool } from "./tools/polygon-tool";
import { USSService } from "./services/uss.service";
import { PolygonVolumeSchema } from "./models/polygon";

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
    this.setupConflictQuery();
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

  private setupConflictQuery(): void {
    const queryButton = document.getElementById(
      "query-conflicts-btn",
    ) as HTMLButtonElement;

    console.log("Setting up conflict query button");

    if (queryButton) {
      console.log("Adding event listener");
      queryButton.addEventListener("click", async () => {
        console.log("Query button clicked");

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

          try {
            await this.queryConflicts(startTime, endTime);
          } catch (error) {
            console.error("Error querying conflicts:", error);
          }
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

  private async queryConflicts(
    startTime: string,
    endTime: string,
  ): Promise<void> {
    console.log("Querying conflicts from", startTime, "to", endTime);
    const queryButton = document.getElementById(
      "query-conflicts-btn",
    ) as HTMLButtonElement;

    if (queryButton) {
      queryButton.disabled = true;
      queryButton.textContent = "Querying...";

      try {
        const cameraPosition = this.viewer.camera.positionCartographic;

        // Sample terrain height at camera's longitude/latitude
        const positions = [
          new Cesium.Cartographic(
            cameraPosition.longitude,
            cameraPosition.latitude,
          ),
        ];

        const terrainProvider = this.viewer.terrainProvider;
        const updatedPositions = await Cesium.sampleTerrainMostDetailed(
          terrainProvider,
          positions,
        );

        // Get the actual ground height at this position
        const groundHeight = updatedPositions[0].height || 0;

        console.log(groundHeight);

        const payload: CylinderVolumeRequestPayload = {
          volume: {
            outline_circle: {
              center: {
                lng: cameraPosition.longitude,
                lat: cameraPosition.latitude,
              },
              radius: {
                value: 10000, // Example radius, adjust as needed
                units: "M",
              },
            },
            altitude_lower: {
              value: groundHeight,
              reference: "W84",
              units: "M",
            },
            altitude_upper: {
              value: groundHeight + 1000,
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

        const conflicts = await this.ussService.queryConflicts(payload);

        // Iterate over conflicts, when CylinderVolumeSchema is returned, ask to display it in the CYlinderTool

        conflicts.data.constraints.forEach((constraint) => {
          // How to verify the type CylinderVolumeSchema or PolygonVolumeSchema?
          if ("outline_circle" in constraint.volume) {
            this.cylinderTool.drawConflictRegion(
              constraint as CylinderVolumeSchema,
            );
          } else if ("outline_polygon" in constraint.volume) {
            this.polygonTool.drawConflictRegion(
              constraint as PolygonVolumeSchema,
            );
          }
        });

        conflicts.data.operational_intents.forEach((intent) => {
          // How to verify the type CylinderVolumeSchema or PolygonVolumeSchema?
          if ("outline_circle" in intent.volume) {
            this.cylinderTool.drawConflictRegion(
              intent as CylinderVolumeSchema,
            );
          } else if ("outline_polygon" in intent.volume) {
            this.polygonTool.drawConflictRegion(intent as PolygonVolumeSchema);
          }
        });
      } catch (error) {
        console.error("Error querying conflicts:", error);
      } finally {
        setTimeout(() => {
          queryButton.disabled = false;
          queryButton.textContent = "Query Conflicts";
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
