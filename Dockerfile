# syntax=docker/dockerfile:experimental
FROM python:3.9-slim as cyclemap

# Set workdir:
WORKDIR /app

# Install requirements:
# Do this prior to the wheel install in order to cache the resulting layer:
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy and install the project's wheel
COPY dist/cyclemap-*-py3-none-any.whl /tmp
RUN pip install /tmp/cyclemap-*-py3-none-any.whl

# Set command:
EXPOSE 8000
CMD ["hypercorn", "--bind", "0.0.0.0:8000", "cyclemap.app:app"]
