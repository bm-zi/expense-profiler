console.log("dashboardStats");

const renderChart = (incomeData, expenseData, labels) => {
  var ctx = document.getElementById("myChart").getContext("2d");
  var myChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels, // months
      datasets: [
        {
          label: "Income",
          data: incomeData,
          backgroundColor: [
            "rgb(255, 99, 132)", //pink
          ],
        },
        {
          label: "Expense",
          data: expenseData,
          backgroundColor: [
            "rgb(75, 192, 192)", //teal
          ],
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
      const expense_monthly_data = results.expense_month_data;
      const [labels, data] = [
        Object.keys(expense_monthly_data),
        Object.values(expense_monthly_data),
      ];
      fetch("/income/income-summary")
        .then((res) => res.json())
        .then((response) => {
          console.log(response);
          const income_monthly_data = response.income_month_data;

          const [incomeLabels, incomeData] = [
            Object.keys(income_monthly_data),
            Object.values(income_monthly_data),
          ];
          renderChart(incomeData, data, labels);
        });
    });
};

document.onload = getChartData();
