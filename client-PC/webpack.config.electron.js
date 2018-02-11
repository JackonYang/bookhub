const webpack = require('webpack');
const path = require('path');

module.exports = {
  target: 'electron-renderer',
  entry: {
    main: './main/index.js',
    './public/background/bundle': './background/index.js',
  },
  output: {
    path: __dirname,
    // publicPath: path.join(__dirname, 'src'),
    filename: "[name].js"
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
