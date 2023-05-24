window.onload = () => {
    loginButt.onclick = loginUser
}

async function loginUser(event) {
    
    let response = await fetch('/restapi/login_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'username': username.value, 'password': password.value, 'rememberMe': rememberMe.checked})
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
        remember.insertAdjacentHTML("afterend", block);
        }
    } 

}
