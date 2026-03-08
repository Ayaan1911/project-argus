export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: '#fafaf9', // warm light beige base
        surface: '#ffffff',
        text: {
          DEFAULT: '#0c0a09',
          muted: '#57534e',
          subtle: '#a8a29e',
        },
        accent: {
          DEFAULT: '#f59e0b', // orange
          light: '#fde68a',
        },
        brand: {
          DEFAULT: '#4f46e5', // indigo
          dark: '#3730a3',
        },
        border: '#e7e5e4',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
        display: ['Inter', 'ui-sans-serif', 'system-ui'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular'],
      },
      backgroundImage: {
        'grid-pattern': "radial-gradient(circle, #e7e5e4 1px, transparent 1px)",
        'glass-gradient': "linear-gradient(rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0))",
      },
    },
  },
  plugins: [],
}
