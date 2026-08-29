/**
 * ==========================================================================
 * MY REGISTRATIONS MODULE (TABBED LIST, TICKET CARDS, CANCEL REGISTRATION)
 * ==========================================================================
 */

let allRegistrations = [];
let activeTab = "upcoming";

async function loadMyRegistrations() {
  const container = document.getElementById("registrations-list");
  if (!container) return;

  container.innerHTML = `<div class="spinner"></div>`;

  try {
    const data = await api.get("/api/my-registrations");
    allRegistrations = data;
    renderRegistrationsList();
  } catch (error) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">⚠️</div>
        <div class="empty-state-title">Failed to load registrations</div>
        <p>${error.message}</p>
        <button class="btn btn-primary btn-sm" onclick="loadMyRegistrations()" style="margin-top: 1rem;">Retry</button>
      </div>
    `;
  }
}

function setRegistrationTab(tabName, buttonElement) {
  activeTab = tabName;

  document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
  if (buttonElement) {
    buttonElement.classList.add("active");
  }

  renderRegistrationsList();
}

function renderRegistrationsList() {
  const container = document.getElementById("registrations-list");
  if (!container) return;

  // Filter based on active tab
  let filtered = [];
  if (activeTab === "upcoming") {
    filtered = allRegistrations.filter(r => r.status === "CONFIRMED" && !r.event.is_past);
  } else if (activeTab === "completed") {
    filtered = allRegistrations.filter(r => r.status === "CONFIRMED" && r.event.is_past);
  } else if (activeTab === "cancelled") {
    filtered = allRegistrations.filter(r => r.status === "CANCELLED");
  } else {
    filtered = allRegistrations;
  }

  // Update tab counters
  const upcomingCount = allRegistrations.filter(r => r.status === "CONFIRMED" && !r.event.is_past).length;
  const completedCount = allRegistrations.filter(r => r.status === "CONFIRMED" && r.event.is_past).length;
  const cancelledCount = allRegistrations.filter(r => r.status === "CANCELLED").length;

  const countUp = document.getElementById("tab-count-upcoming");
  const countComp = document.getElementById("tab-count-completed");
  const countCanc = document.getElementById("tab-count-cancelled");

  if (countUp) countUp.innerText = `(${upcomingCount})`;
  if (countComp) countComp.innerText = `(${completedCount})`;
  if (countCanc) countCanc.innerText = `(${cancelledCount})`;

  if (filtered.length === 0) {
    let emptyTitle = "No registrations found";
    let emptyDesc = "You haven't registered for any upcoming events yet.";
    if (activeTab === "completed") emptyDesc = "No completed events in your history yet.";
    if (activeTab === "cancelled") emptyDesc = "You have no cancelled registrations.";

    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🎟️</div>
        <div class="empty-state-title">${emptyTitle}</div>
        <p>${emptyDesc}</p>
        <a href="events.html" class="btn btn-primary btn-sm" style="margin-top: 1rem;">Browse College Events</a>
      </div>
    `;
    return;
  }

  const defaultImg = "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop&q=80";

  const cardsHtml = filtered.map(reg => {
    const event = reg.event;
    const isCancelled = reg.status === "CANCELLED";
    const isPast = event.is_past;

    let statusBadge = `<span class="badge badge-success">Confirmed</span>`;
    if (isCancelled) {
      statusBadge = `<span class="badge badge-danger">Cancelled</span>`;
    } else if (isPast) {
      statusBadge = `<span class="badge badge-neutral">Completed</span>`;
    }

    const regDateFormatted = new Date(reg.registration_date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric"
    });

    return `
      <div class="ticket-card">
        <img src="${event.image_url || defaultImg}" alt="${event.title}" class="ticket-card-img" onerror="this.src='${defaultImg}'">
        
        <div class="ticket-card-content">
          <div style="display: flex; gap: 0.5rem; margin-bottom: 0.35rem;">
            <span class="badge ${getCategoryBadgeClass(event.category)}">${event.category}</span>
            ${statusBadge}
          </div>

          <h3 class="ticket-card-title">${event.title}</h3>
          
          <div class="ticket-card-meta">
            <div>📅 <strong>${formatDate(event.event_date)}</strong></div>
            <div>🕒 ${formatTime(event.start_time)} - ${formatTime(event.end_time)}</div>
            <div>📍 ${event.venue}</div>
          </div>

          <div style="font-size: 0.8rem; color: var(--text-subtle); margin-top: 0.25rem;">
            Registered on: ${regDateFormatted} • Pass ID: #REG-${reg.id.toString().padStart(4, '0')}
          </div>
        </div>

        <div class="ticket-card-actions">
          <a href="event-details.html?id=${event.id}" class="btn btn-outline-primary btn-sm btn-full">
            View Event
          </a>
          ${(!isCancelled && !isPast) ? `
            <button class="btn btn-secondary btn-sm btn-full" style="color: var(--danger);" onclick="cancelRegistrationFromList(${event.id})">
              Cancel Pass
            </button>
          ` : ''}
        </div>
      </div>
    `;
  }).join("");

  container.innerHTML = cardsHtml;
}

async function cancelRegistrationFromList(eventId) {
  if (!confirm("Are you sure you want to cancel this event registration? Your seat will be made available to other students.")) {
    return;
  }

  try {
    await api.delete(`/api/events/${eventId}/register`);
    showToast("Registration Cancelled", "Your booking has been cancelled.", "info");
    await loadMyRegistrations();
  } catch (error) {
    showToast("Cancellation Error", error.message, "error");
  }
}
