const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        secure: false,
        logLevel: 'debug'
      }
    },
    historyApiFallback: {
      rewrites: [
        { from: /^\/admin/, to: '/index.html' },
        { from: /^\/login/, to: '/index.html' },
        { from: /^\/register/, to: '/index.html' },
        { from: /^\/profile/, to: '/index.html' },
        { from: /./, to: '/index.html' }
      ]
    }
  },
  publicPath: process.env.NODE_ENV === 'production' ? '/static/dist/' : '/',
  outputDir: '../static/dist',
  assetsDir: 'assets',
  lintOnSave: false,
  chainWebpack: config => {
    // Disable ESLint for production builds
    config.module.rules.delete('eslint')
  }
})
