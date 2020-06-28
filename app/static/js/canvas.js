// toolbox components
// transparency slider 
transparency_slider = document.getElementById('transparency');
transparency_slider.addEventListener('change', () => {
  const canvas = document.getElementById('canvas');

  if (canvas.getContext) {
    const ctx = canvas.getContext('2d');
    ctx.globalAlpha = transparency_slider.value;
}
}
)

// color input
color_selector = document.getElementById('color');
color_selector.addEventListener('change', () => {
  const canvas = document.getElementById('canvas');

  if (canvas.getContext) {
    const ctx = canvas.getContext('2d');
    ctx.strokeStyle = color.value;
}
})

// line thickness slider
line_thickness_slider = document.getElementById('line-thickness');
line_thickness_slider.addEventListener('change', () => {
  const canvas = document.getElementById('canvas');

  if (canvas.getContext) {
    const ctx = canvas.getContext('2d');
    ctx.lineWidth = line_thickness_slider.value;
}
}
)

// line cap
line_cap_selector = document.getElementById('line-cap');
line_cap_selector.addEventListener('change', () => {
  const canvas = document.getElementById('canvas');

  if (canvas.getContext) {
    const ctx = canvas.getContext('2d');
    ctx.lineCap = line_cap_selector.value;
}
}
)


// ******************************************//

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

function resizeCanvasSet() {
  // resize height and width of canvas-set div
  const canvasSet = document.querySelector('#canvas-set');
  canvasSet.style.width = window.innerWidth + 'px';
  canvasSet.style.height = window.innerHeight + 'px';

  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');

  // reset the size of canvas in memory if canvas increased in dimension
  if (canvas.height > inMemCanvas.height && canvas.width > inMemCanvas.width) {
    inMemCanvas.height = canvas.height;
    inMemCanvas.width = canvas.width;
  }
  
  // save to inMem canvas
  inMemCtx.drawImage(canvas,0,0);

  // set canvas dimensions to that of canvasWrapper
  const canvasWrapper = document.getElementById('canvas-wrapper');
  canvas.height = window.innerHeight;
  canvas.width = canvasWrapper.offsetWidth;

  // redraw, using inMem canvas contents
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
resizeCanvasSet();
window.addEventListener('load',userDraw);
window.addEventListener('resize',resizeCanvasSet);