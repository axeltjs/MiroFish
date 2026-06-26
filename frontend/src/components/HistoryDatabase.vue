<template>
  <div class="history-wrap">
    <hr>

    <!-- Section header -->
    <div class="history-head" style="margin-top: 1rem;">
      <h2>Simulation History</h2>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="loading-state">
      <span class="loading-spinner"></span>
      <span class="loading-text">{{ $t('history.loadingText') }}</span>
    </div>

    <!-- Empty state -->
    <div v-else-if="projects.length === 0" class="empty-state">
      <i class="ti ti-database-off" style="font-size:28px;color:#d3d3d3;"></i>
      <span>{{ $t('history.noFiles') }}</span>
    </div>

    <!-- Grid -->
    <div v-else class="history-grid">
      <div
        v-for="project in projects"
        :key="project.simulation_id"
        class="hcard"
        @click="navigateToProject(project)"
      >
        <!-- Delete confirm overlay -->
        <Transition name="confirm-fade">
          <div
            v-if="confirmingDeleteId === project.simulation_id"
            class="delete-confirm-overlay"
            @click.stop
          >
            <span class="delete-confirm-text">Delete?</span>
            <div class="delete-confirm-actions">
              <button class="delete-confirm-yes" @click="confirmDelete($event, project.simulation_id)">Yes</button>
              <button class="delete-confirm-no" @click="cancelDelete($event)">No</button>
            </div>
          </div>
        </Transition>

        <!-- Deleting overlay -->
        <div v-if="deletingId === project.simulation_id" class="delete-loading-overlay" @click.stop>
          <span class="delete-loading-spinner"></span>
        </div>

        <!-- Delete button -->
        <button
          class="card-delete-btn"
          @click="requestDelete($event, project.simulation_id)"
          title="Delete simulation"
        >×</button>

        <!-- Card top -->
        <div class="hcard-top">
          <span class="hcard-id">{{ formatSimulationId(project.simulation_id) }}</span>
          <span class="hcard-status" :class="getProgressClass(project)">
            <i
              :class="getProgressClass(project) === 'completed' ? 'ti ti-circle-check' : 'ti ti-clock'"
              style="font-size:13px;"
            ></i>
            {{ formatRounds(project) }}
          </span>
        </div>

        <!-- Files -->
        <div class="hcard-files">
          <template v-if="project.files && project.files.length > 0">
            <div
              v-for="(file, fi) in project.files.slice(0, 3)"
              :key="fi"
              class="hcard-file"
            >
              <span class="ext" :class="getFileType(file.filename)">{{ getFileTypeLabel(file.filename) }}</span>
              <span>{{ truncateFilename(file.filename, 20) }}</span>
            </div>
            <div v-if="project.files.length > 3" class="hcard-more">
              +{{ project.files.length - 3 }} more
            </div>
          </template>
          <span v-else class="hcard-empty">{{ $t('history.noFiles') }}</span>
        </div>

        <!-- Title & desc -->
        <p class="hcard-title">{{ getSimulationTitle(project.simulation_requirement) }}</p>
        <p class="hcard-desc">{{ truncateText(project.simulation_requirement, 80) }}</p>

        <!-- Meta -->
        <div class="hcard-meta">
          <span>{{ formatDate(project.created_at) }} {{ formatTime(project.created_at) }}</span>
        </div>
      </div>
    </div>

    <!-- Detail modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="selectedProject" class="modal-overlay" @click.self="closeModal">
          <div class="modal-content">
            <div class="modal-header">
              <div class="modal-title-section">
                <span class="modal-id">{{ formatSimulationId(selectedProject.simulation_id) }}</span>
                <span class="modal-progress" :class="getProgressClass(selectedProject)">
                  <span class="status-dot">●</span> {{ formatRounds(selectedProject) }}
                </span>
                <span class="modal-create-time">{{ formatDate(selectedProject.created_at) }} {{ formatTime(selectedProject.created_at) }}</span>
              </div>
              <button class="modal-close" @click="closeModal">×</button>
            </div>

            <div class="modal-body">
              <div class="modal-section">
                <div class="modal-label">{{ $t('history.simRequirement') }}</div>
                <div class="modal-requirement">{{ selectedProject.simulation_requirement || $t('common.none') }}</div>
              </div>
              <div class="modal-section">
                <div class="modal-label">{{ $t('history.relatedFiles') }}</div>
                <div class="modal-files" v-if="selectedProject.files && selectedProject.files.length > 0">
                  <div v-for="(file, index) in selectedProject.files" :key="index" class="modal-file-item">
                    <span class="ext" :class="getFileType(file.filename)">{{ getFileTypeLabel(file.filename) }}</span>
                    <span class="modal-file-name">{{ file.filename }}</span>
                  </div>
                </div>
                <div class="modal-empty" v-else>{{ $t('history.noRelatedFiles') }}</div>
              </div>
            </div>

            <div class="modal-divider">
              <span class="divider-line"></span>
              <span class="divider-text">{{ $t('history.replayTitle') }}</span>
              <span class="divider-line"></span>
            </div>

            <div class="modal-actions">
              <button class="modal-btn btn-project" @click="goToProject" :disabled="!selectedProject.project_id">
                <span class="btn-step">Step1</span>
                <span class="btn-icon">◇</span>
                <span class="btn-text">{{ $t('history.step1Button') }}</span>
              </button>
              <button class="modal-btn btn-simulation" @click="goToSimulation">
                <span class="btn-step">Step2</span>
                <span class="btn-icon">◈</span>
                <span class="btn-text">{{ $t('history.step2Button') }}</span>
              </button>
              <button class="modal-btn btn-report" @click="goToReport" :disabled="!selectedProject.report_id">
                <span class="btn-step">Step4</span>
                <span class="btn-icon">◆</span>
                <span class="btn-text">{{ $t('history.step4Button') }}</span>
              </button>
            </div>

            <div class="modal-playback-hint">
              <span class="hint-text">{{ $t('history.replayHint') }}</span>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, onMounted, onActivated, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getSimulationHistory, deleteSimulation } from '../api/simulation'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()

const projects = ref([])
const loading = ref(true)
const selectedProject = ref(null)
const confirmingDeleteId = ref(null)
const deletingId = ref(null)

// ── Formatting helpers ──────────────────────────────────────────────────────

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  try { return new Date(dateStr).toISOString().slice(0, 10) } catch { return dateStr?.slice(0, 10) || '' }
}

const formatTime = (dateStr) => {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr)
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
  } catch { return '' }
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  return text.length > maxLength ? text.slice(0, maxLength) + '...' : text
}

const getSimulationTitle = (requirement) => {
  if (!requirement) return t('history.untitledSimulation')
  return requirement.length > 20 ? requirement.slice(0, 20) + '...' : requirement
}

const formatSimulationId = (simulationId) => {
  if (!simulationId) return 'SIM_UNKNOWN'
  return `SIM_${simulationId.replace('sim_', '').slice(0, 6).toUpperCase()}`
}

const formatRounds = (simulation) => {
  const current = simulation.current_round || 0
  const total = simulation.total_rounds || 0
  if (total === 0) return t('history.notStarted')
  return t('history.roundsProgress', { current, total })
}

const getProgressClass = (simulation) => {
  const current = simulation.current_round || 0
  const total = simulation.total_rounds || 0
  if (total === 0 || current === 0) return 'not-started'
  return current >= total ? 'completed' : 'in-progress'
}

const getFileType = (filename) => {
  if (!filename) return 'other'
  const ext = filename.split('.').pop()?.toLowerCase()
  const map = {
    pdf: 'pdf', doc: 'doc', docx: 'doc',
    xls: 'xls', xlsx: 'xls', csv: 'xls',
    ppt: 'ppt', pptx: 'ppt',
    txt: 'txt', md: 'txt', json: 'code',
    jpg: 'img', jpeg: 'img', png: 'img', gif: 'img', webp: 'img',
    zip: 'zip', rar: 'zip', '7z': 'zip'
  }
  return map[ext] || 'other'
}

const getFileTypeLabel = (filename) => {
  if (!filename) return 'FILE'
  return filename.split('.').pop()?.toUpperCase() || 'FILE'
}

const truncateFilename = (filename, maxLength) => {
  if (!filename) return t('history.unknownFile')
  if (filename.length <= maxLength) return filename
  const ext = filename.includes('.') ? '.' + filename.split('.').pop() : ''
  const base = filename.slice(0, filename.length - ext.length)
  return base.slice(0, maxLength - ext.length - 3) + '...' + ext
}

// ── Navigation ──────────────────────────────────────────────────────────────

const navigateToProject = (simulation) => { selectedProject.value = simulation }
const closeModal = () => { selectedProject.value = null }

const goToProject = () => {
  if (selectedProject.value?.project_id) {
    router.push({ name: 'Process', params: { projectId: selectedProject.value.project_id } })
    closeModal()
  }
}

const goToSimulation = () => {
  if (selectedProject.value?.simulation_id) {
    router.push({ name: 'Simulation', params: { simulationId: selectedProject.value.simulation_id } })
    closeModal()
  }
}

const goToReport = () => {
  if (selectedProject.value?.report_id) {
    router.push({ name: 'Report', params: { reportId: selectedProject.value.report_id } })
    closeModal()
  }
}

// ── Delete ──────────────────────────────────────────────────────────────────

const requestDelete = (event, simulationId) => {
  event.stopPropagation()
  confirmingDeleteId.value = simulationId
}

const cancelDelete = (event) => {
  event.stopPropagation()
  confirmingDeleteId.value = null
}

const confirmDelete = async (event, simulationId) => {
  event.stopPropagation()
  confirmingDeleteId.value = null
  deletingId.value = simulationId
  try {
    await deleteSimulation(simulationId)
    projects.value = projects.value.filter(p => p.simulation_id !== simulationId)
  } catch (err) {
    console.error('Delete failed:', err)
  } finally {
    deletingId.value = null
  }
}

// ── Data loading ────────────────────────────────────────────────────────────

const loadHistory = async () => {
  try {
    loading.value = true
    const response = await getSimulationHistory(20)
    if (response.success) projects.value = response.data || []
  } catch (error) {
    console.error('Failed to load history:', error)
    projects.value = []
  } finally {
    loading.value = false
  }
}

watch(() => route.path, (newPath) => { if (newPath === '/') loadHistory() })

onMounted(loadHistory)
onActivated(loadHistory)
</script>

<style scoped>
.history-wrap {
  margin-top: 40px;
}

/* ── Section header ── */
.history-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.history-title {
  font-size: 11px;
  font-family: 'JetBrains Mono', monospace;
  color: #708090;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* ── States ── */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 48px;
  color: #a0a0a0;
  font-size: 13px;
}

.loading-spinner {
  width: 22px;
  height: 22px;
  border: 2px solid #e3e3e0;
  border-top-color: #708090;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── Grid ── */
.history-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

@media (max-width: 760px) {
  .history-grid { grid-template-columns: 1fr; }
}

/* ── Card ── */
.hcard {
  background: #fff;
  border: 1px solid #e3e3e0;
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  position: relative;
  transition: border-color 0.15s;
}

.hcard:hover { border-color: #708090; }

/* Delete button */
.card-delete-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 22px;
  height: 22px;
  border: 1px solid transparent;
  background: transparent;
  color: #d1d5db;
  font-size: 1rem;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 3px;
  z-index: 20;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  padding: 0;
}

.card-delete-btn:hover {
  background: #fef2f2;
  color: #ef4444;
  border-color: #fca5a5;
}

/* Card top */
.hcard-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.hcard-id {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 700;
  color: #36454f;
}

.hcard-status {
  font-size: 11px;
  font-family: 'JetBrains Mono', monospace;
  display: flex;
  align-items: center;
  gap: 5px;
}

.hcard-status.completed { color: #0f6e56; }
.hcard-status.in-progress { color: #d97706; }
.hcard-status.not-started { color: #708090; }

/* Files */
.hcard-files {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 12px;
  min-height: 24px;
}

.hcard-file {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 11px;
  color: #708090;
}

.hcard-file .ext,
.modal-file-item .ext {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  font-weight: 700;
  color: #fff;
  padding: 1px 4px;
  border-radius: 3px;
  flex-shrink: 0;
  min-width: 26px;
  text-align: center;
  background: #d3d3d3;
}

.ext.pdf { background: #d85a30; }
.ext.img { background: #1d9e75; }
.ext.doc { background: #3b82f6; }
.ext.xls { background: #16a34a; }
.ext.ppt { background: #ea580c; }
.ext.txt { background: #6b7280; }
.ext.code { background: #7c3aed; }
.ext.zip { background: #92400e; }

.hcard-empty { font-size: 11px; color: #d3d3d3; font-style: italic; }

.hcard-more { font-size: 10px; color: #a0a0a0; font-family: 'JetBrains Mono', monospace; }

/* Title & desc */
.hcard-title {
  font-size: 13px;
  font-weight: 700;
  margin: 0 0 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #36454f;
  padding-right: 20px;
}

.hcard-desc {
  font-size: 12px;
  color: #708090;
  line-height: 1.4;
  margin: 0 0 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Meta */
.hcard-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid #e3e3e0;
  padding-top: 10px;
  font-size: 11px;
  color: #708090;
  font-family: 'JetBrains Mono', monospace;
}

/* ── Delete overlays ── */
.delete-confirm-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.96);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  z-index: 30;
  border-radius: 10px;
}

.delete-confirm-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  font-weight: 600;
  color: #111827;
}

.delete-confirm-actions { display: flex; gap: 10px; }

.delete-confirm-yes,
.delete-confirm-no {
  padding: 6px 18px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.15s;
}

.delete-confirm-yes { background: #111827; color: #fff; border: 1px solid #111827; }
.delete-confirm-yes:hover { background: #ef4444; border-color: #ef4444; }
.delete-confirm-no { background: transparent; color: #6b7280; border: 1px solid #e3e3e0; }
.delete-confirm-no:hover { border-color: #9ca3af; color: #111827; }

.delete-loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 30;
  border-radius: 10px;
}

.delete-loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e3e3e0;
  border-top-color: #708090;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.confirm-fade-enter-active,
.confirm-fade-leave-active { transition: opacity 0.15s; }
.confirm-fade-enter-from,
.confirm-fade-leave-to { opacity: 0; }

/* ── Modal ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: #fff;
  width: 560px;
  max-width: 90vw;
  max-height: 85vh;
  overflow-y: auto;
  border: 1px solid #e3e3e0;
  border-radius: 10px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-enter-active,
.modal-leave-active { transition: opacity 0.3s; }
.modal-enter-from,
.modal-leave-to { opacity: 0; }
.modal-enter-active .modal-content { transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.modal-leave-active .modal-content { transition: all 0.2s ease-in; }
.modal-enter-from .modal-content,
.modal-leave-to .modal-content { transform: scale(0.95) translateY(10px); opacity: 0; }

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 28px;
  border-bottom: 1px solid #e3e3e0;
}

.modal-title-section { display: flex; align-items: center; gap: 14px; }

.modal-id {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1rem;
  font-weight: 700;
  color: #36454f;
}

.modal-progress {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  background: #f9fafb;
}

.modal-progress.completed { color: #0f6e56; background: rgba(15, 110, 86, 0.1); }
.modal-progress.in-progress { color: #d97706; background: rgba(217, 119, 6, 0.1); }
.modal-progress.not-started { color: #708090; background: #f3f4f6; }

.status-dot { font-size: 0.5rem; }

.modal-create-time {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  color: #708090;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  font-size: 1.5rem;
  color: #708090;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.modal-close:hover { background: #f3f4f6; color: #36454f; }

.modal-body { padding: 24px 28px; }

.modal-section { margin-bottom: 20px; }
.modal-section:last-child { margin-bottom: 0; }

.modal-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  color: #708090;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 10px;
}

.modal-requirement {
  font-size: 0.9rem;
  color: #36454f;
  line-height: 1.6;
  padding: 14px;
  background: #f9fafb;
  border: 1px solid #e3e3e0;
  border-radius: 6px;
}

.modal-files {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.modal-file-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  background: #fff;
  border: 1px solid #e3e3e0;
  border-radius: 6px;
}

.modal-file-name {
  font-size: 0.85rem;
  color: #36454f;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.modal-empty {
  font-size: 0.85rem;
  color: #a0a0a0;
  padding: 14px;
  background: #f9fafb;
  border: 1px dashed #e3e3e0;
  border-radius: 6px;
  text-align: center;
}

.modal-divider {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 8px 28px 0;
}

.divider-line { flex: 1; height: 1px; background: linear-gradient(90deg, transparent, #e3e3e0, transparent); }

.divider-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: #a0a0a0;
  letter-spacing: 2px;
  text-transform: uppercase;
  white-space: nowrap;
}

.modal-actions { display: flex; gap: 14px; padding: 18px 28px; }

.modal-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px;
  border: 1px solid #e3e3e0;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-btn:hover:not(:disabled) { border-color: #36454f; transform: translateY(-2px); }
.modal-btn:disabled { opacity: 0.45; cursor: not-allowed; background: #f9fafb; }

.btn-step {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  color: #a0a0a0;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.btn-icon { font-size: 1.3rem; }
.btn-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  font-weight: 600;
  color: #36454f;
}

.modal-btn.btn-project .btn-icon { color: #3b82f6; }
.modal-btn.btn-simulation .btn-icon { color: #d97706; }
.modal-btn.btn-report .btn-icon { color: #0f6e56; }

.modal-playback-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 28px 18px;
}

.hint-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: #a0a0a0;
  text-align: center;
  line-height: 1.5;
}

hr{
    border: 0.5px solid #e3e3e0;
}
</style>
