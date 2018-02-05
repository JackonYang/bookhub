const webpack = require('webpack');
const path = require('path');

module.exports = {
  target: 'electron-renderer',
  entry: [
    './main.src.js',
  ],
  output: {
    path: __dirname,
    // publicPath: path.join(__dirname, 'src'),
    filename: 'main.js',
  },
  // https://github.com/electron/electron/issues/5107
  node: {
    __dirname: false,
    __filename: false
  },
  module: {
    rules: []
  },
};
