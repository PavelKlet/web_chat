async function logout() {
    await fetch('/auth/jwt/logout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    });

    window.location.href = '/login/';
}
