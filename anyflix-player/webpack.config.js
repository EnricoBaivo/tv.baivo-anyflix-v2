import path from 'path';
import { fileURLToPath } from 'url';
import HtmlWebpackPlugin from 'html-webpack-plugin';
import CopyWebpackPlugin from 'copy-webpack-plugin';
import webpack from 'webpack';
import TsconfigPathsPlugin from 'tsconfig-paths-webpack-plugin';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default {
  mode: 'development', // Changed from 'production' for better debugging
  entry: './src/main.tsx', // your entry point
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'js/lifecycle.js',
    publicPath: './', // Ensures relative URLs for assets
  },
  watch: false,
  watchOptions: {
    ignored: /node_modules/,
    poll: 500,
  },
  resolve: {
    // Use TsconfigPathsPlugin to automatically map tsconfig paths to webpack aliases
    plugins: [
      new TsconfigPathsPlugin({
        configFile: path.resolve(__dirname, 'tsconfig.json'),
      }),
    ],
    extensions: ['.js', '.jsx', '.ts', '.tsx'],
    // You can also add additional aliases not defined in tsconfig here:
    alias: {
      '/fonts': path.resolve(__dirname, 'public/fonts'),
      '@': path.resolve(__dirname, 'src'),
    },
  },
  module: {
    rules: [
      {
        // Transpile JS/TS/JSX/TSX files with Babel
        test: /\.(js|jsx|ts|tsx)$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'babel-loader',
            options: {
              presets: [
                '@babel/preset-env',
                '@babel/preset-react',
                '@babel/preset-typescript'
              ],
              plugins: [
                ['@babel/plugin-transform-runtime', {
                  regenerator: true
                }],
                "@babel/plugin-syntax-dynamic-import",
                "@babel/plugin-proposal-class-properties",
                "@babel/plugin-proposal-nullish-coalescing-operator",
                "@babel/plugin-proposal-object-rest-spread",
                "@babel/plugin-proposal-optional-chaining",
                "@babel/plugin-proposal-private-methods",
              ]
            }
          }
        ]
      },
      {
        // Process CSS files
        test: /\.css$/,
        use: ['style-loader', 'css-loader', 'postcss-loader'],
      },
      // Add additional loaders (images, fonts, etc.) as needed
    ],
  },
  plugins: [
    // Automatically provide React if it's used globally
    new webpack.ProvidePlugin({
      React: 'react',
    }),
    new HtmlWebpackPlugin({
      template: './index.html',
      minify: false, // Disable HTML minification for better debugging
    }),
    new CopyWebpackPlugin({
      patterns: [
        {
          from: path.resolve(__dirname, 'public'),
          to: '.', // Copy the public folder to the root of dist
          globOptions: {
            ignore: ['**/index.html'], // Ignore index.html if present
          },
        },
        {
          from: path.resolve(__dirname, 'appinfo.json'),
          to: '.', // Copy appinfo.json to the root of dist
        },
      ],
    }),
  ],

  devtool: 'eval-source-map', // Changed from false to enable detailed source maps
  target: ['web', 'es5'], // ensure compatibility with older engines

  optimization: {
    minimize: false, // Disable code minification for better debugging
    minimizer: [],
  },
};