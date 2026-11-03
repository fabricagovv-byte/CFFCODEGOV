<?php
declare(strict_types=1);
require __DIR__ . '/../vendor/autoload.php';

header('Content-Type: application/json');
if (($_SERVER['REQUEST_URI'] ?? '') === '/api/health') {
    echo json_encode(App\Saude::status());
    return;
}
http_response_code(404);
echo json_encode(['erro' => 'não encontrado']);
