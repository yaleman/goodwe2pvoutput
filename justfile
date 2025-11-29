default:
    lint
build_lambda_container:
    docker buildx build \
        --load \
        -t ghcr.io/yaleman/goodwe2pvoutput:lambda \
        .

check: lint test

test:
    uv run pytest

lint:
    uv run ruff check goodwe2pvoutput tests
    uv run mypy --strict goodwe2pvoutput tests
