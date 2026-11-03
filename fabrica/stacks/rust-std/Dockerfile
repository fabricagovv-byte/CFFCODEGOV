FROM rust:1-slim AS build
WORKDIR /src
COPY . .
RUN cargo build --release
FROM debian:stable-slim
COPY --from=build /src/target/release/{{SLUG}} /app/servidor
USER nobody
EXPOSE 8000
CMD ["/app/servidor"]
