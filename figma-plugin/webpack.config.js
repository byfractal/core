const path = require("path");
const CopyPlugin = require("copy-webpack-plugin");
const webpack = require("webpack");
const dotenv = require("dotenv");

// Charger les variables d'environnement
const env =
  dotenv.config({ path: path.resolve(__dirname, "../.env") }).parsed || {};

module.exports = (_, argv) => {
  const isProduction = argv.mode === "production";

  // Convertir les variables d'environnement au format attendu par DefinePlugin
  const envKeys = Object.keys(env).reduce((prev, next) => {
    // Préfixer les variables Vite pour qu'elles fonctionnent avec import.meta.env
    if (next.startsWith("VITE_")) {
      prev[`import.meta.env.${next}`] = JSON.stringify(env[next]);
      // Garder également le format process.env pour la compatibilité
      prev[`process.env.${next}`] = JSON.stringify(env[next]);
    } else {
      prev[`process.env.${next}`] = JSON.stringify(env[next]);
    }
    return prev;
  }, {});

  return {
    mode: isProduction ? "production" : "development",
    devtool: isProduction ? false : "inline-source-map",
    entry: {
      code: "./src/code.ts",
    },
    module: {
      rules: [
        {
          test: /\.tsx?$/,
          use: "ts-loader",
          exclude: /node_modules/,
        },
        {
          test: /\.css$/,
          use: ["style-loader", "css-loader", "postcss-loader"],
        },
        {
          test: /\.(png|jpg|gif|webp|svg)$/,
          loader: "url-loader",
          options: {
            limit: 8192,
          },
        },
      ],
    },
    resolve: {
      extensions: [".tsx", ".ts", ".js", ".jsx"],
      alias: {
        "@": path.resolve(__dirname, "src"),
      },
    },
    output: {
      filename: "[name].js",
      path: path.resolve(__dirname, "dist"),
    },
    plugins: [
      new webpack.DefinePlugin(envKeys),
      new CopyPlugin({
        patterns: [
          {
            from: "./src/ui/ProjectsPage.html",
            to: "./ui.html",
          },
          {
            from: "./manifest.json",
            to: "./",
          },
          {
            from: "./src/ui/ProjectsPage.html",
            to: "./ui/",
          },
          // Ajouter la copie des autres fichiers HTML
          {
            from: "./src/auth-callback.html",
            to: "./",
            noErrorOnMissing: true,
          },
        ],
      }),
    ],
  };
};
