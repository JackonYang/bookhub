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
				loader: 'style-loader!css-loader'
			},
			{
				test: /\.less$/,
				loader: 'style-loader!css-loader!less-loader'
			}
		]
	},
	plugins: [
		new webpack.HotModuleReplacementPlugin()
	]
}
