/**
 * ==========================================================================
 * USER PROFILE MODULE (VIEW PROFILE, EDIT PROFILE, STATS)
 * ==========================================================================
 */

async function loadUserProfilePage() {
  try {
    const [user, myRegs] = await Promise.all([
      api.get("/api/users/me"),
      api.get("/api/my-registrations")
    ]);

    setUser(user); // refresh stored profile

    // Populate profile card
    const nameEl = document.getElementById("profile-name");
    const emailEl = document.getElementById("profile-email");
    const sidEl = document.getElementById("profile-student-id");
    const deptEl = document.getElementById("profile-department");
    const roleBadgeEl = document.getElementById("profile-role-badge");
    const avatarEl = document.getElementById("profile-avatar-initial");
    const joinedEl = document.getElementById("profile-joined-date");
    const totalRegsEl = document.getElementById("profile-total-registrations");

    if (nameEl) nameEl.innerText = user.name;
    if (emailEl) emailEl.innerText = user.email;
    if (sidEl) sidEl.innerText = user.student_id || "N/A (Staff/Admin)";
    if (deptEl) deptEl.innerText = user.department || "General";
    if (roleBadgeEl) {
      roleBadgeEl.className = `badge ${user.role === 'ADMIN' ? 'badge-purple' : 'badge-primary'}`;
      roleBadgeEl.innerText = user.role;
    }
    if (avatarEl) {
      avatarEl.innerText = user.name ? user.name.charAt(0).toUpperCase() : "U";
    }

    if (joinedEl) {
      const joinDate = new Date(user.created_at).toLocaleDateString("en-US", {
        month: "long",
        day: "numeric",
        year: "numeric"
      });
      joinedEl.innerText = joinDate;
    }

    if (totalRegsEl) {
      const activeCount = myRegs.filter(r => r.status === "CONFIRMED").length;
      totalRegsEl.innerText = activeCount;
    }

    // Pre-fill edit modal form
    const editNameInput = document.getElementById("edit-name");
    const editDeptInput = document.getElementById("edit-department");
    const editSidInput = document.getElementById("edit-student-id");

    if (editNameInput) editNameInput.value = user.name;
    if (editDeptInput) editDeptInput.value = user.department || "";
    if (editSidInput) editSidInput.value = user.student_id || "";
  } catch (error) {
    showToast("Profile Error", error.message, "error");
  }
}

function openEditProfileModal() {
  const modal = document.getElementById("edit-profile-modal");
  if (modal) {
    modal.classList.add("active");
  }
}

function closeEditProfileModal() {
  const modal = document.getElementById("edit-profile-modal");
  if (modal) {
    modal.classList.remove("active");
  }
}

async function handleUpdateProfile(event) {
  event.preventDefault();
  const form = event.target;
  const submitBtn = form.querySelector("button[type='submit']");

  const name = document.getElementById("edit-name").value.trim();
  const department = document.getElementById("edit-department").value.trim();
  const studentId = document.getElementById("edit-student-id").value.trim();
  const password = document.getElementById("edit-password").value;

  if (!name) {
    showToast("Validation Error", "Name cannot be empty.", "error");
    return;
  }

  submitBtn.disabled = true;
  submitBtn.innerText = "Saving...";

  const payload = {
    name,
    department: department || null,
    student_id: studentId || null
  };

  if (password && password.length >= 6) {
    payload.password = password;
  }

  try {
    const updatedUser = await api.put("/api/users/me", payload);
    setUser(updatedUser);
    showToast("Profile Updated", "Your profile details have been saved.", "success");
    closeEditProfileModal();
    renderNavbar();
    loadUserProfilePage();
  } catch (error) {
    showToast("Update Failed", error.message, "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerText = "Save Changes";
  }
}
