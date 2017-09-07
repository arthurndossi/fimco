// Doughnut chart
new Chart($("#dailyChart"), {
  type: 'doughnut',
  data: {
    labels: ["Africa", "Asia", "Europe", "Latin America", "North America"],
    datasets: [
        {
          label: "Population (millions)",
          backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
          data: [2478,5267,734,784,433]
        }
    ]
  },
    options: {
      title: {
        display: true,
        text: 'Predicted world population (millions) in 2050'
      }
    }
});

// Bar chart
new Chart($("#balanceChart"), {
    type: 'bar',
    data: {
      labels: ["Africa", "Asia", "Europe", "Latin America", "North America"],
      datasets: [
        {
          label: "Population (millions)",
          backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
          data: [2478,5267,734,784,433]
        }
      ]
    },
    options: {
      legend: { display: false },
      title: {
        display: true,
        text: 'Predicted world population (millions) in 2050'
      }
    }
});

// Currency chart
new Chart($("#USDChart"), {
    type: 'line',
    data: {
      labels: ["January", "February", "March", "April", "May", "June", "July"],
      datasets: [
        {
          label: "Market data",
          data: [2178,2267,2234,2184,2233,2122,2231],
          borderColor: 'red',
          fill: false
        }
      ]
    },
    options: {
        showLines: true,
        scales: {
            yAxes: [{
                ticks: {
                    max: 3000,
                    min: 2000,
                    stepSize: 100
                }
            }]
        },
        animation: {
            duration: 1000
        },
        hover: {
            animationDuration: 1000
        },
        responsiveAnimationDuration: 500
    }
});