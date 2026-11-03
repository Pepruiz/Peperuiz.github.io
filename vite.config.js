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

        // Spanish Project Portfolio Case Studies
        proyecto_rehabilitacion_entramado: 'proyecto-rehabilitacion-entramado.html',
        project_parking_alcobendas: 'project-parking-alcobendas.html',
        project_rio_perales: 'project-rio-perales.html',
        project_viviendas_alcala: 'project-viviendas-alcala.html',

        // English Core Pages
        en_main: 'en/index.html',
        en_about: 'en/about.html',
        en_privacy: 'en/privacy.html',

        // English Engineering Calculation Tools Hub
        en_isolated_footing: 'en/isolated-footing-tool.html',
        en_combined_footing: 'en/combined-footing-tool.html',

        // English Project Portfolio Case Studies
        en_project_timber: 'en/project-timber-retrofitting.html',
        en_project_parking: 'en/project-parking-alcobendas.html',
        en_project_rio_perales: 'en/project-rio-perales.html',
        en_project_viviendas_alcala: 'en/project-viviendas-alcala.html'
      }
    }
  }
});
