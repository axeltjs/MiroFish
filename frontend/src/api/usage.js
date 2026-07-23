import { supabase } from '../lib/supabase.js'
import { useAuth } from '../store/auth.js'

let _pricingCache = null

export async function getPricing() {
  if (_pricingCache) return _pricingCache
  const { data } = await supabase.from('settings').select('value').eq('key', 'token_pricing').single()
  _pricingCache = data?.value ?? {}
  return _pricingCache
}

export function invalidatePricingCache() {
  _pricingCache = null
}

export function calcCost(pricing, model, tokensIn, tokensOut) {
  const p = pricing[model] ?? pricing['default'] ?? { input_per_1m: 0, output_per_1m: 0 }
  const cost = (tokensIn / 1_000_000) * p.input_per_1m + (tokensOut / 1_000_000) * p.output_per_1m
  return +cost.toFixed(8)
}

/**
 * Log a simulation run to Supabase.
 * @param {Object} opts
 * @param {string} opts.simulationId
 * @param {string} [opts.projectId]
 * @param {string} [opts.phase]  e.g. 'ontology', 'graph', 'simulation', 'report'
 * @param {string} [opts.model]  LLM model name
 * @param {number} [opts.tokensIn]
 * @param {number} [opts.tokensOut]
 */
export async function logSimulation({ simulationId, projectId, phase, model, tokensIn = 0, tokensOut = 0 }) {
  const { user } = useAuth()
  if (!user.value) return

  const pricing = await getPricing()
  const cost = calcCost(pricing, model ?? 'default', tokensIn, tokensOut)

  const { error } = await supabase.from('simulation_logs').insert({
    user_id: user.value.id,
    simulation_id: simulationId,
    project_id: projectId ?? null,
    phase: phase ?? 'simulation',
    model: model ?? null,
    tokens_in: tokensIn,
    tokens_out: tokensOut,
    total_tokens: tokensIn + tokensOut,
    estimated_cost_usd: cost,
  })

  if (error) console.error('[usage] Failed to log simulation:', error.message)
}
