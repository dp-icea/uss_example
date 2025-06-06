// Your access token can be found at: https://ion.cesium.com/tokens.
// Replace `your_access_token` with your Cesium ion access token.

Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIyMTgxNzg3NC01ZmE2LTRhNTUtOWRlOS01ZGMyZWU4NTViMTEiLCJpZCI6MzA4MjgyLCJpYXQiOjE3NDg4MTI4ODJ9.2ynR2Qhw8_bCBZhXiSQR7m2vYhKBSc6HfvnyG5kl9yg';

// Initialize the Cesium Viewer in the HTML element with the `cesiumContainer` ID.
const viewer = new Cesium.Viewer('cesiumContainer', {
	terrain: Cesium.Terrain.fromWorldTerrain(),
	selectionIndicator: false,
	infoBox: false,
});    

viewer._cesiumWidget._creditContainer.style.display = "none";

viewer.cesiumWidget.screenSpaceEventHandler.removeInputAction(
  Cesium.ScreenSpaceEventType.LEFT_DOUBLE_CLICK,
);

function createPoint(worldPosition) {
  const point = viewer.entities.add({
    position: worldPosition,
    point: {
      color: Cesium.Color.RED,
      pixelSize: 5,
      heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
  });
  return point;
}

let drawingMode = "polygon";
function drawShape(positionData) {
  let shape;
  if (drawingMode === "line") {
    shape = viewer.entities.add({
      polyline: {
        positions: positionData,
        clampToGround: false,
        width: 3,
      },
    });
  } else if (drawingMode === "polygon") {
    shape = viewer.entities.add({
      polygon: {
        hierarchy: positionData,
        material: new Cesium.ColorMaterialProperty(
          Cesium.Color.WHITE.withAlpha(0.7),
        ),
      },
    });
  } else if (drawingMode === "rectangle") {
    shape = viewer.entities.add({
      rectangle: {
        coordinates: positionData,
        material: new Cesium.ColorMaterialProperty(
          Cesium.Color.WHITE.withAlpha(0.7),
        ),
      },
    });
  }
  return shape;
}

let activeShapePoints = [];
let activeShape;
let floatingPoint;

const handler = new Cesium.ScreenSpaceEventHandler(viewer.canvas);

handler.setInputAction(function (event) {
  // We use `viewer.scene.globe.pick here instead of `viewer.camera.pickEllipsoid` so that
  // we get the correct point when mousing over terrain.
  const ray = viewer.camera.getPickRay(event.position);
  const earthPosition = viewer.scene.globe.pick(ray, viewer.scene);
  // `earthPosition` will be undefined if our mouse is not over the globe.
  if (Cesium.defined(earthPosition)) {
    if (activeShapePoints.length === 0) {
      floatingPoint = createPoint(earthPosition);
      activeShapePoints.push(earthPosition);
      const dynamicPositions = new Cesium.CallbackProperty(function () {
        if (drawingMode === "polygon") {
          return new Cesium.PolygonHierarchy(activeShapePoints);
        }
        return activeShapePoints;
      }, false);
      activeShape = drawShape(dynamicPositions);
    }
    activeShapePoints.push(earthPosition);
    createPoint(earthPosition);
  }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK);

handler.setInputAction(function (event) {
  if (Cesium.defined(floatingPoint)) {
    const ray = viewer.camera.getPickRay(event.endPosition);
    const newPosition = viewer.scene.globe.pick(ray, viewer.scene);
    if (Cesium.defined(newPosition)) {
      floatingPoint.position.setValue(newPosition);
      activeShapePoints.pop();
      activeShapePoints.push(newPosition);
    }
  }
}, Cesium.ScreenSpaceEventType.MOUSE_MOVE);
// Redraw the shape so it's not dynamic and remove the dynamic shape.
function terminateShape() {
  activeShapePoints.pop();
  drawShape(activeShapePoints);
  viewer.entities.remove(floatingPoint);
  viewer.entities.remove(activeShape);
  floatingPoint = undefined;
  activeShape = undefined;
  activeShapePoints = [];
}

handler.setInputAction(function (event) {
  terminateShape();
}, Cesium.ScreenSpaceEventType.RIGHT_CLICK);

const options = [
  {
    text: "Draw Lines",
    onselect: function () {
      if (!Cesium.Entity.supportsPolylinesOnTerrain(viewer.scene)) {
        window.alert("This browser does not support polylines on terrain.");
      }

      terminateShape();
      drawingMode = "line";
    },
  },
  {
    text: "Draw Polygons",
    onselect: function () {
      terminateShape();
      drawingMode = "polygon";
    },
  },
];

viewer.camera.lookAt(
  Cesium.Cartesian3.fromDegrees(-45.873938, -23.212619, 200.0),
  new Cesium.Cartesian3(800.0, 800.0, 800.0),
);
viewer.camera.lookAtTransform(Cesium.Matrix4.IDENTITY);
