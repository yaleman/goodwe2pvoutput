default:
    lint
build_lambda_container:
    docker buildx build \
        --load \
        -t ghcr.io/yaleman/goodwe2pvoutput:lambda \
        .

lint:
    uv run ruff check goodwe2pvoutput tests
    uv run mypy --strict goodwe2pvoutput tests
    uv run pyright goodwe2pvoutput tests