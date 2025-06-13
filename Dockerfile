FROM python:3.11-slim

WORKDIR /app

# Copy only the necessary files for installation
COPY pyproject.toml README.md ./
COPY gh_renovate_silencer ./gh_renovate_silencer/

# Install the package
RUN pip install --no-cache-dir .

# Set the entrypoint
ENTRYPOINT ["gh-renovate-silencer"]
CMD ["silence"]
