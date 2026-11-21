// Teste de carga do encurtador com k6.
//
// Uso:  k6 run -e BASE_URL=http://<endereço> -e TIPO=smoke tests/carga/encurtador.js
//       (ou: make carga BASE_URL=http://<endereço> TIPO=load)
//
// TIPO:
//   smoke  - 1 usuário por 30 s: confere se o roteiro funciona
//   load   - carga esperada: 20 usuários por 3 minutos
//   stress - sobe até 150 usuários para encontrar o limite
import http from "k6/http";
import { check, sleep } from "k6";

const BASE = (__ENV.BASE_URL || "http://localhost:8000").replace(/\/$/, "");
const TIPO = __ENV.TIPO || "smoke";

const PERFIS = {
  smoke: { vus: 1, duration: "30s" },
  load: {
    stages: [
      { duration: "1m", target: 20 }, // sobe
      { duration: "3m", target: 20 }, // mantém
      { duration: "1m", target: 0 }, // desce
    ],
  },
  stress: {
    stages: [
      { duration: "1m", target: 20 },
      { duration: "2m", target: 50 },
      { duration: "2m", target: 100 },
      { duration: "2m", target: 150 },
      { duration: "1m", target: 0 },
    ],
  },
};

if (!PERFIS[TIPO]) {
  throw new Error(`TIPO inválido: ${TIPO} (use smoke, load ou stress)`);
}

export const options = {
  ...PERFIS[TIPO],
  // Critérios de aprovação. A latência medida aqui inclui a rede até a AWS
  // (~150 ms do Brasil à Virgínia), por isso o limite é maior que o do alerta
  // do servidor (500 ms, medido só dentro da aplicação).
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<1000"],
    checks: ["rate>0.99"],
  },
};

// O 404 de um código inexistente é a resposta certa, não uma falha.
http.setResponseCallback(http.expectedStatuses(201, 307, 404));

const JSON_HEADERS = { headers: { "Content-Type": "application/json" } };

function criarLink(sufixo, tags) {
  return http.post(
    `${BASE}/api/links`,
    JSON.stringify({ url: `https://example.com/carga/${sufixo}` }),
    { ...JSON_HEADERS, tags },
  );
}

// Roda uma vez antes do teste: cria os links que os usuários vão abrir.
export function setup() {
  const codigos = [];
  for (let i = 0; i < 50; i++) {
    const r = criarLink(`setup-${i}`, { tipo: "setup" });
    if (r.status === 201) codigos.push(r.json("code"));
  }
  if (codigos.length === 0) {
    throw new Error(`não foi possível criar links em ${BASE}`);
  }
  return { codigos };
}

// O que cada usuário virtual faz, repetidamente.
export default function (dados) {
  const sorteio = Math.random();

  if (sorteio < 0.8) {
    // 80%: abre um link curto (sem seguir o redirecionamento)
    const codigo = dados.codigos[Math.floor(Math.random() * dados.codigos.length)];
    const r = http.get(`${BASE}/${codigo}`, { redirects: 0, tags: { tipo: "redirecionar" } });
    check(r, { "redirecionamento 307": (res) => res.status === 307 });
  } else if (sorteio < 0.95) {
    // 15%: cria um link novo
    const r = criarLink(`vu-${__VU}-${__ITER}`, { tipo: "criar" });
    check(r, { "link criado 201": (res) => res.status === 201 });
  } else {
    // 5%: acessa um código que não existe
    const r = http.get(`${BASE}/naoexiste${Math.floor(Math.random() * 1e9)}`, {
      redirects: 0,
      tags: { tipo: "inexistente" },
    });
    check(r, { "inexistente 404": (res) => res.status === 404 });
  }

  // O usuário "pensa" entre 0,5 e 1,5 s antes da próxima ação.
  sleep(0.5 + Math.random());
}
