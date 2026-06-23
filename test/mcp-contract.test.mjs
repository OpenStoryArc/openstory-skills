// Static contract test for the plugin's .mcp.json.
//
// Why this exists: the plugin once shipped
//   "OPENSTORY_API_URL": "${OPENSTORY_API_URL:-http://localhost:3002}"
// Claude Code passed that string verbatim (it does not always expand
// ${VAR:-default}), so open-story-mcp aimed every REST call at a bogus host and
// every skill silently returned zeros. No test caught it. This one would have.
//
// It validates the manifest against two rules that mirror reality:
//   1. No env value uses ${...} shell-style expansion (use a literal).
//   2. Every env key is one open-story-mcp actually reads.
// Pure JSON checks — no OpenStory boot, no binary, no dependencies.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

// Environment variables open-story-mcp actually consumes. Keep in sync with the
// binary: rs/mcp/src/bin/open-story-mcp.rs (OPENSTORY_API_URL / _API_TOKEN /
// _NATS_URL) and docs/mcp-architecture.md in the OpenStory repo. A key here that
// the binary ignores is a silent misconfiguration waiting to happen — exactly
// the bug class this test guards.
export const ALLOWED_ENV = new Set([
  'OPENSTORY_API_URL',
  'OPENSTORY_API_TOKEN',
  'OPENSTORY_NATS_URL',
]);

// Pure contract check: returns an array of human-readable errors ([] = valid).
export function validateMcpJson(manifest) {
  const servers = manifest?.mcpServers;
  if (!servers || typeof servers !== 'object' || Array.isArray(servers)) {
    return ['mcpServers must be a non-null object'];
  }

  const errors = [];
  const names = Object.keys(servers);
  if (names.length === 0) errors.push('mcpServers is empty');

  for (const [name, server] of Object.entries(servers)) {
    if (typeof server?.command !== 'string' || server.command.length === 0) {
      errors.push(`${name}: "command" must be a non-empty string`);
    }

    const env = server?.env;
    if (env == null) continue;
    if (typeof env !== 'object' || Array.isArray(env)) {
      errors.push(`${name}.env must be an object`);
      continue;
    }

    for (const [key, value] of Object.entries(env)) {
      if (!ALLOWED_ENV.has(key)) {
        errors.push(
          `${name}.env.${key} is not a variable open-story-mcp reads ` +
            `(allowed: ${[...ALLOWED_ENV].join(', ')})`,
        );
      }
      if (typeof value !== 'string') {
        errors.push(`${name}.env.${key} must be a string`);
      } else if (/\$\{.*\}/.test(value)) {
        errors.push(
          `${name}.env.${key} uses \${...} shell-style expansion ("${value}"). ` +
            `Claude Code may pass it verbatim — use a literal value.`,
        );
      }
    }
  }
  return errors;
}

test('the shipped .mcp.json satisfies the contract', () => {
  const manifest = JSON.parse(
    readFileSync(new URL('../.mcp.json', import.meta.url), 'utf8'),
  );
  assert.deepEqual(validateMcpJson(manifest), []);
});

test('rejects ${VAR:-default} shell expansion in env (the historical bug)', () => {
  const errors = validateMcpJson({
    mcpServers: {
      openstory: {
        command: 'open-story-mcp',
        env: { OPENSTORY_API_URL: '${OPENSTORY_API_URL:-http://localhost:3002}' },
      },
    },
  });
  assert.ok(
    errors.some((e) => e.includes('${')),
    `expected a \${...} error, got: ${JSON.stringify(errors)}`,
  );
});

test('rejects an env key open-story-mcp does not read', () => {
  const errors = validateMcpJson({
    mcpServers: {
      openstory: { command: 'open-story-mcp', env: { OPENSTORY_DATA_DIR: '/tmp/x' } },
    },
  });
  assert.ok(
    errors.some((e) => e.includes('OPENSTORY_DATA_DIR')),
    JSON.stringify(errors),
  );
});

test('rejects a server with no command', () => {
  const errors = validateMcpJson({ mcpServers: { openstory: { env: {} } } });
  assert.ok(errors.some((e) => e.includes('command')), JSON.stringify(errors));
});

test('accepts a literal remote URL + token (the documented remote config)', () => {
  const errors = validateMcpJson({
    mcpServers: {
      openstory: {
        command: 'open-story-mcp',
        env: {
          OPENSTORY_API_URL: 'https://openstory.example.com',
          OPENSTORY_API_TOKEN: 'tok',
        },
      },
    },
  });
  assert.deepEqual(errors, []);
});
