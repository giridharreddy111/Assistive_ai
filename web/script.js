const video = document.getElementById("video")

let speaking = false
let lastSpeakTime = 0
let detectionInterval = null
let stream = null

let beepInterval = null

let pressTimer
let lastTap = 0

let emotions = []
let noFaceCount = 0
let faceDetectedRecently = false

window.onload = function(){
 startCamera()
}

async function startCamera(){

 if(stream) return

 stream = await navigator.mediaDevices.getUserMedia({
  video:{ facingMode:{ ideal:"environment" } }
 })

 video.srcObject = stream

 detectionInterval = setInterval(captureFrame,800)

 speak("Assistive AI started")
}

async function captureFrame(){

 if(!video.videoWidth) return

 const canvas = document.createElement("canvas")

 canvas.width = video.videoWidth
 canvas.height = video.videoHeight

 const ctx = canvas.getContext("2d")
 ctx.drawImage(video,0,0)

 canvas.toBlob(async(blob)=>{

  const formData = new FormData()
  formData.append("frame",blob)

  try{

   const res = await fetch("/detect",{
    method:"POST",
    body:formData
   })

   const data = await res.json()

   handleResult(data)

  }catch(err){
   console.log(err)
  }

 })
}

function handleResult(data){

 // -------- FACE DETECTED --------
 if(data.emotion && data.emotion !== "no_face"){

  faceDetectedRecently = true
  noFaceCount = 0

  stopBeep()

  emotions.push({
   emotion:data.emotion,
   confidence:data.confidence
  })

  if(emotions.length >= 5){

   let best = emotions.sort((a,b)=>b.confidence-a.confidence)[0]

   speak("Person looks " + best.emotion)

   emotions = []
  }

 }

 // -------- NO FACE --------
 else{

  noFaceCount++

  if(noFaceCount > 5){
   faceDetectedRecently = false
  }

 }

 // -------- OBSTACLE --------
 if(!faceDetectedRecently && data.obstacle){
  startBeep()
 }else{
  stopBeep()
 }

 if(!faceDetectedRecently && noFaceCount >= 5){
  speak("No face detected")
  noFaceCount = 0
 }

}

function speak(text){

 const now = Date.now()

 if(now - lastSpeakTime < 4000) return

 lastSpeakTime = now

 if(speaking) return

 speaking = true

 const msg = new SpeechSynthesisUtterance(text)

 msg.onend = ()=>{ speaking = false }

 speechSynthesis.speak(msg)

}

function beep(){

 const ctx = new AudioContext()

 const osc = ctx.createOscillator()

 osc.frequency.value = 1000

 osc.connect(ctx.destination)

 osc.start()

 setTimeout(()=>{ osc.stop() },120)

}

function startBeep(){

 if(beepInterval) return

 beepInterval = setInterval(beep,500)

}

function stopBeep(){

 if(beepInterval){
  clearInterval(beepInterval)
  beepInterval = null
 }

}

function stopDetection(){

 if(detectionInterval){
  clearInterval(detectionInterval)
  detectionInterval = null
 }

 if(stream){
  stream.getTracks().forEach(track=>track.stop())
  stream = null
 }

 stopBeep()

 speak("Detection stopped")

}

document.addEventListener("touchstart",function(){

 pressTimer = setTimeout(stopDetection,1500)

})

document.addEventListener("touchend",function(){

 clearTimeout(pressTimer)

})

document.addEventListener("touchend",function(){

 const now = new Date().getTime()

 const tapGap = now - lastTap

 if(tapGap < 300 && tapGap > 0){

  startCamera()

 }

 lastTap = now

})