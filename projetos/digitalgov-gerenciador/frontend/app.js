"use strict";
(function () {
  var token = null;
  var el = function (id) { return document.getElementById(id); };
  var rotulos = { orgaos: "Órgãos", contratos: "Contratos", projetos: "Projetos", profissionais: "Profissionais", tarefas_abertas: "Tarefas abertas" };

  function texto(valor) { return valor === null || valor === undefined || valor === "" ? "—" : String(valor); }
  function tabela(linhas, colunas) {
    if (!linhas || linhas.length === 0) return "<p>Nenhum registro.</p>";
    var cab = colunas.map(function (c) { return "<th>" + c[1] + "</th>"; }).join("");
    var corpo = linhas.map(function (l) {
      return "<tr>" + colunas.map(function (c) { return "<td>" + texto(l[c[0]]).replace(/[<>&]/g, "") + "</td>"; }).join("") + "</tr>";
    }).join("");
    return "<table><thead><tr>" + cab + "</tr></thead><tbody>" + corpo + "</tbody></table>";
  }
  function api(caminho, opcoes) {
    opcoes = opcoes || {};
    opcoes.headers = Object.assign({ "content-type": "application/json" }, token ? { authorization: "Bearer " + token } : {});
    return fetch(caminho, opcoes).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (corpo) {
        if (!r.ok) throw new Error(typeof corpo.detail === "string" ? corpo.detail : "Erro " + r.status);
        return corpo;
      });
    });
  }
  function mostrarPainel() {
    el("entrar").hidden = true; el("painel").hidden = false; el("sair").hidden = false;
    api("/api/painel").then(function (d) {
      el("indicadores").innerHTML = Object.keys(rotulos).map(function (k) {
        return "<div><dt>" + rotulos[k] + "</dt><dd>" + texto(d[k]) + "</dd></div>";
      }).join("");
      var contratos = (d.contratos_resumo || []).map(function (r) {
        return { numero: r.contrato.numero, objeto: r.contrato.objeto, unidade: r.unidade, contratado: r.contratado, executado: r.executado, aceito: r.aceito, saldo: r.saldo };
      });
      el("contratos").innerHTML = tabela(contratos, [["numero", "Número"], ["objeto", "Objeto"], ["unidade", "Unidade"], ["contratado", "Contratado"], ["executado", "Executado"], ["aceito", "Aceito"], ["saldo", "Saldo"]]);
      el("starts").innerHTML = tabela(d.ultimos_start, [["em", "Quando"], ["resultado", "Resultado"], ["projeto_id", "Projeto (id)"]]);
    }).catch(function (e) { el("erro").textContent = e.message; el("erro").hidden = false; });
  }
  el("form-entrar").addEventListener("submit", function (ev) {
    ev.preventDefault(); el("erro").hidden = true;
    api("/api/login", { method: "POST", body: JSON.stringify({ login: el("login").value, senha: el("senha").value }) })
      .then(function (r) { token = r.token; el("senha").value = ""; mostrarPainel(); })
      .catch(function (e) { el("erro").textContent = e.message; el("erro").hidden = false; });
  });
  el("sair").addEventListener("click", function () {
    api("/api/logout", { method: "POST" }).catch(function () {}).then(function () { token = null; location.reload(); });
  });
})();
