<?php
declare(strict_types=1);

use App\Saude;
use PHPUnit\Framework\TestCase;

final class SaudeTest extends TestCase
{
    public function testStatusOk(): void
    {
        $this->assertSame('ok', Saude::status()['status']);
    }
}
