from app import app

if __name__ == "__main__":
    # Start the server on port 3001 as required by the preview environment
    app.run(host="0.0.0.0", port=3001)
