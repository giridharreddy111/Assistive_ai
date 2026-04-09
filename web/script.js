const video = document.getElementById("video")

let speaking = false
let detectionInterval = null
let stream = null

let beepInterval = null
let emotions = []
let audioCtx = null

let textMode = false

// -----------------------------
// UNLOCK AUDIO — critical for mobile
// -----------------------------
let audioUnlocked = false
function unlockAudio() {
    if (audioUnlocked) return
    audioUnlocked = true
    try {
        const utterance = new SpeechSynthesisUtterance("")
        utterance.volume = 0
        speechSynthesis.speak(utterance)
    } catch(e) {}
}

// -----------------------------
// SPEAK — Web Speech API
// Works on ALL mobile browsers
// -----------------------------
function speak(text) {
    try {
        speechSynthesis.cancel()

        const msg = new SpeechSynthesisUtterance(text)
        msg.rate = 0.9
        msg.volume = 1.0
        msg.lang = "en-US"

        msg.onstart = () => { speaking = true }
        msg.onend = () => { speaking = false }
        msg.onerror = () => { speaking = false }

        speechSynthesis.speak(msg)
    } catch(e) {
        speaking = false
    }
}

// -----------------------------
// LONG PRESS
// touchstart for mobile — fires exactly once
// mousedown for laptop
// -----------------------------
const video = document.getElementById("video")

let speaking = false
let detectionInterval = null
let stream = null
let beepInterval = null
let emotions = []
let audioCtx = null
let textMode = false

// -----------------------------
// AUDIO UNLOCK
// -----------------------------
let audioUnlocked = false

function unlockAudio() {
    if (audioUnlocked) return
    audioUnlocked = true

    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(" ")
    u.volume = 0
    window.speechSynthesis.speak(u)
}

// -----------------------------
// SPEAK (FIXED)
// -----------------------------
function speak(text) {
    try {
        if (window.speechSynthesis.speaking) {
            return
        }

        const msg = new SpeechSynthesisUtterance(text)
        msg.lang = "en-IN"
        msg.rate = 1.1
        msg.pitch = 1.0
        msg.volume = 1.0

        msg.onstart = () => { speaking = true }
        msg.onend = () => { speaking = false }
        msg.onerror = () => { speaking = false }

        window.speechSynthesis.speak(msg)

    } catch(e) {
        speaking = false
        console.log("Speak error:", e)
    }
}

// -----------------------------
// LONG PRESS FIXED
// -----------------------------
let pressTimer = null
let isPressed = false
let touchMoved = false
let toggleLocked = false

document.addEventListener("contextmenu", (e) => e.preventDefault())

document.addEventListener("touchstart", (e) => {
    unlockAudio()
    isPressed = true
    touchMoved = false
    clearTimeout(pressTimer)

    pressTimer = setTimeout(() => {
        if (isPressed && !touchMoved && !toggleLocked) {
            isPressed = false
            toggleLocked = true
            toggleTextMode()
            setTimeout(() => { toggleLocked = false }, 1500)
        }
    }, 800)
}, { passive: false })

document.addEventListener("touchmove", () => {
    touchMoved = true
    clearTimeout(pressTimer)
    isPressed = false
}, { passive: false })

document.addEventListener("touchend", () => {
    clearTimeout(pressTimer)
    isPressed = false
})

document.addEventListener("touchcancel", () => {
    clearTimeout(pressTimer)
    isPressed = false
    touchMoved = false
})

// MOUSE
document.addEventListener("mousedown", (e) => {
    if (e.button !== 0) return
    unlockAudio()
    isPressed = true
    clearTimeout(pressTimer)

    pressTimer = setTimeout(() => {
        if (isPressed && !toggleLocked) {
            isPressed = false
            toggleLocked = true
            toggleTextMode()
            setTimeout(() => { toggleLocked = false }, 1500)
        }
    }, 800)
})

document.addEventListener("mouseup", () => {
    clearTimeout(pressTimer)
    isPressed = false
})

// -----------------------------
window.onload = function () {
    startCamera()
}

// -----------------------------
async function toggleTextMode() {
    try {
        const res = await fetch("/toggle-text-mode", { method: "POST" })
        const data = await res.json()

        speaking = false
        emotions = []
        stopBeep()

        if (data.mode === "text") {
            textMode = true
            setTimeout(() => speak("Text mode activated"), 400)
        } else {
            textMode = false
            setTimeout(() => speak("Normal mode activated"), 400)
        }

    } catch (err) {
        toggleLocked = false
        console.log("Toggle error:", err)
    }
}

// -----------------------------
async function startCamera() {
    if (stream) return

    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: { ideal: "environment" },
                width: { ideal: 640 },
                height: { ideal: 480 }
            }
        })

        video.srcObject = stream
        detectionInterval = setInterval(captureFrame, 700)

    } catch(err) {
        console.log("Camera error:", err)
    }
}

// -----------------------------
async function captureFrame() {
    if (!video.videoWidth) return

    const canvas = document.createElement("canvas")
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    const ctx = canvas.getContext("2d")
    ctx.drawImage(video, 0, 0)

    const blob = await (await fetch(canvas.toDataURL("image/jpeg", 0.7))).blob()

    const formData = new FormData()
    formData.append("frame", blob)

    try {
        const res = await fetch("/detect", {
            method: "POST",
            body: formData
        })

        const data = await res.json()

        if (data.mode === "text") {
            if (data.text && data.text.trim() !== "" && !speaking) {
                speaking = true
                speak(data.text)

                setTimeout(() => {
                    speaking = false
                }, 2500)
            }
            return
        }

        handleResult(data)

    } catch (err) {
        console.log("Detect error:", err)
    }
}

// -----------------------------
function handleResult(data) {
    if (textMode) return

    if (data.obstacle && data.distance !== null) {
        if (data.distance === 0) startBeep(150)
        else if (data.distance === 1) startBeep(400)
        else stopBeep()

        emotions = []
        return
    }

    stopBeep()

    if (data.emotion) {
        emotions.push(data)

        if (emotions.length >= 3) {
            let best = emotions.sort(
                (a, b) => b.confidence - a.confidence
            )[0]

            if (!speaking) {
                speak("Person looks " + best.emotion)
            }

            emotions = []
        }
    }
}

// -----------------------------
function beep() {
    try {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)()
        }
        const osc = audioCtx.createOscillator()
        osc.frequency.value = 1200
        osc.connect(audioCtx.destination)
        osc.start()
        setTimeout(() => osc.stop(), 120)
    } catch(e) {}
}

function startBeep(speed = 400) {
    if (beepInterval) clearInterval(beepInterval)
    beepInterval = setInterval(beep, speed)
}

function stopBeep() {
    if (beepInterval) {
        clearInterval(beepInterval)
        beepInterval = null
    }
}
