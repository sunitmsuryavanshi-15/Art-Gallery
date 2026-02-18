function checkUsername() {
    const username = document.getElementById("username").value;
    const msg = document.getElementById("username-msg");

    if (username.length === 0) {
        msg.textContent = "";
        return;
    }

    if (!/[A-Za-z]/.test(username)) {
        msg.textContent = "❌ At least one letter required";
        msg.style.color = "red";
    }
    else if (!/\d/.test(username)) {
        msg.textContent = "❌ At least one number required";
        msg.style.color = "red";
    }
    else if (!/[@._-]/.test(username)) {
        msg.textContent = "❌ Use at least one symbol (@ . _ -)";
        msg.style.color = "red";
    }
    else if (username.length < 6) {
        msg.textContent = "❌ Minimum 6 characters required";
        msg.style.color = "red";
    }
    else {
        msg.textContent = "✅ Username looks good";
        msg.style.color = "green";
    }
}
