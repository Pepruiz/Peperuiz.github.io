import { defineConfig } from 'vite';

export default defineConfig({
  base: './', // Relative paths for assets (GitHub Pages & production deploys)
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      input: {
        // Core Pages
        main: 'index.html',
        conocenos: 'conocenos.html',
        privacidad: 'privacidad.html',

        // Scalable Engineering Calculation Tools Hub
        herramienta_zapatas: 'herramienta-zapatas.html',
        herramienta_zapatas_combinadas: 'herramienta-zapatas-combinadas.html',
        // Add future tools here easily (e.g., herramienta_vigas: 'herramienta-vigas.html')

        // Project Portfolio Case Studies
        proyecto_rehabilitacion_entramado: 'proyecto-rehabilitacion-entramado.html',
        project_parking_alcobendas: 'project-parking-alcobendas.html',
        project_rio_perales: 'project-rio-perales.html',
        project_viviendas_alcala: 'project-viviendas-alcala.html',
        project_detail: 'project-detail.html'
      }
    }
  }
});
