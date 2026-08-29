/**
 * ==========================================================================
 * ADMIN PORTAL MODULE (DASHBOARD, CHARTS, EVENT CRUD, PARTICIPANTS & CSV EXPORT)
 * ==========================================================================
 */

let regChartInstance = null;
let categoryChartInstance = null;
let currentEventParticipants = [];

// ==========================================================================
// ADMIN DASHBOARD
// ==========================================================================
async function loadAdminDashboard() {
  try {
    const [stats, events] = await Promise.all([
      api.get("/api/admin/dashboard"),
      api.get("/api/events")
    ]);

    // Update KPI Stat Cards
    const totalStudentsEl = document.getElementById("admin-stat-students");
    if (totalStudentsEl) totalStudentsEl.innerText = stats.total_students;

    const totalEventsEl = document.getElementById("admin-stat-events");
    if (totalEventsEl) totalEventsEl.innerText = stats.total_events;

    const upcomingEventsEl = document.getElementById("admin-stat-upcoming");
    if (upcomingEventsEl) upcomingEventsEl.innerText = stats.upcoming_events;

    const totalRegsEl = document.getElementById("admin-stat-registrations");
    if (totalRegsEl) totalRegsEl.innerText = stats.active_registrations;

    // Render Chart.js Analytics
    renderAdminCharts(stats);

    // Render Events Management Table
    renderAdminEventsTable(events);
  } catch (error) {
    showToast("Dashboard Error", error.message, "error");
  }
}

function renderAdminCharts(stats) {
  // 1. Registrations per Event Bar Chart
  const regCtx = document.getElementById("chart-registrations");
  if (regCtx && typeof Chart !== "undefined") {
    if (regChartInstance) regChartInstance.destroy();

    const labels = stats.registrations_by_event.map(e => e.title.length > 20 ? e.title.slice(0, 18) + "..." : e.title);
    const dataValues = stats.registrations_by_event.map(e => e.registrations);
    const capacityValues = stats.registrations_by_event.map(e => e.capacity);

    regChartInstance = new Chart(regCtx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Registered Students",
            data: dataValues,
            backgroundColor: "#4f46e5",
            borderRadius: 6
          },
          {
            label: "Total Capacity",
            data: capacityValues,
            backgroundColor: "#e2e8f0",
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "top" }
        },
        scales: {
          y: { beginAtZero: true, grid: { color: "#f1f5f9" } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  // 2. Events by Category Doughnut Chart
  const catCtx = document.getElementById("chart-categories");
  if (catCtx && typeof Chart !== "undefined") {
    if (categoryChartInstance) categoryChartInstance.destroy();

    const catLabels = stats.events_by_category.map(c => c.category);
    const catCounts = stats.events_by_category.map(c => c.count);

    const colors = [
      "#4f46e5", "#0ea5e9", "#10b981", "#f59e0b",
      "#8b5cf6", "#ec4899", "#f97316", "#64748b"
    ];

    categoryChartInstance = new Chart(catCtx, {
      type: "doughnut",
      data: {
        labels: catLabels,
        datasets: [
          {
            data: catCounts,
            backgroundColor: colors.slice(0, catLabels.length),
            borderWidth: 2,
            borderColor: "#ffffff"
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "right" }
        },
        cutout: "68%"
      }
    });
  }
}

function renderAdminEventsTable(events) {
  const tbody = document.getElementById("admin-events-tbody");
  if (!tbody) return;

  if (!events || events.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; padding: 2rem;">No events found. Click "Create Event" to add one.</td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = events.map(event => {
    return `
      <tr>
        <td>
          <div style="font-weight: 700; color: var(--text-main);">${event.title}</div>
          <div style="font-size: 0.8rem; color: var(--text-muted);">${event.organizer}</div>
        </td>
        <td>
          <span class="badge ${getCategoryBadgeClass(event.category)}">${event.category}</span>
        </td>
        <td>
          <div>${formatDate(event.event_date)}</div>
          <div style="font-size: 0.8rem; color: var(--text-muted);">${formatTime(event.start_time)} - ${formatTime(event.end_time)}</div>
        </td>
        <td>${event.venue}</td>
        <td><strong>${event.capacity}</strong></td>
        <td>
          <span class="badge ${event.registered_count >= event.capacity ? 'badge-danger' : 'badge-primary'}">
            ${event.registered_count}
          </span>
        </td>
        <td>
          ${event.is_past ? '<span class="badge badge-neutral">Completed</span>' : (event.is_full ? '<span class="badge badge-danger">Full</span>' : '<span class="badge badge-success">Active</span>')}
        </td>
        <td>
          <div class="action-btn-group">
            <a href="participants.html?id=${event.id}" class="action-btn view-btn" title="View Participants">
              👥 ${event.registered_count}
            </a>
            <a href="edit-event.html?id=${event.id}" class="action-btn edit-btn" title="Edit Event">
              ✏️
            </a>
            <button class="action-btn delete-btn" onclick="promptDeleteEvent(${event.id}, '${escapeHtml(event.title)}')" title="Delete Event">
              🗑️
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

function escapeHtml(str) {
  return (str || "").replace(/'/g, "\\'").replace(/"/g, "&quot;");
}

// ==========================================================================
// CREATE EVENT
// ==========================================================================
async function handleCreateEvent(event) {
  event.preventDefault();
  const form = event.target;
  const submitBtn = form.querySelector("button[type='submit']");

  const title = document.getElementById("title").value.trim();
  const description = document.getElementById("description").value.trim();
  const category = document.getElementById("category").value;
  const venue = document.getElementById("venue").value.trim();
  const eventDate = document.getElementById("event_date").value;
  const startTime = document.getElementById("start_time").value;
  const endTime = document.getElementById("end_time").value;
  const capacity = parseInt(document.getElementById("capacity").value, 10);
  const organizer = document.getElementById("organizer").value.trim();
  const imageUrl = document.getElementById("image_url").value.trim();

  // Validation
  if (!title || !description || !category || !venue || !eventDate || !startTime || !endTime || !capacity || !organizer) {
    showToast("Validation Error", "Please fill in all required fields.", "error");
    return;
  }

  if (capacity <= 0) {
    showToast("Invalid Capacity", "Capacity must be greater than 0.", "error");
    return;
  }

  if (startTime >= endTime) {
    showToast("Time Error", "End time must be after start time.", "error");
    return;
  }

  submitBtn.disabled = true;
  submitBtn.innerText = "Creating Event...";

  try {
    await api.post("/api/events", {
      title,
      description,
      category,
      venue,
      event_date: eventDate,
      start_time: startTime,
      end_time: endTime,
      capacity,
      organizer,
      image_url: imageUrl || null
    });

    showToast("Success!", "Event created successfully.", "success");
    setTimeout(() => {
      window.location.href = "admin-dashboard.html";
    }, 1000);
  } catch (error) {
    showToast("Failed to Create Event", error.message, "error");
    submitBtn.disabled = false;
    submitBtn.innerText = "Publish Event";
  }
}

// ==========================================================================
// EDIT EVENT
// ==========================================================================
async function loadEventForEdit() {
  const urlParams = new URLSearchParams(window.location.search);
  const eventId = urlParams.get("id");

  if (!eventId) {
    showToast("Error", "Event ID not provided", "error");
    window.location.href = "admin-dashboard.html";
    return;
  }

  try {
    const event = await api.get(`/api/events/${eventId}`);
    
    document.getElementById("event-id").value = event.id;
    document.getElementById("title").value = event.title;
    document.getElementById("description").value = event.description;
    document.getElementById("category").value = event.category;
    document.getElementById("venue").value = event.venue;
    document.getElementById("event_date").value = event.event_date;
    document.getElementById("start_time").value = event.start_time;
    document.getElementById("end_time").value = event.end_time;
    document.getElementById("capacity").value = event.capacity;
    document.getElementById("organizer").value = event.organizer;
    if (event.image_url) {
      document.getElementById("image_url").value = event.image_url;
      updateImagePreview(event.image_url);
    }
  } catch (error) {
    showToast("Error", "Could not load event for editing", "error");
    window.location.href = "admin-dashboard.html";
  }
}

async function handleEditEvent(event) {
  event.preventDefault();
  const form = event.target;
  const submitBtn = form.querySelector("button[type='submit']");
  const eventId = document.getElementById("event-id").value;

  const title = document.getElementById("title").value.trim();
  const description = document.getElementById("description").value.trim();
  const category = document.getElementById("category").value;
  const venue = document.getElementById("venue").value.trim();
  const eventDate = document.getElementById("event_date").value;
  const startTime = document.getElementById("start_time").value;
  const endTime = document.getElementById("end_time").value;
  const capacity = parseInt(document.getElementById("capacity").value, 10);
  const organizer = document.getElementById("organizer").value.trim();
  const imageUrl = document.getElementById("image_url").value.trim();

  if (startTime >= endTime) {
    showToast("Time Error", "End time must be after start time.", "error");
    return;
  }

  submitBtn.disabled = true;
  submitBtn.innerText = "Saving Changes...";

  try {
    await api.put(`/api/events/${eventId}`, {
      title,
      description,
      category,
      venue,
      event_date: eventDate,
      start_time: startTime,
      end_time: endTime,
      capacity,
      organizer,
      image_url: imageUrl || null
    });

    showToast("Updated!", "Event details updated successfully.", "success");
    setTimeout(() => {
      window.location.href = "admin-dashboard.html";
    }, 1000);
  } catch (error) {
    showToast("Update Failed", error.message, "error");
    submitBtn.disabled = false;
    submitBtn.innerText = "Save Changes";
  }
}

// Live Image URL Preview helper
function updateImagePreview(url) {
  const preview = document.getElementById("image-preview");
  if (preview) {
    if (url) {
      preview.src = url;
      preview.style.display = "block";
    } else {
      preview.style.display = "none";
    }
  }
}

// ==========================================================================
// DELETE EVENT
// ==========================================================================
async function promptDeleteEvent(eventId, eventTitle) {
  const confirmed = confirm(`Are you sure you want to permanently delete event "${eventTitle}"? All associated registrations will also be removed.`);
  if (!confirmed) return;

  try {
    await api.delete(`/api/events/${eventId}`);
    showToast("Event Deleted", "The event has been permanently deleted.", "info");
    loadAdminDashboard();
  } catch (error) {
    showToast("Delete Failed", error.message, "error");
  }
}

// ==========================================================================
// PARTICIPANTS ROSTER & CSV EXPORT
// ==========================================================================
async function loadParticipantsPage() {
  const urlParams = new URLSearchParams(window.location.search);
  const eventId = urlParams.get("id");

  if (!eventId) {
    showToast("Error", "Event ID not specified", "error");
    window.location.href = "admin-dashboard.html";
    return;
  }

  try {
    const summary = await api.get(`/api/admin/events/${eventId}/participants`);
    currentEventParticipants = summary.participants;

    const titleEl = document.getElementById("event-title-header");
    if (titleEl) titleEl.innerText = summary.title;

    const metaEl = document.getElementById("event-meta-summary");
    if (metaEl) metaEl.innerText = `${summary.total_participants} Registered Attendees • Capacity: ${summary.capacity}`;

    // Populate Department Filter options
    populateDepartmentFilter(summary.participants);

    renderParticipantsTable(summary.participants);
  } catch (error) {
    showToast("Error", error.message, "error");
  }
}

function populateDepartmentFilter(participants) {
  const deptSelect = document.getElementById("filter-dept");
  if (!deptSelect) return;

  const depts = new Set();
  participants.forEach(p => {
    if (p.department) depts.add(p.department);
  });

  deptSelect.innerHTML = `<option value="All">All Departments</option>` + 
    Array.from(depts).map(d => `<option value="${d}">${d}</option>`).join("");
}

function filterParticipantsList() {
  const search = (document.getElementById("search-participant") ? document.getElementById("search-participant").value : "").toLowerCase();
  const dept = document.getElementById("filter-dept") ? document.getElementById("filter-dept").value : "All";

  const filtered = currentEventParticipants.filter(p => {
    const matchSearch = p.student_name.toLowerCase().includes(search) ||
                        (p.student_id && p.student_id.toLowerCase().includes(search)) ||
                        p.email.toLowerCase().includes(search);
    const matchDept = (dept === "All") || (p.department === dept);
    return matchSearch && matchDept;
  });

  renderParticipantsTable(filtered);
}

function renderParticipantsTable(participants) {
  const tbody = document.getElementById("participants-tbody");
  const countEl = document.getElementById("filtered-count");
  if (countEl) countEl.innerText = participants.length;

  if (!tbody) return;

  if (participants.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
          No registered participants found matching your criteria.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = participants.map((p, index) => {
    const regDate = new Date(p.registration_date).toLocaleString("en-US", {
      dateStyle: "medium",
      timeStyle: "short"
    });

    return `
      <tr>
        <td>${index + 1}</td>
        <td>
          <strong>${p.student_name}</strong>
        </td>
        <td><code>${p.student_id || 'N/A'}</code></td>
        <td><a href="mailto:${p.email}">${p.email}</a></td>
        <td>${p.department || 'N/A'}</td>
        <td>${regDate}</td>
        <td>
          <span class="badge ${p.status === 'CONFIRMED' ? 'badge-success' : 'badge-danger'}">
            ${p.status}
          </span>
        </td>
      </tr>
    `;
  }).join("");
}

// Export CSV Functionality
function exportParticipantsCSV() {
  if (!currentEventParticipants || currentEventParticipants.length === 0) {
    showToast("Export Notice", "No participants to export.", "warning");
    return;
  }

  const eventTitle = document.getElementById("event-title-header") ? document.getElementById("event-title-header").innerText : "event";
  const filename = `${eventTitle.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_participants.csv`;

  const headers = ["Index", "Student Name", "Student ID", "Email", "Department", "Registration Date", "Status"];
  const rows = currentEventParticipants.map((p, idx) => [
    idx + 1,
    `"${p.student_name.replace(/"/g, '""')}"`,
    `"${(p.student_id || '').replace(/"/g, '""')}"`,
    `"${p.email}"`,
    `"${(p.department || '').replace(/"/g, '""')}"`,
    `"${new Date(p.registration_date).toISOString()}"`,
    `"${p.status}"`
  ]);

  const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  showToast("Export Complete", `Downloaded ${filename}`, "success");
}
