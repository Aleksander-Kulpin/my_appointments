// Select tables on Admin page

// Select table 1 on Admin page
function showFirstTableAdmin() {
  var x = document.getElementById("adminInfoTab");
  var y = document.getElementById("adminTemplateTab");
  var z = document.getElementById("adminSettingsTab");
  //One element - to show, other - to hide
  x.style.display = "block";
  y.style.display = "none";
  z.style.display = "none";
}

// Select table 2 on Admin page
function showSecondTableAdmin() {
  var x = document.getElementById("adminInfoTab");
  var y = document.getElementById("adminTemplateTab");
  var z = document.getElementById("adminSettingsTab");
  // One element - to show, other - to hide
  x.style.display = "none";
  y.style.display = "block";
  z.style.display = "none";
}

// Select table 3 on Admin page
function showThirdTableAdmin() {
  var x = document.getElementById("adminInfoTab");
  var y = document.getElementById("adminTemplateTab");
  var z = document.getElementById("adminSettingsTab");
  // One element - to show, other - to hide
  x.style.display = "none";
  y.style.display = "none";
  z.style.display = "block";
}

// Select tables on Specialist page

// Select table 1 on Specialist page
function showFirstTableSpecialist() {
  var x = document.getElementById("specialistRosterTab");
  var y = document.getElementById("specialistHistoryTab");
  // One element - to show, other - to hide
  x.style.display = "block";
  y.style.display = "none";
}

// Select table 2 on Specialist page
function showSecondTableSpecialist() {
  var x = document.getElementById("specialistRosterTab");
  var y = document.getElementById("specialistHistoryTab");
  // One element - to show, other - to hide
  x.style.display = "none";
  y.style.display = "block";
}

// Select tables on Client page

// Select table 1 on Client page
function showFirstTableClient() {
  var x = document.getElementById("clientSearchTab");
  var y = document.getElementById("clientScheduleTab");
  var z = document.getElementById("clientHistoryTab");
  // First element - to show other - to hide
  var x = document.getElementById("clientSearchTab");
  x.style.display = "block"
  y.style.display = "none"
  z.style.display = "none"
}

  // Select table 2 on Client page
function showSecondTableClient() {
  var x = document.getElementById("clientSearchTab");
  var y = document.getElementById("clientScheduleTab");
  var z = document.getElementById("clientHistoryTab");
  // First element - to show other - to hide
  var x = document.getElementById("clientSearchTab");
  x.style.display = "none"
  y.style.display = "block"
  z.style.display = "none"
}

    // Select table 3 on Client page
function showThirdTableClient() {
  var x = document.getElementById("clientSearchTab");
  var y = document.getElementById("clientScheduleTab");
  var z = document.getElementById("clientHistoryTab");
  // First element - to show other - to hide
  var x = document.getElementById("clientSearchTab");
  x.style.display = "none"
  y.style.display = "none"
  z.style.display = "block"
}



