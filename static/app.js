const form = document.getElementById("appointment-form");
const message = document.getElementById("message");
const body = document.getElementById("appointments-body");
const cancelEditButton = document.getElementById("cancel-edit-button");

let appointments = [];

function showMessage(text, isError = false) {
    message.textContent = text;
    message.className = isError ? "error" : "success";
}

async function loadCustomers() {
    const response = await fetch("/api/customers");
    const customers = await response.json();
    const select = document.getElementById("customer-id");

select.innerHTML = `
        <option value="" disabled selected>בחר/י לקוח/ה</option>
        ${customers.map(customer => `
            <option value="${customer.customer_id}">
                ${customer.full_name} -${customer.id_number}
            </option>
        `).join("")}
    `;
}

async function loadAppointments() {
    const response = await fetch("/api/appointments");
    appointments = await response.json();

    if (!appointments.length) {
        body.innerHTML = `<tr><td colspan="7">לא נמצאו תורים.</td></tr>`;
        return;
    }

    body.innerHTML = appointments.map(appointment => `
        <tr>
            <td>${appointment.customer_name}</td>
            <td>
                <strong>${appointment.doctor_name}</strong><br>
                ${appointment.specialization}
            </td>
            <td>${appointment.clinic_name}</td>
            <td>${appointment.appointment_date}<br>${appointment.appointment_time}</td>
            <td>${appointment.appointment_type}</td>
            <td><span class="${appointment.status === 'בוטל' ? 'status-canceled' : 'status'}">${appointment.status}</span></td>
            <td>
                <div class="row-actions">
                    <button class="secondary"
                        onclick="startEdit(${appointment.appointment_id})"
                        ${appointment.status === "בוטל" ? "disabled" : ""}>
                        עדכון
                    </button>
                    <button class="danger"
                        onclick="cancelAppointment(${appointment.appointment_id})"
                        ${appointment.status === "בוטל" ? "disabled" : ""}>
                        ביטול
                    </button>
                </div>
            </td>
        </tr>
    `).join("");
}

function startEdit(id) {
    const appointment = appointments.find(item => item.appointment_id === id);
    if (!appointment) return;

    document.getElementById("appointment-id").value = appointment.appointment_id;
    document.getElementById("customer-id").value = appointment.customer_id;
    document.getElementById("customer-id").disabled = true;
    document.getElementById("doctor-name").value = appointment.doctor_name;
    document.getElementById("specialization").value = appointment.specialization;
    document.getElementById("clinic-name").value = appointment.clinic_name;
    document.getElementById("appointment-date").value = appointment.appointment_date;
    document.getElementById("appointment-time").value = appointment.appointment_time;
    document.getElementById("appointment-type").value = appointment.appointment_type;
    document.getElementById("notes").value = appointment.notes;

    document.getElementById("form-title").textContent = "עדכון תור";
    document.getElementById("submit-button").textContent = "שמרי שינויים";
    cancelEditButton.classList.remove("hidden");

    window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetForm() {
    form.reset();
    document.getElementById("appointment-id").value = "";
    document.getElementById("customer-id").disabled = false;
    document.getElementById("form-title").textContent = "קביעת תור חדש";
    document.getElementById("submit-button").textContent = "קבעי תור";
    cancelEditButton.classList.add("hidden");
}

async function cancelAppointment(id) {
    if (!confirm("האם לבטל את התור?")) return;

    const response = await fetch(`/api/appointments/${id}`, { method: "DELETE" });
    const result = await response.json();

    if (!response.ok) {
        showMessage(result.detail || "אירעה שגיאה", true);
        return;
    }

    showMessage(result.message);
    await loadAppointments();
}

form.addEventListener("submit", async event => {
    event.preventDefault();

    const appointmentId = document.getElementById("appointment-id").value;
    const formData = new FormData();

    if (!appointmentId) {
        formData.append("customer_id", document.getElementById("customer-id").value);
    }

    formData.append("doctor_name", document.getElementById("doctor-name").value);
    formData.append("specialization", document.getElementById("specialization").value);
    formData.append("clinic_name", document.getElementById("clinic-name").value);
    formData.append("appointment_date", document.getElementById("appointment-date").value);
    formData.append("appointment_time", document.getElementById("appointment-time").value);
    formData.append("appointment_type", document.getElementById("appointment-type").value);
    formData.append("notes", document.getElementById("notes").value);

    const url = appointmentId
        ? `/api/appointments/${appointmentId}`
        : "/api/appointments";

    const method = appointmentId ? "PUT" : "POST";
    const response = await fetch(url, { method, body: formData });
    const result = await response.json();

    if (!response.ok) {
        showMessage(result.detail || "אירעה שגיאה", true);
        return;
    }

    showMessage(result.message);
    resetForm();
    await loadAppointments();
});

cancelEditButton.addEventListener("click", resetForm);
document.getElementById("refresh-button").addEventListener("click", loadAppointments);

Promise.all([loadCustomers(), loadAppointments()])
    .catch(error => showMessage(`שגיאה בטעינת הנתונים: ${error.message}`, true));
