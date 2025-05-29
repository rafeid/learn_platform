import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueDevTools from 'vite-plugin-vue-devtools';
import viteSvgLoader from 'vite-svg-loader';

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    viteSvgLoader({
      svgo: {
        plugins: [
          { name: 'removeTitle' },
          { name: 'removeAttrs', params: { attrs: 'fill' } }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  assetsInclude: ['**/*.svg'],
  optimizeDeps: {
    include: ['@vue/runtime-core']
  }
});