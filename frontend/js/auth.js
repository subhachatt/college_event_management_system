/**
 * ==========================================================================
 * AUTHENTICATION MODULE (LOGIN, REGISTER, DEMO ACCOUNTS, ROUTE GUARDS)
 * ==========================================================================
 */

// Route Guard to protect pages based on role
function requireAuth(allowedRole = null) {
  const user = getUser();
  const token = getToken();

  if (!token || !user) {
    showToast("Access Restricted", "Please log in to continue.", "warning");
    window.location.href = `login.html?redirect=${encodeURIComponent(window.location.pathname)}`;
    return false;
  }

  if (allowedRole && user.role !== allowedRole) {
    showToast("Access Denied", `This area is restricted to ${allowedRole.toLowerCase()}s.`, "error");
    if (user.role === "ADMIN") {
      window.location.href = "admin-dashboard.html";
    } else {
      window.location.href = "dashboard.html";
    }
    return false;
  }

  return true;
}

// Redirect if already logged in (for login.html / register.html)
function redirectIfAuthenticated() {
  const user = getUser();
  if (user) {
    if (user.role === "ADMIN") {
      window.location.href = "admin-dashboard.html";
    } else {
      window.location.href = "dashboard.html";
    }
  }
}

// Quick Demo Login Helper
function fillDemoCredentials(role, email, password) {
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");

  if (emailInput && passwordInput) {
    emailInput.value = email;
    passwordInput.value = password;
    showToast("Credentials Loaded", `Filled demo credentials for ${role}.`, "info", 2000);
  }
}

// Handle Student Registration Form
async function handleRegister(event) {
  event.preventDefault();
  const form = event.target;
  const submitBtn = form.querySelector("button[type='submit']");

  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const studentId = document.getElementById("student_id").value.trim();
  const department = document.getElementById("department").value;

  if (!name || !email || !password || !department) {
    showToast("Validation Error", "Please fill in all required fields.", "error");
    return;
  }

  if (password.length < 6) {
    showToast("Weak Password", "Password must be at least 6 characters.", "warning");
    return;
  }

  submitBtn.disabled = true;
  submitBtn.innerText = "Creating Account...";

  try {
    const data = await api.post("/api/auth/register", {
      name,
      email,
      password,
      student_id: studentId || null,
      department
    });

    setToken(data.access_token);
    setUser(data.user);

    showToast("Welcome!", "Account created successfully. Redirecting...", "success");
    setTimeout(() => {
      window.location.href = "dashboard.html";
    }, 1000);
  } catch (error) {
    showToast("Registration Failed", error.message, "error");
    submitBtn.disabled = false;
    submitBtn.innerText = "Create Account";
  }
}

// Handle Login Form
async function handleLogin(event) {
  event.preventDefault();
  const form = event.target;
  const submitBtn = form.querySelector("button[type='submit']");

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  if (!email || !password) {
    showToast("Validation Error", "Please enter your email and password.", "error");
    return;
  }

  submitBtn.disabled = true;
  submitBtn.innerText = "Signing in...";

  try {
    const data = await api.post("/api/auth/login", {
      email,
      password
    });

    setToken(data.access_token);
    setUser(data.user);

    showToast("Welcome Back!", `Logged in as ${data.user.name}`, "success");

    setTimeout(() => {
      // Check query parameter redirect
      const urlParams = new URLSearchParams(window.location.search);
      const redirect = urlParams.get("redirect");

      if (redirect && !redirect.includes("login.html") && !redirect.includes("register.html")) {
        window.location.href = redirect;
      } else if (data.user.role === "ADMIN") {
        window.location.href = "admin-dashboard.html";
      } else {
        window.location.href = "dashboard.html";
      }
    }, 800);
  } catch (error) {
    showToast("Login Failed", error.message, "error");
    submitBtn.disabled = false;
    submitBtn.innerText = "Sign In";
  }
}
