FROM composer:2 AS deps
WORKDIR /app
COPY composer.json .
RUN composer install --no-dev --no-interaction
FROM php:8.3-cli-alpine
WORKDIR /app
COPY --from=deps /app/vendor ./vendor
COPY src ./src
COPY public ./public
USER www-data
EXPOSE 8000
CMD ["php", "-S", "0.0.0.0:8000", "-t", "public"]
