/**
 * LRP-108 — demo auth gate rules (node:test, no build step).
 * Mirrors resolveDemoAuthEnabled in realms.ts — keep in sync.
 */
import assert from 'node:assert/strict';
import { test } from 'node:test';

function resolveDemoAuthEnabled({ nodeEnv, envValue, enableDemoLogin }) {
  if (nodeEnv === 'production') return false;
  if (enableDemoLogin !== undefined && enableDemoLogin !== '') {
    if (enableDemoLogin === '0' || String(enableDemoLogin).toLowerCase() === 'false') {
      return false;
    }
  }
  const raw = envValue;
  if (raw === undefined || raw === '') return true;
  return raw !== '0' && String(raw).toLowerCase() !== 'false';
}

test('production always disables demo auth even when env is true', () => {
  assert.equal(resolveDemoAuthEnabled({ nodeEnv: 'production', envValue: 'true' }), false);
  assert.equal(resolveDemoAuthEnabled({ nodeEnv: 'production', envValue: undefined }), false);
});

test('development defaults to demo auth enabled', () => {
  assert.equal(resolveDemoAuthEnabled({ nodeEnv: 'development', envValue: undefined }), true);
  assert.equal(resolveDemoAuthEnabled({ nodeEnv: 'development', envValue: '' }), true);
});

test('development respects explicit disable', () => {
  assert.equal(resolveDemoAuthEnabled({ nodeEnv: 'development', envValue: 'false' }), false);
  assert.equal(resolveDemoAuthEnabled({ nodeEnv: 'development', envValue: '0' }), false);
});

test('development respects explicit enable', () => {
  assert.equal(resolveDemoAuthEnabled({ nodeEnv: 'development', envValue: 'true' }), true);
  assert.equal(resolveDemoAuthEnabled({ nodeEnv: 'development', envValue: '1' }), true);
});

test('ENABLE_DEMO_LOGIN global gate disables demo auth', () => {
  assert.equal(
    resolveDemoAuthEnabled({
      nodeEnv: 'development',
      envValue: 'true',
      enableDemoLogin: 'false',
    }),
    false,
  );
});
