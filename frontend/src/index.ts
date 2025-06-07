import * as Cesium from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";
import "./css/main.css";

if (process.env.ION_KEY) {
  Cesium.Ion.defaultAccessToken = process.env.ION_KEY;
}

// Initialize the Cesium Viewer in the HTML element with the `cesiumContainer` ID.
const viewer = new Cesium.Viewer("cesiumContainer", {
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

viewer.cesiumWidget.creditContainer.remove();

const osmBuildingsTileset = await Cesium.createOsmBuildingsAsync();
viewer.scene.primitives.add(osmBuildingsTileset);

const scene = viewer.scene;

viewer.scene.screenSpaceCameraController.zoomEventTypes = [
  Cesium.CameraEventType.RIGHT_DRAG,
  Cesium.CameraEventType.WHEEL,
  Cesium.CameraEventType.PINCH,
];

function createPoint(worldPosition: any) {
  const point = viewer.entities.add({
    position: worldPosition,
    point: {
      color: Cesium.Color.RED,
      pixelSize: 10,
    },
  });
  return point;
}

viewer.cesiumWidget.screenSpaceEventHandler.removeInputAction(
  Cesium.ScreenSpaceEventType.LEFT_DOUBLE_CLICK,
);

const handler = new Cesium.ScreenSpaceEventHandler(viewer.canvas);

let groundPoint: any;
let groundPosition: Cesium.Cartesian3 | undefined = undefined;
let height: any;
let radius = 50.0;
let lineFromGroundToHeaven;
let floatingPoint: any;
let floatingLabel: any;
let cylinder: any;
let maxCylinder: any;
let wheelAcceleration = 1.0;

let volumeAdded: any[] = [];

handler.setInputAction(function(movement: any) {
  if (!Cesium.defined(groundPoint)) {
    const ray = viewer.camera.getPickRay(movement.position);
    const earthPosition = viewer.scene.globe.pick(ray, viewer.scene);

    if (!Cesium.defined(earthPosition)) {
      return;
    }

    groundPoint = createPoint(earthPosition);
    floatingPoint = createPoint(earthPosition);
    groundPosition = earthPosition;

    let earthCartographic = Cesium.Cartographic.fromCartesian(earthPosition);
    earthCartographic.height += 120.0;

    maxCylinder = viewer.entities.add({
      position: groundPosition,
      cylinder: {
        length: 120.0,
        topRadius: radius + 1.0,
        bottomRadius: radius + 1.0,
        material: Cesium.Color.YELLOW.withAlpha(0.01),
      },
    });

    height = 0;
    cylinder = viewer.entities.add({
      position: groundPosition,
      cylinder: {
        length: height,
        topRadius: radius,
        bottomRadius: radius,
        material: Cesium.Color.RED.withAlpha(0.5),
        outline: true,
        outlineColor: Cesium.Color.BLACK,
      },
    });

    viewer.scene.screenSpaceCameraController.zoomEventTypes = [
      Cesium.CameraEventType.RIGHT_DRAG,
      Cesium.CameraEventType.PINCH,
    ];
  } else {
    if (height === undefined) return;

    volumeAdded.push({
      position: groundPosition,
      radius: radius,
      height: height,
    });

    viewer.entities.remove(maxCylinder);
    viewer.entities.remove(groundPoint);
    viewer.entities.remove(floatingPoint);
    annotations.remove(floatingLabel);

    radius = 50.0;

    groundPoint = undefined;
    floatingPoint = undefined;
    lineFromGroundToHeaven = undefined;

    viewer.scene.screenSpaceCameraController.zoomEventTypes = [
      Cesium.CameraEventType.RIGHT_DRAG,
      Cesium.CameraEventType.WHEEL,
      Cesium.CameraEventType.PINCH,
    ];
  }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK);

handler.setInputAction(function(movement: any) {
  if (Cesium.defined(floatingPoint)) {
    const feature = scene.pick(movement.endPosition);
    if (!Cesium.defined(feature)) return;
    if (feature.id === undefined || feature.id !== maxCylinder) return;

    const cartesian = scene.pickPosition(movement.endPosition);
    if (!Cesium.defined(cartesian)) return;

    const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
    let groundCartographic = Cesium.Cartographic.fromCartesian(groundPosition);
    height = 2 * (cartographic.height - groundCartographic.height);
    const heightText = `${height.toFixed(2)} m`;

    annotations.remove(floatingLabel);

    floatingLabel = annotations.add({
      position: cartesian,
      text: heightText,
      showBackground: true,
      font: "14px monospace",
      horizontalOrigin: Cesium.HorizontalOrigin.LEFT,
      verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
      disableDepthTestDistance: Number.POSITIVE_INFINITY,
    });

    viewer.entities.remove(cylinder);
    cylinder = viewer.entities.add({
      position: groundPosition,
      cylinder: {
        length: height,
        topRadius: radius,
        bottomRadius: radius,
        material: Cesium.Color.RED.withAlpha(0.5),
        outline: true,
        outlineColor: Cesium.Color.BLACK,
      },
    });

    // viewer.entities.remove(floatingPoint);
    // floatingPoint = createPoint(
    floatingPoint.position.setValue(cartesian);
    // floatingLabel.text = heightText;
    // floatingLabel.position = cartesian;
  }
}, Cesium.ScreenSpaceEventType.MOUSE_MOVE);

handler.setInputAction(function(movement: any) {
  if (!Cesium.defined(groundPoint)) return;

  radius += Math.sign(movement) * wheelAcceleration;

  viewer.entities.remove(maxCylinder);
  maxCylinder = viewer.entities.add({
    position: groundPosition,
    cylinder: {
      length: 120.0,
      topRadius: radius + 1.0,
      bottomRadius: radius + 1.0,
      material: Cesium.Color.YELLOW.withAlpha(0.01),
    },
  });

  viewer.entities.remove(cylinder);
  cylinder = viewer.entities.add({
    position: groundPosition,
    cylinder: {
      length: height,
      topRadius: radius,
      bottomRadius: radius,
      material: Cesium.Color.RED.withAlpha(0.5),
      outline: true,
      outlineColor: Cesium.Color.BLACK,
    },
  });
}, Cesium.ScreenSpaceEventType.WHEEL);

if (!scene.pickPositionSupported) {
  window.alert("This browser does not support picking positions.");
}

const annotations = scene.primitives.add(new Cesium.LabelCollection());

handler.setInputAction(function(movement: any) {
  if (!scene.pickPositionSupported) return;

  const feature = scene.pick(movement.position);
  if (!Cesium.defined(feature)) return;

  const cartesian = scene.pickPosition(movement.position);
  if (!Cesium.defined(cartesian)) return;

  const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
  const height = `${cartographic.height.toFixed(2)} m`;

  annotations.add({
    position: cartesian,
    text: height,
    showBackground: true,
    font: "14px monospace",
    horizontalOrigin: Cesium.HorizontalOrigin.LEFT,
    verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
    disableDepthTestDistance: Number.POSITIVE_INFINITY,
  });
}, Cesium.ScreenSpaceEventType.RIGHT_CLICK);

viewer.camera.lookAt(
  Cesium.Cartesian3.fromDegrees(-45.873938, -23.212619, 200.0),
  new Cesium.Cartesian3(800.0, 800.0, 800.0),
);
viewer.camera.lookAtTransform(Cesium.Matrix4.IDENTITY);

const volumeRequestForm = document.getElementById(
  "volumeRequestForm",
) as HTMLFormElement;

if (volumeRequestForm) {
  volumeRequestForm.addEventListener("submit", function(event: Event) {
    event.preventDefault(); // Prevent default form submission

    const startTimeInput = document.getElementById(
      "startTime",
    ) as HTMLInputElement;
    const endTimeInput = document.getElementById("endTime") as HTMLInputElement;

    if (startTimeInput && endTimeInput) {
      const startTime = startTimeInput.value;
      const endTime = endTimeInput.value;

      // Validate that end time is after start time
      if (new Date(startTime) >= new Date(endTime)) {
        alert("End time must be after start time");
        return;
      }

      // Call function to handle the request
      handleVolumeRequest(startTime, endTime);
    }
  });
}

// Function to handle the volume request
function handleVolumeRequest(startTime: string, endTime: string) {
  console.log("Volume request:", { startTime, endTime });

  const submitButton = document.querySelector(
    '#volumeRequestForm button[type="submit"]',
  ) as HTMLButtonElement;

  if (submitButton) {
    submitButton.disabled = true;
    submitButton.textContent = "Requesting...";


    /*
     Request format
     {
      "volume": {
          "outline_circle": {
          "center": {
              "lng": -118.456,
              "lat": 34.123
          },
          "radius": {
              "value": 300.183,
              "units": "M"
          }
          },
          "altitude_lower": {
          "value": 100000,
          "reference": "W84",
          "units": "M"
          },
          "altitude_upper": {
          "value": 100000,
          "reference": "W84",
          "units": "M"
          }
      },
      "time_start": {
          "value": "2025-06-29T07:00:17Z",
          "format": "RFC3339"
      },
      "time_end": {
          "value": "2025-06-29T07:01:16Z",
          "format": "RFC3339"
      }
    }
    */
    if (volumeAdded.length === 0) {
      return;
    }

    const object: any = volumeAdded[volumeAdded.length - 1];
    console.log(object);

    let center = Cesium.Cartographic.fromCartesian(object.position);

    fetch("http://localhost:8000/uss/v1/flight_plan/", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        volume: {
          outline_circle: {
            center: {
              lng: center.longitude,
              lat: center.latitude,
            },
            radius: {
              value: object.radius,
              units: "M",
            },
          },
          altitude_lower: {
            value: center.height, // Adjust as needed
            reference: "W84",
            units: "M",
          },
          altitude_upper: {
            value: center.height + object.height, // Adjust as needed
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
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Server response:", data);
        // Handle success response
      })
      .catch((error) => {
        console.error("Error:", error);
        // Handle error
      });

    // Your request logic here

    // Re-enable button after request completes
    setTimeout(() => {
      submitButton.disabled = false;
      submitButton.textContent = "Request";
    }, 2000);
  }

  // For now, just show an alert
  alert(`Request submitted for period: ${startTime} to ${endTime}`);
}
