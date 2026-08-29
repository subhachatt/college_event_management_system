/**
 * ==========================================================================
 * COLLEGE EVENT MANAGEMENT SYSTEM - CENTRAL API CLIENT & UTILITIES
 * ==========================================================================
 */

const API_BASE_URL = "http://127.0.0.1:8000";

// Auth Storage Keys
const TOKEN_KEY = "college_events_jwt";
const USER_KEY = "college_events_user";

// Token & Session Helpers
function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

function getUser() {
  const userStr = localStorage.getItem(USER_KEY);
  try {
    return userStr ? JSON.parse(userStr) : null;
  } catch (e) {
    return null;
  }
}

function setUser(user) {
  if (user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  } else {
    localStorage.removeItem(USER_KEY);
  }
}

function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function isAuthenticated() {
  return !!getToken();
}

function isAdmin() {
  const user = getUser();
  return user && user.role === "ADMIN";
}

function isStudent() {
  const user = getUser();
  return user && user.role === "STUDENT";
}

// Toast Notifications System
function showToast(title, message, type = "info", duration = 4000) {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    document.body.appendChild(container);
  }

  const icons = {
    success: "✓",
    error: "✕",
    warning: "⚠",
    info: "ℹ"
  };

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <div class="toast-icon">${icons[type] || "ℹ"}</div>
    <div class="toast-content">
      <div class="toast-title">${title}</div>
      <div class="toast-msg">${message}</div>
    </div>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// Central Request Method
async function apiRequest(endpoint, options = {}) {
  const url = endpoint.startsWith("http") ? endpoint : `${API_BASE_URL}${endpoint}`;
  const token = getToken();

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers
  };

  if (options.body && typeof options.body === "object") {
    config.body = JSON.stringify(options.body);
  }

  try {
    const response = await fetch(url, config);

    // Handle 401 Unauthorized
    if (response.status === 401) {
      if (token) {
        showToast("Session Expired", "Please log in again.", "warning");
        clearAuth();
        setTimeout(() => {
          window.location.href = "login.html";
        }, 1200);
      }
      throw new Error("Authentication required");
    }

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMsg = (data && data.detail) 
        ? (typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail))
        : `Request failed with status ${response.status}`;
      throw new Error(errorMsg);
    }

    return data;
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

// REST Helper methods
const api = {
  get: (endpoint, params = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== "") {
        query.append(key, val);
      }
    });
    const queryString = query.toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    return apiRequest(url, { method: "GET" });
  },

  post: (endpoint, body) => apiRequest(endpoint, { method: "POST", body }),
  put: (endpoint, body) => apiRequest(endpoint, { method: "PUT", body }),
  delete: (endpoint) => apiRequest(endpoint, { method: "DELETE" })
};

// Date & String Formatting Helpers
function formatDate(dateStr) {
  if (!dateStr) return "N/A";
  const date = new Date(dateStr + "T00:00:00");
  return date.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric"
  });
}

function formatTime(timeStr) {
  if (!timeStr) return "";
  const [hours, minutes] = timeStr.split(":");
  const hourNum = parseInt(hours, 10);
  const ampm = hourNum >= 12 ? "PM" : "AM";
  const formattedHour = hourNum % 12 || 12;
  return `${formattedHour}:${minutes} ${ampm}`;
}

function getCategoryBadgeClass(category) {
  const cat = (category || "").toLowerCase();
  switch (cat) {
    case "technical": return "badge-category-technical";
    case "hackathon": return "badge-category-hackathon";
    case "workshop": return "badge-category-workshop";
    case "cultural": return "badge-category-cultural";
    case "sports": return "badge-category-sports";
    case "seminar": return "badge-category-seminar";
    case "competition": return "badge-category-competition";
    default: return "badge-category-other";
  }
}

// Global Nav bar renderer
function renderNavbar() {
  const user = getUser();
  const navLinks = document.getElementById("nav-links");
  const navActions = document.getElementById("nav-actions");

  if (!navLinks || !navActions) return;

  const currentPath = window.location.pathname.split("/").pop() || "index.html";

  // Common links
  let linksHtml = `
    <li><a href="index.html" class="nav-link ${currentPath === 'index.html' ? 'active' : ''}">Home</a></li>
    <li><a href="events.html" class="nav-link ${currentPath === 'events.html' ? 'active' : ''}">Explore Events</a></li>
  `;

  if (user) {
    if (user.role === "ADMIN") {
      linksHtml += `
        <li><a href="admin-dashboard.html" class="nav-link ${currentPath.includes('admin') || currentPath === 'create-event.html' || currentPath === 'edit-event.html' || currentPath === 'participants.html' ? 'active' : ''}">Admin Portal</a></li>
      `;
    } else {
      linksHtml += `
        <li><a href="dashboard.html" class="nav-link ${currentPath === 'dashboard.html' ? 'active' : ''}">Dashboard</a></li>
        <li><a href="my-registrations.html" class="nav-link ${currentPath === 'my-registrations.html' ? 'active' : ''}">My Registrations</a></li>
      `;
    }
  }

  navLinks.innerHTML = linksHtml;

  // Actions / Profile
  if (user) {
    navActions.innerHTML = `
      <div style="display: flex; align-items: center; gap: 0.75rem;">
        <a href="profile.html" class="btn btn-secondary btn-sm" title="View Profile">
          <span>👤</span>
          <span>${user.name.split(" ")[0]}</span>
          <span class="badge ${user.role === 'ADMIN' ? 'badge-purple' : 'badge-primary'}">${user.role}</span>
        </a>
        <button id="logout-btn" class="btn btn-secondary btn-sm" onclick="handleLogout()">
          Logout
        </button>
      </div>
    `;
  } else {
    navActions.innerHTML = `
      <a href="login.html" class="btn btn-secondary btn-sm">Log In</a>
      <a href="register.html" class="btn btn-primary btn-sm">Register</a>
    `;
  }

  // Mobile menu toggle
  const mobileToggle = document.getElementById("mobile-menu-toggle");
  if (mobileToggle) {
    mobileToggle.onclick = () => {
      navLinks.classList.toggle("active");
    };
  }
}

function handleLogout() {
  clearAuth();
  showToast("Logged Out", "You have been signed out successfully.", "info");
  setTimeout(() => {
    window.location.href = "login.html";
  }, 500);
}

// Initialize common page behaviors
document.addEventListener("DOMContentLoaded", () => {
  renderNavbar();
});
