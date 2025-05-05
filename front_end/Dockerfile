# Use official Node.js image for Angular app
FROM node:16-alpine

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json /app/

# Install dependencies
RUN npm install

# Copy the Angular app code
COPY . /app

# Build the Angular project
# RUN npm run build --prod

# Expose the port that Angular app runs on
EXPOSE 80

# Serve the Angular app using Nginx
CMD ["ng", "serve", "-open", "dist"]
