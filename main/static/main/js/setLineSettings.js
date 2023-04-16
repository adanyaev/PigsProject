
// window.onload = () => {
//     var ctx = sampleImage.getContext('2d');
//     var img = new Image();      // Новый объект
//     img.onload = function() { // Событие которое будет исполнено в момент когда изображение будет загружено
//         ctx.drawImage(img, 0, 0, sampleImage.width, sampleImage.height);
//         ctx.strokeStyle = "orange";
//         ctx.strokeRect(0, 300, 640, 40)
//     }
//     img.src = '/media/test.png';    // Путь к изображению
//     moveDirection.oninput = updateImage
//     linePlace.oninput = updateImage
//     lineWidth.oninput = updateImage

// }


window.onload = () => {
    var ctx = sampleImage.getContext('2d');
    ctx.strokeStyle = "orange";
    let lwid = parseInt(lineWidth.value)
    let lplace = parseFloat(linePlace.value)
    ctx.strokeRect(0, sampleImage.height*lplace-lwid/2, sampleImage.width, lwid)
    moveDirection.oninput = updateImage
    linePlace.oninput = updateImage
    lineWidth.oninput = updateImage
    submitButt.onclick = setLineSettings
    arrow.style.transform = 'rotate(180deg)';

}


async function setLineSettings(event) {
    let lwid = parseInt(lineWidth.value)
    let lplace = parseFloat(linePlace.value)
    let direct = moveDirection.value
    let response = await fetch('/api/setLineSettings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'lineWidth': lwid, 'linePlace': lplace, 'lineDirection': direct, 'camId': submitButt.dataset.id})
    });

    if (response.ok) {
        data = await response.json()
        if (data['success'] == true) {
            window.location.replace(`/camera/${submitButt.dataset.id}`);
        } else {
        block = `<div class="mb-3"><div class="alert alert-warning alert-dismissible fade show" role="alert">
        ${data['message']}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>
      </div>`
        submitButt.insertAdjacentHTML("afterend", block);
        }
    } 

}




function updateImage(){
    lineWidthValueLabel.textContent = lineWidth.value
    linePlaceValueLabel.textContent = linePlace.value
    let lwid = parseInt(lineWidth.value)
    let lplace = parseFloat(linePlace.value)
    let direct = moveDirection.value
    var ctx = sampleImage.getContext('2d');
    ctx.strokeStyle = "orange";
    ctx.clearRect(0, 0, sampleImage.width, sampleImage.height);
    if (direct == 1){
        arrow.style.transform = 'rotate(180deg)';
    } else if (direct == 2){
        arrow.style.transform = 'rotate(0deg)';
    } else if (direct == 3){
        arrow.style.transform = 'rotate(90deg)';
    } else if (direct == 4){
        arrow.style.transform = 'rotate(270deg)';
    }
    if (direct == 1 || direct == 2){
        ctx.strokeRect(0, sampleImage.height*lplace-lwid/2, sampleImage.width, lwid)
    } else {
        ctx.strokeRect(sampleImage.width*lplace-lwid/2, 0, lwid, sampleImage.height)
    }

}


