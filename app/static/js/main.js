// Make in-memory canvas
var inMemCanvas = document.createElement('canvas');
var inMemCtx = inMemCanvas.getContext('2d');
inMemCanvas.width = window.innerWidth;
inMemCanvas.height = window.innerHeight;

function userDraw() {
  const canvas = document.getElementById('canvas');

  if (canvas.getContext) {
    const ctx = canvas.getContext('2d');
    
    let painting = false;

    // when to start drawing
    function startPosition(e) {
      painting = true;
      ctx.beginPath();
      draw(e);
    }

    // when to stop drawing
    function finishPosition(e) {
      painting = false;
    }

    // between start and stop of drawing
    function draw(e) {
      if (!painting) return;
      ctx.lineWidth=3;
      ctx.lineCap = 'round';

      ctx.lineTo(e.clientX,e.clientY);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(e.clientX,e.clientY);
    }

    // event listeners 
    canvas.addEventListener("mousedown",startPosition);
    canvas.addEventListener("mouseup",finishPosition);
    canvas.addEventListener("mousemove",draw)
  }
}

function resizeCanvas() {
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');

  if (canvas.height > inMemCanvas.height && canvas.width > inMemCanvas.width) {
    inMemCanvas.height = canvas.height;
    inMemCanvas.width = canvas.width;
  }
  
  // save to inMem canvas
  inMemCtx.drawImage(canvas,0,0);

  canvas.height = window.innerHeight;
  canvas.width = window.innerWidth;
  ctx.drawImage(inMemCanvas,0,0);
}

function getBackCanvas(dataURL,ctx) {
  var image = new Image();
  image.src = dataURL;
  image.onload=function() {
    ctx.drawImage(image,0,0);
  }
}

// window event listeners
resizeCanvas();
window.addEventListener('load',userDraw);
window.addEventListener('resize',resizeCanvas);