# Stage 1: Build React application
FROM node:20.12.2 AS build

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build the React application
RUN npm run build

# Stage 2: Serve React application using Nginx
FROM nginx:latest

# Remove default Nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy the built React files from the build stage to Nginx's HTML directory
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
