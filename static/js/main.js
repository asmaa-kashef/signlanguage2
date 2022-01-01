
  let video = document.querySelector("#videoElement");
  let canvas = document.querySelector("#canvasElement");
  let ctx = canvas.getContext('2d');
  photo = document.getElementById('photo');
  let camera_button = document.querySelector("#start-camera");
  let start_button = document.querySelector("#start-record");
  let stop_button = document.querySelector("#stop-record");
  let download_link = document.querySelector("#download-video");
  var playButton = document.querySelector('button#play');
  var recordedVideo = document.querySelector('video#recorded');
  var localMediaStream = null;
  let media_recorder = null;
  let blobs_recorded = [];
  let namespace = "/test";
  var stream =null;

  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

  function sendSnapshot() {
    if (!localMediaStream) {
      return;
    }

    ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight, 0, 0, 300, 150);

    let dataURL = canvas.toDataURL('image/jpeg');
    socket.emit('input image', dataURL);

    socket.emit('output image')

    var img = new Image();
    socket.on('out-image-event',function(data){


    img.src = dataURL//data.image_data
    photo.setAttribute('src', data.image_data);

    });


  }

  socket.on('connect', function() {
    console.log('Connected!');
  });

  var constraints = {
    video: {
      width: { min: 640 },
      height: { min: 480 }
    }
  };
 
 
camera_button.addEventListener('click', async function() {
 camera_stream=navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
    video.srcObject = stream;
    localMediaStream = stream;
    setInterval(function () {
      sendSnapshot();
    }, 50);
   
  }).catch(function(error) {
    console.log(error);
  });
 
});

 start_button.addEventListener('click', function() {
  alert(video.srcObject) 
    // set MIME type of recording as video/webm
    media_recorder = new MediaRecorder(video.srcObject, { mimeType: 'video/webm' });
    
    // event : new recorded video blob available 
    media_recorder.addEventListener('dataavailable', function(e) {
    blobs_recorded.push(e.data);
    });

    // event : recording stopped & all blobs sent
  media_recorder.addEventListener('stop', function() {
      // create local object URL from the recorded video blobs
      let video_local = URL.createObjectURL(new Blob(blobs_recorded, { type: 'video/webm' }));
      download_link.href = video_local;
    });

    // start recording with each recorded blob having 1 second video
    media_recorder.start(1000);
});

stop_button.addEventListener('click', function() {
  media_recorder.stop(); 
});

function play() {
  var type = (blobs_recorded[0] || {}).type;
  var superBuffer = new Blob(blobs_recorded, {type});
  recordedVideo.src = window.URL.createObjectURL(superBuffer);
}
playButton.onclick = play;