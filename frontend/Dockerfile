# Use the official Node.js image as the base
FROM node:20.18.1-alpine

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy package.json and yarn.lock for dependency installation
COPY package.json yarn.lock ./

# Install dependencies using yarn
RUN yarn install

# Copy the rest of the application code into the container
COPY . .

# Expose the port that the app runs on
EXPOSE 3000

# Command to run the React development server
CMD ["yarn", "start"]