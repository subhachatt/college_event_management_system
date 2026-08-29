/**
 * ==========================================================================
 * STUDENT DASHBOARD MODULE
 * ==========================================================================
 */

async function loadStudentDashboard() {
  const user = getUser();
  if (!user) return;

  // Personalized Greeting
  const greetingEl = document.getElementById("dashboard-greeting");
  if (greetingEl) {
    greetingEl.innerText = `Welcome back, ${user.name.split(" ")[0]}! 👋`;
  }

  const deptEl = document.getElementById("dashboard-dept");
  if (deptEl && user.department) {
    deptEl.innerText = `${user.department} • Student ID: ${user.student_id || 'N/A'}`;
  }

  try {
    // 1. Fetch all events & student registrations concurrently
    const [events, myRegistrations] = await Promise.all([
      api.get("/api/events", { date_filter: "upcoming" }),
      api.get("/api/my-registrations")
    ]);

    // Compute stats
    const totalUpcomingEvents = events.length;
    const activeRegistrations = myRegistrations.filter(r => r.status === "CONFIRMED");
    const upcomingRegistered = activeRegistrations.filter(r => !r.event.is_past);

    // Update Stat Cards
    const totalEventsCountEl = document.getElementById("stat-total-upcoming");
    if (totalEventsCountEl) totalEventsCountEl.innerText = totalUpcomingEvents;

    const myRegsCountEl = document.getElementById("stat-my-regs");
    if (myRegsCountEl) myRegsCountEl.innerText = activeRegistrations.length;

    const nextEventCountEl = document.getElementById("stat-upcoming-regs");
    if (nextEventCountEl) nextEventCountEl.innerText = upcomingRegistered.length;

    // Render Next Registered Event Spotlight (if any)
    const spotlightContainer = document.getElementById("next-event-spotlight");
    if (spotlightContainer) {
      if (upcomingRegistered.length > 0) {
        // Sort by date closest to today
        const nextEvent = upcomingRegistered[0].event;
        spotlightContainer.innerHTML = `
          <div class="card" style="border-left: 4px solid var(--primary); margin-bottom: 2rem;">
            <div class="card-body" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
              <div>
                <span class="badge badge-success" style="margin-bottom: 0.5rem;">Next Up On Your Calendar</span>
                <h3 style="margin-bottom: 0.25rem;">${nextEvent.title}</h3>
                <p style="margin: 0;">📅 ${formatDate(nextEvent.event_date)} at ${formatTime(nextEvent.start_time)} • 📍 ${nextEvent.venue}</p>
              </div>
              <a href="event-details.html?id=${nextEvent.id}" class="btn btn-primary btn-sm">
                View Event Pass →
              </a>
            </div>
          </div>
        `;
      } else {
        spotlightContainer.innerHTML = `
          <div class="card" style="background: var(--bg-subtle); border-style: dashed; margin-bottom: 2rem;">
            <div class="card-body" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
              <div>
                <h4 style="margin-bottom: 0.25rem;">No upcoming events registered</h4>
                <p style="margin: 0;">Discover thrilling workshops, cultural nights, and hackathons happening on campus.</p>
              </div>
              <a href="events.html" class="btn btn-primary btn-sm">
                Explore Events
              </a>
            </div>
          </div>
        `;
      }
    }

    // Render Upcoming Events Preview
    const previewGrid = document.getElementById("dashboard-events-preview");
    if (previewGrid) {
      renderEventsGrid(events.slice(0, 3), previewGrid);
    }
  } catch (error) {
    showToast("Dashboard Error", error.message, "error");
  }
}
