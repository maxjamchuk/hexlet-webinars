FROM python:3.12-slim
ARG DEMO_TOKEN
ENV DEMO_TOKEN=$DEMO_TOKEN
CMD ["python", "-c", "import os; print(os.environ.get('DEMO_TOKEN', 'missing'))"]
