<template>
  <div ref="threeContainer" class="three-background"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { gsap } from 'gsap' // If gsap is not installed, we can use simple lerp.

const route = useRoute()
const threeContainer = ref<HTMLElement | null>(null)

let scene: THREE.Scene, camera: THREE.PerspectiveCamera, renderer: THREE.WebGLRenderer, controls: OrbitControls
let animationId: number
let stadiumModel: THREE.Group | null = null

// 目标位置，用于平滑过渡
const targetCameraPos = new THREE.Vector3(0, 80, 150) // 首页默认机位拉近放大
const targetControlsTarget = new THREE.Vector3(0, -10, 0)
let isUserInteracting = false // 记录用户是否在手动控制

const initThreeJS = () => {
  const container = threeContainer.value
  if (!container) return

  scene = new THREE.Scene()
  scene.background = null

  const width = window.innerWidth
  const height = window.innerHeight

  camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 10000)
  camera.position.copy(targetCameraPos)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(window.devicePixelRatio)
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.2
  container.appendChild(renderer.domElement)

  // 灯光
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
  scene.add(ambientLight)

  const dirLight = new THREE.DirectionalLight(0xffffff, 1.5)
  dirLight.position.set(100, 200, 50)
  scene.add(dirLight)

  const blueLight = new THREE.PointLight(0x409EFF, 2000, 500)
  blueLight.position.set(-50, 50, 0)
  scene.add(blueLight)

  const greenLight = new THREE.PointLight(0x67C23A, 2000, 500)
  greenLight.position.set(50, 50, 0)
  scene.add(greenLight)

  // 控制器
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.enableZoom = true
  controls.minDistance = 10
  controls.maxDistance = 1000
  controls.enablePan = true
  controls.autoRotate = true
  controls.autoRotateSpeed = 0.5
  controls.maxPolarAngle = Math.PI
  controls.target.copy(targetControlsTarget)

  // 监听用户手动操作，打断自动运镜
  controls.addEventListener('start', () => {
    isUserInteracting = true
  })
  
  // 如果需要用户停止操作后恢复自动运镜，可以监听 'end' 并设置延时，这里保持用户手动控制的优先级
  // controls.addEventListener('end', () => { ... })

  // 加载模型
  const loader = new GLTFLoader()
  loader.load('/stadium.glb', (gltf) => {
    stadiumModel = gltf.scene
    stadiumModel.scale.set(5, 5, 5) 
    const box = new THREE.Box3().setFromObject(stadiumModel)
    const center = box.getCenter(new THREE.Vector3())
    stadiumModel.position.sub(center)
    stadiumModel.position.y -= 30 
    scene.add(stadiumModel)
  })

  const animate = () => {
    animationId = requestAnimationFrame(animate)
    
    // 只有在用户没有手动干预时，才执行自动平滑运镜
    if (!isUserInteracting) {
      camera.position.lerp(targetCameraPos, 0.02)
      controls.target.lerp(targetControlsTarget, 0.02)
    }

    controls.update()
    renderer.render(scene, camera)
  }
  animate()

  window.addEventListener('resize', onWindowResize)
}

const onWindowResize = () => {
  if (!threeContainer.value || !camera || !renderer) return
  const width = window.innerWidth
  const height = window.innerHeight
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

// 监听路由变化，动态改变机位
watch(() => route.path, (newPath) => {
  // 每次切换页面时，重置用户交互状态，允许自动运镜生效
  isUserInteracting = false 

  if (newPath === '/prediction') {
    // 比赛详情页：赛场内部中心机位，沉浸式
    targetCameraPos.set(0, 10, 50)
    targetControlsTarget.set(0, 10, 0)
  } else {
    // 首页或其他：拉近的大屏环绕机位
    targetCameraPos.set(0, 80, 150)
    targetControlsTarget.set(0, -10, 0)
  }
}, { immediate: true })

onMounted(() => {
  setTimeout(() => {
    initThreeJS()
  }, 100)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onWindowResize)
  if (animationId) cancelAnimationFrame(animationId)
  if (renderer && threeContainer.value) {
    renderer.dispose()
    threeContainer.value.removeChild(renderer.domElement)
  }
})
</script>

<style scoped>
.three-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
  pointer-events: auto; /* 允许交互 */
}
</style>