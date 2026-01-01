const API_URL = window.ENV.API_URL

document.addEventListener('DOMContentLoaded', async function() {
    const res = await fetch(API_URL + '/users/check_session', {
        credentials: "include"
    })

    if (!res.ok){
        return
    }

    const data = await res.json()
    console.log(data)

    // if (data.verified === true) {
    //     showLogoutButton()
    // }

    if (data.verified === true) {
        window.location.href = "/chat"
    }
})


const showLogoutButton = () => {
    const logoutDiv = document.getElementById('logout-div')
    const button = document.createElement('button')
    button.addEventListener("click", logout)
    button.textContent = "Logout"
    logoutDiv.append(button)
}

async function logout() {
    const res = await fetch(API_URL + '/users/logout', {
        method: "POST",
        credentials: "include"
    })

    if (!res.ok) return

    const data = await res.json()

    console.log(data)
}

async function authenticate(type) {
    const email = document.getElementById("email").value
    const password = document.getElementById("password").value

    if (!email || !password) {
        console.error("invalid " + type + " details")
        return
    }

    const res = await fetch(API_URL + '/users/' + type, {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password })
    }).catch(err => {
        console.error("Error: ", err)
    })

    const data = await res.json()

    console.log(data)

    if (data.verified === true) {
        window.location.href = "/chat"
    }
}