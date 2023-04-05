window.onload = () => {
    createCameraBtn.onclick = createCamera
}

async function createCamera(event) {

    if (!create_camera.reportValidity()){
        console.log("Error in form")
        return
      }
    
    let response = await fetch('/api/createCamera', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'url': url.value, 'direction': direction.value, 'line_place': line_place.value,
            'line_width': line_width.value, 'model': model.value
        })
    });

    if (response.ok) {
        data = await response.json()
        if (data['success'] == true) {
            window.location.replace("/cameras");
        } else {
        block = `<div class="mb-3"><div class="alert alert-warning alert-dismissible fade show" role="alert">
        ${data['message']}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>
      </div>`
        block_last.insertAdjacentHTML("afterend", block);
        }
    } 

}
