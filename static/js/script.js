let performanceChart;
let attendanceChart;

function showPopup() {
  const popup = document.getElementById("popup");
  popup.style.display = "flex";
  document.querySelector("#popup button").focus();
}

function closePopup() {
  const popup = document.getElementById("popup");
  popup.style.display = "none";
  document.querySelector("form #name").focus();
}

document.addEventListener("DOMContentLoaded", () => {
  const messagesExist =
    document.getElementById("popup").dataset.messagesExist === "true";
  if (messagesExist) {
    showPopup();
  }
});

function updatePerformanceChart(id) {
  const year = document.getElementById("performance_year").value;
  fetch(`/get_performance_data/${id}?year=${year}`)
    .then((response) => response.json())
    .then((data) => {
      console.log(data);

      if (performanceChart) {
        performanceChart.data.labels = data.labels;
        performanceChart.data.datasets[0].data = data.ratings;
        performanceChart.update();
      } else {
        const ctx = document
          .getElementById("performanceChart")
          .getContext("2d");
        performanceChart = new Chart(ctx, {
          type: "bar",
          data: {
            labels: data.labels,
            datasets: [
              {
                label: "Performance Rating",
                data: data.ratings,
                backgroundColor: "rgba(54, 162, 235, 0.6)",
                borderColor: "rgba(54, 162, 235, 1)",
                borderWidth: 1,
                barThickness: 70,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: true,
                position: "bottom",
              },
              tooltip: {
                enabled: true,
              },
            },
            scales: {
              x: {
                title: {
                  display: true,
                  text: "Review Periods",
                  font: {
                    size: 16,
                  },
                },
              },
              y: {
                beginAtZero: true,
                max: 5,
                title: {
                  display: true,
                  text: "Rating (Out of 5)",
                  font: {
                    size: 16,
                  },
                },
              },
            },
          },
        });
      }
    })
    .catch((e) => {
      alert("Data unavailable !");
      const date = new Date();
      document.getElementById("performance_year").value = date.getFullYear();
    });
}

function updateAttendanceChart(id) {
  const year = document.getElementById("attendance_year").value;
  const month = document.getElementById("attendance_month").value;
  fetch(`/get_attendance_data/${id}?month=${month}&year=${year}`)
    .then((response) => response.json())
    .then((data) => {
      if (attendanceChart) {
        attendanceChart.data.labels = data.labels;
        attendanceChart.data.datasets[0].data = data.data;
        attendanceChart.update();
      } else {
        const ctx = document.getElementById("attendanceChart").getContext("2d");
        attendanceChart = new Chart(ctx, {
          type: "pie",
          data: {
            labels: data.labels,
            datasets: [
              {
                data: data.data,
                backgroundColor: [
                  "rgba(40, 100, 255, 0.7)",
                  "rgba(255, 40, 100, 0.7)",
                ],
                borderColor: ["rgba(40, 100, 255, 1)", "rgba(255, 40, 100, 1)"],
                borderWidth: 1,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: "bottom",
                labels: {
                  font: {
                    size: 14,
                  },
                },
              },
              tooltip: {
                callbacks: {
                  label: function (context) {
                    const total = context.dataset.data.reduce(
                      (a, b) => a + b,
                      0
                    );
                    const value = context.raw;
                    const percentage = ((value / total) * 100).toFixed(2);
                    return `${context.label}: ${value} days (${percentage}%)`;
                  },
                },
              },
            },
          },
        });
      }
    })
    .catch((e) => {
      alert("Data unavailable !");
      const date = new Date();
      document.getElementById("attendance_month").value = date.getMonth() + 1;
      document.getElementById("attendance_year").value = date.getFullYear();
    });
}
