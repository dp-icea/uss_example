import * as Cesium from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";
import "./css/main.css";

//Cesium.Ion.defaultAccessToken =
//  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIyMTgxNzg3NC01ZmE2LTRhNTUtOWRlOS01ZGMyZWU4NTViMTEiLCJpZCI6MzA4MjgyLCJpYXQiOjE3NDg4MTI4ODJ9.2ynR2Qhw8_bCBZhXiSQR7m2vYhKBSc6HfvnyG5kl9yg";
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
let groundPosition: any;
let height: any;
let radius = 50.0;
let lineFromGroundToHeaven;
let floatingPoint: any;
let floatingLabel: any;
let cylinder: any;
let maxCylinder: any;
let wheelAcceleration = 1.0;

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
    //floatingLabel = annotations.add({
    //  position: groundPosition,
    //  text: '0 m',
    //  showBackground: true,
    //  font: "14px monospace",
    //  horizontalOrigin: Cesium.HorizontalOrigin.LEFT,
    //  verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
    //  disableDepthTestDistance: Number.POSITIVE_INFINITY,
    //});

    let earthCartographic = Cesium.Cartographic.fromCartesian(earthPosition);
    earthCartographic.height += 120.0;
    const infinityPosition = Cesium.Cartographic.toCartesian(earthCartographic);

    //lineFromGroundToHeaven = viewer.entities.add({
    //  name: "lineFromGroundToHeaven",
    //  position: earthPosition,
    //  polyline: {
    //    positions: [earthPosition, infinityPosition],
    //    width: 200,
    //    // Almost invisible
    //    material: Cesium.Color.YELLOW.withAlpha(0.7),
    //    //material: Cesium.Color.YELLOW.withAlpha(0.01),
    //  },
    //});

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

// handler.setInputAction(function (event) {
//   // We use `viewer.scene.globe.pick here instead of `viewer.camera.pickEllipsoid` so that
//   // we get the correct point when mousing over terrain.
//   const ray = viewer.camera.getPickRay(event.position);
//   const earthPosition = viewer.scene.globe.pick(ray, viewer.scene);
//   // `earthPosition` will be undefined if our mouse is not over the globe.
//   if (Cesium.defined(earthPosition)) {
//
//     // Create a cilinder
//     const cylinder = viewer.entities.add({
//       position: earthPosition,
// 	cylinder: {
// 		    length: 400.0,
// 		    topRadius: 50.0,
// 		    bottomRadius: 50.0,
// 		    material: Cesium.Color.RED.withAlpha(0.5),
// 		    outline: true,
// 		    outlineColor: Cesium.Color.BLACK,
// 		},
// 	  });
//
//
//   }
// }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

if (!scene.pickPositionSupported) {
  window.alert("This browser does not support picking positions.");
}

const greenCylinder = viewer.entities.add({
  position: Cesium.Cartesian3.fromDegrees(-45.873938, -23.212619, 700.0),
  cylinder: {
    length: 200.0,
    topRadius: 50.0,
    bottomRadius: 50.0,
    material: Cesium.Color.GREEN.withAlpha(0.5),
    outline: true,
    outlineColor: Cesium.Color.BLACK,
  },
});

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
