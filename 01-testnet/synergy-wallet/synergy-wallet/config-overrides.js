// config-overrides.js
const webpack = require("webpack");

module.exports = function override(config) {
  config.resolve.fallback = {
    ...config.resolve.fallback,
    buffer: require.resolve("buffer/"),
    stream: require.resolve("stream-browserify"),   // <--- Add this line
    assert: require.resolve("assert/"),
    // (other polyfills as needed)
  };
  config.plugins = (config.plugins || []).concat([
    new webpack.ProvidePlugin({
      Buffer: ['buffer', 'Buffer'],
      // process: 'process/browser', // Uncomment if you get process errors
    }),
  ]);
  return config;
};
