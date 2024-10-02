document.getElementById('loadButton').addEventListener('click', function() {
    const urlInput = document.getElementById('urlInput').value;
    const video = document.getElementById('videoPlayer');

    if (Hls.isSupported()) {
        const hls = new Hls();

        hls.loadSource(urlInput);
        hls.attachMedia(video);

        hls.on(Hls.Events.MANIFEST_PARSED, function() {
            video.play();
        });

        hls.on(Hls.Events.ERROR, function(event, data) {
            if (data.fatal) {
                switch (data.fatal) {
                    case Hls.ErrorTypes.NETWORK_ERROR:
                        alert("A network error occurred.");
                        break;
                    case Hls.ErrorTypes.MEDIA_ERROR:
                        alert("A media error occurred.");
                        break;
                    case Hls.ErrorTypes.OTHER_ERROR:
                        alert("An error occurred.");
                        break;
                    default:
                        break;
                }
            }
        });
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = urlInput;
        video.addEventListener('loadedmetadata', function() {
            video.play();
        });
    } else {
        alert("Your browser does not support M3U8.");
    }
});

// Handle playback speed change
document.getElementById('speedControl').addEventListener('change', function() {
    const video = document.getElementById('videoPlayer');
    video.playbackRate = parseFloat(this.value);
});

// Toggle Picture-in-Picture mode
document.getElementById('pipButton').addEventListener('click', function() {
    const video = document.getElementById('videoPlayer');
    if (video !== document.pictureInPictureElement) {
        video.requestPictureInPicture().catch(err => {
            console.error(err);
        });
    } else {
        document.exitPictureInPicture();
    }
});

// Toggle fullscreen mode
document.getElementById('fullscreenButton').addEventListener('click', function() {
    const video = document.getElementById('videoPlayer');
    if (video.requestFullscreen) {
        video.requestFullscreen();
    } else if (video.webkitRequestFullscreen) { // Safari
        video.webkitRequestFullscreen();
    } else if (video.msRequestFullscreen) { // IE11
        video.msRequestFullscreen();
    }
});

// Load subtitles
document.getElementById('loadSubtitleButton').addEventListener('click', function() {
    const subtitleInput = document.getElementById('subtitleInput').value;
    const video = document.getElementById('videoPlayer');
    
    if (subtitleInput) {
        const track = document.createElement('track');
        track.kind = 'subtitles';
        track.src = subtitleInput;
        track.srclang = 'en'; // Change this to the appropriate language code
        track.label = 'English'; // Change this to the appropriate label
        video.appendChild(track);
    } else {
        alert("Please enter a valid subtitle URL.");
    }
});

// Display thumbnail on hover
document.querySelectorAll('.thumbnail').forEach(thumbnail => {
    thumbnail.addEventListener('mouseenter', function() {
        const video = document.getElementById('videoPlayer');
        video.poster = this.dataset.url; // Change video poster to the thumbnail image
    });

    thumbnail.addEventListener('mouseleave', function() {
        const video = document.getElementById('videoPlayer');
        video.poster = ''; // Remove poster when mouse leaves
    });
});
