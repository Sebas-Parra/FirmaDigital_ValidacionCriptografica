const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    host: 'localhost',
    client: {
      webSocketURL: 'ws://localhost:8080/ws'
    }
  }
})
