<template>
  <div class="wrap">

    <!-- Flow strip -->
    <h2>Working Flow</h2>
    <br>
    <div class="flow">
      <div class="flow-step">
        <span class="n">01</span>
        <div class="t"><i class="ti ti-file-upload"></i>Upload</div>
        <div class="d">Upload source documents as reality seed</div>
      </div>
      <div class="flow-step">
        <span class="n">02</span>
        <div class="t"><i class="ti ti-affiliate"></i>Build</div>
        <div class="d">System auto-builds persona &amp; agent graph</div>
      </div>
      <div class="flow-step">
        <span class="n">03</span>
        <div class="t"><i class="ti ti-players"></i>Simulate</div>
        <div class="d">Agents run the  per your prompt</div>
      </div>
      <div class="flow-step">
        <span class="n">04</span>
        <div class="t"><i class="ti ti-report"></i>Review</div>
        <div class="d">Read the report or chat with agents directly</div>
      </div>
    </div>

    <hr>
    
    <h2 style="margin-top:1rem;">Simulation Section</h2>
    <br>

    <!-- Simulation panel -->
    <div class="panel">
      <div class="field-label">
        <span><i class="ti ti-paperclip" style="font-size:14px;vertical-align:-2px;margin-right:4px;"></i>Reality seed</span>
        <!-- <span class="hint">PDF · MD · TXT · JPG · PNG · WEBP</span> -->
      </div>
      <div
        class="dropzone"
        :class="{ 'drag-over': isDragOver, 'has-files': files.length > 0 }"
        @dragover.prevent="handleDragOver"
        @dragleave.prevent="handleDragLeave"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
      >
        <input
          ref="fileInput"
          type="file"
          multiple
          accept=".pdf,.md,.txt,.png,.jpg,.jpeg,.webp"
          @change="handleFileSelect"
          style="display:none"
          :disabled="loading"
        />
        <template v-if="files.length === 0">
          <i class="ti ti-cloud-upload"></i>
          <div class="main">{{ $t('home.dragToUpload') }}</div>
          <div class="sub">{{ $t('home.orBrowse') }}</div>
        </template>
        <div v-else class="file-list" @click.stop>
          <div v-for="(file, index) in files" :key="index" class="file-chip">
            <span class="ext">{{ file.name.split('.').pop().toUpperCase() }}</span>
            <span class="name">{{ file.name }}</span>
            <i class="ti ti-x rm" @click.stop="removeFile(index)"></i>
          </div>
          <div class="add-more" @click.stop="triggerFileInput">
            <i class="ti ti-plus"></i> Add more
          </div>
        </div>
      </div>
      <p class="field-hint"><i class="ti ti-files"></i> PDF, MD, TXT, JPG, PNG, WEBP — multiple files allowed.</p>

      <div class="field-label" style="margin-top:18px;">
        <span><i class="ti ti-terminal" style="font-size:14px;vertical-align:-2px;margin-right:4px;"></i>{{ $t('home.simulationPrompt') }}</span>
      </div>
      <textarea
        v-model="formData.simulationRequirement"
        :placeholder="$t('home.promptPlaceholder')"
        :disabled="loading"
      ></textarea>
      <p class="field-hint"><i class="ti ti-clock"></i> Typically completes in 20 rounds, depending on prompt complexity.</p>

      <div class="submit-row">
        <button
          class="btn-primary"
          @click="startSimulation"
          :disabled="!canSubmit || loading"
        >
          <span v-if="!loading">{{ $t('home.startEngine') }}</span>
          <span v-else>{{ $t('home.initializing') }}</span>
          <i class="ti ti-arrow-right"></i>
        </button>
        <span class="engine-tag">MiroFish-V1.0</span>
      </div>
    </div>

    <!-- History -->
    <HistoryDatabase />

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import HistoryDatabase from '../components/HistoryDatabase.vue'
const router = useRouter()

const formData = ref({ simulationRequirement: '' })
const files = ref([])
const loading = ref(false)
const isDragOver = ref(false)
const fileInput = ref(null)

const canSubmit = computed(() =>
  formData.value.simulationRequirement.trim() !== '' && files.value.length > 0
)

const triggerFileInput = () => {
  if (!loading.value) fileInput.value?.click()
}

const handleFileSelect = (event) => {
  addFiles(Array.from(event.target.files))
  event.target.value = ''
}

const handleDragOver = () => { if (!loading.value) isDragOver.value = true }
const handleDragLeave = () => { isDragOver.value = false }
const handleDrop = (e) => {
  isDragOver.value = false
  if (!loading.value) addFiles(Array.from(e.dataTransfer.files))
}

const addFiles = (newFiles) => {
  const valid = newFiles.filter(f =>
    ['pdf', 'md', 'txt', 'png', 'jpg', 'jpeg', 'webp'].includes(f.name.split('.').pop().toLowerCase())
  )
  files.value.push(...valid)
}

const removeFile = (index) => files.value.splice(index, 1)

const startSimulation = () => {
  if (!canSubmit.value || loading.value) return
  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(files.value, formData.value.simulationRequirement)
    router.push({ name: 'Process', params: { projectId: 'new' } })
  })
}
</script>

<style scoped>
:root {
  --charcoal: #36454f;
  --slate: #708090;
  --light: #d3d3d3;
  --bg: #fafafa;
  --line: #e3e3e0;
  --card: #ffffff;
  --mono: 'JetBrains Mono', 'SF Mono', Consolas, monospace;
  --sans: 'Space Grotesk', -apple-system, 'Segoe UI', sans-serif;
}

* { box-sizing: border-box; }

.wrap {
  max-width: 1080px;
  margin: 0 auto;
  padding: 32px 24px 80px;
  background: #fafafa;
  min-height: 100vh;
  font-family: var(--sans, 'Space Grotesk', sans-serif);
  color: #36454f;
  -webkit-font-smoothing: antialiased;
}

/* ── Flow strip ── */
.flow {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
  border: 1px solid #e3e3e0;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 32px;
  background: #fff;
}

.flow-step {
  padding: 16px 18px;
  border-right: 1px solid #e3e3e0;
  position: relative;
}

.flow-step:last-child { border-right: none; }

.flow-step .n {
  font-family: var(--mono, monospace);
  font-size: 11px;
  color: #708090;
  display: block;
  margin-bottom: 6px;
}

.flow-step .t {
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 3px;
  display: flex;
  align-items: center;
  gap: 6px;
  color: #36454f;
}

.flow-step .t i { font-size: 15px; color: #708090; }

.flow-step .d { font-size: 12px; color: #708090; line-height: 1.4; }

.flow-step::after {
  content: "";
  position: absolute;
  right: -5px;
  top: 50%;
  width: 7px;
  height: 7px;
  border-top: 1.5px solid #d3d3d3;
  border-right: 1.5px solid #d3d3d3;
  transform: translateY(-50%) rotate(45deg);
  background: #fff;
  z-index: 1;
}

.flow-step:last-child::after { display: none; }

@media (max-width: 760px) {
  .flow { grid-template-columns: repeat(2, 1fr); }
}

/* ── Panel ── */
.panel {
  background: #fff;
  border: 1px solid #e3e3e0;
  border-radius: 10px;
  padding: 22px;
}

/* ── Upload panel ── */
.field-label {
  font-size: 12px;
  font-family: var(--mono, monospace);
  color: #36454f;
  font-weight: 700;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.field-label .hint { color: #708090; font-weight: 400; font-size: 11px; }

.dropzone {
  border: 1.5px dashed #d3d3d3;
  border-radius: 8px;
  padding: 28px 16px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  min-height: 110px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 6px;
}

.dropzone.has-files {
  padding: 14px;
  align-items: flex-start;
  justify-content: flex-start;
}

.dropzone:hover { border-color: #708090; background: #f7f7f6; }

.dropzone.drag-over { border-color: #36454f; background: #f0f0ee; }

.dropzone > i { font-size: 26px; color: #708090; margin-bottom: 8px; }

.dropzone .main { font-size: 14px; font-weight: 700; margin-bottom: 3px; color: #36454f; }

.dropzone .sub { font-size: 12px; color: #708090; }

.file-list { display: flex; flex-direction: column; gap: 6px; width: 100%; }

.file-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  border: 1px solid #e3e3e0;
  border-radius: 6px;
  padding: 7px 10px;
  background: #fbfbfa;
}

.file-chip .ext {
  font-family: var(--mono, monospace);
  font-size: 10px;
  font-weight: 700;
  color: #fff;
  background: #708090;
  padding: 2px 5px;
  border-radius: 4px;
  flex-shrink: 0;
}

.file-chip .name { flex: 1; color: #36454f; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.file-chip i.rm { color: #708090; cursor: pointer; font-size: 14px; flex-shrink: 0; }

.file-chip i.rm:hover { color: #36454f; }

.add-more {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: #708090;
  font-family: var(--mono, monospace);
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  transition: color 0.15s;
}

.add-more:hover { color: #36454f; }

textarea {
  width: 100%;
  min-height: 100px;
  border: 1px solid #e3e3e0;
  border-radius: 8px;
  padding: 12px 14px;
  font-family: var(--mono, monospace);
  font-size: 13px;
  color: #36454f;
  resize: vertical;
  margin-bottom: 6px;
  background: #fbfbfa;
}

.field-hint {
  font-size: 11px;
  color: #a0a0a0;
  font-family: var(--mono, monospace);
  margin: 0 0 18px;
  display: flex;
  align-items: center;
  gap: 5px;
  line-height: 1.4;
}

.field-hint i { font-size: 12px; flex-shrink: 0; }

textarea::placeholder { color: #708090; }

textarea:focus { outline: none; border-color: #708090; background: #fff; }

.submit-row { display: flex; align-items: center; gap: 12px; }

.btn-primary {
  flex: 1;
  background: #36454f;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 13px 20px;
  font-size: 14px;
  font-weight: 700;
  font-family: var(--sans, sans-serif);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background 0.15s;
}

.btn-primary:hover:not(:disabled) { background: #28333b; }

.btn-primary:disabled {
  background: #e3e3e0;
  color: #a0a0a0;
  cursor: not-allowed;
}

.btn-primary i { font-size: 16px; }

.engine-tag {
  font-family: var(--mono, monospace);
  font-size: 11px;
  color: #708090;
  white-space: nowrap;
}

hr{
    border: 0.5px solid #e3e3e0;
}
</style>
