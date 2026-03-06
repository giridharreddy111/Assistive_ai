const video = document.getElementById("video")

let emotions = []
let speaking = false
let lastSpeakTime = 0
let detectionInterval = null
let stream = null

// START CAMERA AUTOMATICALLY
window.onload = function(){
 startCamera()
}

async function startCamera(){

 if(stream) return

 stream = await navigator.mediaDevices.getUserMedia({
  video:{
   facingMode:{ ideal:"environment" }
  }
 })

 video.srcObject = stream

 detectionInterval = setInterval(captureFrame,2000)

 speak("Assistive AI started")

}

async function captureFrame(){

 const canvas = document.createElement("canvas")

 canvas.width = video.videoWidth
 canvas.height = video.videoHeight

 const ctx = canvas.getContext("2d")
 ctx.drawImage(video,0,0)

 canvas.toBlob(async(blob)=>{

  const formData = new FormData()
  formData.append("frame",blob)

  try{

   const res = await fetch("http://127.0.0.1:8000/detect",{
    method:"POST",
    body:formData
   })

   const data = await res.json()

   console.log("API RESULT:",data)

   handleResult(data)

  }catch(err){

   console.log("API ERROR:",err)

  }

 })

}

function handleResult(data){

 let message = ""

 if(data.emotion){
  emotions.push(data.emotion)
 }

 if(emotions.length > 5){
  emotions.shift()
 }

 if(emotions.length === 5){

  const counts = {}

  emotions.forEach(e=>{
   counts[e] = (counts[e] || 0) + 1
  })

  const dominant = Object.keys(counts).reduce((a,b)=>
   counts[a] > counts[b] ? a : b
  )

  message = "Person looks " + dominant

  emotions = []
 }

 if(data.obstacle){
  message += ". Obstacle " + data.obstacle.object + " ahead"
 }

 if(message !== ""){
  speak(message)
 }

}

function speak(text){

 const now = Date.now()

 if(now - lastSpeakTime < 5000) return

 lastSpeakTime = now

 if(speaking) return

 speaking = true

 const msg = new SpeechSynthesisUtterance(text)

 msg.onend = ()=>{
  speaking = false
 }

 speechSynthesis.speak(msg)

}

// STOP DETECTION
function stopDetection(){

 if(detectionInterval){
  clearInterval(detectionInterval)
  detectionInterval = null
 }

 if(stream){
  stream.getTracks().forEach(track=>track.stop())
  stream = null
 }

 speak("Detection stopped")

}

// LONG PRESS TO STOP
let pressTimer

document.addEventListener("touchstart", function(){

 pressTimer = setTimeout(stopDetection,1500)

})

document.addEventListener("touchend", function(){

 clearTimeout(pressTimer)

})

// DOUBLE TAP TO START
let lastTap = 0

document.addEventListener("touchend", function(){

 const now = new Date().getTime()
 const tapGap = now - lastTap

 if(tapGap < 300 && tapGap > 0){

  startCamera()

 }

 lastTap = now

})