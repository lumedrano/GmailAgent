# Use the official Node.js 23 image
FROM node:23.6.0

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN npm install

# Build the React app
RUN npm run build

# Serve the build using a static server
RUN npm install -g serve
CMD ["serve", "-s", "build", "-l", "3000"]
