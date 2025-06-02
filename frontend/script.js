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

const handler = new Cesium.ScreenSpaceEventHandler(viewer.canvas);

handler.setInputAction(function (event) {
  // We use `viewer.scene.globe.pick here instead of `viewer.camera.pickEllipsoid` so that
  // we get the correct point when mousing over terrain.
  const ray = viewer.camera.getPickRay(event.position);
  const earthPosition = viewer.scene.globe.pick(ray, viewer.scene);
  // `earthPosition` will be undefined if our mouse is not over the globe.
  if (Cesium.defined(earthPosition)) {

    // Create a cilinder
    const cylinder = viewer.entities.add({
      position: earthPosition,
	cylinder: {
		    length: 400.0,
		    topRadius: 50.0,
		    bottomRadius: 50.0,
		    material: Cesium.Color.RED.withAlpha(0.5),
		    outline: true,
		    outlineColor: Cesium.Color.BLACK,
		},
	  });


  }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK);

// const greenCylinder = viewer.entities.add({
//   name: "Green cylinder with black outline",
//   position: Cesium.Cartesian3.fromDegrees(-45.873938, -23.212619, 200.0),
//   cylinder: {
//     length: 400.0,
//     topRadius: 50.0,
//     bottomRadius: 50.0,
//     material: Cesium.Color.GREEN.withAlpha(0.5),
//     outline: true,
//     outlineColor: Cesium.Color.BLACK,
//   },
// });

viewer.camera.lookAt(
  Cesium.Cartesian3.fromDegrees(-45.873938, -23.212619, 200.0),
  new Cesium.Cartesian3(800.0, 800.0, 800.0),
);
viewer.camera.lookAtTransform(Cesium.Matrix4.IDENTITY);
