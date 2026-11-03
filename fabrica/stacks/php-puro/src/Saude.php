<?php
declare(strict_types=1);

namespace App;

final class Saude
{
    /** @return array{status: string, sistema: string} */
    public static function status(): array
    {
        return ['status' => 'ok', 'sistema' => '{{NOME}}'];
    }
}
