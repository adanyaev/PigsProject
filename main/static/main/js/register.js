window.onload = () => {
    regButt.onclick = regUser
}

async function regUser(event) {

    if (!reg.reportValidity()){
        return
      }
    
    let response = await fetch('/api/regUser', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'username': username.value, 'password': password.value, 'email': email.value,
                                'name': nameU.value, 'surname': surname.value
                                })
    });

    if (response.ok) {
        data = await response.json()
        if (data['success'] == true) {
            window.location.replace("/");
        } else {
        block = `<div class="mb-3"><div class="alert alert-warning alert-dismissible fade show" role="alert">
        ${data['message']}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>
      </div>`
        block_last.insertAdjacentHTML("afterend", block);
        }
    } 

}
