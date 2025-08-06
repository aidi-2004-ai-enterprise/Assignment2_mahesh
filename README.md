# README.md - Penguin Classification API 🐧

This repository contains a FastAPI application for classifying penguin species based on their physical measurements. The application is containerized using Docker and designed for deployment on Google Cloud Run.

-----

## 1\. Project Overview

The Penguin Classification API provides a machine learning inference service that predicts the species of a penguin (Adelie, Chinstrap, or Gentoo) given specific biological measurements. It leverages a pre-trained model (`model.pkl`), a label encoder (`label_encoder.pkl`), and a list of expected features (`columns.pkl`).

**Key Technologies:**

  * **FastAPI:** For building the web API.
  * **Pydantic:** For data validation and serialization.
  * **Pandas & Joblib:** For data handling and model loading.
  * **Docker:** For containerization.
  * **Google Cloud Run:** For serverless deployment.

-----

## 2\. Setup Instructions

To get the project running locally, follow these steps:

### 2.1 Clone the Repository

```bash
git clone https://github.com/your-username/penguin_classification.git # Replace with your actual repo URL
cd penguin_classification
```

### 2.2 Create a Virtual Environment and Install Dependencies

It's recommended to use a virtual environment to manage dependencies.

```bash
python -m venv venv
.\venv\Scripts\activate # On Windows
source venv/bin/activate # On macOS/Linux
pip install -r requirements.txt
```

### 2.3 Local API Execution

Once dependencies are installed, you can run the FastAPI application locally:

```bash
uvicorn penguin_app.main:app --host 0.0.0.0 --port 8080 --reload
```

The API will be accessible at `http://localhost:8080`.

### 2.4 Running Tests

To run the unit and integration tests, including code coverage:

```bash
pytest --cov=penguin_app tests/
```

-----

## 3\. API Documentation

The API provides the following endpoints:

  * **Root Endpoint**:

      * **GET `/`**: Returns a welcome message.
      * **Response**: `{"message": "Penguin Predictor Active!"}`

  * **Health Check Endpoint**:

      * **GET `/health`**: Checks the service health.
      * **Response**: `{"status": "ok"}`

  * **Prediction Endpoint**:

      * **POST `/predict`**: Predicts the penguin species based on input features.
      * **Request Body (JSON)**:
        ```json
        {
          "bill_length_mm": 39.1,
          "bill_depth_mm": 18.7,
          "flipper_length_mm": 181.0,
          "body_mass_g": 3750.0,
          "sex": "male",
          "island": "Torgersen"
        }
        ```
      * **Response (JSON)**:
        ```json
        {"prediction": "Adelie"}
        ```
      * **Error Response (JSON)**: Returns `422 Unprocessable Entity` for invalid inputs (missing fields, wrong types, out-of-range values).

You can access the interactive API documentation (Swagger UI) at `http://localhost:8080/docs` when running locally, or at your Cloud Run service URL followed by `/docs`.

-----

## 4\. Answers to Key Questions

### 4.1 What edge cases might break your model in production that aren't in your training data?

While Pydantic validation handles basic data integrity (types, ranges, enums), the model itself might break or provide inaccurate predictions if it encounters:

  * **Out-of-distribution data**: Penguin measurements significantly outside the range seen in the training data (e.g., extremely large or small penguins, or combinations of features that don't exist in reality).
  * **Environmental shifts (data drift)**: If the characteristics of penguin populations change over time (e.g., due to climate change affecting their size or diet), the model's learned patterns might become outdated.
  * **New penguin species**: The model is trained on specific species. If a new, unrepresented species needs classification, the model will incorrectly force it into one of the known categories.
  * **Corrupted or malformed feature values**: Even if the type is correct, a `bill_length_mm` of `0.000001` or `1000.0` (if not explicitly constrained by `Field` or business logic) could lead to unexpected model behavior.

### 4.2 What happens if your model file becomes corrupted?

If the `model.pkl`, `label_encoder.pkl`, or `columns.pkl` files become corrupted (e.g., due to incomplete upload, disk error, or malicious tampering), the application will **fail to start**.

In `main.py`, the `joblib.load()` calls are wrapped in a `try-except FileNotFoundError` block. If the files are corrupted (but exist), `joblib.load()` would likely raise a different exception (e.g., `EOFError`, `UnpicklingError`, or a generic `Exception`). This would be caught, logged as an error, and then a `RuntimeError` would be raised, preventing the FastAPI application from initializing. This is a **fail-fast** approach, preventing the service from running with a broken model.

### 4.3 What's a realistic load for a penguin classification service?

For a specialized ML inference API like penguin classification, a "realistic load" is likely **low to moderate**. It's not a high-frequency trading system or a social media feed.

  * **Typical usage:** A few requests per minute or hour, perhaps from researchers, data scientists, or an internal application.
  * **Normal load:** 1-10 requests per second (RPS).
  * **Peak load (e.g., batch processing, new data ingestion):** Could temporarily spike to 50-100 RPS.

The load test results (up to 29.40 RPS in a spike scenario) indicate the current setup can handle typical and even moderate peak loads effectively, especially if cold starts are mitigated.

### 4.4 How would you optimize if response times are too slow?

If response times are consistently too slow, I would investigate the following:

1.  **Cold Starts (Primary Suspect)**:
      * **Cloud Run Configuration**: Enable "CPU is always allocated" and set a minimum number of instances (e.g., 1 or 2) to keep the service warm.
      * **Pre-loading**: Ensure the model and other necessary assets are loaded into memory *once* during application startup, not per request. (This is already implemented in `main.py`).
2.  **Resource Allocation**:
      * **CPU/Memory**: Increase CPU and memory limits in Cloud Run if monitoring shows instances are consistently hitting their limits.
      * **Concurrency**: Adjust Cloud Run's concurrency setting. If too high, it can lead to contention; if too low, it can lead to excessive cold starts.
3.  **Code Optimization**:
      * **Profiling**: Use Python profilers (e.g., `cProfile`) to identify slow sections of the prediction code.
      * **Preprocessing**: Optimize data preprocessing steps (e.g., one-hot encoding, reindexing) for efficiency.
      * **Model Optimization**: If the model itself is slow, consider:
          * Using a faster inference library (e.g., ONNX Runtime).
          * Quantization or pruning the model.
          * Switching to a simpler, faster model if accuracy trade-offs are acceptable.
4.  **Network Latency**: Ensure the client making requests is geographically close to the Cloud Run region.
5.  **Database/External Dependencies**: If the API relied on a database or other external services, I'd optimize those connections and queries.

### 4.5 What metrics matter most for ML inference APIs?

For an ML inference API, the most crucial metrics are:

1.  **Latency (Response Time)**:
      * **Average Latency**: Overall typical speed.
      * **P95/P99 Latency**: Critical for identifying outliers and cold start issues, ensuring a good experience for most users.
2.  **Throughput (Requests Per Second - RPS)**: How many predictions the API can handle per unit of time.
3.  **Error Rate**: Percentage of failed requests (e.g., 4xx, 5xx errors). Should ideally be 0% for valid inputs.
4.  **Model Accuracy/Performance (Offline)**: While not an API metric, the underlying model's accuracy, precision, recall, F1-score, etc., are paramount to the *business value* of the API.
5.  **Resource Utilization (CPU, Memory)**: Helps in optimizing Cloud Run costs and identifying bottlenecks.
6.  **Cold Start Rate/Duration**: Specific to serverless, measures how often and for how long new instances take to become ready.

### 4.6 Why is Docker layer caching important for build speed? (Did you leverage it?)

**Docker layer caching** is crucial for build speed because Docker builds images layer by layer. Each instruction in a `Dockerfile` (e.g., `FROM`, `COPY`, `RUN`) creates a new layer. If an instruction and its context (the files copied, the command run) haven't changed since the last build, Docker can reuse the cached layer from a previous build instead of re-executing that instruction. This significantly speeds up subsequent builds.

**Yes, it was leveraged.** In this project's `Dockerfile`:

  * `FROM python:3.10-slim`: The base image is pulled once and cached.
  * `COPY requirements.txt .` followed by `RUN pip install --no-cache-dir -r requirements.txt`: If `requirements.txt` doesn't change, the `pip install` step (which can be time-consuming) is cached.
  * Subsequent `COPY` commands for application code and data: If only the application code changes, the dependency installation layer remains cached.

This layering strategy ensures that only the modified parts of the image are rebuilt, saving considerable time during development iterations.

### 4.7 What security risks exist with running containers as root?

Running containers as the `root` user (which is the default in many Docker images, including `python:3.10-slim` unless specified otherwise) poses significant security risks:

1.  **Principle of Least Privilege Violation**: The container has more privileges than it needs, increasing the blast radius if compromised.
2.  **Container Escape**: If a vulnerability exists in the container runtime or the application, a malicious actor could potentially "escape" the container and gain root access to the underlying host system.
3.  **Host System Compromise**: With root privileges inside the container, an attacker could mount host directories, modify system files, or install malicious software on the host.
4.  **Supply Chain Attacks**: If a dependency or a base image contains malicious code, running as root exacerbates the potential damage.

**Mitigation**:

  * **Run as Non-Root User**: Specify a non-root user in the `Dockerfile` using the `USER` instruction.
  * **Read-Only Filesystems**: Mount parts of the container's filesystem as read-only where possible.
  * **Minimize Privileges**: Drop unnecessary Linux capabilities.

### 4.8 How does cloud auto-scaling affect your load test results?

Cloud auto-scaling (like Cloud Run's automatic scaling) significantly affects load test results by:

  * **Masking Cold Starts**: For tests with gradual ramp-up or sustained load, auto-scaling will spin up new instances. The average response time might look good, but the **P95/P99 latency** will likely show spikes due to the cold start time of newly provisioned instances. This was observed in your load test results.
  * **Preventing Overload Failures**: Instead of the service crashing or returning 5xx errors under high load, Cloud Run scales out, absorbing the traffic. This means you'll see a **0% failure rate** even at high RPS, as long as the scaling limits aren't hit and there are no application-level errors.
  * **Influencing Throughput**: Auto-scaling allows the service to achieve higher overall throughput by distributing requests across multiple instances. The maximum RPS observed in load tests directly reflects the platform's ability to scale.
  * **Cost Implications**: While not a direct result metric, auto-scaling means you pay for what you use. Load tests help understand the number of instances required for specific loads, informing cost estimates.

### 4.9 What would happen with 10x more traffic?

With 10x more traffic (e.g., 1000 concurrent users or 300 RPS sustained), several things would happen:

1.  **Increased Cold Starts**: More new instances would be spun up more frequently, leading to a higher frequency of cold start latency spikes, potentially impacting a larger percentage of users.
2.  **Resource Saturation**: Instances might hit their CPU or memory limits more often, leading to performance degradation (higher average latency, more timeouts) before new instances are fully ready.
3.  **Increased Cost**: Cloud Run would scale to significantly more instances, leading to a proportional increase in billing.
4.  **Potential Throttling/Errors**: If the scaling limits of Cloud Run are reached (e.g., maximum instances per region) or if the underlying model/database cannot keep up, you might start seeing `429 Too Many Requests` or `5xx` errors.
5.  **External Dependencies**: If the service relied on external APIs or databases, those dependencies might become the new bottleneck if they cannot handle the increased request volume.

### 4.10 How would you monitor performance in production?

In production, I would implement a robust monitoring strategy using Google Cloud's native tools:

1.  **Cloud Monitoring**:
      * **Custom Dashboards**: Create dashboards to visualize key metrics:
          * **Latency**: Average, P95, P99 for all endpoints, especially `/predict`.
          * **Throughput**: Requests per second (RPS).
          * **Error Rate**: Percentage of 4xx/5xx responses.
          * **Resource Utilization**: CPU, memory, and instance count for Cloud Run.
      * **Alerting**: Set up alerts for:
          * High latency (e.g., P99 \> 500ms).
          * Increased error rates.
          * Low throughput.
          * Resource saturation (CPU \> 80%).
          * Zero instances (if a minimum is configured).
2.  **Cloud Logging**:
      * **Structured Logging**: Ensure the application logs in a structured format (JSON) with relevant fields (request ID, user ID, input features, prediction, errors).
      * **Error Reporting**: Integrate with Cloud Error Reporting to automatically capture and group application errors (e.g., exceptions from `main.py`).
      * **Log-based Metrics**: Create custom metrics from logs to track specific application events (e.g., "model loading events").
3.  **Cloud Trace**: For deep dives into request flows and identifying latency sources across different components (e.g., network, application code, model inference time).
4.  **Cloud Run Revisions**: Monitor the performance of different revisions to identify regressions after deployments.

### 4.11 How would you implement blue-green deployment?

Blue-green deployment is a strategy to reduce downtime and risk by running two identical production environments, "Blue" and "Green."

**Implementation for Cloud Run:**

1.  **Current Version (Blue)**: Your currently deployed and serving Cloud Run service (e.g., `penguin-api` revision `v1`).
2.  **New Version (Green)**: Deploy the new version of your container image to Cloud Run as a *new revision* within the *same service*. Cloud Run allows you to manage traffic distribution to different revisions.
3.  **Traffic Shifting**:
      * Initially, 100% of traffic goes to the Blue revision.
      * Gradually shift a small percentage of traffic (e.g., 5-10%) to the Green revision.
      * Monitor key metrics (latency, errors) on the Green revision.
      * If stable, gradually increase traffic to Green (e.g., 25%, 50%, 75%, 100%).
4.  **Rollback**: If any issues are detected with the Green revision, immediately shift 100% of traffic back to the Blue revision.
5.  **Decommission**: Once the Green revision is stable and handling all traffic, the Blue revision can be decommissioned or kept as a quick rollback option.

**Benefits**: Near-zero downtime, easy rollback, reduced risk during deployments.

### 4.12 What would you do if deployment fails in production?

If a deployment fails in production, I would follow an incident response protocol:

1.  **Immediate Rollback**: The first priority is to restore service. If Cloud Run deployment fails, it typically won't switch traffic to the new revision. If it partially switched or if a previous deployment was problematic, I would immediately revert to the last known good revision via the Cloud Run console or `gcloud` CLI.
2.  **Gather Information**:
      * **Cloud Build Logs**: Check the build logs for the failed deployment to identify issues during image creation.
      * **Cloud Run Deployment Logs**: Review the deployment logs in the Cloud Run service history for specific errors during container startup or service initialization.
      * **Application Logs**: If the container started but failed later, check Cloud Logging for application-level errors (e.g., `FileNotFoundError` for models, dependency issues).
      * **Monitoring Metrics**: Check dashboards for sudden drops in throughput, spikes in latency, or error rates.
3.  **Diagnose**: Analyze the gathered logs and metrics to pinpoint the root cause (e.g., incorrect environment variable, missing file, code bug, resource exhaustion).
4.  **Remediate**: Fix the identified issue (e.g., correct `Dockerfile`, update code, adjust Cloud Run settings).
5.  **Re-deploy**: Deploy the corrected version, ideally to a staging environment first for verification, then to production.
6.  **Post-mortem**: Conduct a review to understand why the failure occurred and implement measures to prevent recurrence (e.g., better testing, pre-deployment checks, automated rollbacks).

### 4.13 What happens if your container uses too much memory?

If a Cloud Run container uses too much memory, it will lead to:

1.  **Out-Of-Memory (OOM) Errors**: Cloud Run will terminate the instance with an "Out of Memory" (OOMKilled) error. This will be visible in Cloud Logging and will result in failed requests.
2.  **Increased Latency**: Before an OOM error, the container might start swapping memory to disk (if available), leading to significantly slower response times.
3.  **Increased Cold Starts**: Terminated instances need to be replaced by new ones, leading to more cold starts and impacting overall service availability and latency.
4.  **Service Degradation**: If many instances are OOMKilled, the service might become unresponsive or experience a high error rate.
5.  **Higher Costs**: While OOMKilled instances don't incur full compute costs, the constant spinning up and down of instances due to memory issues can lead to inefficient resource utilization and potentially higher billing due to increased instance hours.

**Monitoring**: Keep a close eye on the memory utilization metric for your Cloud Run service in Cloud Monitoring. If it consistently approaches the allocated limit, it's a strong indicator to increase the memory limit.
