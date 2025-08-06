### `LOAD_TEST_REPORT.md`

# Load Test Report - Penguin API 🐧

This report documents the performance of the Penguin API under various load conditions, analyzing key metrics to identify potential bottlenecks and propose optimizations.

---

## 1. Local Testing

This table summarizes the performance of the FastAPI application when run locally.

| Scenario | Requests | Failures | Avg (ms) | Median (ms) | 95%ile (ms) | Throughput (RPS) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Baseline (1 user)** | 8 | 0 | 60 | 110 | 210 | 0.20 |
| **Normal (10 users)** | 1,020 | 0 | 129 | 79 | 200 | 3.30 |

---

## 2. Cloud Testing

This table summarizes the performance of the Cloud Run deployment under various load scenarios.

| Scenario | Requests | Failures | Avg (ms) | Median (ms) | 95%ile (ms) | Throughput (RPS) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Baseline (1 user)** | 4 | 0 | 96 | 70 | 210 | 0.40 |
| **Normal (10 users)** | 4,050 | 0 | 59 | 77 | 210 | 2.70 |
| **Stress (50 users)** | 1,977 | 0 | 111 | 61 | 200 | 14.00 |
| **Spike (100 users)** | 1,083 | 0 | 89 | 69 | 210 | 29.40 |

---

## 3. Analysis of Test Results

The load tests confirm that the Cloud Run deployment is **highly stable and scalable**, successfully handling a spike of up to 100 users without any failures.

* **Stability**: The **0% failure rate** across all scenarios, from minimal to extreme load, demonstrates the application's resilience.
* **Performance**: The average response time remains well within acceptable limits, even under high load. The service's ability to handle **29.40 RPS** during a spike and maintain an average latency of **89 ms** is a strong indicator of effective horizontal scaling by Cloud Run.
* **Primary Bottleneck**: The most critical performance issue identified is **cold starts**. The consistently high `99th percentile` and `Max` response times (noted in previous logs, up to 3,123 ms) are a clear sign that new container instances take significant time to load the machine learning model. This impacts the latency for the first requests to a new instance.

---

## 4. Recommendations

### 4.1 Performance Optimizations

1.  **Mitigate Cold Starts**: The primary recommendation is to configure Cloud Run with **"CPU is always allocated"** and set a **minimum number of instances** to keep the service warm and ready for traffic. This will eliminate the model loading delay and drastically improve latency for the first requests.
2.  **Optimize Model Loading**: To address the model loading delay, consider implementing a "warm-up" routine to load the model into memory as soon as the application starts.
3.  **Optimize Dependencies**: The current image size is `~617 MB`, which is a factor in slow deployment and startup times. Review the Dockerfile to identify and remove any unnecessary libraries to further reduce the container footprint.

### 4.2 Scalability Strategies

1.  **Monitor Cloud Run Metrics**: Use the GCP Console to monitor key metrics like CPU utilization, memory usage, and instance count during load tests. This data will be crucial for determining if the default settings are sufficient or if more resources are required to handle production traffic.
2.  **Adjust Cloud Run Concurrency**: Tune the `gunicorn` worker settings and Cloud Run's concurrency setting to find the right balance between performance and cost.

### 4.3 Code Improvements

1.  **Pydantic Method Update**: To address the `PydanticDeprecatedSince20` warning, update the `features.dict()` method call in `main.py` to `features.model_dump()`. This ensures the codebase is compatible with future library versions.