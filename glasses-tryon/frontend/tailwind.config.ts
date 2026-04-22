import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        brand: {
          50:  '#eef1fa',
          100: '#d3dcf4',
          200: '#a7b9e9',
          300: '#6e8ed8',
          400: '#3d65c4',
          500: '#1a3faf',
          600: '#15328c',
          700: '#102469',
          800: '#0b1847',
          900: '#060c28',
          950: '#030612',
        },
        gold: {
          50:  '#fdf8ee',
          100: '#f9ead0',
          200: '#f2d09b',
          300: '#e8ad4e',
          400: '#d4911f',
          500: '#b87416',
          600: '#8f5910',
          700: '#6b420b',
        },
        stone: {
          50: '#fafaf8',
        },
      },
      boxShadow: {
        card: '0 2px 8px 0 rgba(10,24,71,0.07), 0 1px 2px 0 rgba(10,24,71,0.04)',
        'card-hover': '0 8px 24px 0 rgba(10,24,71,0.12), 0 2px 6px 0 rgba(10,24,71,0.06)',
        'gold': '0 4px 16px 0 rgba(212,145,31,0.25)',
      },
    },
  },
  plugins: [],
} satisfies Config
