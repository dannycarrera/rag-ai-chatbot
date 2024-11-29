# Stage 1: Build
FROM node:20.18.1-alpine AS builder

# Set the working directory
WORKDIR /usr/src/app

# Copy package.json and yarn.lock for dependency installation
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install

# Copy the application code into the container
COPY . .

# Build the app for production
RUN yarn build

# Stage 2: Serve
FROM nginx:stable-alpine

# Copy the production build from the builder stage to the Nginx web directory
COPY --from=builder /usr/src/app/build /usr/share/nginx/html

# Expose the port Nginx serves on
EXPOSE 80

# Command to start Nginx
CMD ["nginx", "-g", "daemon off;"]
