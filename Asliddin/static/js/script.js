function goToHome() {
    window.location.href = "index.html";
}

function viewBookings() {
    window.location.href = "bookings.html";
}

function goToSettings() {
    alert("Redirecting to Settings...");
}

function addService() {
    alert("Add Service Functionality Coming Soon...");
}

function filterByDate() {
    let selectedDate = document.getElementById("datePicker").value;
    alert("Filtering bookings for: " + selectedDate);
}
