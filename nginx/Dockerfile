# Use an official Nginx image as a base image
FROM nginx:latest

# Copy Nginx configuration file
COPY ./default.conf /etc/nginx/conf.d/default.conf

# Remove default Nginx website
RUN rm -rf /usr/share/nginx/html/*

# Expose port
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
