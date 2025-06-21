"use strict";

const path = require("path");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const webpack = require("webpack");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const Dotenv = require("dotenv-webpack");

const cesiumSource = "node_modules/cesium/Build/Cesium";
const cesiumBaseUrl = "cesiumStatic";

module.exports = (env) => {
	return {
		entry: "./src/index.ts",
		devtool: "inline-source-map",
		module: {
			rules: [
				{
					test: /\.tsx?$/,
					use: "ts-loader",
					exclude: /node_modules/,
				},
				{
					test: /\.css$/,
					use: ["style-loader", "css-loader"],
				},
				{
					test: /\.(png|gif|jpg|jpeg|svg|xml|json)$/,
					type: "asset/inline",
				},
			],
		},
		resolve: {
			mainFiles: ["index", "Cesium"],
			extensions: [".tsx", ".ts", ".js"],
		},
		output: {
			filename: "bundle.js",
			path: path.resolve(__dirname, "dist"),
		},
		devServer: {
			static: {
				directory: path.join(__dirname, "dist"),
			},
			liveReload: true,
			port: 9000,
		},
		plugins: [
			new HtmlWebpackPlugin({
				template: "src/index.html",
			}),
			new CopyWebpackPlugin({
				patterns: [
					{
						from: path.join(cesiumSource, "Workers"),
						to: `${cesiumBaseUrl}/Workers`,
					},
					{
						from: path.join(cesiumSource, "ThirdParty"),
						to: `${cesiumBaseUrl}/ThirdParty`,
					},
					{
						from: path.join(cesiumSource, "Assets"),
						to: `${cesiumBaseUrl}/Assets`,
					},
					{
						from: path.join(cesiumSource, "Widgets"),
						to: `${cesiumBaseUrl}/Widgets`,
					},
				],
			}),
			new webpack.DefinePlugin({
				// Define relative base path in cesium for loading assets
				CESIUM_BASE_URL: JSON.stringify(cesiumBaseUrl),
				"process.env.ENVIRONMENT": JSON.stringify("development"),
			}),
			new Dotenv({
				path:
					env.ENV === "prod"
						? path.resolve(__dirname, ".env.prod")
						: path.resolve(__dirname, ".env.dev"),
				safe: true,
			}),
		],
		mode: "development",
		devtool: "eval",
	};
};
