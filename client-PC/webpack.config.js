const webpack = require('webpack');
const path = require('path');

module.exports = {
    entry: {
        app: ['webpack/hot/dev-server', './react_entry.js'],
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
    module: {
        loaders: [
            {
                test: /\.js$/,
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
