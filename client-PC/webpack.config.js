const webpack = require('webpack');
const path = require('path');

module.exports = {
  entry: {
    app: ['webpack/hot/dev-server', './react_entry.jsx'],
  },
  output: {
    path: path.join(__dirname, 'public/built'),
    filename: 'bundle.js',
    publicPath: 'http://localhost:8080/built/'
  },
  devServer: {
    contentBase: path.join(__dirname, 'public'),
    publicPath: 'http://localhost:8080/built/'
  },
  resolve: {
    extensions: ['.js', '.jsx'],
    alias: {
      '@': path.join(__dirname, 'src'),
      '@p': path.join(__dirname, 'src', 'components'),
      '@n': path.join(__dirname, 'src', 'containers'),
    }
  },
  module: {
    loaders: [
      {
        test: /\.(js|jsx)$/,
        loader: 'eslint-loader',
        enforce: 'pre',
        exclude: /(node_modules)/,
        options: {
          extends: path.join(__dirname, '/.eslintrc.js'),
          configFile: '.eslintrc.js',
          // failOnWarning: true,
          // failOnError: true,
          cache: false,
        },
      },
      {
        test: /\.(js|jsx)$/,
        exclude: /(node_modules)/,
        use: {
          loader: 'babel-loader',
        }
      },
      {
        test: /\.css$/,
        oneOf: [{
          resourceQuery: /^\?raw$/,
          use: [
            require.resolve('style-loader'),
            require.resolve('css-loader')
          ]
        }, {
          use: [
            require.resolve('style-loader'),
            {
              loader: require.resolve('css-loader'),
              options: {
                importLoaders: 1,
                modules: true,
                localIdentName: '[name]__[local]___[hash:base64:5]'
              }
            },
          ]
        }]
        // loader: 'style-loader!css-loader?modules&localIdentName=[name]__[local]-[hash:base64:5]'
      },
      {
        test: /\.scss$/,
        loader: 'style-loader!css-loader?modules&localIdentName=[name]__[local]-[hash:base64:5]!sass-loader'
      },
      {
        test: /\.(png|jpe?g|gif|svg)(\?.*)?$/,
        loader: 'url-loader',
        options: {
          limit: 10000,
        }
      },
    ]
  },
  plugins: [
    new webpack.HotModuleReplacementPlugin()
  ]
}
