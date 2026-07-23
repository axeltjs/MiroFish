<template>
  <div class="wrap">

    <h2>Penggunaan Saya</h2>

    <!-- Stats row -->
    <div v-if="loadingData" class="loading-state">Loading…</div>
    <template v-else>
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-label">Simulations this month</div>
          <div class="stat-value">{{ stats.count }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Tokens in</div>
          <div class="stat-value mono">{{ fmtNum(stats.tokensIn) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Tokens out</div>
          <div class="stat-value mono">{{ fmtNum(stats.tokensOut) }}</div>
        </div>
        <div class="stat-card highlight">
          <div class="stat-label">Est. cost (USD)</div>
          <div class="stat-value mono">${{ stats.cost.toFixed(4) }}</div>
        </div>
      </div>

      <!-- Period selector -->
      <div class="period-row">
        <span class="period-label">Period:</span>
        <select v-model="period" @change="loadData">
          <option value="month">This month</option>
          <option value="all">All time</option>
        </select>
      </div>

      <!-- Log table -->
      <div class="table-card">
        <div v-if="logs.length === 0" class="empty-state">
          No simulation logs yet. Logs appear here after you run a simulation.
        </div>
        <div v-else class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Simulation</th>
                <th>Phase</th>
                <th>Model</th>
                <th class="r">Tokens in</th>
                <th class="r">Tokens out</th>
                <th class="r">Est. cost</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in logs" :key="log.id">
                <td class="mono">{{ fmtDate(log.created_at) }}</td>
                <td class="mono dim">{{ log.simulation_id?.slice(0, 8) }}…</td>
                <td>{{ log.phase }}</td>
                <td class="mono dim">{{ log.model || '—' }}</td>
                <td class="r mono">{{ fmtNum(log.tokens_in) }}</td>
                <td class="r mono">{{ fmtNum(log.tokens_out) }}</td>
                <td class="r mono">${{ Number(log.estimated_cost_usd).toFixed(6) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { supabase } from '../lib/supabase.js'

const logs = ref([])
const loadingData = ref(true)
const period = ref('month')

const stats = computed(() => {
  const count = logs.value.length
  const tokensIn = logs.value.reduce((s, l) => s + (l.tokens_in || 0), 0)
  const tokensOut = logs.value.reduce((s, l) => s + (l.tokens_out || 0), 0)
  const cost = logs.value.reduce((s, l) => s + Number(l.estimated_cost_usd || 0), 0)
  return { count, tokensIn, tokensOut, cost }
})

async function loadData() {
  loadingData.value = true
  let query = supabase
    .from('simulation_logs')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(500)

  if (period.value === 'month') {
    const start = new Date()
    start.setDate(1)
    start.setHours(0, 0, 0, 0)
    query = query.gte('created_at', start.toISOString())
  }

  const { data, error } = await query
  if (!error) logs.value = data ?? []
  loadingData.value = false
}

function fmtNum(n) {
  if (!n) return '0'
  return n.toLocaleString()
}

function fmtDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(loadData)
</script>

<style scoped>
* { box-sizing: border-box; }

.wrap {
  max-width: 1080px;
  margin: 0 auto;
  padding: 32px 24px 80px;
  background: #fafafa;
  min-height: 100vh;
  font-family: 'Space Grotesk', -apple-system, 'Segoe UI', sans-serif;
  color: #36454f;
  -webkit-font-smoothing: antialiased;
}

/* Content */
h2 {
  font-size: 20px;
  font-weight: 700;
  color: #36454f;
  margin: 0 0 20px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 24px;
}

@media (max-width: 700px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
}

.stat-card {
  background: #fff;
  border: 1px solid #e3e3e0;
  border-radius: 10px;
  padding: 18px;
}

.stat-card.highlight { border-color: #E60012; }

.stat-label {
  font-size: 11px;
  font-family: 'JetBrains Mono', monospace;
  color: #708090;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #36454f;
}

.stat-value.mono { font-family: 'JetBrains Mono', monospace; font-size: 18px; }

.period-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.period-label {
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  color: #708090;
}

select {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: #36454f;
  background: #fff;
  border: 1px solid #e3e3e0;
  border-radius: 6px;
  padding: 5px 10px;
  cursor: pointer;
  outline: none;
}

.table-card {
  background: #fff;
  border: 1px solid #e3e3e0;
  border-radius: 10px;
  overflow: hidden;
}

.table-wrap { overflow-x: auto; }

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

thead { background: #fafafa; border-bottom: 1px solid #e3e3e0; }

th {
  padding: 11px 14px;
  font-size: 11px;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #708090;
  text-align: left;
  white-space: nowrap;
}

td {
  padding: 11px 14px;
  color: #36454f;
  border-bottom: 1px solid #f0f0ee;
  white-space: nowrap;
}

tr:last-child td { border-bottom: none; }
tr:hover td { background: #fafafa; }

.mono { font-family: 'JetBrains Mono', monospace; }
.dim { color: #708090; }
.r { text-align: right; }

.empty-state {
  padding: 40px;
  text-align: center;
  font-size: 13px;
  color: #a0a0a0;
  font-family: 'JetBrains Mono', monospace;
}

.loading-state {
  padding: 40px;
  text-align: center;
  font-size: 13px;
  color: #a0a0a0;
  font-family: 'JetBrains Mono', monospace;
}
</style>
