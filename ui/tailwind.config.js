/** @type {import('tailwindcss').Config} */
export default {
    darkMode: ["class"],
    content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  safelist: [
    {
      pattern: /bg-(red|green|blue|yellow|purple|orange|pink|cyan|teal|indigo)-(500|600|700)/,
    }
  ],
  theme: {
  	extend: {
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		},
      width: {
        '1/10': '10%',
        '1/8': '12.5%',
      },
  		colors: {}
  	}
  },
  plugins: [require("tailwindcss-animate")],
}

