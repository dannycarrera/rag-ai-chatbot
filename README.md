# RAG AI Chatbot
A starting point for a RAG AI Chatbot that acts as a sales agent for any website by scraping its data. This project has a Flask backend and a React frontend.

## Run Locally
Make a copy of `.env.backend.template` and `.env.frontend.template` and modify them according to your configuration and place them as `.env`. in their respective folders.

# Run in Docker
Both the backend and frontend provide Dockerfiles to build docker images locally.
Use `docker build -t rag-chat-backend .` and `docker build -t rag-chat-frontend .` to build images.

Make a copy of `.env.backend.template` and `.env.frontend.template` and modify them according to your configuration and place them as `.env.backend` and `.env.frontend` next to the `docker-compose.yml` file.

The provided `docker-compose.yml` file runs a complete working example from the created docker images. Use {} and {} to pull from the published repos instead.