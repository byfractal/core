#!/bin/bash

# HCentric Interface Backend Server Runner
# This script starts the backend API server with proper configuration

# Set environment variables if needed
export PYTHONPATH="$(pwd)/.."

# Change to the API directory
cd api

# Start the server
echo "Starting HCentric Interface API server..."
echo "API will be available at http://localhost:8080"
echo "Press Ctrl+C to stop the server"

# Run with uvicorn
uvicorn main_simple:app --host 0.0.0.0 --port 8080

# Add proper error handling
if [ $? -ne 0 ]; then
    echo "Server startup failed. Please check the logs above for errors."
    exit 1
fi 