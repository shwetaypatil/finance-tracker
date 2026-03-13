async function loginUser() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const res = await fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();

  if (data.success) {
    window.location.href = "/dashboard";
  } else {
    alert(data.msg);
  }
}

async function signupUser() {
  const username = document.getElementById("username").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const confirm = document.getElementById("confirm").value;

  const res = await fetch("/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password, confirm })
  });

  const data = await res.json();

  if (data.success) {
    alert("Signup successful");
    window.location.href = "/";
  } else {
    alert(data.msg);
  }
}
