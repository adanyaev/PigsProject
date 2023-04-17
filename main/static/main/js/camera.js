async function resetCounter(id) {
    let response = await fetch('/api/resetCounter', {
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
            window.location.reload();
        } else {
            console.log(data['message'])
        }
    }
}

async function deleteCamera(id) {
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
