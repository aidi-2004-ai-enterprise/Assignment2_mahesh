# Deployment Documentation - Penguin API 🐧

This document outlines the process for building, running, and deploying the Penguin API using Docker.


## 1. Docker Build and Run

### 1.1 Build Docker Image

To create the Docker image, run the following command from the project's root directory. The `-t` flag tags the image with a human-readable name.

```bash
docker build -t penguin-api .
````

### 1.2 Run Docker Container

To run the container locally and map the exposed port, use this command. It makes the API accessible on `http://localhost:8080`.

```bash
docker run -p 8080:8080 penguin-api
```

## 2\. Docker Image Inspection

### 2.1 Key Findings

A review of the final `penguin-api` image reveals the following details:

  * **Image ID:** `sha256:9b3ff03ed9c74fb1e79bd9bfce84c37a64f65cf4bc77de5f4006a7f90087f11a`
  * **Repo Tags:** `penguin-api:latest`
  * **OS / Architecture:** `linux / amd64`
  * **Size:** `~617 MB`
  * **Exposed Ports:** `8080/tcp`
  * **Layers:** 9 distinct layers were created, leveraging Docker's caching mechanism for efficient rebuilds.

The final size of the image is considered **reasonable** for a Python application with its dependencies.

-----

## 3\. Optimizations

### 3.1 `.dockerignore` Usage

The `.dockerignore` file plays a crucial role in optimizing the build process. It prevents unnecessary files and directories from being included in the Docker build context, which **reduces the image size** and **improves build times**.

The file's contents are:

```
__pycache__/
*.pyc
.env
.git
.gitignore
*.md
venv/
tests/
```

These exclusions ensure that only essential application code and configuration files are included in the final image.

### 3.2 Security and Performance Considerations

  * **Slim Base Image:** We used the `python:3.10-slim` base image to minimize the container's footprint and reduce the attack surface.
  * **Dependency Caching:** The `--no-cache-dir` flag was used during the `pip install` command to prevent temporary cache files from being stored in the final image layer.
  * **Sensitive Files:** Sensitive configuration files like `.env` are explicitly excluded using `.dockerignore`.
  * **Port Exposure:** Only the required port `8080` is exposed, aligning with security best practices and compatibility for cloud platforms like Google Cloud Run.

-----

## 4\. Manual Cloud Deployment ☁️

This section documents the manual process of deploying the container to Cloud Run using the GCP Console.

### 4.1 Build and Push to Artifact Registry

1.  **Build and Tag Image:**
    Build the Docker image for a specific platform compatible with Cloud Run.
    ```bash
    docker build --platform linux/amd64 -t penguin-api .
    ```
    Tag the image with your project details for pushing to Artifact Registry.
    ```bash
    docker tag penguin-api us-central1-docker.pkg.dev/assignment2-467919/penguin-repo/penguin-api:latest
    ```
2.  **Push Image:**
    Authenticate Docker with the Artifact Registry.
    ```bash
    gcloud auth configure-docker us-central1-docker.pkg.dev
    ```
    Push the tagged image to your repository.
    ```bash
    docker push us-central1-docker.pkg.dev/assignment2-467919/penguin-repo/penguin-api:latest
    ```

### 4.2 Deploy to Cloud Run via GCP Console

1.  Navigate to the **Cloud Run** service in the GCP Console.
2.  Click **"Create Service"**.
3.  Select the container image you just pushed from the **Artifact Registry** (`us-central1-docker.pkg.dev/assignment2-467919/penguin-repo/penguin-api:latest`).
4.  Configure the service settings:
      * **Authentication**: Select **"Allow unauthenticated invocations"** to make the API publicly accessible.
      * **Port**: The container port is hardcoded to **8080**.
      * **CPU/Memory**: Set conservative limits, such as **1 CPU** and **4 GB** memory, to manage costs.
5.  Click **"Create"** or **"Deploy"**. The deployment will take a few minutes.

### 4.3 Test Deployment

This is the URL for deployed model: https://penguin-api-408534553654.us-central1.run.app/docs

1.  Access the **`/docs`** endpoint to view the interactive API documentation.
2.  Use the documentation to send a sample request to the `/predict` endpoint and verify that you receive a correct prediction.

### 4.4 Troubleshooting

  * Check the **Logs** tab in the Cloud Run service details page for any deployment or runtime errors.
  * Review the **Cloud Run troubleshooting guide** for common issues related to container configuration, startup, or serving errors.

-----

## 5\. Deployment and Testing Report 🚀

All development and testing criteria have been successfully met.

### 5.1 Test Metrics

  * **Total Tests Passed**: 7 out of 7
  * **Code Coverage**: 63%
      * `main.py`: 86% coverage
      * `models.py`: 0% coverage (implicitly tested)
      * `utils.py`: 0% coverage

### 5.2 Functionality Verified

  * The API's **happy path** is fully tested, confirming that valid inputs result in a successful prediction.
  * **All specified error cases** are handled correctly, including requests with missing fields, invalid data types, and out-of-range values. The API returns the expected `422` validation error status code.
  * The model is successfully loaded and used for inference as confirmed by the passing `test_model.py` test.

### 5.3 Final Recommendation

To address the `PydanticDeprecatedSince20` warning, it is recommended to update the `features.dict()` method call in `main.py` to `features.model_dump()` to ensure long-term compatibility with newer versions of the library.

-----

## 6\. Summary

This document details the successful process of building a portable, production-ready Docker image for the Penguin API. The image was optimized for size and security, and the full deployment workflow to Google Cloud was documented for future use.
