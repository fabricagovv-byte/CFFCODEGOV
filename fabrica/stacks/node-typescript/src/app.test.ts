import { test } from "node:test";
import assert from "node:assert/strict";
import type { AddressInfo } from "node:net";
import { criarServidor } from "./app.ts";

test("GET /api/health responde ok", async () => {
  const srv = criarServidor().listen(0);
  const { port } = srv.address() as AddressInfo;
  const r = await fetch(`http://127.0.0.1:${port}/api/health`);
  assert.equal(r.status, 200);
  assert.equal((await r.json()).status, "ok");
  srv.close();
});
