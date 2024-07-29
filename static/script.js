const dropArea=document.getElementById("drop-area");
const inputFile=document.getElementById("input-file");
const imgView=document.getElementById("img-view");

inputFile.addEventListener("change",uploadImage);

var startButton = document.getElementById('start_button');
var stopButton = document.getElementById('stop_button');
var videoFeed = document.getElementById('video_feed');

startButton.addEventListener('click', function() {
    fetch('/start_video_feed')
        .then(response => {
            if (response.ok) {
                videoFeed.src = '/video_feed';
            }
        });
});

stopButton.addEventListener('click', function() {
    fetch('/stop_video_feed')
        .then(response => {
            if (response.ok) {
                videoFeed.src = '';
            }
        });
});


function uploadImage()
{    
    let imgLink=URL.createObjectURL(inputFile.files[0]);
    imgView.style.backgroundImage=`url(${imgLink})`;
    imgView.textContent="";
    imgView.style.border=0;
}

dropArea.addEventListener("dragover",function(e)
{
    e.preventDefault();    
});

dropArea.addEventListener("drop",function(e)
{
    e.preventDefault();
    inputFile.files=e.dataTransfer.files;
    uploadImage();
      if (e.dataTransfer.items) {
        for (var i = 0; i < e.dataTransfer.items.length; i++) {
            if (e.dataTransfer.items[i].kind === 'file') {
                var file = e.dataTransfer.items[i].getAsFile();
                var formData = new FormData();
                formData.append('image', file);
                var xhr = new XMLHttpRequest();
                xhr.open('POST', '/upload', true);
                xhr.onload = function() {
                    if (xhr.status === 200) {
                        console.log('Image uploaded successfully');
                    } else {
                        console.error('Image upload failed. Status code: ' + xhr.status);
                    }
                };
                xhr.onerror = function() {
                    console.error('Error occurred while sending the request.');
                };
                xhr.send(formData);
            }
        }
    }
});


