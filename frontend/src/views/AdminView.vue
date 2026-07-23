<template>
  <div class="wrap">

    <!-- Tabs -->
    <div class="tabs">
      <button
        v-for="t in tabs"
        :key="t.key"
        class="tab"
        :class="{ active: activeTab === t.key }"
        @click="activeTab = t.key"
      >
        <i :class="['ti', t.icon]"></i> {{ t.label }}
      </button>
    </div>

    <!-- ===================== TAB: OVERVIEW ===================== -->
    <div v-if="activeTab === 'overview'">
      <div class="section-head">
        <h2>Usage overview</h2>
        <select v-model="overviewPeriod" @change="loadOverview">
          <option value="month">This month</option>
          <option value="all">All time</option>
        </select>
      </div>

      <div v-if="loadingOverview" class="loading-state">Loading…</div>
      <template v-else>
        <!-- Summary -->
        <div class="stats-row">
          <div class="stat-card">
            <div class="stat-label">Total simulations</div>
            <div class="stat-value">{{ overviewStats.count }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Tokens in</div>
            <div class="stat-value mono">{{ fmtNum(overviewStats.tokensIn) }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Tokens out</div>
            <div class="stat-value mono">{{ fmtNum(overviewStats.tokensOut) }}</div>
          </div>
          <div class="stat-card highlight">
            <div class="stat-label">Total cost (USD)</div>
            <div class="stat-value mono">${{ overviewStats.cost.toFixed(4) }}</div>
          </div>
        </div>

        <!-- Per-user breakdown -->
        <div class="table-card">
          <div class="table-header">Per-user breakdown</div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>User</th>
                  <th class="r">Simulations</th>
                  <th class="r">Tokens in</th>
                  <th class="r">Tokens out</th>
                  <th class="r">Est. cost</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in userBreakdown" :key="row.email">
                  <td class="mono">{{ row.email }}</td>
                  <td class="r">{{ row.count }}</td>
                  <td class="r mono">{{ fmtNum(row.tokensIn) }}</td>
                  <td class="r mono">{{ fmtNum(row.tokensOut) }}</td>
                  <td class="r mono">${{ row.cost.toFixed(4) }}</td>
                </tr>
                <tr v-if="userBreakdown.length === 0">
                  <td colspan="5" class="empty-cell">No logs yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </div>

    <!-- ===================== TAB: USERS ===================== -->
    <div v-if="activeTab === 'users'">
      <div class="section-head">
        <h2>Users</h2>
        <button class="btn-action" @click="showInviteModal = true">
          <i class="ti ti-user-plus"></i> Invite user
        </button>
      </div>

      <div v-if="loadingUsers" class="loading-state">Loading…</div>
      <div v-else class="table-card">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Joined</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in profiles" :key="u.id">
                <td class="mono">{{ u.email }}</td>
                <td>
                  <span class="badge" :class="u.role === 'admin' ? 'badge-admin' : 'badge-user'">
                    {{ u.role }}
                  </span>
                </td>
                <td>
                  <span class="badge" :class="u.is_active ? 'badge-active' : 'badge-inactive'">
                    {{ u.is_active ? 'active' : 'inactive' }}
                  </span>
                </td>
                <td class="mono dim">{{ fmtDate(u.created_at) }}</td>
                <td>
                  <div class="actions-row">
                    <button
                      v-if="u.role !== 'admin'"
                      class="btn-sm"
                      @click="changeRole(u, 'admin')"
                      title="Promote to admin"
                    >Make admin</button>
                    <button
                      v-if="u.role === 'admin' && u.id !== currentUserId"
                      class="btn-sm danger"
                      @click="changeRole(u, 'user')"
                      title="Demote to user"
                    >Remove admin</button>
                  </div>
                </td>
              </tr>
              <tr v-if="profiles.length === 0">
                <td colspan="5" class="empty-cell">No users found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ===================== TAB: PRICING ===================== -->
    <div v-if="activeTab === 'pricing'">
      <div class="section-head">
        <h2>Token pricing</h2>
        <button class="btn-action" @click="addModelRow">
          <i class="ti ti-plus"></i> Add model
        </button>
      </div>
      <p class="section-hint">Prices in USD per 1 million tokens. The "default" row is used for unknown models.</p>

      <div v-if="loadingPricing" class="loading-state">Loading…</div>
      <div v-else class="table-card">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Model</th>
                <th class="r">Input ($/1M)</th>
                <th class="r">Output ($/1M)</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in pricingRows" :key="idx">
                <td>
                  <input
                    v-model="row.model"
                    class="inline-input"
                    placeholder="model-name"
                    :disabled="row.model === 'default' && idx === 0"
                  />
                </td>
                <td class="r">
                  <input v-model.number="row.input_per_1m" class="inline-input num" type="number" min="0" step="0.01" />
                </td>
                <td class="r">
                  <input v-model.number="row.output_per_1m" class="inline-input num" type="number" min="0" step="0.01" />
                </td>
                <td>
                  <button class="btn-sm danger" @click="removeModelRow(idx)" :disabled="row.model === 'default' && idx === 0">
                    <i class="ti ti-trash"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="table-footer">
          <span v-if="pricingMsg" class="msg" :class="pricingMsgType">{{ pricingMsg }}</span>
          <button class="btn-action" @click="savePricing" :disabled="savingPricing">
            <span v-if="!savingPricing"><i class="ti ti-device-floppy"></i> Save pricing</span>
            <span v-else>Saving…</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Invite modal -->
    <div v-if="showInviteModal" class="modal-overlay" @click.self="showInviteModal = false">
      <div class="modal">
        <div class="modal-head">
          <span>Invite user</span>
          <button class="modal-close" @click="showInviteModal = false"><i class="ti ti-x"></i></button>
        </div>
        <div class="modal-body">
          <label class="field-label">Email address</label>
          <input v-model="inviteEmail" type="email" placeholder="user@mmksi.com" @keyup.enter="sendInvite" />
          <div v-if="inviteMsg" class="msg" :class="inviteMsgType" style="margin-top:10px;">{{ inviteMsg }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showInviteModal = false">Cancel</button>
          <button class="btn-action" @click="sendInvite" :disabled="inviteSending || !inviteEmail.trim()">
            <span v-if="!inviteSending"><i class="ti ti-send"></i> Send invitation</span>
            <span v-else>Sending…</span>
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { supabase } from '../lib/supabase.js'
import { useAuth } from '../store/auth.js'
import { invalidatePricingCache } from '../api/usage.js'
import service from '../api/index.js'

const router = useRouter()
const { user } = useAuth()
const currentUserId = computed(() => user.value?.id)

const tabs = [
  { key: 'overview', label: 'Usage overview', icon: 'ti-chart-bar' },
  { key: 'users', label: 'Users', icon: 'ti-users' },
  { key: 'pricing', label: 'Pricing', icon: 'ti-currency-dollar' },
]
const activeTab = ref('overview')

// ── Overview ────────────────────────────────────────────────────
const overviewLogs = ref([])
const loadingOverview = ref(false)
const overviewPeriod = ref('month')

const overviewStats = computed(() => ({
  count: overviewLogs.value.length,
  tokensIn: overviewLogs.value.reduce((s, l) => s + (l.tokens_in || 0), 0),
  tokensOut: overviewLogs.value.reduce((s, l) => s + (l.tokens_out || 0), 0),
  cost: overviewLogs.value.reduce((s, l) => s + Number(l.estimated_cost_usd || 0), 0),
}))

const userBreakdown = computed(() => {
  const map = {}
  for (const log of overviewLogs.value) {
    const email = log.profiles?.email ?? log.user_id ?? 'unknown'
    if (!map[email]) map[email] = { email, count: 0, tokensIn: 0, tokensOut: 0, cost: 0 }
    map[email].count++
    map[email].tokensIn += log.tokens_in || 0
    map[email].tokensOut += log.tokens_out || 0
    map[email].cost += Number(log.estimated_cost_usd || 0)
  }
  return Object.values(map).sort((a, b) => b.cost - a.cost)
})

async function loadOverview() {
  loadingOverview.value = true
  let query = supabase
    .from('simulation_logs')
    .select('*, profiles(email)')
    .order('created_at', { ascending: false })
    .limit(5000)

  if (overviewPeriod.value === 'month') {
    const start = new Date()
    start.setDate(1)
    start.setHours(0, 0, 0, 0)
    query = query.gte('created_at', start.toISOString())
  }

  const { data, error } = await query
  if (!error) overviewLogs.value = data ?? []
  loadingOverview.value = false
}

// ── Users ────────────────────────────────────────────────────────
const profiles = ref([])
const loadingUsers = ref(false)
const showInviteModal = ref(false)
const inviteEmail = ref('')
const inviteMsg = ref('')
const inviteMsgType = ref('success')
const inviteSending = ref(false)

async function loadProfiles() {
  loadingUsers.value = true
  const { data } = await supabase.from('profiles').select('*').order('created_at')
  profiles.value = data ?? []
  loadingUsers.value = false
}

async function sendInvite() {
  if (!inviteEmail.value.trim() || inviteSending.value) return
  inviteSending.value = true
  inviteMsg.value = ''
  try {
    const token = (await supabase.auth.getSession()).data.session?.access_token
    await service.post('/admin/invite-user', { email: inviteEmail.value.trim() }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    inviteMsg.value = `Invitation sent to ${inviteEmail.value.trim()}`
    inviteMsgType.value = 'success'
    inviteEmail.value = ''
    await loadProfiles()
  } catch (err) {
    inviteMsg.value = err.response?.data?.error || err.message || 'Failed to send invitation'
    inviteMsgType.value = 'error'
  } finally {
    inviteSending.value = false
  }
}

async function changeRole(u, newRole) {
  const token = (await supabase.auth.getSession()).data.session?.access_token
  try {
    await service.post('/admin/update-role', { user_id: u.id, role: newRole }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    await loadProfiles()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to update role')
  }
}

// ── Pricing ────────────────────────────────────────────────────────
const pricingRows = ref([])
const loadingPricing = ref(false)
const savingPricing = ref(false)
const pricingMsg = ref('')
const pricingMsgType = ref('success')

async function loadPricing() {
  loadingPricing.value = true
  const { data } = await supabase.from('settings').select('value').eq('key', 'token_pricing').single()
  const obj = data?.value ?? {}
  pricingRows.value = Object.entries(obj).map(([model, prices]) => ({
    model,
    input_per_1m: prices.input_per_1m ?? 0,
    output_per_1m: prices.output_per_1m ?? 0,
  }))
  // Ensure 'default' row is first
  const defIdx = pricingRows.value.findIndex(r => r.model === 'default')
  if (defIdx > 0) {
    const [def] = pricingRows.value.splice(defIdx, 1)
    pricingRows.value.unshift(def)
  }
  loadingPricing.value = false
}

function addModelRow() {
  pricingRows.value.push({ model: '', input_per_1m: 0, output_per_1m: 0 })
}

function removeModelRow(idx) {
  pricingRows.value.splice(idx, 1)
}

async function savePricing() {
  savingPricing.value = true
  pricingMsg.value = ''

  const obj = {}
  for (const row of pricingRows.value) {
    if (!row.model.trim()) continue
    obj[row.model.trim()] = {
      input_per_1m: Number(row.input_per_1m) || 0,
      output_per_1m: Number(row.output_per_1m) || 0,
    }
  }

  const { error } = await supabase.from('settings').upsert({
    key: 'token_pricing',
    value: obj,
    updated_by: user.value?.id,
    updated_at: new Date().toISOString(),
  })

  if (error) {
    pricingMsg.value = error.message
    pricingMsgType.value = 'error'
  } else {
    pricingMsg.value = 'Pricing saved.'
    pricingMsgType.value = 'success'
    invalidatePricingCache()
  }
  savingPricing.value = false
}

// ── Utils ─────────────────────────────────────────────────────────
function fmtNum(n) { return (n || 0).toLocaleString() }
function fmtDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}

// Load data on tab switch
watch(activeTab, (tab) => {
  if (tab === 'overview') loadOverview()
  else if (tab === 'users') loadProfiles()
  else if (tab === 'pricing') loadPricing()
})

onMounted(() => {
  loadOverview()
})
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

/* Tabs */
.tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 24px;
  border-bottom: 1px solid #e3e3e0;
}

.tab {
  padding: 10px 16px;
  font-size: 13px;
  font-family: 'JetBrains Mono', monospace;
  color: #708090;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: -1px;
}

.tab:hover { color: #36454f; }
.tab.active { color: #36454f; font-weight: 700; border-bottom-color: #36454f; }

/* Section */
.section-head {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 16px; flex-wrap: wrap; gap: 10px;
}

.section-head h2 { font-size: 18px; font-weight: 700; margin: 0; }

.section-hint { font-size: 12px; color: #708090; font-family: 'JetBrains Mono', monospace; margin: -8px 0 16px; }

/* Stats */
.stats-row {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 14px; margin-bottom: 20px;
}
@media (max-width: 700px) { .stats-row { grid-template-columns: repeat(2, 1fr); } }

.stat-card { background: #fff; border: 1px solid #e3e3e0; border-radius: 10px; padding: 18px; }
.stat-card.highlight { border-color: #36454f; }
.stat-label { font-size: 11px; font-family: 'JetBrains Mono', monospace; color: #708090; margin-bottom: 8px; }
.stat-value { font-size: 22px; font-weight: 700; color: #36454f; }
.stat-value.mono { font-family: 'JetBrains Mono', monospace; font-size: 18px; }

/* Table card */
.table-card { background: #fff; border: 1px solid #e3e3e0; border-radius: 10px; overflow: hidden; }
.table-header { padding: 13px 16px; font-size: 12px; font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #708090; border-bottom: 1px solid #e3e3e0; }
.table-wrap { overflow-x: auto; }

table { width: 100%; border-collapse: collapse; font-size: 13px; }
thead { background: #fafafa; border-bottom: 1px solid #e3e3e0; }
th { padding: 11px 14px; font-size: 11px; font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #708090; text-align: left; white-space: nowrap; }
td { padding: 11px 14px; color: #36454f; border-bottom: 1px solid #f0f0ee; white-space: nowrap; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: #fafafa; }

.mono { font-family: 'JetBrains Mono', monospace; }
.dim { color: #708090; }
.r { text-align: right; }
.empty-cell { color: #a0a0a0; font-family: 'JetBrains Mono', monospace; text-align: center; padding: 30px; }

.table-footer {
  display: flex; align-items: center; justify-content: flex-end; gap: 12px;
  padding: 12px 16px; border-top: 1px solid #e3e3e0;
}

/* Buttons */
.btn-action {
  background: #36454f; color: #fff; border: none; border-radius: 7px;
  padding: 9px 16px; font-size: 13px; font-weight: 700;
  font-family: 'Space Grotesk', sans-serif; cursor: pointer;
  display: flex; align-items: center; gap: 6px; transition: background 0.15s;
}
.btn-action:hover:not(:disabled) { background: #28333b; }
.btn-action:disabled { background: #e3e3e0; color: #a0a0a0; cursor: not-allowed; }

.btn-secondary {
  background: none; color: #708090; border: 1px solid #e3e3e0; border-radius: 7px;
  padding: 9px 16px; font-size: 13px; font-family: 'Space Grotesk', sans-serif;
  cursor: pointer; transition: border-color 0.15s;
}
.btn-secondary:hover { border-color: #708090; }

.btn-sm {
  font-size: 11px; font-family: 'JetBrains Mono', monospace; color: #708090;
  background: none; border: 1px solid #e3e3e0; border-radius: 5px; padding: 4px 8px;
  cursor: pointer; transition: border-color 0.15s, color 0.15s; white-space: nowrap;
}
.btn-sm:hover { border-color: #708090; color: #36454f; }
.btn-sm.danger { color: #c0392b; border-color: #f5c6c2; }
.btn-sm.danger:hover { background: #fdf3f2; }
.btn-sm:disabled { opacity: 0.4; cursor: not-allowed; }

.actions-row { display: flex; gap: 6px; }

/* Badges */
.badge {
  display: inline-block; font-size: 11px; font-family: 'JetBrains Mono', monospace;
  padding: 2px 7px; border-radius: 4px;
}
.badge-admin { background: #36454f; color: #fff; }
.badge-user { background: #f0f0ee; color: #708090; }
.badge-active { background: #e8f5ef; color: #2d7a55; }
.badge-inactive { background: #f0f0ee; color: #a0a0a0; }

/* Select */
select {
  font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #36454f;
  background: #fff; border: 1px solid #e3e3e0; border-radius: 6px;
  padding: 5px 10px; cursor: pointer; outline: none;
}

/* Inline table inputs */
.inline-input {
  font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #36454f;
  border: 1px solid #e3e3e0; border-radius: 5px; padding: 5px 8px;
  background: #fbfbfa; outline: none; width: 100%; min-width: 80px;
  transition: border-color 0.15s;
}
.inline-input:focus { border-color: #708090; background: #fff; }
.inline-input.num { text-align: right; width: 90px; }
.inline-input:disabled { opacity: 0.5; }

/* Messages */
.msg { font-size: 12px; font-family: 'JetBrains Mono', monospace; }
.msg.success { color: #2d7a55; }
.msg.error { color: #c0392b; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.3); backdrop-filter: blur(2px);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}

.modal {
  background: #fff; border-radius: 12px; border: 1px solid #e3e3e0;
  width: 100%; max-width: 420px; overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
}

.modal-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px; border-bottom: 1px solid #e3e3e0;
  font-weight: 700; font-size: 14px;
}

.modal-close {
  background: none; border: none; cursor: pointer; color: #708090;
  font-size: 18px; padding: 0; line-height: 1; transition: color 0.15s;
}
.modal-close:hover { color: #36454f; }

.modal-body { padding: 20px; display: flex; flex-direction: column; gap: 8px; }

.modal-footer {
  display: flex; align-items: center; justify-content: flex-end; gap: 10px;
  padding: 14px 20px; border-top: 1px solid #e3e3e0;
}

.field-label { font-size: 12px; font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #36454f; }

input[type="email"] {
  width: 100%; border: 1px solid #e3e3e0; border-radius: 7px; padding: 10px 13px;
  font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #36454f;
  background: #fbfbfa; outline: none; transition: border-color 0.15s;
}
input[type="email"]:focus { border-color: #708090; background: #fff; }

/* States */
.loading-state { padding: 40px; text-align: center; font-size: 13px; color: #a0a0a0; font-family: 'JetBrains Mono', monospace; }
</style>
