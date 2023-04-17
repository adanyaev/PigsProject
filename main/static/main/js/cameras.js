window.onload = () => {
    createCameraBtn.onclick = createCamera
    saveCameraBtn.onclick = saveCamera
}

function clearModal()
{
    document.getElementById('saveCameraBtn').hidden = true
    document.getElementById('createCameraBtn').hidden = false

    document.getElementById('url').setAttribute('value', "")
    document.getElementById('model').setAttribute('value', "")
}

async function editCamera(id)
{
    let element = document.getElementById("camera_" + id)
    if (!element)
        return
        
    document.getElementById('saveCameraBtn').hidden = false;
    document.getElementById('createCameraBtn').hidden = true;
    document.getElementById('url').setAttribute('value', element.getAttribute("data-url"))
    document.getElementById('line_place').setAttribute('value', +(element.getAttribute("data-line_place").replace(',', '.')))
    document.getElementById('line_width').setAttribute('value', +(element.getAttribute("data-line_width").replace(',', '.')))
    document.getElementById('model').setAttribute('value', element.getAttribute("data-model"))
    document.getElementById('direction').value = element.getAttribute("data-direction")
    document.getElementById('saveCameraBtn').setAttribute("data-id", id)
}

async function saveCamera()
{
    if (!create_camera.reportValidity()){
        console.log("Error in form")
        return
    }

    let id = saveCameraBtn.getAttribute("data-id")
    let response = await fetch('/api/editCamera', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'id': id, 'url': url.value, 'direction': direction.value, 'line_place': line_place.value,
        'line_width': line_width.value, 'model': model.value})
    });

    if (response.ok)
    {
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

async function deleteCamera(id) {
    let element = document.getElementById("camera_" + id)
    if (!element)
        return
    
    let response = await fetch('/api/deleteCamera', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'id': id})
    });

    if (response.ok)
    {
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

async function createCamera(event) {

    if (!create_camera.reportValidity()){
        console.log("Error in form")
        return
      }
    submitSpinner.hidden = false
    let response = await fetch('/api/createCamera', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'name': camName.value, 'url': url.value, 'model': model.value
        })
    });
    submitSpinner.hidden = true
    if (response.ok) {
        data = await response.json()
        if (data['success'] == true) {
            let id = data['cam_id']
            window.location.replace(`/setLineSettings/${id}`);
        } else {
        block = `<div class="mb-3"><div class="alert alert-warning alert-dismissible fade show" role="alert">
        ${data['message']}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>
      </div>`
        block_last.insertAdjacentHTML("afterend", block);
        }
    } 

}
