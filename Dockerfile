FROM python:3.13

WORKDIR /p_choa

RUN pip install uv

COPY . .

RUN uv sync

CMD [".venv/bin/python", "-m", "service.telegram.bot"]
