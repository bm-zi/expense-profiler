const renderChart = (data, labels) => {
  var ctx = document.getElementById("myChart").getContext("2d");
  var myChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Expenses from the past 6 months",
          data: data,
          backgroundColor: [
            "rgb(75, 192, 192)", //teal
            "rgb(255, 99, 132)", //pink
            "rgb(54, 162, 235)", //blue
            "rgb(255, 206, 86)", //yellow
            "rgb(255, 159, 64)", //orange
            "rgb(153, 102, 255)", //purple
          ],
        },
      ],
    },
    options: {
      plugins: {
        title: {
          display: true,
          text: "Expenses per category",
        },
      },
    },
  });
};

const renderLineChart = (data, labels) => {
  var ctx = document.getElementById("lineChart").getContext("2d");
  var myChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Expenses by month",
          data: data,
          borderColor: "rgb(54, 162, 235)",
          borderWidth: "5",
        },
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
        },
        x: {
          title: {
            display: true,
            text: "Months ago",
          },
        },
      },
    },
  });
};

const getChartData = () => {
  fetch("/expense/expense-summary")
    .then((res) => res.json())
    .then((results) => {
      console.log(results);
      const category_data = results.expense_category_data;
      const [labels, data] = [
        Object.keys(category_data),
        Object.values(category_data),
      ];
      const month_data = results.expense_month_data;
      const [lineLabels, lineData] = [
        Object.keys(month_data),
        Object.values(month_data),
      ];

      renderChart(data, labels);
      renderLineChart(lineData, lineLabels);
    });
};

document.onload = getChartData();
