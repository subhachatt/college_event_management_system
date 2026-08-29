/**
 * ==========================================================================
 * EVENTS MODULE (CATALOG, DISCOVERY, SEARCH/FILTER, DETAILS & REGISTRATION)
 * ==========================================================================
 */

let allEventsCache = [];
let currentCategoryFilter = "All";

// Fetch and render events on catalog page
async function loadEventsCatalog() {
  const container = document.getElementById("events-grid");
  if (!container) return;

  container.innerHTML = `<div class="spinner"></div>`;

  try {
    const search = document.getElementById("search-input") ? document.getElementById("search-input").value.trim() : "";
    const dateFilter = document.getElementById("date-filter") ? document.getElementById("date-filter").value : "";
    const sortBy = document.getElementById("sort-select") ? document.getElementById("sort-select").value : "date_asc";

    const params = {
      sort_by: sortBy
    };
    if (search) params.search = search;
    if (currentCategoryFilter && currentCategoryFilter !== "All") params.category = currentCategoryFilter;
    if (dateFilter) params.date_filter = dateFilter;

    const events = await api.get("/api/events", params);
    allEventsCache = events;

    renderEventsGrid(events, container);
  } catch (error) {
    container.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <div class="empty-state-icon">⚠️</div>
        <div class="empty-state-title">Failed to load events</div>
        <p>${error.message}</p>
        <button class="btn btn-primary btn-sm" onclick="loadEventsCatalog()" style="margin-top: 1rem;">Retry</button>
      </div>
    `;
  }
}

// Render event cards into grid
function renderEventsGrid(events, container) {
  if (!events || events.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <div class="empty-state-icon">🔍</div>
        <div class="empty-state-title">No events found</div>
        <p>Try adjusting your search query, category filter, or date range.</p>
      </div>
    `;
    return;
  }

  const cardsHtml = events.map(event => {
    const percentFilled = Math.min(100, Math.round((event.registered_count / event.capacity) * 100));
    let progressColorClass = "";
    if (percentFilled >= 90) progressColorClass = "danger";
    else if (percentFilled >= 70) progressColorClass = "warning";

    const defaultImg = "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop&q=80";
    const imgUrl = event.image_url || defaultImg;

    return `
      <div class="event-card">
        <div class="event-card-img-wrapper">
          <img src="${imgUrl}" alt="${event.title}" class="event-card-img" onerror="this.src='${defaultImg}'" loading="lazy">
          <span class="badge ${getCategoryBadgeClass(event.category)} event-card-category">${event.category}</span>
          <div class="event-card-date-badge">
            <span>📅</span>
            <span>${formatDate(event.event_date)}</span>
          </div>
        </div>
        <div class="event-card-body">
          <h3 class="event-card-title">${event.title}</h3>
          <p class="event-card-desc">${event.description}</p>
          
          <div class="event-card-meta">
            <div class="event-card-meta-item">
              <span>🕒</span>
              <span>${formatTime(event.start_time)} - ${formatTime(event.end_time)}</span>
            </div>
            <div class="event-card-meta-item">
              <span>📍</span>
              <span>${event.venue}</span>
            </div>
          </div>

          <div class="capacity-wrapper">
            <div class="capacity-header">
              <span>Capacity</span>
              <span>${event.registered_count} / ${event.capacity} seats</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill ${progressColorClass}" style="width: ${percentFilled}%;"></div>
            </div>
          </div>

          <div class="event-card-footer">
            <div>
              ${event.is_full ? '<span class="badge badge-danger">Event Full</span>' : (event.is_past ? '<span class="badge badge-neutral">Completed</span>' : `<span class="badge badge-success">${event.available_seats} seats left</span>`)}
            </div>
            <a href="event-details.html?id=${event.id}" class="btn btn-outline-primary btn-sm">
              View Details →
            </a>
          </div>
        </div>
      </div>
    `;
  }).join("");

  container.innerHTML = cardsHtml;
}

// Category filter chip click handler
function setCategoryFilter(category, chipElement) {
  currentCategoryFilter = category;

  // Update active chip UI
  document.querySelectorAll(".category-chip").forEach(chip => chip.classList.remove("active"));
  if (chipElement) {
    chipElement.classList.add("active");
  }

  loadEventsCatalog();
}

// Setup search & filter listeners
function setupEventFilterListeners() {
  const searchInput = document.getElementById("search-input");
  const dateFilter = document.getElementById("date-filter");
  const sortSelect = document.getElementById("sort-select");

  let debounceTimer;
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        loadEventsCatalog();
      }, 300);
    });
  }

  if (dateFilter) {
    dateFilter.addEventListener("change", () => loadEventsCatalog());
  }

  if (sortSelect) {
    sortSelect.addEventListener("change", () => loadEventsCatalog());
  }
}

// ==========================================================================
// EVENT DETAILS PAGE LOGIC
// ==========================================================================
let currentEventDetails = null;

async function loadEventDetailsPage() {
  const urlParams = new URLSearchParams(window.location.search);
  const eventId = urlParams.get("id");

  if (!eventId) {
    showToast("Error", "No event specified", "error");
    window.location.href = "events.html";
    return;
  }

  const container = document.getElementById("event-details-container");
  if (!container) return;

  container.innerHTML = `<div class="spinner"></div>`;

  try {
    const event = await api.get(`/api/events/${eventId}`);
    currentEventDetails = event;
    renderEventDetails(event, container);
  } catch (error) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">⚠️</div>
        <div class="empty-state-title">Event not found</div>
        <p>${error.message}</p>
        <a href="events.html" class="btn btn-primary btn-sm" style="margin-top: 1rem;">Back to Events</a>
      </div>
    `;
  }
}

function renderEventDetails(event, container) {
  const user = getUser();
  const isUserStudent = user && user.role === "STUDENT";
  const defaultImg = "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop&q=80";
  const imgUrl = event.image_url || defaultImg;

  const percentFilled = Math.min(100, Math.round((event.registered_count / event.capacity) * 100));

  // Determine Action Button
  let actionButtonHtml = "";

  if (!user) {
    actionButtonHtml = `
      <a href="login.html?redirect=${encodeURIComponent(window.location.href)}" class="btn btn-primary btn-lg btn-full">
        Sign in to Register
      </a>
      <p class="form-text" style="text-align: center; margin-top: 0.5rem;">Only registered college students can join.</p>
    `;
  } else if (user.role === "ADMIN") {
    actionButtonHtml = `
      <div style="display: flex; flex-direction: column; gap: 0.75rem;">
        <a href="participants.html?id=${event.id}" class="btn btn-primary btn-lg btn-full">
          👥 View Participants (${event.registered_count})
        </a>
        <a href="edit-event.html?id=${event.id}" class="btn btn-secondary btn-full">
          ✏️ Edit Event Details
        </a>
      </div>
    `;
  } else if (event.is_registered) {
    actionButtonHtml = `
      <div style="display: flex; flex-direction: column; gap: 0.75rem;">
        <div style="background: var(--success-bg); border: 1px solid var(--success); border-radius: var(--radius-md); padding: 0.85rem; text-align: center; color: #15803d; font-weight: 700;">
          ✓ You are registered for this event!
        </div>
        <button id="cancel-reg-btn" class="btn btn-danger btn-full" onclick="handleEventCancellation(${event.id})">
          Cancel Registration
        </button>
        <a href="my-registrations.html" class="btn btn-secondary btn-full btn-sm">
          View in My Registrations
        </a>
      </div>
    `;
  } else if (event.is_past) {
    actionButtonHtml = `
      <button class="btn btn-secondary btn-lg btn-full disabled" disabled>
        Event Completed
      </button>
    `;
  } else if (event.is_full) {
    actionButtonHtml = `
      <button class="btn btn-danger btn-lg btn-full disabled" disabled>
        Event is Fully Booked
      </button>
    `;
  } else {
    actionButtonHtml = `
      <button id="register-event-btn" class="btn btn-primary btn-lg btn-full" onclick="handleEventRegistration(${event.id})">
        Register Now (Free)
      </button>
    `;
  }

  container.innerHTML = `
    <div class="event-details-layout">
      <div class="event-details-main">
        <div class="event-hero">
          <img src="${imgUrl}" alt="${event.title}" class="event-hero-banner" onerror="this.src='${defaultImg}'">
          <div class="event-hero-content">
            <div class="event-detail-tags">
              <span class="badge ${getCategoryBadgeClass(event.category)}">${event.category}</span>
              ${event.is_full ? '<span class="badge badge-danger">Capacity Full</span>' : '<span class="badge badge-success">Registration Open</span>'}
              ${event.is_past ? '<span class="badge badge-neutral">Past Event</span>' : ''}
            </div>
            <h1>${event.title}</h1>
            <p style="color: var(--text-muted); font-size: 0.95rem; margin-top: 0.5rem;">
              Organized by <strong style="color: var(--text-main);">${event.organizer}</strong>
            </p>
          </div>
        </div>

        <div class="card" style="margin-bottom: 2rem;">
          <div class="card-header">
            <h3>About This Event</h3>
          </div>
          <div class="card-body">
            <div style="white-space: pre-line; line-height: 1.8; color: var(--text-main); font-size: 1rem;">
              ${event.description}
            </div>
          </div>
        </div>
      </div>

      <div class="event-details-sidebar">
        <div class="card">
          <div class="card-header">
            <h3>Event Information</h3>
          </div>
          <div class="card-body">
            <div class="meta-box-list">
              <div class="meta-box-item">
                <div class="meta-box-icon">📅</div>
                <div class="meta-box-text">
                  <h4>Date</h4>
                  <p>${formatDate(event.event_date)}</p>
                </div>
              </div>

              <div class="meta-box-item">
                <div class="meta-box-icon">🕒</div>
                <div class="meta-box-text">
                  <h4>Time</h4>
                  <p>${formatTime(event.start_time)} - ${formatTime(event.end_time)}</p>
                </div>
              </div>

              <div class="meta-box-item">
                <div class="meta-box-icon">📍</div>
                <div class="meta-box-text">
                  <h4>Venue</h4>
                  <p>${event.venue}</p>
                </div>
              </div>

              <div class="meta-box-item">
                <div class="meta-box-icon">👥</div>
                <div class="meta-box-text">
                  <h4>Capacity & Availability</h4>
                  <p>${event.available_seats} remaining of ${event.capacity} total</p>
                </div>
              </div>
            </div>

            <div class="capacity-wrapper" style="margin: 1.5rem 0;">
              <div class="capacity-header">
                <span>Registration Meter</span>
                <span>${percentFilled}% Booked</span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill ${percentFilled >= 90 ? 'danger' : (percentFilled >= 70 ? 'warning' : '')}" style="width: ${percentFilled}%;"></div>
              </div>
            </div>

            <div id="event-action-container">
              ${actionButtonHtml}
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

// Handle Student Registration
async function handleEventRegistration(eventId) {
  const btn = document.getElementById("register-event-btn");
  if (btn) {
    btn.disabled = true;
    btn.innerText = "Registering...";
  }

  try {
    await api.post(`/api/events/${eventId}/register`, {});
    showToast("Success!", "You have been registered for this event.", "success");
    // Reload details to update real-time seat counts & state without full page reload
    await loadEventDetailsPage();
  } catch (error) {
    showToast("Registration Error", error.message, "error");
    if (btn) {
      btn.disabled = false;
      btn.innerText = "Register Now (Free)";
    }
  }
}

// Handle Student Cancellation
async function handleEventCancellation(eventId) {
  if (!confirm("Are you sure you want to cancel your registration for this event?")) {
    return;
  }

  const btn = document.getElementById("cancel-reg-btn");
  if (btn) {
    btn.disabled = true;
    btn.innerText = "Cancelling...";
  }

  try {
    await api.delete(`/api/events/${eventId}/register`);
    showToast("Cancelled", "Your registration has been cancelled.", "info");
    await loadEventDetailsPage();
  } catch (error) {
    showToast("Cancellation Error", error.message, "error");
    if (btn) {
      btn.disabled = false;
      btn.innerText = "Cancel Registration";
    }
  }
}
