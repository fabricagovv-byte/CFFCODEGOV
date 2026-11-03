FROM golang:1.23-alpine AS build
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /app .
FROM gcr.io/distroless/static
COPY --from=build /app /app
USER nonroot
EXPOSE 8000
ENTRYPOINT ["/app"]
